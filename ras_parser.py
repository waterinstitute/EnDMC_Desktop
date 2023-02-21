import glob
import copy
import yaml, json
import os
import argparse
import geopandas as gpd
from datetime import datetime
import h5py

def trimKeyValuePairsToDict(lines):

    keyValueList = copy.deepcopy(lines)  
    # Create a pop list of indices to remove because missing key=value pairs.
    popList = []
    
    for i,v in enumerate(keyValueList):
        if '=' not in v:
            popList.append(i)
    
    # Remove indices in popList
    for index in sorted(popList, reverse=True):
        del keyValueList[index]

    # Create dictionary from trimmed list
    keyValues_dict = dict(s.split('=',1) for s in keyValueList)
    
    return keyValues_dict, popList

def getDSSPaths(lines):
    # Get lines with 'DSS Filename'
    dss_file_lines= [[i,v] for i,v in enumerate(lines) if "DSS File" in v]
    
    # Get dss pathnames for each dss_file_line
    dss_file_and_paths = []
    for dss_file_line in dss_file_lines:
        # The line in the u file with a dss pathname is always +1 lines from the line specifying the DSS File.
        dss_pathname = lines[dss_file_line[0]+1]
        # Create a list of lists containing just the [[DSS Files, DSS Pathnames]]
        dss_file_and_paths.append([dss_file_line[1],dss_pathname])    

    return dss_file_and_paths

def dict_to_model_app_json(keyValues_dict, output_prj_json):    
        # Open ras_model_application Json template
        with open(r"example\input\json\ras_model_application.json", 'r') as f:
            ras_model_template_json = json.load(f)

        # keys to drop from json template
        drop_keys = ['_id', 'linked_resources', 'common_parameters', 'common_software_version', 'authors', 
        'spatial_extent_resolved', 'spatial_valid_extent_resolved', 'temporal_extent', 'temporal_resolution', 'spatial_valid_extent', 'common_files_details']
        for key in drop_keys:
            del ras_model_template_json[key]

        # set basic keywords
        ras_model_template_json['keywords'] = ['hec-ras','hec','ras','hydraulic','model','lwi']

        # Map to web-app Json
        ras_model_template_json['title'] = keyValues_dict['Proj Title']
        ras_model_template_json['description'] = keyValues_dict['Description']
        ras_model_template_json['purpose'] = keyValues_dict['Description']
        ras_model_template_json['simulations'] = keyValues_dict['Plans']
        ras_model_template_json['grid']['coordinate_system'] = keyValues_dict['coordinate_system']
        ras_model_template_json['spatial_extent'][0] = keyValues_dict['spatial_extent']
        ras_model_template_json['common_files_details'] = []
        ras_model_template_json['common_files_details'].append( {
            'source_dataset': None,
            'description': 'RAS project file which links projects with plans, geometry, and flow files',
            'location': keyValues_dict['Project File'],
            'title': 'prj file'
        })

        # output mapped json
        with open(output_prj_json, "w") as outfile:
            json.dump(ras_model_template_json, outfile)

