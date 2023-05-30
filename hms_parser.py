# HMS Parser - Parses metadata from an HMS project and the association simulations runs.
# The files asscoaited with an HMS project are similar to a YAML but is invalid, so it is parsed by finding headers and pulling the wanted nested fields from each header

import glob
import copy
import traceback
import yaml, json
import os
import argparse
from utils import get_wkt_crs
from datetime import datetime

def gage_file_parse(prj_dir, prj_name):
    gage_kv ={}
    # open the .gage file
    try:
        with open(os.path.join(prj_dir,f'{prj_name}.gage'), 'r') as r:
            gage_file = r.readlines()
    except EnvironmentError:
        print(f"Gage File not found: {gage_file}")

    gage_file = [s.strip('\n') for s in gage_file]
    # gage_file

    line_start = 0
    gageList = []
    for i,v in enumerate(gage_file):
            if v == 'End:':
                    # If not the beginning of the file, skip a blank line (+1) for the start of the subList.
                    if len(gageList) > 0:
                            gageList.append(gage_file[line_start+1:i])
                    else:
                            gageList.append(gage_file[line_start:i])
                    line_start = i+1
    
    # For each gage in .gage file, Get gage type and associated dss file name.
    gage_kv['Gage DSS Files'] ={}
    for gage in gageList:
        # get gage title
        title = gage[0].split(":")[1].strip()
        # Init ditionary for each gage title
        gage_kv['Gage DSS Files'][title] = {}
        # findList is used to search the wanted .gage file fields for each gage title.
        findList = ["Gage Type", "DSS File Name"]
        # search each gage for the keys in findList, append as key:value pairs for each gage title.
        for find_key in findList:
            found_value = [s for s in gage if find_key in s]
            
            # Omit blank fields by testing the length
            if len(found_value) > 0:
                found_value = found_value[0].split(":")[1:][0].strip()
                
                gage_kv['Gage DSS Files'][title][find_key] = found_value

        # Remove gage titles that did not contain the findList fields.
        if len(gage_kv['Gage DSS Files'][title]) == 0:
            del gage_kv['Gage DSS Files'][title]

        # get values from dictionary in to a list without the keys.
        temp_list = []
        for key, value in gage_kv['Gage DSS Files'].items():
            temp_list.append(value)

    # Get a list of unique DSS File values in a list.
    gage_dss_files = []
    for t in temp_list:
        gage_dss_files.append(t['DSS File Name'])
    gage_dss_files = list(set(gage_dss_files))

    # Create list in the format needed for the hms simulation json.
    gage_dss_json_list = []
    for dss_file in gage_dss_files:
        for key, value in gage_kv['Gage DSS Files'].items():
            # print (key, value)
            if gage_kv['Gage DSS Files'][key]['DSS File Name'] == dss_file:
                gage_dss_json_list.append(
                    {
                        "title": gage_kv['Gage DSS Files'][key]['Gage Type'] + " DSS File",
                        "source_dataset": None,
                        "location": dss_file,
                        "description": f"Parsed from {prj_name}.gage file"
                    }
                )
    # Remove duplicates from list
    gage_dss_json_list = [dict(t) for t in {tuple(d.items()) for d in gage_dss_json_list}]

    return gage_dss_json_list

def get_extra_dss_files(input_dss_dir):
    extra_dss_files_list = []
    for pFile in glob.glob(rf'{input_dss_dir}/*.dss'):
        extra_dss_files_list.append(pFile)

    # extra_dss_files_list
    dss_common_files_input = []
    if len(extra_dss_files_list)>0:
        for f in extra_dss_files_list:
            head, tail = os.path.split(f)
            dss_title = tail.split(".")[0]
            dss_common_files_input.append(
                {
                        "description": "User Added from Input DSS File Directory",
                        "location": f,
                        "source_dataset": None,
                        "title": dss_title
                },
            )

    return extra_dss_files_list

