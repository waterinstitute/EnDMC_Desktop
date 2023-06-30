import argparse
import os
import datetime
import geopandas as gpd
from shapely.geometry import box
import json

# prj = "./dev/go-consequences/main.go"
# prj_name = "Amite"
# description = "Amite Go-Consequences Model Based on Dewberry Amite River HEC-RAS Model Results"
# data_dir = "./dev/go-consequences/data"
# out_dir = "./dev/go-consequences/output"


def parse_single_run_sim(args):
    # Parse the Go-Consequences run file
    try:
        with open(args.prj_file, "r") as f:
            lines = f.readlines()
    except:
        raise ValueError(f"Error reading specified prj_file:\n\
                         {args.prj_file}")
    lines = [s.strip('\n') for s in lines]

    # Unless Layer Manually Specified via args.hazard_layer, Get Hazard Layer (WSE geotif from HEC-RAS)
    if args.hazard_layer is not None:
        hazard_layer = args.hazard_layer
    else:
        # splitting by double quotes because GoLang always uses double quotes for defining strings.
        try:
            hazard_layer = [s for s in lines if "hazardproviders.Init" in s][0].split('"')[1]
        except IndexError:
            print ("No hazard layer found. Please Specify the Layer Manually. Setting Layer to None.")
            hazard_layer = None
    
    # Unless Layer is Manually Specified via args.inventory_layer Get Inventory Layer (Structure Inventory Feature Layer)
    if args.inventory_layer is not None:
        try:
            structure_inventory_layer = args.inventory_layer
            gdf = gpd.read_file(structure_inventory_layer)
            crs = gdf.crs
            gdf.to_crs(epsg=4326, inplace=True)
            bounding_box = box(*gdf.total_bounds)
            gpd.GeoSeries([bounding_box]).to_file("bounding_box.geojson", driver='GeoJSON')
            spatial_extent = str(gpd.GeoSeries([bounding_box])[0])
        except:
            print ("Error reading specified structure inventory layer, setting layer and derived spatial_extent:\n\
                         {args.inventory_layer}")
            structure_inventory_layer = None
            crs = None
            spatial_extent = None
    else:
        try:
            structure_inventory = [s for s in lines if "inventoryproviders.Init" in s][0].split('"')[1]
            # Create a bounding box feature from the structure inventory layer
            gdf = gpd.read_file(structure_inventory_layer)
            crs = gdf.crs
            gdf.to_crs(epsg=4326, inplace=True)
            bounding_box = box(*gdf.total_bounds)
            gpd.GeoSeries([bounding_box]).to_file("bounding_box.geojson", driver='GeoJSON')
            spatial_extent = str(gpd.GeoSeries([bounding_box])[0])
        except IndexError:
            print ("No structure inventory layer found. Please Specify the Layer Manually. Setting layer and derived spatial_extent to None.")
            structure_inventory_layer = None
            crs = None
            spatial_extent = None
    
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
            print ("No results layer found. Please Specify the Layer Manually. Setting Layer to None.")
            results_layer = None
            results_projection = None
    
    # Open simulation template
    # Output simulation_template.json
    model_application_template_fn = r".\example\input\json\go_consequences_model_application_template.json"
    with open(model_application_template_fn, "r") as f:
        model_application_template = json.load(f)
    C:\py\hec_meta_extract\example\input\json\go-consequences_simulation_template.json