def dict_to_sim_json(keyValues_dict, prj_name, p_file, output_p_json):
    # Open RAS Simulation Json Template 
    with open(r"C:\py\hec_meta_extract\example\input\json\ras_simulation.json", 'r') as f:
        ras_sim_template_json = json.load(f)

    # keys to drop
    drop_keys = ['_id', 'model_software', 'model_application', 'parameters', 
    'linked_resources', 'type', 'output_files']
    for key in drop_keys:
        del ras_sim_template_json[key]
    
    # Format Simulation Date to match web app format
    dt_raw = keyValues_dict['Simulation Date'].split(",")
    sDate_dt = datetime.strptime(dt_raw[0], '%d%b%Y')
    sDate_str = datetime.strftime(sDate_dt, '%Y-%m-%d')
    eDate_dt = datetime.strptime(dt_raw[2], '%d%b%Y')
    eDate_str = datetime.strftime(eDate_dt, '%Y-%m-%d')
    temporal_extent = [sDate_str, eDate_str]

    # Get pertinent filename numbers
    p_num = p_file.split(".")[-1][1:]
    g_num = keyValues_dict['Geom File'][1:]
    u_num = keyValues_dict['Flow File'][1:]

    # Get Unique input DSS files
    dss_input_file_list = [el[0] for el in keyValues_dict['DSS Input Files']]
    list_unique = list(set(dss_input_file_list))

    # Parsing out variations of DSS Filenames and Titles
    input_files = []
    for i in list_unique:
        j = i.split("=")
        if len(j) == 3:
            input_files.append(
                {
                    "title": j[0]+" "+j[1],
                    "location": j[-1],
                    "description": j[0]+" "+j[1],
                    "source_dataset": None
                }
            )
        else:
            input_files.append(
                {
                    "title": j[0],
                    "location": j[-1],
                    "description": j[0],
                    "source_dataset": None
                }
            )
    
    # Extending input files list with common files
    input_files.extend(
        [{
            "title": "Terrain",
            "location": keyValues_dict['terrain'],
            "description": "Terrain used by model",
            "source_dataset": None
        },
        {
            "title": "b file",
            "location": 'f{prj_name}.b{p_num}',
            "description": "RAS master input text file",
            "source_dataset": None
        },
        {
            "title": "g file",
            "location": f"{prj_name}.{keyValues_dict['Geom File']}",
            "description": "RAS geometry file",
            "source_dataset": None
        },
        {
            "title": "prj file",
            "location": f'{prj_name}.prj',
            "description": "RAS project file which links projects with plans, geometry, and flow files",
            "source_dataset": None
            },
        {
            "title": "c file",
            "location": f"{prj_name}.c{g_num}",
            "description": "Binary Geometry file from Geom Prep",
            "source_dataset": None
        },
        {
            "title": "x file",
            "location": f"{prj_name}.x{g_num}",
            "description": "Geometry master input text file",
            "source_dataset": None
        },
        {
            "title": "p file",
            "location": f"{prj_name}.p{p_num}",
            "description": "Model plan data",
            "source_dataset": None
        },
        {
            "title": "u file",
            "location": f"{prj_name}.u{u_num}",
            "description": "unsteady flow file",
            "source_dataset": None
        },
        {
            "title": "u hdf file",
            "location": f"{prj_name}.u{u_num}.hdf",
            "description": "unsteady flow file in HDF format",
            "source_dataset": None
        }]
    )

    # Map from yaml format to json format

    ras_sim_template_json['title'] = keyValues_dict['Plan Title']
    try:
        ras_sim_template_json['description'] = keyValues_dict['Description']
    except:
        print (f'No Description found for: {p_file}.')
    ras_sim_template_json['temporal_extent'] = temporal_extent
    ras_sim_template_json['temporal_resolution'] = keyValues_dict['Computation Interval']
    ras_sim_template_json['output_files'] = [
        {
                "title": "output dss file",
                "location": keyValues_dict['DSS Output File'],
                "description": "output model data in dss",
                "source_dataset": None
            },
            {
                "title": "p hdf file",
                "location": f"{prj_name}.p{p_num}.hdf",
                "description": "result output in HDF format",
                "source_dataset": None
            }
    ]

    ras_sim_template_json['input_files'] = input_files

    # Output json
    with open(output_p_json, "w") as outfile:
        json.dump(ras_sim_template_json, outfile)