def parse_prj(prj, wkt, crs, extra_dss_files_list, output_dir):

    prj_dir, prj_file_tail = os.path.split(prj)
    prj_name = prj_file_tail.split(".")[0]
    
    try:
        with open(prj, "r") as f:
            lines = f.readlines()
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        print (f'.HMS file not found: {prj}')

    lines = [s.strip('\n') for s in lines]

    # Break up the file in to headers and fields by using the keyword "End:" to define blocks of text.
    nest_start = 0
    nestList = []
    for i,v in enumerate(lines):
            if v == 'End:':
                # If not the beginning of the file, skip a blank line (+1) for the start of the subList.
                if len(nestList) > 0:
                        nestList.append(lines[nest_start+1:i])
                else:
                        nestList.append(lines[nest_start:i])
                nest_start = i+1

    # Create a dictionary based on keys using unique headers with fields of Title, Filename, and Description
    kv = {}
    kv['Control Files'] = {}
    kv['Basin'] = {}
    kv['Precipitaion'] = {}
    
    # A list that defines which headers can be parsed the same way to obtain the wanted fields.
    headers_with_same_parsing = ['Control', 'Basin', 'Precipitation']
    
    # For each block of text as an item in nestList, parse headers and fields
    for subList in nestList:
        header = subList[0].split(":")[0]
        title = subList[0].split(":")[1]
        find_str = 'Description'
        description = [s for s in subList if find_str in s][0].split(":")[1:][0].strip()

        # The Project header is parsed differently from the headers in the list: headers_with_same_parsing
        if header == 'Project':
            find_str = 'File Name'
            filename = [s for s in subList if find_str in s][0].split(":")[1:][0].strip()
            kv['Project'] = {
                'Title': title,
                'Project Output DSS File': filename,
                'Description': description
            }
    
        # Search for any of the headers in headers_with_same_parsing and parse them.    
        if any(header == i for i in headers_with_same_parsing):
            find_str = 'filename'
            filename = [s for s in subList if find_str in s.lower()][0].split(":")[1:][0].strip()
            kv['Project'][title] = {
                'File Name': filename,
                'Description': description
            }
    
    # Add application_date from prj_file modified date
    modTimeUnix = os.path.getmtime(prj) 
    kv['application_date'] = datetime.fromtimestamp(modTimeUnix).strftime('%Y-%m-%d')

    # open the model application Json template, del unnecessary keys, update, add, export 
    with open(r"example\input\json\hms_model_application.json", 'r') as f:
                model_template_json = json.load(f)

    # keys to drop from json template
    drop_keys = ['_id', 'linked_resources', 'common_parameters', 'common_software_version', 'authors', 
    'spatial_extent_resolved', 'spatial_valid_extent_resolved', 'temporal_extent', 'temporal_resolution', 
    'spatial_valid_extent', 'common_files_details', 'grid']
    for key in drop_keys:
        del model_template_json[key]

    # set basic keywords
    model_template_json['keywords'] = ['hec-hms','hec','hms','hydrology','model','lwi']

    model_template_json['purpose'] = kv['Project']['Description']
    model_template_json['description'] = kv['Project']['Description']
    model_template_json['title'] = f"{kv['Project']['Title']} HEC-HMS Model"

    # common_files_details[]
    model_template_json['common_files_details'] = []
    model_template_json['common_files_details'].append(
        [{
            "description": "The HMS Project File",
            "location": prj_file_tail,
            "source_dataset": None,
            "title": "Project File"
        },
        {
            "description": "There may be multiple basins in the HMS model project",
            "location": f"{prj_name}/*.basin",
            "source_dataset": None,
            "title": "Basin Files"
        },
        {
            "description": "There may be multiple Meteorological Models",
            "location": f"{prj_name}/*.met",
            "source_dataset": None,
            "title": "Meteorological Model Files"
        },
        {
            "description": "There may be multiple control specifications.",
            "location": f"{prj_name}/*.control",
            "source_dataset": None,
            "title": "Control Specification Files"
        }]
    )

    # Add optional input DSS files list to list of input files.
    if extra_dss_files_list is not None:
        model_template_json['common_files_details'].extend(extra_dss_files_list)
    
    # open the .gage file and pull input dss files
    gage_dss_files = gage_file_parse(prj_dir,prj_name)
    model_template_json['common_files_details'].extend(gage_dss_files)
    
    # output model application json
    output_prj_json = os.path.join(output_dir,f'{prj_name}_model_application.json')
    with open(output_prj_json, "w") as outfile:
        json.dump(model_template_json, outfile)
    print (f'\nmodel_application file output to: {output_prj_json}')

