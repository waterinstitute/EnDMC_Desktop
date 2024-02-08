import argparse
import os
import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import json

def parse_sim_single_run(args, output_dir):
    # Parse the Go-Consequences run file
    try:
        with open(args.prj_file, "r") as f:
            lines = f.readlines()
        print (f'\nReading Go File: {args.prj_file}')
    except:
        raise ValueError(f"Error reading specified prj_file:\n\
                         {args.prj_file}")
    lines = [s.strip('\n') for s in lines]

    # Unless Layer Manually Specified via args.hazard_layer, Get Hazard Layer (WSE geotif from HEC-RAS)
    if args.hazard_layer is not None:
        hazard_layer = args.hazard_layer
        print (f'\nHazard Layer Specified as: {hazard_layer}')
    else:
        # splitting by double quotes because GoLang always uses double quotes for defining strings.
        try:
            hazard_layer = [s for s in lines if "hazardproviders.Init" in s][0].split('"')[1]
            print (f'\nHazard Layer Found within Go File: {hazard_layer}')
        except IndexError:
            print ("\nNo hazard layer found. Please Specify the Layer Manually. Setting Layer to None.")
            hazard_layer = None
    
    # Unless Layer is Manually Specified via args.inventory_layer Get Inventory Layer (Structure Inventory Feature Layer)
    if args.inventory_layer is not None:
        print (f'\nStructure Inventory Layer Specified as: {args.inventory_layer}')
        try:
            structure_inventory_layer = args.inventory_layer
        except:
            print ("\nError reading specified structure inventory layer, setting layer to None.\n\
                    {args.inventory_layer}")
            structure_inventory_layer = None
    else:
        try:
            structure_inventory_layer = [s for s in lines if "structureprovider.InitSHP" in s][0].split('"')[1]  
        except:
            print ("\nError reading structure inventory layer. Please Specify the Layer Manually, or update the Go File. \
                    Setting layer to None.")
            structure_inventory_layer = None
    
    # Get Projected Results Layer
    try:
        results_layer = [s for s in lines if "resultswriters.InitGpkResultsWriter_Projected" in s][0].split('"')[1]
        # Getting the projection from the last parameter of the InitGpkResultsWriter_Projected function call.
        results_projection = [s for s in lines if "resultswriters.InitGpkResultsWriter_Projected" in s][0].split(',')[-1].split(')')[0]
    except:
        # Get Results Layer that assumes 4326 projection
        # If resusltswriters line not found, exception will be thrown and the results layer will be set to None.
        try:
            results_layer = [s for s in lines if "resultswriters.InitGpkResultsWriter" in s][0].split('"')[1]
            results_projection = "4326"
        except IndexError:
            print ("\nNo results layer found. Please Specify the Layer Manually. Setting Layer to None.")
            results_layer = None
            results_projection = None
    
    # Open simulation template
    # Output simulation_template.json
    sim_template_fn = r".\example\input\json\go-consequences_simulation_template.json"
    with open(sim_template_fn, "r") as f:
        sim_template = json.load(f)

    # Keys to not include in the simulation json output
    dropkeys_list = ['_id', 'temporal_resolution', 'temporal_extent', 'type', 
                     'model_application', 'linked_resources', 'parameters']
    
    # Remove keys from model_application_template that are in dropkeys_list
    for dropkey in dropkeys_list:
        sim_template.pop(dropkey)
        
    # Get root project directory from prj_file
    prj_dir = os.path.dirname(args.prj_file)
    # get parent directory of prj_dir
    prj_parent_dir = os.path.dirname(prj_dir)
    # Remove parent directory from lists
    prj_parent_dir = os.path.dirname(os.path.dirname(args.prj_file))
    hazard_layer = hazard_layer.replace('\\', '/').replace(prj_parent_dir, '')
    structure_inventory_layer = structure_inventory_layer.replace('\\', '/').replace(prj_parent_dir, '')
    results_layer = results_layer.replace('\\', '/').replace(prj_parent_dir, '')

    # Update/Add values to simulation output.
    sim_template['title'] = f'{args.prj_name} Go-Consequences Simulation: {args.sim_name}'
    sim_template['description'] = f'{args.sim_description}'
    sim_template['output_files'] = [
        {
            "description": "The Go-Consequences Simulation output feature layer.",
            "location": results_layer,
            "source_dataset": "Go-Consequences Output",
            "title": f"{args.prj_name} Go-Consequences Simulation: {args.sim_name} Output Feature Layer"
        }
    ]
    sim_template['input_files'] = [
        {
            "description": "The Go-Consequences Simulation Hazard Layer.",
            "location": hazard_layer,
            "source_dataset": "HEC-RAS",
            "title": f"{args.prj_name} Go-Consequences Simulation: {args.sim_name} Input Hazard Layer"
        },
        {
            "description": "The Go-Consequences Simulation Structure Inventory Layer.",
            "location": structure_inventory_layer,
            "source_dataset": "NSI",
            "title": f"{args.prj_name} Go-Consequences Simulation: {args.sim_name} Input Structure Inventory Layer"
        }
    ]

    # output simulation json
    sim_name = args.sim_name.replace(" ", "_")
    output_sim_json = os.path.join(output_dir,f'{args.prj_name}_simulation_{sim_name}.json')
    with open(output_sim_json, "w") as outfile:
        json.dump(sim_template, outfile)
    print (f'\nSimulation file output to: {output_sim_json}')

    return hazard_layer, structure_inventory_layer, results_layer