def parse_prj(prj_file, prj_name, wkt, crs, plan_titles, output_dir):
    output_prj_yaml = os.path.join(output_dir, f'{prj_name}_ras_prj.yml')
    output_prj_json = os.path.join(output_dir, f'{prj_name}_ras_model_application.json')

    with open(prj_file, "r") as f:
        lines = f.readlines()
    
    lines = [s.strip('\n') for s in lines]
    keyValues_dict, popList = trimKeyValuePairsToDict(lines)

    # Remove unneeded keys
    # for key, value in keyValues_dict.items() :
    #     print (key)
    popKeys = ['Current Plan', 'Default Exp/Contr','Geom File',
    'Unsteady File','Plan File','Background Map Layer','Y Axis Title',
    'X Axis Title(PF)','X Axis Title(XS)','DSS Start Date',
    'DSS Start Time','DSS End Date','DSS End Time','DXF Filename',
    'DXF OffsetX','DXF OffsetY','DXF ScaleX','DXF ScaleY']
    
    for key in popKeys:
        try:
            del keyValues_dict[key]
        except:
            continue

    # Add specific popList lines from prj file to keyValue_dict
    for i,v in enumerate(popList):
        if "BEGIN DESCRIPTION:" in lines[v]:
            description = lines[v+1]

    keyValues_dict['Description'] = description

    # Update project title
    keyValues_dict['Proj Title'] = f'{prj_name} HEC-RAS Model'
    # Add project file location
    keyValues_dict['Project File'] = prj_file

    # Add spatial_extent and coordinate_system from wkt and crs.
    keyValues_dict["spatial_extent"] = wkt
    keyValues_dict["coordinate_system"] = crs

    # Add plan titles
    keyValues_dict["Plans"] = plan_titles

    # Add application_date from prj_file modified date
    modTimeUnix = os.path.getmtime(prj_file) 
    keyValues_dict['application_date'] = datetime.fromtimestamp(modTimeUnix).strftime('%Y-%m-%d')

    with open(output_prj_yaml, 'w+') as f:
        yaml.dump(keyValues_dict, f)
    
    dict_to_model_app_json(keyValues_dict, output_prj_json)


def parse_shp(shp, prj_name, output_dir):
    gdf = gpd.read_file(shp)
    crs = str(gdf.crs)
    gdf = gdf.to_crs(4326)
    wkt = gdf.to_wkt().geometry[0]
    wkt_dict = {}
    wkt_dict["spatial_extent"] = wkt
    wkt_dict["coordinate_system"] = crs

    with open(os.path.join(output_dir, f'{prj_name}_ras_wkt.yml'), 'w+') as f:
        yaml.dump(wkt_dict, f)
    
    return wkt, crs


def get_p_files(prj_dir, prj_name):
    # prj = 'Z:\Amite\Amite_LWI\Models\Amite_RAS\Amite_2022.prj'
    # prj_dir, prj_file_tail = os.path.split(prj)
    # prj_name = prj_file_tail.split(".")[0]
    pList = []

    for pFile in glob.glob(r'Z:\Amite\Amite_LWI\Models\Amite_RAS\*.p' + '[0-9]' * 2):
        prj_dir, p_file_tail = os.path.split(pFile)
        p_file_prj_name = p_file_tail.split(".")[0]
        if p_file_prj_name == prj_name:
            pList.append(pFile)

    return pList


