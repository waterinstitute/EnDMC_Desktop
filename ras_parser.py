import glob
import copy
import traceback
import yaml
import json
import os
import argparse
from datetime import datetime
import h5py
from utils import get_wkt_crs, trimmer, get_schema_keys


def get_ras_prj_wkt(p_file):
    # Open a plan hdf file, get WKT from it.
    try:
        with h5py.File(f'{p_file}.hdf', "r") as f:
            ras_prj_wkt = f.attrs['Projection'].decode('UTF-8')
            # print (f'Extracted spatial projection from HDF: {ras_prj_wkt}')
    except:
        print(f'''
               Unable to extract spatial projection from HDF plan file:
               {p_file}.hdf
               May have to manually specify .shp projection using a GIS.''')

    return ras_prj_wkt


def getDSSPaths(lines):
    # Get lines with 'DSS Filename'
    dss_file_lines = [[i, v] for i, v in enumerate(lines) if "DSS File" in v]

    # Get dss pathnames for each dss_file_line
    dss_file_and_paths = []
    for dss_file_line in dss_file_lines:
        # The line in the u file with a dss pathname is always +1 lines from the line specifying the DSS File.
        dss_pathname = lines[dss_file_line[0]+1]
        # Create a list of lists containing just the [[DSS Files, DSS Pathnames]]
        dss_file_and_paths.append([dss_file_line[1], dss_pathname])

    return dss_file_and_paths


def dict_to_model_app_json(keyValues_dict, output_prj_json, args, model_application_key_order):
    # Open ras_model_application Json template
    with open(r"example\input\json\ras_model_application.json", 'r') as f:
        ras_model_template_json = json.load(f)

    # keys to drop from json template
    drop_keys = ['_id', 'linked_resources', 'common_parameters', 'common_software_version', 'authors',
                 'spatial_extent_resolved', 'spatial_valid_extent_resolved', 'temporal_extent', 'temporal_resolution', 'spatial_valid_extent', 'common_input_files', 'common_output_files']
    for key in drop_keys:
        del ras_model_template_json[key]

    # set basic keywords
    ras_model_template_json['keywords'] = [
        'hec-ras', 'hec', 'ras', 'hydraulic', 'model']
    # Add any optional keywords
    try:
        if args.keywords is not None and len(args.keywords[0]) > 0:
            ras_model_template_json['keywords'].extend(args.keywords)
        if args.id is not None and len(args.id[0]) > 0:
            ras_model_template_json['keywords'].append(args.id)
    except:
        pass

    # Map to web-app Json
    ras_model_template_json['title'] = keyValues_dict['Proj Title']
    ras_model_template_json['description'] = {}
    ras_model_template_json['description']['Project Description'] = keyValues_dict['Description']
    # join simulation titles as a single string from the list in keyValues_dict['Plans']['Plan Title']
    ras_model_template_json['description']['Simulations'] = ', '.join(keyValues_dict['Plans']['Plan Title'])
    # join description keys and values
    ras_model_template_json['description'] = ' '.join(
        [f'\n{k}: {v}' for k, v in ras_model_template_json['description'].items()])
    # trim first and last newline characters
    ras_model_template_json['description'] = ras_model_template_json['description'].strip('\n')
    ras_model_template_json['purpose'] = keyValues_dict['Description']
    ras_model_template_json['grid']['coordinate_system'] = keyValues_dict['coordinate_system']
    ras_model_template_json['spatial_extent'][0] = keyValues_dict['spatial_extent']
    ras_model_template_json['common_input_files'] = []
    ras_model_template_json['common_output_files'] = []
    ras_model_template_json['common_input_files'].extend([{
        'title': 'Model Project file',
        'source_dataset': None,
        'description': 'HEC-RAS project file which links projects with plans, geometry, and flow files',
        'location': keyValues_dict['Project File'],
    },
    {
        'title': 'Model Boundary',
        'source_dataset': None,
        'description': 'TThe HEC-RAS model boundary spatial extent',
        'location': keyValues_dict['shp'],
    
    }])

    # Add each p file to common_file_details
    plan_zipList = zip(
        keyValues_dict['Plans']['Plan Title'], keyValues_dict['Plans']['P File'])
    for plan in plan_zipList:
        ras_model_template_json['common_output_files'].append({
            'title': f"p file for {plan[0]}",
            'source_dataset': None,
            'description': plan[0],
            'location': plan[1],
        })

    # use key order to sort output json
    ras_model_template_json = {k: ras_model_template_json[k] for k in model_application_key_order if k in ras_model_template_json.keys()}

    # Output mapped json
    with open(output_prj_json, "w") as outfile:
        json.dump(ras_model_template_json, outfile, indent=4)