def parse_sim_multiple_runs(args, output_dir):
    # Parse the Go-Consequences run file
    try:
        with open(args.prj_file, "r") as f:
            lines = f.readlines()
        print (f'\nReading Go File: {args.prj_file}')
    except:
        raise ValueError(f"Error reading specified prj_file:\n\
                         {args.prj_file}")
    lines = [s.strip('\n') for s in lines]

    # Parse the Go-Consequences run table
    run_table_df = pd.read_csv(args.run_table)

    # init lists of layers to use in model application json.
    hazard_layer_list = []
    inventory_layer_list = []
    results_layer_list = []
    sim_list = []
    

    # For each row in the run table, create a simulation json
    for index, row in run_table_df.iterrows():
        print (f'\n\nBeging Parsing Simulation: {row["Simulation Name"]}')
        args.sim_name = row["Simulation Name"]
        args.sim_description = row["Description"]
        sim_list.append(f'{args.sim_name} - {args.sim_description}')
        args.hazard_layer = row["WSE File"]
        args.inventory_layer = row["Structure Inventory File"]
        args.results_layer = os.path.dirname(row["Model Result Output File"])
        hazard_layer, inventory_layer, results_layer = parse_sim_single_run(args, output_dir)
        
        # Add layers to lists for model application json
        hazard_layer_list.append(args.hazard_layer)
        inventory_layer_list.append(args.inventory_layer)
        results_layer_list.append(row["Model Result Output File"])

        
        print ('-----Done Parsing Simulation-----')
    # Remove duplicates from lists
    hazard_layer_list = list(set(hazard_layer_list))
    inventory_layer_list = list(set(inventory_layer_list))
    results_layer_list = list(set(results_layer_list))
    sim_list = list(set(sim_list))

    return hazard_layer_list, inventory_layer_list, results_layer_list, sim_list

