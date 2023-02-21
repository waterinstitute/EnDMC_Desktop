import geopandas as gpd
import yaml
import os

def parse_shp(shp, prj_name, output_dir):
    gdf = gpd.read_file(shp)
    crs = str(gdf.crs)
    gdf = gdf.to_crs(4326)
    wkt = gdf.to_wkt().geometry[0]
    wkt_dict = {}
    wkt_dict["spatial_extent"] = wkt
    wkt_dict["coordinate_system"] = crs

    with open(os.path.join(output_dir, f'{prj_name}_wkt.yml'), 'w+') as f:
        yaml.dump(wkt_dict, f)
    
    return wkt, crs