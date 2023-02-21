import glob
import copy
import yaml, json
import os
import argparse
from utils import get_wkt_crs
from datetime import datetime

def parse(prj, shp):

    # Get project name
    prj_dir, prj_file_tail = os.path.split(prj)
    prj_name = prj_file_tail.split(".")[0]

    # Set output directory
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'output', 'hms', prj_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get WKT and CRS from shp
    wkt, crs = get_wkt_crs.parse_shp(shp, prj_name, output_dir)

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

    args = p.parse_args()
    parse(args.hms, args.shp)