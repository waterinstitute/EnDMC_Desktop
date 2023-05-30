import os
import glob
import json
from datetime import datetime
import traceback
from bs4 import BeautifulSoup
# import lxml
# import copy
import pandas as pd
from utils import get_wkt_crs

def parse_prj(prj, prj_dir, prj_name, prj_template_json, shp, output_dir):
    # Open the project file, read lines, strip newlines, copy lines to keyValueList
    with open(prj, "r") as f:
        lines = f.readlines()
    
    lines = [s.strip('\n') for s in lines]
    # print (lines)

    # get fia version, author, and date
    proj_fia_version        = None
    proj_created_date_unix  = None
    proj_created_date       = None
    proj_description        = None
    proj_author             = None

    # get project info
    for i,v in enumerate(lines):
            # print (v)
            if 'Version=' in v:
                    proj_fia_version = v.split('=')[-1]
            
            if 'Created=' in v:
                    # Timestamp is in milliseconds. Divided by 1000 to get timestamp in seconds
                    proj_created_date_unix = int(v.split('=')[-1])/1000
                    # Convert to datetime format 
                    proj_created_date = datetime.utcfromtimestamp(proj_created_date_unix).strftime("%Y-%m-%d")

            if 'ProjectDescription=' in v:
                    proj_description = v.split('=')[-1]

            if 'Created By=' in v:
                    proj_author = v.split('=')[-1]
            
    # Find the first wanted header to start parsing Map and Manager blocks, get the line number, break the loop.
    for i,v in enumerate(lines):
            if (v == 'MapBegin') or (v == 'ManagerBegin'):
                    startLine_after_proj_info = i
                    break

    # Parse the wanted blocks of Manager and Map.
    nestList = []
    for i,v in enumerate(lines):
            if (v == 'ManagerEnd') or (v == 'MapEnd'):
                    # If not the beginning of the file, skip a blank line (+1) for the start of the subList.
                    if len(nestList) > 0:
                            nestList.append(lines[startLine_after_proj_info+1:i])
                    else:
                            nestList.append(lines[startLine_after_proj_info:i])
                    startLine_after_proj_info = i+1

    # Break the nestList into 2 lists each for Maps and Managers by chcking the first value in each subList.
    # Only appending the values in each subList from columns [1:4] for mapList and [1:5] for managerList. The others deemed unnecessary.
    mapList = []
    managerList = []
    for subList in nestList:
        if subList[0] == 'MapBegin':
            mapList.append(subList[1:4])
        if subList[0] == 'ManagerBegin':
            managerList.append(subList[1:5])

    map_kv_list = []
    for subList in mapList:
        kv = {
            # Name
            subList[0].split('=')[0] : subList[0].split('=')[-1],
            # Description
            subList[1].split('=')[0] : subList[1].split('=')[-1],
            # Path
            subList[2].split('=')[0] : subList[2].split('=')[-1],  
        }
        map_kv_list.append(kv)

    manager_kv_list = []
    for subList in managerList:
        kv = {
            # Name
            subList[0].split('=')[0] : subList[0].split('=')[-1],
            # Description
            subList[1].split('=')[0] : subList[1].split('=')[-1],
            # File
            subList[2].split('=')[0] : subList[2].split('=')[-1],
            # Class
            subList[3].split('=')[0] : subList[3].split('=')[-1].split('.')[-1],   
        }
        manager_kv_list.append(kv)

    # Create dataframes for manager and map key value lists.
    manager_df = pd.DataFrame(manager_kv_list)
    map_df = pd.DataFrame(map_kv_list)
    map_df.loc[manager_df.Description == '', 'Description'] = ' '

    #  Update Names to be more descriptive based on Class &/or Description Columns.
    manager_df.loc[manager_df.Class == 'AgricultureManager', 'Name'] =  'Agriculture Data: ' + manager_df.loc[manager_df.Class == "AgricultureManager"].Name
    manager_df.loc[manager_df.Class == 'Alternative', 'Name'] =  'Alternative: ' + manager_df.loc[manager_df.Class == "Alternative"].Name
    manager_df.loc[manager_df.Class == 'BoundaryManager', 'Name'] =  manager_df.loc[manager_df.Class == "BoundaryManager"].Class.str.replace('Manager', ': ') + manager_df.loc[manager_df.Class == "BoundaryManager"].Name
    manager_df.loc[manager_df.Class == 'AnalysisGroup', 'Name'] = manager_df.loc[manager_df.Class == "AnalysisGroup"].Description
    manager_df.loc[manager_df.Class == 'GridsInundationConfiguration', 'Name'] =  'Grid Configuration: ' + manager_df.loc[manager_df.Class == "GridsInundationConfiguration"].Name
    manager_df.loc[manager_df.Class == 'ImpactAreaSetManager', 'Name'] =  "Impact Area Set"
    manager_df.loc[manager_df.Class == 'LifeSimModel', 'Name'] =  'LifeSim Model: ' + manager_df.loc[manager_df.Class == "LifeSimModel"].Name
    manager_df.loc[manager_df.Class == 'Simulation', 'Name'] =  'Simulation: ' + manager_df.loc[manager_df.Class == "Simulation"].Name
    manager_df.loc[manager_df.Class == 'StructureManager', 'Name'] =  'Structures: ' + manager_df.loc[manager_df.Class == "StructureManager"].Name
    manager_df.loc[manager_df.Class == 'TerrainModelManager', 'Name'] =  'Terrain: ' + manager_df.loc[manager_df.Class == "TerrainModelManager"].Name
    manager_df.loc[manager_df.Class == 'TimeWindow', 'Name'] =  'Time Window: ' + manager_df.loc[manager_df.Class == "TimeWindow"].Name
    manager_df.loc[manager_df.Class == 'WarningIssuanceManager', 'Name'] =  'Warning Issuance: ' + manager_df.loc[manager_df.Class == "WarningIssuanceManager"].Name
    manager_df.loc[manager_df.Class == 'WatershedConfiguration', 'Name'] =  'Watershed Configuration: ' + manager_df.loc[manager_df.Class == "WatershedConfiguration"].Name

    # Include proj_description in study description
    manager_df.loc[manager_df.Name == 'Study', 'Description'] =  proj_description
    manager_df.loc[manager_df.Description == '', 'Description'] = ' '

    # open the model application Json template, del unnecessary keys, update, add, export 
    with open(prj_template_json, 'r') as f:
                model_template_json = json.load(f)

    # keys to drop from json template
    drop_keys = ['_id', 'linked_resources', 'common_parameters', 'common_software_version', 'authors', 
    'spatial_extent_resolved', 'spatial_valid_extent_resolved', 'temporal_extent', 'temporal_resolution', 
    'spatial_valid_extent', 'common_files_details', 'grid', '__created_at', '__created_by']
    for key in drop_keys:
        del model_template_json[key]

    model_template_json['description'] = proj_description
    model_template_json['purpose'] = proj_description
    model_template_json['title'] = f'HEC-FIA Model: {prj_name}'
    model_template_json['application_date'] = proj_created_date

    wkt, crs = get_wkt_crs.parse_shp(shp, prj_name, './output/fia')

    model_template_json['spatial_extent'] = wkt
    model_template_json['grid'] = {
        "coordinate_system": crs,
        "description": "terrain based",
        "shape": "rectangular",
        "dimension": "2D"
    }

    model_template_json["common_files_details"] = [
            {
                "description": "AgricultureManager",
                "location": "Inventory/Agriculture Data/AgriculturalGrid.tif",
                "title": "Agricultural Manager: AgriculturalGrid"
            }
        ]

    # Match common_files dataframe to template
    manager_df = manager_df.rename(columns={"Name": "title", "Description": "description", "File": "location"})
    manager_df_clean = manager_df.drop(['Class'], axis=1)
    map_df = map_df.rename(columns={"Name": "title", "Description": "description", "Path": "location"})

    #Concatenate manager and map dataframes
    df = pd.concat([manager_df_clean, map_df], axis=0)

    # Use Pandas to_dict("records") method, it outputs to the required list of objects format: [{}, {}].
    model_template_json["common_files_details"] = df.to_dict('records')
    model_template_json["common_files_details"]

    # output model application json
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_model_json = os.path.join(output_dir,f'{prj_name}_model_application.json')
    with open(output_model_json, "w") as outfile:
        json.dump(model_template_json, outfile)


    # Get Sim Files.
    sim_paths = manager_df.loc[manager_df['Class'] =='Simulation', 'location'].to_list()
    sim_pathnames = []
    for path in sim_paths:
        sim_pathnames.append(os.path.join(prj_dir, path))

    return sim_pathnames