def dict_to_sim_json(keyValues_dict, prj_name, p_file, output_p_json, simulation_key_order, layers_wanted):
    # Open RAS Simulation Json Template
    cwd = os.getcwd()
    with open(r"example\input\json\ras_simulation.json", 'r') as f:
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
                    "source_dataset": None,
                    "description": j[0]+" "+j[1],
                    "location": j[-1],
                }
            )
        else:
            input_files.append(
                {
                    "title": j[0],
                    "source_dataset": None,
                    "description": j[0],
                    "location": j[-1],
                }
            )

    # Add additional input files for layers_wanted found in plan hdf
    for layer in layers_wanted:
        layer = layer.replace(' Filename', '').lower()
        if keyValues_dict[layer] is not None:
            input_files.append(
                {
                    "title": layer.capitalize(),
                    "source_dataset": None,
                    "description": layer + " used by plan",
                    "location": keyValues_dict[layer],
                }
            )



    input_files.extend(
        [{
            "title": "prj file",
            "source_dataset": None,
            "description": "RAS project file which links projects with plans, geometry, and flow files",
            "location": f'{prj_name}.prj',
        },
        {
            "title": "Model Boundary",
            "source_dataset": None,
            "description": "The HEC-RAS model boundary spatial extent",
            "location": keyValues_dict['shp'],
        },
        {
            "title": "b file",
            "source_dataset": None,
            "description": "RAS master input text file",
            "location": f'{prj_name}.b{p_num}',
        },
            {
            "title": "g file",
            "source_dataset": None,
            "description": "RAS geometry file",
            "location": f"{prj_name}.{keyValues_dict['Geom File']}",
        },
            {
            "title": "c file",
            "source_dataset": None,
            "description": "Binary Geometry file from Geom Prep",
            "location": f"{prj_name}.c{g_num}",
        },
            {
            "title": "x file",
            "source_dataset": None,
            "description": "Geometry master input text file",
            "location": f"{prj_name}.x{g_num}",
        },
            {
            "title": "u file",
            "source_dataset": None,
            "description": "unsteady flow file",
            "location": f"{prj_name}.u{u_num}",
        },
            {
            "title": "u hdf file",
            "source_dataset": None,
            "description": "unsteady flow file in HDF format",
            "location": f"{prj_name}.u{u_num}.hdf",
        }]
    )

    # Map to json format

    ras_sim_template_json['title'] = keyValues_dict['Plan Title']
    try:
        ras_sim_template_json['description'] = keyValues_dict['Description']
    except:
        print(f'No Description found for: {p_file}.')
    ras_sim_template_json['temporal_extent'] = temporal_extent
    ras_sim_template_json['temporal_resolution'] = keyValues_dict['Computation Interval']
    ras_sim_template_json['output_files'] = [
        {
            "title": "output dss file",
            "source_dataset": None,
            "description": "output model data in dss",
            "location": keyValues_dict['DSS Output File'],
        },
        {
            "title": "p file",
            "source_dataset": None,
            "description": "Model plan data",
            "location": f"{prj_name}.p{p_num}",
        },
        {
            "title": "p hdf file",
            "source_dataset": None,
            "description": "result output in HDF format",
            "location": f"{prj_name}.p{p_num}.hdf",
        }
    ]

    ras_sim_template_json['input_files'] = input_files

    # use key order to sort output json
    ras_sim_template_json = {k: ras_sim_template_json[k] for k in simulation_key_order if k in ras_sim_template_json.keys()}

    # Output json
    with open(output_p_json, "w") as outfile:
        json.dump(ras_sim_template_json, outfile, indent=4)