def parse_model_application(args, output_dir, hazard_layer_list=None, inventory_layer_list=None, results_layer_list=None, sim_list=None):

    print("\nModel Application Parsing Begin...")

    # Get root project directory from prj_file
    prj_dir = os.path.dirname(args.prj_file)
    # get parent directory of prj_dir
    prj_parent_dir = os.path.dirname(prj_dir)
    
    # Get list of tifs from data directory
    tif_endswith = [".tif", ".tiff", ".geotif", ".geotiff"]
    try:
        tif_list = [os.path.join(args.model_data_dir, f) for f in os.listdir(args.model_data_dir) if f.lower().endswith(tuple(tif_endswith))]
    except:
        tif_list = []

    

    if len(tif_list) == 0 and args.hazard_layer is None and hazard_layer_list is None:
        print("No tifs found in data directory. Please Specify the Layer Manually. Setting Common Files Hazard Layer List to None.")
        tif_list = []
    
    if len(tif_list) == 0 and args.hazard_layer is not None:
        print(f'Using Specified Hazard Layer: {args.hazard_layer}')
        hazard_layer = args.hazard_layer.replace('\\', '/').replace(prj_parent_dir, '')
        tif_list = [args.hazard_layer]
        

    # Add hazard layer list to tif_list for common_files output key.
    if hazard_layer_list is not None:
        tif_list.extend(hazard_layer_list)
        tif_list = list(set(tif_list))
    
    tif_list = [i.replace('\\', '/') for i in tif_list]
    # Remove prj_parent_dir from tif_list
    tif_list = [i.replace(prj_parent_dir, '') for i in tif_list]
    if len(tif_list) == 1:
        tif_list = tif_list[0]
        
    
    # Get list of shps from data directory
    shp_endswith = [".shp", ".geojson", ".json", ".gpkg"]
    try:
        shp_list = [os.path.join(args.model_data_dir, f) for f in os.listdir(args.model_data_dir) if f.lower().endswith(tuple(shp_endswith))]
    except:
        shp_list = []

    shp_list = [i.replace('\\', '/') for i in shp_list]

    # Remove prj_parent_dir from shp_list
    shp_list = [i.replace(prj_parent_dir, '') for i in shp_list]
    
    # Try to create spatial extent from structure inventory layer from data directory.
    if len(shp_list) > 0:
        structure_inventory_layer = shp_list[0]
        print(f'Creating Geospatial Bounds from first Structure Inventory Layer found within Specified Data Directory, this may take a few minutes...\n\
              Structure Inventory Layer: {structure_inventory_layer}')
        
        try:

            # You may comment out these lines for testing purposes to speed up the script.
            gdf = gpd.read_file(structure_inventory_layer)
            crs = gdf.crs
            gdf.to_crs(epsg=4326, inplace=True)
            bounding_box = box(*gdf.total_bounds)
            gpd.GeoSeries([bounding_box]).to_file(os.path.join(output_dir,f"{args.prj_name}_bounding_box.geojson"), driver='GeoJSON')
            spatial_extent = str(gpd.GeoSeries([bounding_box])[0])
            
            # The lines below are commented out for testing, because creating the spatial_extent takes a few minutes.
            # spatial_extent = 'Testing'
            # crs = 'Testing'
            
            print (f'Done creating geospatial extent: {os.path.join(output_dir,f"{args.prj_name}_bounding_box.geojson")}')
        except:
            print("Error reading inventory layer, setting spatial_extent to None.")
            spatial_extent = None
            crs = None

    # Else if no shp's found in data directory, try to create spatial extent from specified layer or from run table.
    else: 

        # If no shps in data_dir and run_type is Single, attempt to create spaital extent from specified inventory layer.
        if args.run_type == 0 and args.inventory_layer is not None:
            print (f'Using Specified Inventory Layer to Create Spatial Extent, this may take a few minutes...: \n\
                {args.inventory_layer}')
            try:
                
                # You may comment out these lines for testing purposes to speed up the script.
                gdf = gpd.read_file(args.inventory_layer)
                crs = gdf.crs
                gdf.to_crs(epsg=4326, inplace=True)
                bounding_box = box(*gdf.total_bounds)
                gpd.GeoSeries([bounding_box]).to_file(os.path.join(output_dir,f"{args.prj_name}_bounding_box.geojson"), driver='GeoJSON')
                spatial_extent = str(gpd.GeoSeries([bounding_box])[0])

                # The lines below are commented out for testing, because creating the spatial_extent takes a few minutes.
                # spatial_extent = 'Testing'
                # crs = 'Testing'

                print (f'Done creating geospatial extent: {os.path.join(output_dir,f"{args.prj_name}_bounding_box.geojson")}')
            except:
                print("Error reading inventory layer, setting spatial_extent to None.")
                spatial_extent = None
                crs = None
            
        elif args.run_type == 0 and args.inventory_layer is None:
            print("No Structure Inventory layer found in data directory. Please Specify the Layer Manually. \n\
            Setting Common Files Structure Inventory Layer List to None. Setting spatial_extent to None.")
            spatial_extent = None
            crs = None

        # If run_type is Multiple, attempt to create spatial extent from run table.
        elif args.run_type == 1 and inventory_layer_list is not None:
            print(f"No Structure Inventory layers found in data directory, attempting to use first run_table inventory layer to define spatial extent. \n\
            This may take a few minutes...\n\
                Structure Inventory Layer: {inventory_layer_list[0]}")
            try:

                # You may comment out these lines for testing purposes to speed up the script.
                gdf = gpd.read_file(inventory_layer_list[0])
                crs = gdf.crs
                gdf.to_crs(epsg=4326, inplace=True)
                bounding_box = box(*gdf.total_bounds)
                gpd.GeoSeries([bounding_box]).to_file(os.path.join(output_dir,f"{args.prj_name}_bounding_box.geojson"), driver='GeoJSON')
                spatial_extent = str(gpd.GeoSeries([bounding_box])[0])

                # The lines below are commented out for testing, because creating the spatial_extent takes a few minutes.
                # spatial_extent = 'Testing'
                # crs = 'Testing'

                print (f'Spatial extent created based on Run Table: {os.path.join(output_dir,f"{args.prj_name}_bounding_box.geojson")}')
            except:
                print("Error reading inventory layer from run table, setting spatial_extent to None.")
                spatial_extent = None
                crs = None
    
    # Add inventory layer list to shp_list for common_files output key. 
    if inventory_layer_list is not None:
        # Remove prj_parent_dir from inventory_layer_list
        inventory_layer_list = [i.replace(prj_parent_dir, '') for i in inventory_layer_list]
        inventory_layer_list = [i.replace('\\', '/') for i in inventory_layer_list]
        shp_list.extend(inventory_layer_list)
        shp_list = list(set(shp_list))
    
    # Add Specified Inventory Layer to shp_list for common_files output key.
    if args.inventory_layer is not None:
        shp_list.append(args.inventory_layer.replace('\\', '/').replace(prj_parent_dir, ''))
        shp_list = list(set(shp_list))
    
    if len(shp_list) == 1:
        shp_list = shp_list[0]

    # Get list of output files from out_dir.
    output_endswith = [".gpkg"]
    try:
        output_list = [os.path.join(args.model_out_dir, f) for f in os.listdir(args.model_out_dir) if f.lower().endswith(tuple(output_endswith))]
    except:
        output_list = []
    
    # Get specified results layer if run_type is 0
    if args.run_type == 0 and args.results_layer is not None:
        print (f'Using Specified Results Layer: {args.results_layer}')
        output_list.append(args.results_layer)

    output_list = [i.replace('\\', '/') for i in output_list]
    # Remove prj_parent_dir from output_list
    output_list = [i.replace(prj_parent_dir, '') for i in output_list]

    # Add results layer list to output_list for common_files output key.
    if results_layer_list is not None:
        # Remove prj_parent_dir from results_layer_list
        results_layer_list = [i.replace(prj_parent_dir, '') for i in results_layer_list]
        
        output_list.extend(results_layer_list)
        output_list = list(set(output_list))
    
    if len(output_list) == 1:
        output_list = output_list[0]
    
    # Set to none if no output layers are found in run table and data directory.
    if len(output_list) == 0 and results_layer_list is None:
        print("No gpkg files found in output directory. Please Specify the Layer Manually. \n\
            Setting Common Files Output Layer List to None.")
        output_list = None
    
    
    
    # Output model_application.json
    model_application_template_fn = "./example/input/json/go_consequences_model_application_template.json"
    with open(model_application_template_fn, "r") as f:
        model_application_template = json.load(f)
    
    # Keys to not include in the model_application.json output
    dropkeys_list = ['_id', 'common_parameters', 'spatial_valid_extent', 'common_software_version', 'temporal_resolution', \
                 'temporal_extent', 'spatial_valid_extent_resolved', 'linked_resources', 'spatial_extent_resolved', \
                 'authors', 'purpose']
    
    key_list = list(model_application_template.keys())
    # Remove keys from model_application_template that are in dropkeys_list
    for dropkey in dropkeys_list:
        model_application_template.pop(dropkey)

    # Remove prj_parent_dir from args.pr_file
    prj_file = args.prj_file.replace(prj_parent_dir, '')
    
    # Update Decription with line breaks.
    description_str = f"Description: {args.prj_description}"
    description_str += '\n\nSimulations:'
    for s in sim_list:
        # print('\n\n',s)
        description_str += '\n\n\n'+s

    # Add any optional keywords
    try:
        if args.keywords is not None and len(args.keywords[0]) > 0:
            model_application_template['keywords'].extend(args.keywords)
        if args.id is not None and len(args.id[0]) > 0:
            model_application_template['keywords'].append(args.id)
    except:
        pass

    # Add values to model_application output
    model_application_template['title'] = f'Go-Consequences {args.prj_name}'
    model_application_template['description'] = description_str
    model_application_template['spatial_extent'] = spatial_extent
    model_application_template['grid']['coordinate_system'] = str(crs)
    model_application_template['application_date'] = datetime.datetime.now().strftime("%Y-%m-%d")

    # Add Common Files to model_application output
    model_application_template['common_input_files'] = []
    model_application_template['common_output_files'] = []
    model_application_template['common_input_files'].extend(
        [{
            "description": "The project's Main Go-Consequences run script file",
            "location": prj_file,
            "source_dataset": None,
            "title": "Project File"
        },
        {
            "description": "There may be multiple Water Surface Elevation Rasters in the Go-Consequences data directory.",
            "location": tif_list,
            "source_dataset": "HEC-RAS",
            "title": "Hazard Layers as Water Surface Elevation Raster Files"
        },
        {
            "description": "There may be multiple Structure Inventories in the Go-Consequences data directory.",
            "location": shp_list,
            "source_dataset": None,
            "title": "Structure Inventory Feature Layers"
        }]
    )
    model_application_template['common_output_files'].extend(
        [{
            "description": "There may be multiple Output Feature Layers.",
            "location": output_list,
            "source_dataset": "Go-Consequences Output",
            "title": "Output Feature Layers"
        }]
    )

    # output model application json
    output_model_json = os.path.join(output_dir,f'{args.prj_name}_model_application.json')
    with open(output_model_json, "w") as outfile:
        json.dump(model_application_template, outfile)
    
    print (f'\nModel Application file output to: {output_model_json}')