def parse_sims(sim_pathnames, prj_dir, prj_name, sim_template_json, output_dir):
    # Parse Sims from each sim file get basics and alt file. from alt file get inputs
    path = sim_pathnames[0]
    # for path in sim_pathnames:
    with open(path, 'r') as f:
        sim_file = f.read()

    soupData_sim = BeautifulSoup(sim_file, 'xml')
    sim_name = soupData_sim.find_all('Name')[0].text
    sim_description = soupData_sim.find_all('Description')[0].text
    alt_name = soupData_sim.find_all('AlternativeName')[0].text
    alt_path = soupData_sim.find_all('AlternativePath')[0].text.split("../")[-1]
    event_name = soupData_sim.find_all('EventName')[0].text
    timewindow_name = soupData_sim.find_all('TimeWindowName')[0].text
    timewindow_path = soupData_sim.find_all('TimeWindowPath')[0].text.split("../")[-1]

    with open(os.path.join(prj_dir, alt_path), 'r') as f:
        alt_file = f.read()

    soupData_alt = BeautifulSoup(alt_file, 'xml')

    alt_description = soupData_alt.find_all('Description')[0].text

    wanted_tags = ['Impact Area', 'Inundation Configuration', 'Structrue Inventory', 'Agriculture Inventory', 'Warning Issuance']
    # The grid_wanted_tags list comes from the gridlc xml file which is linked in the Alternative XML file.
    grid_wanted_tags = ['Inundation Grid', 'Depth Velocity Grid', 'Life Lose Arrival Grid', 'Agriculture Arrival Grid', 'Agriculgure Duration Grid']
    alt_kv_list = []

    for tag in wanted_tags:
        
        try:
            # Removing spaces from the tag and adding either 'Name' or 'Path', this matches the tag format in the xml file
            # doing this allows the formatting to be controlled by the wanted_tags list. 
            # If more than spaces are needed, should update to use a dictionary of wantedFormattedName:XMLtagName pairs instead of the wanted_tag list.
            tag_formatted = tag.replace(" ", "")
            text_name = soupData_alt.find_all(tag_formatted+'Name')[0].text
            text_path = soupData_alt.find_all(tag_formatted+'Path')[0].text
            
            if '../' in text_path:
                text_path = text_path.split('../')[-1]
            
            alt_kv_list.append({
                'title':tag,
                'description': ' ',
                'location': text_path
            })

            # Innundation Config input files
            if tag == 'Inundation Configuration':

                # open gridslc file
                with open(os.path.join(prj_dir, text_path), 'r') as f:
                        grids_file = f.read()
                
                soupData_grids = BeautifulSoup(grids_file, 'xml')
                
                for tag in grid_wanted_tags:
                        tag_formatted = tag.replace(" ", "")
                        text_path = soupData_grids.find_all(tag_formatted+'Path')[0].text
                        
                        if '../' in text_path:
                            text_path = text_path.split('../')[-1]

                        alt_kv_list.append({
                            'title':tag,
                            'description': ' ',
                            'location': text_path
                        })
        
        except:
            print(f'Missing XML Tag. "<{tag_formatted}Path>" not found in Alternative File: "{os.path.join(prj_dir, alt_path)}"')
            continue
        
    # outputs in dir: runs/{Alt}/{Event}/{TW}. Get *.shp's.
    sim_results_dir = os.path.join('runs', alt_name, event_name, timewindow_name)
    sim_results_abs_dir = os.path.join(prj_dir, 'runs', alt_name, event_name, timewindow_name)
    output_kv_list = []
    for result_shp in glob.glob(rf'{sim_results_abs_dir}/*.shp'):
        head, tail = os.path.split(result_shp)
        sim_results_dir_forwardslash = sim_results_dir.replace("\\", "/")
        output_kv_list.append({
            'title': tail.split('.shp')[0],
            'description': ' ',
            'location': f'{sim_results_dir_forwardslash}/{tail}'
        })

    # Parameters from Alternative file
    parameter_tags = ['Random Seed', 'Confidence', 'Convergence Tolerance', 'Convergence Variables', 'Evacuation Velocity']
    parameter_kv_list = []
    for tag in parameter_tags:
        try:
            # Removing spaces from the tag and adding either 'Name' or 'Path', this matches the tag format in the xml file
            # doing this allows the formatting to be controlled by the wanted_tags list. 
            # If more than spaces are needed, should update to use a dictionary of wantedFormattedName:XMLtagName pairs instead of the wanted_tag list.
            tag_formatted = tag.replace(" ", "")
            text = soupData_alt.find_all(tag_formatted)[0].text
            parameter_kv_list.append({
                'value': text,
                'parameter': tag
            })        
        except:
            print(f'Missing XML Tag. "<{tag_formatted}>" not found in Alternative File: "{os.path.join(prj_dir, alt_path)}"')
            continue

    # Open Time Window File and Parse Temporal Extent
    with open(os.path.join(prj_dir,timewindow_path), 'r') as f:
        lines = f.readlines()

    lines = [s.strip('\n') for s in lines]
    # get StartTime & EndTime line index
    for i, v in enumerate(lines):
        if 'FLD=m_startTime' in v:
            startTime_idx = i + 1
        if 'FLD=m_endTime' in v:
            endTime_idx = i + 1
    startTime_hecTime = lines[startTime_idx].split('=')[-1].split(',')[0]
    startTime_utc= int(startTime_hecTime) * 24
    startTime_dt = datetime.utcfromtimestamp(startTime_utc)
    endTime_hecTime = lines[endTime_idx].split('=')[-1].split(',')[0]
    endTime_utc= int(endTime_hecTime) * 24
    endTime_dt = datetime.utcfromtimestamp(endTime_utc)

    # Open simulation template, drop unwanted keys, update values, output json.
    with open(sim_template_json, 'r') as f:
                sim_template_json = json.load(f)

    # keys to drop from json template
    drop_keys = ['_id', 'linked_resources', 'model_application', 'model_software',
                '__created_at', '__created_by', 'temporal_resolution']
    for key in drop_keys:
        del sim_template_json[key]

    sim_template_json['title'] = f'HEC-FIA {prj_name} Simulation: {sim_name}'
    sim_template_json['description'] = f'HEC-FIA Simulation: {sim_name}, {sim_description}, for project: {prj_name}, using Alternative: {alt_name}.'
    sim_template_json['input_files'] = alt_kv_list
    sim_template_json['output_files'] = output_kv_list
    sim_template_json['parameters'] = parameter_kv_list

    # output sim json
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_sim_json = os.path.join(output_dir,f'{prj_name}_{sim_name}_simulation.json')
    with open(output_sim_json, "w") as outfile:
        json.dump(sim_template_json, outfile)