def parse_runs(prj, output_dir):
    # Get project name
    prj_dir, prj_file_tail = os.path.split(prj)
    prj_name = prj_file_tail.split(".")[0]

    # Open .run file
    run_file_name = os.path.join(prj_dir,f'{prj_name}.run')
    try:
        with open(run_file_name, 'r') as r:
            run_file = r.readlines()
    except EnvironmentError:
        print (f'Run file not found: {run_file_name}')
    run_file = [s.strip('\n') for s in run_file]

    # Break run file into text blocks representing each Simulation as a list by the keyword "End:"
    line_start = 0
    runList = []
    for i,v in enumerate(run_file):
            if v == 'End:':
                    # If not the beginning of the file, skip a blank line (+1) for the start of the subList.
                    if len(runList) > 0:
                            runList.append(run_file[line_start+1:i])
                    else:
                            runList.append(run_file[line_start:i])
                    line_start = i+1
    
    # Parse each Simulation in the run file.
    sim_kv = {}
    for subList in runList:
        title = subList[0].split(":")[1].strip()
        # print(title)
        sim_kv[title] = {}
        # Create a list of fields to parse for each simulation.
        findList = ['Basin', 'DSS File', 'Precip', 'Control']
        for find_key in findList:
            found_value = [s for s in subList if find_key in s][0].split(":")[1:][0].strip()
            sim_kv[title][find_key] = found_value
            
            # Add data from each simulation's met file.
            if find_key == 'Precip':
                precip_name = sim_kv[title][find_key].replace(" ","_").replace("(","_").replace(")","_") + '.met'
                precip_file = os.path.join(prj_dir, precip_name)
                
                with open(precip_file, 'r') as p:
                    p_file = p.readlines()
                
                p_file  = [s.strip('\n') for s in p_file]
                p_findList = ['Description', 'Precipitation Method']
                
                for p_find_key in p_findList:
                    found_value = [s for s in p_file if p_find_key in s][0].split(":")[1:][0].strip()
                    sim_kv[title][f'Meteorology {p_find_key}'] = found_value
                    # if not found, set to None
                    if not f'Meteorology {p_find_key}' in sim_kv[title].keys():
                          sim_kv[title][f'Meteorology {p_find_key}']= None
                     
            
            # Add data from each simulation's control file.
            if find_key == 'Control':
                control_name = sim_kv[title][find_key].replace(" ","_").replace("(","_").replace(")","_") + '.control'
                control_file = os.path.join(prj_dir, control_name)
                
                with open(control_file, 'r') as c:
                    c_file = c.readlines()
                
                c_file  = [s.strip('\n') for s in c_file]
                c_findList = ['Description', 'Start Date', 'End Date', 'Time Interval']
                
                for c_find_key in c_findList:
                    found_value = [s for s in c_file if c_find_key in s][0].split(":")[1:][0].strip()
                    sim_kv[title][f'Control {c_find_key}'] = found_value
                    # if not found, set to None
                    if not f'Control {p_find_key}' in sim_kv[title].keys():
                          sim_kv[title][f'Control {p_find_key}']= None

            # Add data from each simulations's basin file
            parameterList = []
            if find_key == 'Basin':
                basin_name = sim_kv[title][find_key].replace(" ","_").replace("(","_").replace(")","_") + '.basin'
                basin_file = os.path.join(prj_dir, basin_name)

                with open(basin_file, 'r') as b:
                    b_file = b.readlines()
                # print (b_file)
                b_file  = [s.strip('\n') for s in b_file]

                line_start = 0
                basinList = []
                # print (b_file)
                for i,v in enumerate(b_file):
                    # print (v + '\n')
                    # if (v == 'Basin:'):
                         
                    if (v == 'End:'):
                        # print(i, v)
                        # If not the beginning of the file, skip a blank line (+1) for the start of the subList.
                        if len(basinList) > 0:
                                basinList.append(b_file[line_start+1:i])
                        else:
                                basinList.append(b_file[line_start:i])
                        line_start = i+1

                # find basin description
                for i, v in enumerate(basinList):
                    if ('Basin: ') in v[0]:
                        basinblock_index = i
                for basinblock_line in basinList[basinblock_index]:
                    if 'Description: ' in basinblock_line:
                        basin_description = basinblock_line.split('Description: ')[-1]
                        sim_kv[title]['Basin Description'] = basin_description  
                    else:                         
                    # if not found, set to None
                        sim_kv[title]['Basin Description']= None      
                                
                # List of Parameters to look for in each .basin file. Each Parameter will be added as a key to a temporary dictionary before formatting.
                b_findList = ['Canopy', 'LossRate', 'Transform', 'Baseflow', 'Route']
                params = {}
                # initialize empty lists for each parameter key
                for key in b_findList:
                        params[key] = []
                # For each line of each element block in a .basin file, look for each parameter (key) in b_findList 
                for el in basinList:
                    for line in el:
                        for key in b_findList:
                            
                            if f'{key}: ' in line:
                                # Append the parameter values to the parameter dictionary
                                params[key].append(line.split(': ')[-1])   
                            
                            # remove duplicates from each key's list of values
                            params[key] = list(set(params[key]))

                # Put parameters dictionary into the required Json format and add to kv dictionary for each run title.    
                for key in params.keys():
                    parameterList.append(
                        {
                            "parameter": key,
                            "value": params[key]
                        }
                    )
            
                sim_kv[title]['parameters'] = parameterList
        
        sim_kv[title]['parameters'].append(
                    {
                    "parameter": 'Precipitation Method',
                    "value": sim_kv[title]['Meteorology Precipitation Method']
                    }
            )
        # open the simulation Json template, del unnecessary keys, update, add, export 
        with open(r"example\input\json\hms_simulation.json", 'r') as f:
                    simulation_template_json = json.load(f)

        # keys to drop from json template
        drop_keys = ['_id', 'model_application', 'model_software', 'linked_resources','type']
        for key in drop_keys:
            del simulation_template_json[key]

        simulation_template_json['description'] = f"Basin: {sim_kv[title]['Basin']}, {sim_kv[title]['Basin Description']}. \
Meteorology: {sim_kv[title]['Precip']}, {sim_kv[title]['Meteorology Description']}. \
Control: {sim_kv[title]['Control']}, {sim_kv[title]['Control Description']}."
        simulation_template_json['title'] = f"{prj_name} HEC-HMS Simulation: {title}"
        simulation_template_json['output_files'] = [
            {
                "title": "Output DSS File",
                "source_dataset": None,
                "location": sim_kv[title]['DSS File'],
                "description": None
            }
        ]
        
        simulation_template_json['input_files'] = gage_file_parse(prj_dir, prj_name)
        simulation_template_json['input_files'].extend([
             {
                "title": "Basin File",
                "source_dataset": None,
                "location": basin_name,
                "description": sim_kv[title]['Basin Description']
            },
            {
                "title": "Meteorology File",
                "source_dataset": None,
                "location": precip_name,
                "description": sim_kv[title]['Meteorology Description']
            },
            {
                "title": "Control File",
                "source_dataset": None,
                "location": control_name,
                "description": sim_kv[title]['Control Description']
            },

        ])
        simulation_template_json['temporal_extent'] = [
            datetime.strptime(sim_kv[title]['Control Start Date'], '%d  %B %Y').strftime('%Y-%m-%d'),
            datetime.strptime(sim_kv[title]['Control End Date'], '%d  %B %Y').strftime('%Y-%m-%d')
        ]
    
        simulation_template_json["temporal_resolution"] = sim_kv[title]['Control Time Interval'] + ' Minutes'

        simulation_template_json["parameters"] = sim_kv[title]['parameters']    

        # output each simulation json
        output_sim_json = os.path.join(output_dir,f'{prj_name}_{title}_simulation.json')
        with open(output_sim_json, "w") as outfile:
            json.dump(simulation_template_json, outfile)
        print (f'{prj_name}_{title}_simulation.json')