def parse_prj(args, prj_name, wkt, crs, plan_titles, output_dir, model_application_key_order):
    # output_prj_yaml = os.path.join(output_dir, f'{prj_name}_ras_prj.yml')
    output_prj_json = os.path.join(
        output_dir, f'{prj_name}_ras_model_application.json')

    with open(args.prj, "r") as f:
        lines = f.readlines()

    lines = [s.strip('\n') for s in lines]
    keyValues_dict, popList = trimmer.trim(lines)

    # Remove unneeded keys
    # for key, value in keyValues_dict.items() :
    #     print (key)
    popKeys = ['Current Plan', 'Default Exp/Contr', 'Geom File',
               'Unsteady File', 'Plan File', 'Background Map Layer', 'Y Axis Title',
               'X Axis Title(PF)', 'X Axis Title(XS)', 'DSS Start Date',
               'DSS Start Time', 'DSS End Date', 'DSS End Time', 'DXF Filename',
               'DXF OffsetX', 'DXF OffsetY', 'DXF ScaleX', 'DXF ScaleY']

    for key in popKeys:
        try:
            del keyValues_dict[key]
        except:
            continue

    # Add specific popList lines from prj file to keyValue_dict
        beginDescriptionIndex = None
        endDescriptionIndex = None
    for i, v in enumerate(popList):
        if "BEGIN DESCRIPTION:" in lines[v]:
            beginDescriptionIndex = v+1
        if "END DESCRIPTION:" in lines[v]:
            endDescriptionIndex = v

    if beginDescriptionIndex and endDescriptionIndex is not None:
        description = ' '.join(
            lines[beginDescriptionIndex:endDescriptionIndex])
    else:
        description = None

    keyValues_dict['Description'] = description

    # Update project title
    keyValues_dict['Proj Title'] = f'{prj_name} HEC-RAS Model'

    # Get root project directory from args.prj
    prj_dir = os.path.dirname(args.prj)
    
    # Get parent directory of prj_dir
    prj_parent_dir = os.path.dirname(prj_dir)
   
   # get project file and shp location relative to prj_parent_dir
    prj_file = args.prj.replace(prj_parent_dir, '').replace('\\', '/')
    shp_file = args.shp.replace(prj_parent_dir, '').replace('\\', '/')
    
    # Add processed variables keyValues_dict
    keyValues_dict['Project File'] = prj_file
    keyValues_dict['shp'] = shp_file
    keyValues_dict["Plans"] = plan_titles
    keyValues_dict["spatial_extent"] = wkt
    keyValues_dict["coordinate_system"] = crs

    # Add application_date from args.prj modified date
    modTimeUnix = os.path.getmtime(args.prj)
    keyValues_dict['application_date'] = datetime.fromtimestamp(
        modTimeUnix).strftime('%Y-%m-%d')

    dict_to_model_app_json(keyValues_dict, output_prj_json, args, model_application_key_order)


def get_p_files(prj_dir, prj_name):
    pList = []

    for pFile in glob.glob(rf'{prj_dir}/*.p' + '[0-9]' * 2):
        prj_dir, p_file_tail = os.path.split(pFile)
        # check if the p file is associated with the project name. project name may have multiple periods.
        p_file_prj_name = '.'.join(p_file_tail.split(".")[:-1])
        if p_file_prj_name == prj_name:
            pList.append(pFile)

    return pList


