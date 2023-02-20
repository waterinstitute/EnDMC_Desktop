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

def parse_prj(prj_file, prj_name, wkt, crs, plan_titles, output_dir):
    output_prj_yaml = os.path.join(output_dir, f'{prj_name}_ras_prj.yml')

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
        plan_titles.append(keyValues_dict['Plan Title']) 

        # Write the output yaml for each .p## file.
        with open(os.path.join(output_dir,f'{p_file_tail}.yml'), 'w+') as f:
            yaml.dump(keyValues_dict, f)

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