def parse_p(p_file_list, prj_name, wkt, crs, output_dir):
    
    plan_titles = []
    for p in p_file_list:
        # print (p)
        prj_dir, p_file_tail = os.path.split(p)
        print (p_file_tail)
        with open(p, "r") as f:
            # print(f.readlines())
            lines = f.readlines()
        
        lines = [s.strip('\n') for s in lines]

        # Create Dictionary
        keyValues_dict, popList = trimKeyValuePairsToDict(lines)

        # Add specific popList lines from prj file to keyValue_dict
        for i,v in enumerate(popList):
            if "BEGIN DESCRIPTION:" in lines[v]:
                description = lines[v+1]
                keyValues_dict['Description'] = description
        
        # Add spatial_extent and coordinate_system from wkt and crs
        keyValues_dict["spatial_extent"] = wkt
        keyValues_dict["coordinate_system"] = crs

        # Get associated geometry file
        geom_file_extension = keyValues_dict['Geom File']
        geom_file = os.path.join(prj_dir, prj_name +"."+ geom_file_extension)
        with open(geom_file, "r") as f:
            geom_lines = f.readlines()
        geom_lines = [s.strip('\n') for s in geom_lines]

        # Create geometry Dictionary
        geom_keyValues_dict, geom_popList = trimKeyValuePairsToDict(geom_lines)

        # Add Specified key value pairs from geom file to p file.
        keyValues_dict['Geom Title'] = geom_keyValues_dict['Geom Title']

        # Get associated u flow file
        flow_file_extension = keyValues_dict['Flow File']
        flow_file = os.path.join(prj_dir, prj_name +"."+ flow_file_extension)
        with open(flow_file, "r") as f:
            flow_lines = f.readlines()
        flow_lines = [s.strip('\n') for s in flow_lines]

        # Create flow file Dictionary
        flow_keyValues_dict, flow_popList = trimKeyValuePairsToDict(flow_lines)

        # Get associated plan hdf file
        with h5py.File(r"Z:\Amite\Amite_LWI\Models\Amite_RAS\Amite_20200114.p07.hdf", "r") as f:
            terrain = f['Geometry'].attrs['Terrain Filename'].decode('UTF-8')
        keyValues_dict['terrain'] = terrain

         # Get Input DSS files and paths from flow file to p file.
        dss_file_and_paths = getDSSPaths(flow_lines)
        keyValues_dict['DSS Input Files'] = dss_file_and_paths

        # Add Specified key value pairs from flow file to p file.
        keyValues_dict['Flow Title'] = flow_keyValues_dict['Flow Title']

        # Append plan title list
        keyValues_dict['Plan Title'] = f"{prj_name} HEC-RAS Model Simulation: {keyValues_dict['Plan Title']}"
        plan_titles.append(keyValues_dict['Plan Title'])

        # Set dss output file to default path
        keyValues_dict['DSS Output File'] = f'{prj_name}.dss'

        # Write the output yaml for each .p## file.
        with open(os.path.join(output_dir,f'{p_file_tail}.yml'), 'w+') as f:
            yaml.dump(keyValues_dict, f)
        
        # Write output Json for each .p## file.
        output_p_json = os.path.join(output_dir,f'{p_file_tail}.json')
        dict_to_sim_json(keyValues_dict, prj_name, p, output_p_json)

    return plan_titles

def parse(prj, shp):

    # Get project name
    prj_dir, prj_file_tail = os.path.split(prj)
    prj_name = prj_file_tail.split(".")[0]

    # Set output directory
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'output', 'ras', prj_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get WKT and CRS from shp
    wkt, crs = parse_shp(shp, prj_name, output_dir)

    # Get .p## files in prj_dir
    p_file_list = get_p_files(prj_dir, prj_name)
    
    # Parse p files and include data from geometry, flow files. and add wkt. 
    # Returns the plan titles of each p file as a list.
    plan_titles = parse_p(p_file_list, prj_name, wkt, crs, output_dir)

    # Parse prj, remove extra fields, add list of p file titles, and wkt.
    parse_prj(prj, prj_name, wkt, crs, plan_titles, output_dir)

if __name__ == '__main__':
    # Parse Command Line Arguments
    p = argparse.ArgumentParser(description="HEC-RAS metadata extraction. \
        Requires a RAS project file (*.prj) and an ESRI shapefile (*.shp) for the spatial boundary of the model.")
    
    p.add_argument(
    "--prj", help="The HEC-RAS project file. (Ex: C:\RAS_Models\Amite\Amite_2022.prj)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--shp", help="The HEC-RAS model boundary spatial extent as ESRI shapefile. \
        (Ex: C:\RAS_Models\Amite\Features\Amite_Optimized_Geometry.shp)", 
    required=True, 
    type=str
    )

    args = p.parse_args()
    parse(args.prj, args.shp)