def parse_p(p_file_list, prj_name, wkt, crs, output_dir, args, simulation_key_order):

    plan_titles = {}
    plan_titles['Plan Title'] = []
    plan_titles['Plan Title w P File'] = []
    plan_titles['P File'] = []
    for p in p_file_list:
        # print (p)
        prj_dir, p_file_tail = os.path.split(p)
        print(p_file_tail)
        with open(p, "r") as f:
            # print(f.readlines())
            lines = f.readlines()

        lines = [s.strip('\n') for s in lines]

        # Create Dictionary
        keyValues_dict, popList = trimmer.trim(lines)

        # Add specific popList lines from prj file to keyValue_dict
        beginDescriptionIndex = None
        endDescriptionIndex = None
        for v in popList:
            if "BEGIN DESCRIPTION:" in lines[v]:
                beginDescriptionIndex = v+1
            if "END DESCRIPTION:" in lines[v]:
                endDescriptionIndex = v


        if beginDescriptionIndex and endDescriptionIndex is not None:
            description = ' '.join(
                lines[beginDescriptionIndex:endDescriptionIndex])
        else:
            description = None

        keyValues_dict['Description'] = description

        # Add spatial_extent and coordinate_system from wkt and crs
        keyValues_dict["spatial_extent"] = wkt
        keyValues_dict["coordinate_system"] = crs

        # Get associated geometry file
        geom_file_extension = keyValues_dict['Geom File']
        geom_file = os.path.join(prj_dir, prj_name + "." + geom_file_extension)
        with open(geom_file, "r") as f:
            geom_lines = f.readlines()
        geom_lines = [s.strip('\n') for s in geom_lines]

        # Create geometry Dictionary
        geom_keyValues_dict, geom_popList = trimmer.trim(geom_lines)

        # Add Specified key value pairs from geom file to p file.
        keyValues_dict['Geom Title'] = geom_keyValues_dict['Geom Title']

        # Get associated u flow file
        flow_file_extension = keyValues_dict['Flow File']
        flow_file = os.path.join(prj_dir, prj_name + "." + flow_file_extension)
        with open(flow_file, "r") as f:
            flow_lines = f.readlines()
        flow_lines = [s.strip('\n') for s in flow_lines]

        # Create flow file Dictionary
        flow_keyValues_dict, flow_popList = trimmer.trim(flow_lines)

        # Get associated plan hdf file
        try:
            with h5py.File(rf"{p}.hdf", "r") as f:
                # get the terrain, inifiltration, land cover, and percent impervious filenames if available.
                layers_wanted = ['Terrain Filename', 'Infiltration Filename', 'Land Cover Filename', 'Percent Impervious Filename']
                for layer in layers_wanted:
                    try:
                        layer_filename = f['Geometry'].attrs[layer].decode('UTF-8')
                        layer = layer.replace(' Filename', '')
                        layer = layer.lower()
                        keyValues_dict[layer] = layer_filename
                    except:
                        print(
                            f'Unable to extract {layer} file from HDF: {p}.hdf.\nSetting {layer} to None.')
                        layer = layer.replace(' Filename', '')
                        layer = layer.lower()
                        keyValues_dict[layer] = None
        except:
            print(
                f'Unable to open HDF File: {p}.hdf.\nSetting Terrain, Infiltration, Land Cover, and Percent Impervious to None.')
            keyValues_dict['terrain'] = None
            keyValues_dict['infiltration'] = None
            keyValues_dict['land cover'] = None
            keyValues_dict['percent impervious'] = None

         # Get Input DSS files and paths from flow file to p file.
        dss_file_and_paths = getDSSPaths(flow_lines)
        keyValues_dict['DSS Input Files'] = dss_file_and_paths

        # Add Specified key value pairs from flow file to p file.
        keyValues_dict['Flow Title'] = flow_keyValues_dict['Flow Title']

        # Append plan title list
        keyValues_dict['Plan Title'] = f"{keyValues_dict['Plan Title']}"
        keyValues_dict['Plan Title w P File'] = f"Simulation: {keyValues_dict['Plan Title']}, File: {p_file_tail}"
        plan_titles['Plan Title'].append(keyValues_dict['Plan Title'])
        plan_titles['Plan Title w P File'].append(
            keyValues_dict['Plan Title w P File'])
        plan_titles['P File'].append(p_file_tail)

        # Set dss output file to default path
        if ('DSS Output File' not in keyValues_dict.keys()
        or keyValues_dict['DSS Output File'] == 'dss' 
        or keyValues_dict['DSS Output File'] == ''):
            keyValues_dict['DSS Output File'] = f'{prj_name}.dss'
        else: 
            keyValues_dict['DSS Output File'] = keyValues_dict['DSS Output File']

        # Get root project directory from args.prj
        prj_dir = os.path.dirname(args.prj)
        # Get parent directory of prj_dir
        prj_parent_dir = os.path.dirname(prj_dir)
        # If the shp file is in the project directory or subdirectory, then use the relative path by removing the parent directory.
        shp_file = args.shp.replace(prj_parent_dir, '').replace('\\', '/')
        # Add shp file location
        keyValues_dict['shp'] = shp_file

        # Write the output yaml for each .p## file.
        # with open(os.path.join(output_dir,f'{p_file_tail}.yml'), 'w+') as f:
        #     yaml.dump(keyValues_dict, f)

        # Write output Json for each .p## file.
        output_p_json = os.path.join(
            output_dir, f'{p_file_tail}_Simulation.json')
        dict_to_sim_json(keyValues_dict, prj_name, p, output_p_json, simulation_key_order, layers_wanted)

    return plan_titles


