# hec_meta_extract

This tool is used to automatically pull key:value metadata from HEC-RAS and HEC-HMS models with the intent to assist in inputting meta data for the TWI web application: https://metadata-creation-tool.herokuapp.com/

To install - Clone the repo and run:

"python setup.py install"

Tested with Python version 3.11.0

To run the ras_parser.py:

  ras_parser.py requires command-line argument inputs for:
  
    "--prj", help="The HEC-RAS project file. (Ex: C:\RAS_Models\Amite\Amite_2022.prj)", 
    "--shp", help="The HEC-RAS model boundary spatial extent as ESRI shapefile. (Ex: C:\RAS_Models\Amite\Features\Amite_Optimized_Geometry.shp)"
    
Example command line input to run:

     python ras_parser.py --prj Z:/Amite/Amite_LWI/Models/Amite_RAS/Amite_2022.prj --shp Z:/Amite/Amite_LWI/Models/Amite_RAS/Features/OptimizedGeometryBoundary.shp 
      
  Do not confuse an HEC-RAS project file for an ESRI projection file. They both have the filename extension *.prj. An HEC-RAS .prj file will be located in the root directory of an HEC-RAS model folder and can be viewed with any text editor. The screenshot below is an example of an HEC-RAS Project File.
    
Amite_2022.prj:

![image](https://user-images.githubusercontent.com/64209352/220175130-8bb33379-7652-4db5-b5fc-d25b05ed5d4d.png)

The output is YAML and JSON files located in /output/ras/{Project_Name}. There will be output files for the RAS model project and for each plan file (simulation).
    
![image](https://user-images.githubusercontent.com/64209352/220175255-e5267795-7a58-401b-a7ea-4b21206b2b49.png)

The JSON files can be ingested by the meta-data web app site by creating a new model application or simulation selecting 'Load JSON File'. This will auto-fill the form with the data this script was able to extract in the format currently required by the [meta-data web app](https://metadata-creation-tool.herokuapp.com/).
 
![image](https://user-images.githubusercontent.com/64209352/220424883-e40654d1-d8c5-4d10-860e-9413020ea272.png)

