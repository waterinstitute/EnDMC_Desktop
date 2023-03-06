# hec_meta_extract

This tool is used to automatically pull key:value metadata from HEC-RAS and HEC-HMS models with the intent to assist in inputting meta data for the TWI web application: https://metadata-creation-tool.herokuapp.com/

To run the application download the release, unzip, and run the executable - https://github.com/mylesmc123/hec_meta_extract/releases

This release is primarily meant for the Louisiana Watershed Initiative to assist in extracting metadata from HEC-RAS and HEC-HMS to Json files that can be used to auto-populate the meta data fields for model applications and simulations on the meta-data web app located at: https://metadata-creation-tool.herokuapp.com/signup

The output will be a model application json, and individual simulation jsons as found in the project directories.

No installation required, unzip and run the file: Extract_HEC_Meta_Data.exe. This will open 2 windows: The application GUI, and a terminal. Output Messages will be written to the terminal window.

With the application GUI open, select the required files on your system for an HMS or RAS project file and an associated model boundary shapefile and select the Parse button for the model you which to extra meta data for.

![image](https://user-images.githubusercontent.com/64209352/221915813-d7507a8f-77fd-4f82-bb08-5280dec3a6ae.png)

*Note: Do not confuse an HEC-RAS project file for an ESRI projection file. They both have the filename extension *.prj. An HEC-RAS .prj file will be located in the root directory of an HEC-RAS model folder and can be viewed with any text editor. The screenshot below is an example of an HEC-RAS Project File.

Amite_2022.prj:

![image](https://user-images.githubusercontent.com/64209352/220175130-8bb33379-7652-4db5-b5fc-d25b05ed5d4d.png)



Output messages will be written to the terminal window with progress or any error messages.Output files will be written to the output folder where the application Extract_HEC_Meta_Data.exe is located.

To upload the output Jsons to the TWI Meta Data Creation Web App, you can click the Link and Create a New Model Application and Simulations and Load your output Jsons to fill the meta data fields automatically.

![image](https://user-images.githubusercontent.com/64209352/221949013-f261fdd6-a6bc-49ff-9a62-552b10eb781e.png)


![image](https://user-images.githubusercontent.com/64209352/221950326-dd95efdf-c9d5-432d-899d-2ef1db4dfbf8.png)

The JSON files can be ingested by the meta-data web app site by creating a new model application or simulation:

![image](https://user-images.githubusercontent.com/64209352/220426076-3e00c148-cf10-45ee-8dea-d9484a0b2ded.png)


Then, selecting 'Load JSON File'. This will auto-fill the form with the data this script was able to extract in the format currently required by the [meta-data web app](https://metadata-creation-tool.herokuapp.com/).


------For Developers Only Below------

To get the source code running, clone the repo and run:

"python setup.py install"

Requires Python version 3.9.13 in the setup.py. This is due to the requirements of the pyInstaller package, which is only necessary for creating the releases: https://github.com/mylesmc123/hec_meta_extract/releases
Otherwise, everything else works with Python version >=3.9


To run the ras_parser.py:

  ras_parser.py requires command-line argument inputs for:
  
    "--prj", help="The HEC-RAS project file. (Ex: C:\RAS_Models\Amite\Amite_2022.prj)", 
    "--shp", help="The HEC-RAS model boundary spatial extent as ESRI shapefile. (Ex: C:\RAS_Models\Amite\Features\Amite_Optimized_Geometry.shp)"
    
Example command line input to run:

     python ras_parser.py --prj Z:/Amite/Amite_LWI/Models/Amite_RAS/Amite_2022.prj --shp Z:/Amite/Amite_LWI/Models/Amite_RAS/Features/OptimizedGeometryBoundary.shp 

The output is YAML and JSON files located in /output/ras/{Project_Name}. There will be output files for the RAS model project and for each plan file (simulation).
    
![image](https://user-images.githubusercontent.com/64209352/220175255-e5267795-7a58-401b-a7ea-4b21206b2b49.png)


 
![image](https://user-images.githubusercontent.com/64209352/220424883-e40654d1-d8c5-4d10-860e-9413020ea272.png)