def parse_consequences(args):
    # Create output directory
    output_dir = os.path.join(os.getcwd(), "output", "go-consequences", args.prj_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if args.run_type == 0:
        hazard_layer, inventory_layer, results_layer = parse_sim_single_run(args, output_dir)
        sim_list = [f'{args.sim_name} - {args.sim_description}']
        parse_model_application(args, output_dir, sim_list=sim_list)
    elif args.run_type == 1:
        args.hazard_layer = None
        args.inventory_layer = None
        args.results_layer = None
        hazard_layer_list, inventory_layer_list, results_layer_list, sim_list = parse_sim_multiple_runs(args, output_dir)
        parse_model_application(args, output_dir, hazard_layer_list, inventory_layer_list, results_layer_list, sim_list)

if __name__ == '__main__':
    # Parse Command Line Arguments
    p = argparse.ArgumentParser(description="HEC Go-Consequences metadata extraction. \
        Requires a Go-Consequences run file (Ex: main.go), a project name, description, \
        other dependencies are required based on if a single run or multiple runs are to be extracted. \n\
        If a single run is to be extracted: \n\
            1. A Model Data directory containing the Hazard and Inventory layers. \n\
            2. A Model Output directory containing the Go-Consequences output .gpkg file. \n")
    
    p.add_argument(
    "--run_type", help="Value of 0 or 1. \n\
        0: For a single simulation run to be extracted. \n\
        1: for multiple simulation runs to be extracted based on a csv run table.", 
    required=True, 
    type=int
    )

    p.add_argument(
    "--prj_file", help="The Go-Consequences run file. (Ex: main.go)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--prj_name", help="The Go-Consequences Model's Name file. (Ex: Amite River)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--prj_description", help="The Go-Consequences Model's Description. \n\
        (Ex: Amite Go-Consequences Model Based on Dewberry Amite River HEC-RAS Model Results and USACE National Structure Inventory Data)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--model_data_dir", help="The Go-Consequences model's input data directory that should contain all Hazard Layer Raster's and all Structure Inventory Feature Layers. \
        (Ex: C:\Consequence_Models\Amite\data)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--model_out_dir", help="The Go-Consequences model's output data directory that should contain all output result feature layers. \
        (Ex: C:\Consequence_Models\Amite\output)", 
    required=True, 
    type=str
    )

    p.add_argument(
    "--sim_name", help="For a single simulation run extraction, the Go-Consequences model's Simulation name. Required if run_type set to 0 as a Single Simulation Run.", 
    required=False, 
    type=str
    )
    p.add_argument(
    "--sim_description", help="For a single simulation run extraction, the Go-Consequences model's Simulation Description. Required if run_type set to 0 as a Single Simulation Run.", 
    required=False, 
    type=str
    )

    p.add_argument(
    "--run_table", help="The Go-Consequences model's run table csv file. Required is run_type set to 1 as a Multiple Simulation Run. \
        (An Example run table is available at ./example/input/go-consequences/run_table.csv)", 
    required=False, 
    type=str
    )

    p.add_argument(
    "--hazard_layer", help="Optional. A Specified filepath to a Go-Consequences model's raster hazard layer. \
        Typically this is a Max WSE geotiff exported from HEC-RAS.",
    required=False, 
    type=str
    )
    p.add_argument(
    "--inventory_layer", help="Optional. A Specified filepath to a Go-Consequences model's structure inventory feature layer. \
        Typically this is a shapefile from NSI (https://nsi.sec.usace.army.mil/downloads/).",
    required=False, 
    type=str
    )
    p.add_argument(
    "--results_layer", help="Optional. A Specified filepath to a Go-Consequences model's output results feature layer. \
        Typically this is a geopackage file (*.gpkg).",
    required=False, 
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
    
    ### Validate Arguments

    args.keywords = args.keywords.split(",")
    args.keywords = [x.strip() for x in args.keywords]

    # Project file exists
    if not os.path.exists(args.prj_file):
        raise ValueError(f"prj_file specified does not exist:\n\
                         {args.prj_file}")

    # If optional arguments are not specified, set to None.
    if not hasattr(args, 'hazard_layer'):
        args.hazard_layer = None
    if not hasattr(args, 'inventory_layer'):
        args.inventory_layer = None
    if not hasattr(args, 'results_layer'):
        args.results_layer = None

    # Run type is 0 or 1
    if (args.run_type != 0) & (args.run_type != 1):
        raise ValueError("Invalid run_type. Value must be 0 or 1.")
    
    # Sim name required if run_type is 0
    if (args.run_type == 0) & (args.sim_name is None):
        raise ValueError("sim_name must be provided if run_type is 0.")
    
    # Sim description required if run_type is 0
    if (args.run_type == 0) & (args.sim_description is None):
        raise ValueError("sim_description must be provided if run_type is 0.")
    
    # Run table required if run_type is 1
    if (args.run_type == 1) & (args.run_table is None):
        raise ValueError("run_table csv must be provided if run_type is 1. \n\
            (An Example run table is available at ./example/input/go-consequences/run_table.csv)") 

    # Run table exists if run_type is 1
    if (args.run_type == 1) & (args.run_table is not None):
        if not os.path.exists(args.run_table):
            raise ValueError(f"run_table specified does not exist:\n\
                            {args.run_table}")
    
    # Run table is readable
    if (args.run_type == 1) & (args.run_table is not None):
        try:
            run_table_df = pd.read_csv(args.run_table)
        except:
            raise ValueError(f"Error reading specified run_table:\n\
                            {args.run_table}")
    
    # Check that the run table has the required columns
    if (args.run_type == 1) & (args.run_table is not None):
            run_table_df = pd.read_csv(args.run_table)
            required_columns = ['Simulation Name',	'Description',	'Structure Inventory File',	'WSE File',	'Model Result Output File']
            if not all(elem in run_table_df.columns for elem in required_columns):
                raise ValueError(f"run_table must contain the following column names and order:\n\
                    {required_columns} \n\
                        An Example run table is available at ./example/input/go-consequences/run_table.csv")
    
    # If run_type is 1, hazard_layer and inventory_layer should not be specified.
    if (args.run_type == 1) & (args.hazard_layer is not None):
        print("Warning: hazard_layer specified, but run_type is 1. hazard_layer will be ignored and run_table used.")
    if (args.run_type == 1) & (args.inventory_layer is not None):
        print("Warning: inventory_layer specified, but run_type is 1. inventory_layer will be ignored and run_table used.")
    
    #  If run_type is 1, sim_name and sim_description should not be specified.
    if (args.run_type == 1) & (args.sim_name is not None):
        print("Warning: sim_name specified, but run_type is 1. sim_name will be ignored and run_table used.")
    if (args.run_type == 1) & (args.sim_description is not None):
        print("Warning: sim_description specified, but run_type is 1. sim_description will be ignored and run_table used.")

    # If run_type is 1, results_layer should not be specified.
    if (args.run_type == 1) & (args.results_layer is not None):
        print("Warning: results_layer specified, but run_type is 1. results_layer will be ignored and run_table used.")
    
    
    parse_consequences(args)