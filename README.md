# EnDMC Desktop

To run the application download the release, unzip, and run the executable - [EnDMC Desktop - Releases](https://github.com/waterinstitute/hec_meta_extract/releases/)

## Description
This software is used to aid users of The Water Institute's `Environmental Data Model Catalog (EnDMC)` websites:

[Louisiana Watershed Initiative EnDMC](https://lwi.endmc.org)

[The Water Institute EnDMC](https://twi.endmc.org)


`EnDMC Desktop` is a separate Windows PC application that can automate extracting metadata from:

- HEC-RAS
- HEC-HMS
- HEC-FIA
- HEC Go-Consequences

`EnDMC Desktop` outputs JSON files that can be used to auto-populate the meta data fields for model applications and simulations on any `EnDMC website`.



## Directions:

No installation is required. Unzip and run the file: EnDMC_Desktop.exe on a Windows PC. This will open 2 windows: The application GUI, and a terminal. Output Messages will be written to the terminal window.

With the application GUI open, select the required files on your system for any model (HMS, RAS, etc.). For example, to extract a model application and simulation JSONs for HEC-RAS, select a project file and an associated model boundary shapefile, and select the Extract button.

![image](https://github.com/waterinstitute/hec_meta_extract/assets/64209352/7ec3c63b-7482-4bed-b358-514b3fcd90cd)

Output messages will be written to the terminal window with progress or any error messages. Output files will be written to the output folder where the application Extract_HEC_Meta_Data.exe is located.

The output will be a model application Json, and individual simulation Json's as found in the project directories. The figure below illustrates the meta data desktop application's output for an HMS model:

![image](https://github.com/waterinstitute/hec_meta_extract/assets/64209352/e2db237e-48bc-42fa-b5c8-7ee0ef59048f)

Each model will output a single model_application Json. The tool will automatically find all RAS plan files, all HMS simulations, and all FIA scenarios and output a Json for each respectively to input to the web app as model simulations.

For Go-Consequences there are a few more options. Notice in the UI the first option is a selection of `Run Type` which can either be `Single` or `Multiple`. The remaining input fields will be enabled/disabled based on the `Run Type` selection.

Go-Consequences does not have a GUI like the other HEC models; instead it runs from a Go-lang script file. This file is required to read the other input files from and is requested in the field named: `Model Run File`. `EnDMC Desktop` will attempt to automatically parse the Input data based on the Go-lang script provided. 

In addition, there are fields for the `Model Input Data Directory` and `Model Results Directory`. These fields will provide additional options for automatic extraction based on file types found in these directories. It is recommended for the purposes of automation, to have the input files for inventory as ESRI shapefiles (*.shp), so that `EnDMC Desktop` can differentiate these input files from the output Geopackage (*.gpkg) file types. Go-Consequences, by default, will output a Geopackage result layer.

For a Single `Run Type`, there are optional fields for the user to specify the exact input and output layers. These can be used should `EnDMC Desktop` not parse the correct files automatically.

For a Multiple `Run Type` a `Run Table` is required. This CSV table is used to specify multiple simulations and their respective associated input and output files. An example of this CSV file is available in the application folder: `example\input\go-consequences\run_table.csv

![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/226d6ca1-2e63-472c-80a5-e8e82029291a)

## EnDMC Website Directions

To upload the output Json's to `EnDMC`, you can click the Link to go to a specific EnDMC Website instance.

![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/85fede6a-5ec1-4003-8934-315ca7e349e6)

This will open EnDMC website to the front page.
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/121c4cc2-7b3c-4c6b-ba7b-5619907ae18c)

If you have not done so already, Create an EnDMC account.

-  Go to:
    -  [Create Account - LWI EnDMC](https://lwi.endmc.org/signup)
    -  [Create Account - TWI EnDMC](https://twi.endmc.org/signup)

- Note that you’ll be requesting an editor role which needs to be approved by the organization’s admin, so it’s best to do this a few days before you plan to start creating metadata records.

![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/cfb068e7-d3b7-4f1c-a86c-dc93e73899f6)

-	Once you have been given an editor role in EnDMC, login, go to the `Create` menu on the navigation bar and select `Model Application`.

![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/28acbd5f-9062-4ba1-8eef-6a3a872814c3)

-	On the Model Application creation page, select `Load an existing metadate file`
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/a92746ba-c988-4f9a-911b-ba7a7cb0681d)

- and select the `model_application .json` output file you created with the desktop tool. 

-	Please note that not all fields required by EnDMC will be provided by the metadata file created by the desktop tool. **PLEASE BE SURE TO REVIEW EACH FIELD AND CORRECT / ADD ANY MISSING OR INCORRECT INFORMATION ON THE CREATE MODEL APPLICATION PAGE.** 

- Also note after adding the common software version, you will be asked if you want to overwrite the files currently entered with those inherited from the common software version – select `Cancel`. 
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/9afe4099-728a-4ca3-88c4-cd698ed5db82)

-	Upload the model application itself under the Upload Files section.
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/5484c15c-639a-4316-b111-b389aaceb8dd)

-	After the upload is complete and you have reviewed all entries, click Submit. 
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/ff7f4fd4-40f8-4cc5-abd2-29ee8bef05e6)

- Go to the `Create` menu on the navigation bar and select `Simulation.
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/877413f0-985c-420a-a04a-1d3983e869f2)

-	On the `Simulation` creation page, select `Load an existing metadate file`
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/a92746ba-c988-4f9a-911b-ba7a7cb0681d)

- and select one of the `simulation .json` output files you created with the desktop tool. 

- o	Note simulation files need to be added one at a time. 

-	On the `Model Application` field, search for the model application you just created previously.
-	**PLEASE BE SURE TO REVIEW EACH FIELD AND CORRECT / ADD ANY MISSING OR INCORRECT INFORMATION ON THE CREATE SIMULATION PAGE.** 

- o	Also note, just as on the model application creation page, after adding the common software version, you will be asked if you want to overwrite the files currently entered with those inherited from the common software version – select Cancel for input files, output files, and common parameters.
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/3e05798b-91ca-47fa-bab5-e3f9fd32240d)

-	To double check that the simulations are associated with the model application you created, find your model application record using either the Search bar at the top of the screen or the `See all` menu in the navigation bar. 
![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/84907c3b-f62d-4612-8cf5-7653b204eff6)

![image](https://github.com/waterinstitute/EnDMC_Desktop/assets/64209352/64876c91-2dd1-4b3c-907b-f398025317cb)

## Additional Boundary Shapefile Directions

The desktop application requires the user to input a shapefile for the boundary of model. This allows for mapping the geospatial location of the model. The directions below will assist in creating this file and ensuring it is in the correct location for your model's meta data.

### RAS Boundary Shapefile Extraction:
From RAS Mapper, the geometry can be exported directly by right clicking the geometry and selecting to export as a shapefile.

![1d 2d export boundary shp](https://github.com/waterinstitute/hec_meta_extract/assets/64209352/54670785-69b8-46ef-b7e7-27aefd94c585)

### HMS Boundary Shapefile Extraction:
For HMS, the subbasin multi-part polygon shapefile can be used directly or by using a GIS can be 'Dissolved' to a single polygon. To extract a subbasin shapefile from an HMS project you can export directly, but often times there will be a shapefile already located in the HMS project's 'maps' directory. 

The figure below illustrates how to export a subbasin shapefile using the GIS capabilities within HMS.

![image](https://github.com/waterinstitute/hec_meta_extract/assets/64209352/a8ab88d1-56ad-4470-a9ec-2309ee502555)

For FIA, there is also a 'maps' folder located in the project directory.

You can always create your own boundary shapefile in a GIS application such as ArcpMap or QGIS as well.

After processing the meta data for HMS, RAS, or FIA; the output will include a Well-Known Text (WKT) File to make it easy to check the geospatial layer that is being included in the metadata json output files. This WKT will be located in the output directory and named as {project_name}_wkt.yml

![image](https://github.com/waterinstitute/hec_meta_extract/assets/64209352/04ad37bc-6584-46f5-b974-fbabc5f51451)

This data will also be automatically added to the 'spatial-extent' of our metadata Json's that we load to the [metadata web app](https://metadata-creation-tool.herokuapp.com/), but we can use this WKT to easily look at our boundary on a map. For example, by going to the following address and then pasting the 'spatial-extent' value into the dialog box, we will see our model outline on a map:

[WKT Playground](https://clydedacruz.github.io/openstreetmap-wkt-playground/)

![image](https://github.com/waterinstitute/hec_meta_extract/assets/64209352/334ea8f2-8974-40be-b702-a63152dbd5de)

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

Build Notes:

 To minimize the .exe file size, only needed dependencies are included in the environment. Created the environment using Python 3.9 venv and the dependencies found in setup.py.

 The .exe was first built using pyInstaller from the project directory:
    
    pyinstaller main.py -F -n Extract_HEC_Meta_Data.exe
    
  However, all subsequent releases use the Spec file:
    
    pyinstaller Extract_HEC_Meta_Data.exe.spec

  This creates an .exe in the directory ./dist. When the .exe is zipped as on the Releases page, the ./Example directory is packaged with it because the Json templates used for creating new Json files are required and in that directory. 
  
  If any changes are made to the example directory, update the /dist/Example directory with the new files to then include in the zipped release.
  
  .ico and png files need to be included in zipped release as well.
  