def parse(args):
    try:
        msg = None
        # Get project name
        prj_dir, prj_file_tail = os.path.split(args.prj)
        # Get project name without extension, it is possible to have multiple periods in the project name.
        prj_name = '.'.join(prj_file_tail.split(".")[:-1])

        # Set output directory
        cwd = os.getcwd()
        output_dir = os.path.join(cwd, 'output', 'ras', prj_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get .p## files in prj_dir
        p_file_list = get_p_files(prj_dir, prj_name)

        # Validate that project has plan files.
        if len(p_file_list) == 0:
            msg = f'\nError: No .p## files found in {prj_dir} . Please check project file location.'
            raise Exception(msg)
        
        # Else continue parsing.
        else:
            # Ensure each p file has a corresponding hdf file. Iterate through p files in reverse order to remove p files without hdf files.
            for p in p_file_list[::-1]:
                if not os.path.exists(f'{p}.hdf'):
                    p_file_list.remove(p)
                    print(f'\nWarning: {p}.hdf file not found. Removing {p} from list of plan files to parse as simulations.')
            # Get RAS Project's Spatial Projection WKT
            ras_prj_wkt = get_ras_prj_wkt(p_file_list[0])

            # Get WKT and CRS from shp
            wkt, crs = get_wkt_crs.parse_shp(
                args.shp, ras_prj_wkt, prj_name, output_dir)
            
            # get schema keys
            model_application_key_order = get_schema_keys.get_schema_keys("./example/input/json/model_application_schema.json")
            simulation_key_order = get_schema_keys.get_schema_keys("./example/input/json/simulation_schema.json")  

            # Parse p files and include data from geometry, flow files. and add wkt.
            # Returns the plan titles of each p file as a list.
            plan_titles = parse_p(p_file_list, prj_name,
                                  wkt, crs, output_dir, args, simulation_key_order)
            
            

            # Parse prj, remove extra fields, add list of p file titles, and wkt.
            parse_prj(args, prj_name, wkt, crs, plan_titles, output_dir, model_application_key_order)

            #  Return Successful Output message.
            msg = f'RAS Parsing Complete. Output files located at: {output_dir}'
            return msg

    except Exception:
        if msg is None:
            msg = traceback.format_exc()
        print(msg)
        return msg


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
    p.add_argument(
        '--keywords', help='Optional. Additional Keywords for the project such as the client. Add multiple keywords with a comma (Ex: "LWI, National Park Service, CPRA")',
        required=False,
        type=str
    )

    p.add_argument(
        "--id", help="The Internal Organizational Project ID. This is ussually specifc to your own organization or company. \
        (Ex: P00813)",
        required=False,
        type=str
    )

    args = p.parse_args()

    # Split keywords argument into a list
    if args.keywords is not None:
        args.keywords = args.keywords.split(",")
        args.keywords = [x.strip() for x in args.keywords]

    parse(args)