def parse_model_application(args):

    # Get list of tifs from data directory
    tif_endswith = [".tif", ".tiff", ".geotif", ".geotiff"]
    tif_list = [os.path.join(args.model_data_dir, f) for f in os.listdir(args.model_data_dir) if f.lower().endswith(tuple(tif_endswith))]
    tif_list = [i.replace('\\', '/') for i in tif_list]
    if len(tif_list) == 0:
        print("No tifs found in data directory. Please Specify the Layer Manually. Setting Common Files Hazard Layer List to None.")
        tif_list = None

    # Get list of shps from data directory
    shp_endswith = [".shp", ".geojson", ".json", ".gpkg"]
    shp_list = [os.path.join(args.model_data_dir, f) for f in os.listdir(args.model_data_dir) if f.lower().endswith(tuple(shp_endswith))]
    shp_list = [i.replace('\\', '/') for i in shp_list]
    if len(shp_list) == 0:
        print("No shps found in data directory. Please Specify the Layer Manually. \
            Setting Common Files Structure Inventory Layer List to None.")
        shp_list = None
    
    if shp_list is not None:
        structure_inventory_layer = shp_list[0]
        gdf = gpd.read_file(structure_inventory_layer)
        crs = gdf.crs
        gdf.to_crs(epsg=4326, inplace=True)
        bounding_box = box(*gdf.total_bounds)
        gpd.GeoSeries([bounding_box]).to_file(f"./output/go-consequences/{args.prj_name}_bounding_box.geojson", driver='GeoJSON')
        spatial_extent = str(gpd.GeoSeries([bounding_box])[0])
    else:
        spatial_extent = None
        crs = None
        structure_inventory_layer = None
        print("No Structure Inventory layer found in data directory. Please Specify the Layer Manually. \
            Setting Common Files Structure Inventory Layer List to None. Setting spatial_extent to None.")
    # Get list of output files from out_dir.
    output_endswith = [".gpkg"]
    output_list = [os.path.join(args.model_out_dir, f) for f in os.listdir(args.model_out_dir) if f.lower().endswith(tuple(output_endswith))]
    output_list = [i.replace('\\', '/') for i in output_list]
    
    if len(output_list) == 0:
        print("No gpkg files found in output directory. Please Specify the Layer Manually. \
            Setting Common Files Output Layer List to None.")
        output_list = None
    
    # Output model_application.json
    model_application_template_fn = r".\example\input\json\go_consequences_model_application_template.json"
    with open(model_application_template_fn, "r") as f:
        model_application_template = json.load(f)
    
    # Keys to not include in the model_application.json output
    dropkeys_list = ['_id', 'keywords', 'common_parameters', 'spatial_valid_extent', 'common_software_version', 'temporal_resolution', \
                 'temporal_extent', 'spatial_valid_extent_resolved', 'linked_resources', 'spatial_extent_resolved', \
                 'authors', 'purpose']
    
    key_list = list(model_application_template.keys())
    # Remove keys from model_application_template that are in dropkeys_list
    for dropkey in dropkeys_list:
        model_application_template.pop(dropkey)
    
    # Add values to model_application output
    model_application_template['spatial_extent'] = spatial_extent
    model_application_template['title'] = f'Go-Consequences {args.prj_name}'
    model_application_template['description'] = f'{args.prj_description}'
    model_application_template['grid']['coordinate_system'] = str(crs)
    model_application_template['application_date'] = datetime.datetime.now().strftime("%Y-%m-%d")

    # Add Common Files to model_application output
    model_application_template['common_files_details'] = []
    model_application_template['common_files_details'].append(
        [{
            "description": "The project's Main Go-Consequences run script file",
            "location": args.prj_file,
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
        },
        {
            "description": "There may be multiple Output Feature Layers.",
            "location": output_list,
            "source_dataset": "Go-Consequences Output",
            "title": "Output Feature Layers"
        }]
    )

    # output model application json
    output_dir = os.path.join(os.getcwd(), "output")
    output_model_json = os.path.join(output_dir,f'{args.prj_name}_model_application.json')
    with open(output_model_json, "w") as outfile:
        json.dump(model_application_template, outfile)

def parse_consequences(args):
    if args.run_type == 0:
        parse_single_run(args)
    # elif args.run_type == 1:
    #     parse_multiple_runs(args)

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
    "--run_table", help="The Go-Consequences model's run table csv file. Required is run_type set to 1 as a Multiple Simulation Run. \
        (An Example run table is available at ./example/input/go-consequences/run_table.csv)", 
    required=False, 
    type=str
    )

    p.add_argument(
    "--hazard_layer", help="Optional. A Specified filepath to a Go-Consequences model's raster hazard layer. Typically this is a Max WSE geotiff exported from HEC-RAS.
    required=False, 
    type=str
    )
    p.add_argument(
    "--inventory_layer", help="Optional. A Specified filepath to a Go-Consequences model's structure inventory feature layer. Typically this is a shapefile from NSI (https://nsi.sec.usace.army.mil/downloads/).
    required=False, 
    type=str
    )

    args = p.parse_args()

    # Validate Arguments

    # Project file exists
    if not os.path.exists(args.prj_file):
        raise ValueError(f"prj_file specified does not exist:\n\
                         {args.prj_file}")

    # Run type is 0 or 1
    if (args.run_type != 0) & (args.run_type != 1):
        raise ValueError("Invalid run_type. Value must be 0 or 1.")
    
    # Run table required if run_type is 1
    if (args.run_type == 1) & (args.run_table is None):
        raise ValueError("run_table csv must be provided if run_type is 1. \n\
            (An Example run table is available at ./example/input/go-consequences/run_table.csv)") 

    # Run table exists if run_type is 1
    if (args.run_type == 1) & (args.run_table is not None):
        if not os.path.exists(args.run_table):
            raise ValueError(f"run_table specified does not exist:\n\
                            {args.run_table}")
    
    
    parse_consequences(args)