def parse(prj, shp, dss):
    try:
        # Get project name
        prj_dir, prj_file_tail = os.path.split(prj)
        prj_name = prj_file_tail.split(".")[0]

        # Set output directory
        cwd = os.getcwd()
        output_dir = os.path.join(cwd, 'output', 'hms', prj_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get 

        # Get WKT and CRS from shp
        wkt, crs = get_wkt_crs.parse_shp(shp, prj_name, output_dir)

        # if args.dss, get dss input files
        if dss is not None:
            extra_dss_files_list = get_extra_dss_files(dss)
        else:
            extra_dss_files_list = None

        # Parse project file
        parse_prj(prj, wkt, crs, extra_dss_files_list, output_dir)

        # Run file parse
        parse_runs(prj, output_dir)

        # Return Successful Output message.
        msg = f'HMS Parsing Complete. Output files located at: {output_dir}'
        return msg
    
    except Exception: 
        msg = traceback.format_exc()
        # print(msg)
        return msg

if __name__ == '__main__':
    # Parse Command Line Arguments
    p = argparse.ArgumentParser(description="HEC-RAS metadata extraction. \
        Requires a RAS project file (*.prj) and an ESRI shapefile (*.shp) or GeoJson for the spatial boundary of the model.")
    
    p.add_argument(
    "--hms", help="The HEC-HMS project file. (Ex: C:\HMS_Models\Amite\Amite_HMS.hms)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--shp", help="The HEC-HMS model boundary spatial extent as an ESRI shapefile or GeoJson. \
        (Ex: C:\HMS_Models\Amite\maps\Amite_HMS_Basin_Outline.shp)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--dss", help="Optional. The directory containing any additonal input DSS files beyond what is linked in the .gage file for the HEC-HMS model such as Observed Timeseries, Reservoir Releases, Gridded Rainfall, or Specified Hyetogrpahs. \
        (Ex: C:\HMS_Models\Amite\data)", 
    required=False, 
    type=str
    )

    args = p.parse_args()
    parse(args.hms, args.shp, args.dss)