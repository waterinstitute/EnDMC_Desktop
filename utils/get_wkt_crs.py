import geopandas as gpd
import yaml
import os

def parse_shp(shp, prj_wkt, prj_name, output_dir):
    gdf = gpd.read_file(shp)
    # check if crs set in input file
    if gdf.crs is None and prj_wkt is not None:
        # if not, set based on project's spatial projection.
        try:
            gdf.set_crs(prj_wkt, inplace=True)
        except: 
            raise Exception("CRS not set in input file, and unable to be applied automatically. Please set CRS Projection in input file using a GIS application.")
    # Edge case where crs of .shp is none and no prj_wkt was extracted.
    elif gdf.crs is None and prj_wkt is None: 
        raise Exception("CRS not set in input file, and unable to be applied automatically. Please set CRS Projection in input file using a GIS application.")
    
    crs = str(gdf.crs)
    
    gdf = gdf.to_crs(4326)
    wkt = gdf.to_wkt().geometry[0]
    wkt_dict = {}
    wkt_dict["spatial_extent"] = wkt
    wkt_dict["coordinate_system"] = crs

    # ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(os.path.join(output_dir, f'{prj_name}_wkt.yml'), 'w+') as f:
        yaml.dump(wkt_dict, f)
    
    return wkt, crs

if __name__ == '__main__':
    # For testing purposes only.
    shp = r"Z:\LWI\WSP\RAS_Export_Geometry_Region.shp"
    prj_name = "SDeerCr"
    output_dir = r"Z:\LWI\WSP"
    parse_shp(shp, prj_name, output_dir)