def parse(prj, shp):
    try:
        prj_dir, prj_file_tail = os.path.split(prj)
        prj_name = prj_file_tail.split(".")[0]
        prj_template_json =  r"example\input\json\fia_model_application_template.json"
        sim_template_json =  r"example\input\json\fia_simulation_template.json"
        print(os.getcwd())

        output_dir = os.path.join(os.getcwd(), 'output', 'fia')

        sim_pathnames = parse_prj(prj, prj_dir, prj_name, prj_template_json, shp, output_dir)
        parse_sims(sim_pathnames, prj_dir, prj_name, sim_template_json, output_dir)

        # Return Successful Output message
        msg = f'FIA Parsing Complete. Output files located at: {output_dir}'
        print('FIA Parsing Complete.')
        return msg
    except Exception: 
        msg = traceback.format_exc()
        # print(msg)
        return msg
    

if __name__ == '__main__':
    prj = r"C:\Users\mmcmanus\Documents\Working\models\FIA Darlington\AmiteWatershed_2016Event_WithDarlingtonReservoir\AmiteWatershed_2016Event.prj"
    shp = r"C:\Users\mmcmanus\Documents\Working\models\FIA Darlington\AmiteWatershed_2016Event_WithDarlingtonReservoir\maps\AmiteHUC8_NAD83_Albers.shp"
    parse(prj, shp)