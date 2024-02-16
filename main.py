from argparse import Namespace
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox, Radiobutton, Label, Scrollbar, Frame, Canvas

import hms_parser
import ras_parser
import fia_parser
import go_consequences_parser
import os
import webbrowser
from types import SimpleNamespace


version = '2.1'

gui = Tk()
# gui.geometry("800x50")
gui.title(f"EnDMC Desktop: Metadata Extraction for HEC Models v{version}")
gui.resizable(False, False)

# Set Column Weight
gui.columnconfigure(0, weight=1)
gui.rowconfigure(0, weight=1)

img = PhotoImage(file=os.path.join(os.getcwd(), 'icon.png'))
gui.tk.call('wm', 'iconphoto', gui._w, img)
# gui.wm_iconbitmap('icon.ico')

# Add a frame for the Canvas and Scrollbar
frame = Frame(gui)
frame.grid(row=0, column=0, sticky='news')

# Add a canvas in that frame
canvas = Canvas(frame, width=720, height=700)
# canvas.grid(row=0, column=0, sticky="news")

# Link a scrollbar to the canvas
scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=0, column=0)
scrollbar.grid(row=0, column=1, sticky='ns')

# Define a callback function


def callback(url):
    webbrowser.open_new_tab(url)


class FileSelect(Frame):
    def __init__(self, parent=None, fileDescription="", **kw):
        Frame.__init__(self, master=parent, **kw)
        self.filePath = StringVar()
        self.lblName = Label(self, text=fileDescription, width=37, anchor=E)
        self.lblName.grid(row=0, column=0, ipady=1)
        self.entPath = Entry(self, textvariable=self.filePath, width=50)
        self.entPath.grid(row=0, column=1, ipady=1)
        self.btnFind = ttk.Button(
            self, text="Browse...", command=self.setFilePath)
        self.btnFind.grid(row=0, column=2, ipady=1)

    def setFilePath(self):
        file_selected = filedialog.askopenfilename(
            # filetypes=[("Excel files", ".xlsx .xls")]
            filetypes=[("File Types", ".dss .hms .prj .shp .geojson .json .gpkg .go .tif .tiff .geotif .geotiff")])
        self.filePath.set(file_selected)

    @property
    def file_path(self):
        return self.filePath.get()


class FolderSelect(Frame):
    def __init__(self, parent=None, folderDescription="", **kw):
        Frame.__init__(self, master=parent, **kw)
        self.folderPath = StringVar()
        self.lblName = Label(self, text=folderDescription, width=37, anchor=E)
        self.lblName.grid(row=0, column=0, ipady=1)
        self.entPath = Entry(self, textvariable=self.folderPath, width=50)
        self.entPath.grid(row=0, column=1, ipady=1)
        self.btnFind = ttk.Button(
            self, text="Browse...", command=self.setFolderPath)
        self.btnFind.grid(row=0, column=2, ipady=1)

    def setFolderPath(self):
        folder_selected = filedialog.askdirectory()
        self.folderPath.set(folder_selected)

    @property
    def folder_path(self):
        return self.folderPath.get()


class TextField(Frame):
    def __init__(self, parent=None, textDescription="", **kw):
        Frame.__init__(self, master=parent, **kw)
        self.text = StringVar()
        self.lblName = Label(self, text=textDescription, width=37, anchor=E)
        self.lblName.grid(row=0, column=0, ipady=1)
        self.entPath = Entry(self, textvariable=self.text, width=63)
        self.entPath.grid(row=0, column=1, ipady=1)
        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.grid(row=row, ipady=1)


def parse_ras():
    args = Namespace(prj=ras_prj_select.file_path, shp=ras_shp_select.file_path, keywords=global_keywords.text.get(), id=global_prj_id.text.get())
    args.keywords = args.keywords.split(",")
    args.keywords = [x.strip() for x in args.keywords]
    print("Parsing RAS..")
    msg = ras_parser.parse(args)
    print(msg)
    messagebox.showinfo(title='RAS', message=msg)


def parse_hms():
    args = Namespace(prj=hms_prj_select.file_path, shp=hms_shp_select.file_path, dss=hms_dss_select.folder_path, keywords=global_keywords.text.get(), id=global_prj_id.text.get())
    args.keywords = args.keywords.split(",")
    args.keywords = [x.strip() for x in args.keywords]
    print("\nParsing HMS..")
    msg = hms_parser.parse(args.prj, args.shp, args.dss, args.keywords, args.id)
    print(msg)
    messagebox.showinfo(title='HMS', message=msg)


def parse_fia():
    args = Namespace(prj=fia_prj_select.file_path, shp=fia_shp_select.file_path, keywords=global_keywords.text.get(), id=global_prj_id.text.get())
    args.keywords = args.keywords.split(",")
    args.keywords = [x.strip() for x in args.keywords]
    print("\nParsing FIA..")
    msg = fia_parser.parse(args.prj, args.shp, args.keywords, args.id)
    print(msg)
    messagebox.showinfo(title='FIA', message=msg)


def parse_consequences():
    cons_args = SimpleNamespace()
    cons_args.run_type = run_type.get()
    print('Run Type: ', cons_args.run_type)

    # Get Global Keywords
    cons_args.keywords = global_keywords.text.get()
    cons_args.keywords = cons_args.keywords.split(",")
    cons_args.keywords = [x.strip() for x in cons_args.keywords]

    # Get Project ID
    cons_args.prj_id = global_prj_id.text.get()

    # Ensure Project Name and Desc are not empty
    if cons_prj_name.text == "" or cons_prj_desc.text == "":
        messagebox.showinfo(title='Go-Consequences',
                            message="Project Name and Description must be provided")
    else:
        cons_args.prj_name = cons_prj_name.text.get()
        cons_args.prj_description = cons_prj_desc.text.get()

    # Ensure Run File is not empty
    if cons_prj_select.file_path == "":
        messagebox.showinfo(title='Go-Consequences',
                            message="Go-Consequences Run File must be provided")
    else:
        cons_args.prj_file = cons_prj_select.file_path

    # Ensure Data and Results Directory are not empty
    if cons_data_dir_select.folder_path == "" or cons_results_dir_select.folder_path == "":
        messagebox.showinfo(title='Go-Consequences',
                            message="Go-Consequences Input Data Directory and Model Results Directory must be provided.")
    else:
        cons_args.model_data_dir = cons_data_dir_select.folder_path
        cons_args.model_out_dir = cons_results_dir_select.folder_path

    # Check all Single Run specific fields.
    if cons_args.run_type == 0:  # single run
        # Ensure Sim Name and Sim Desc are not empty.
        if cons_sim_name.text.get() == "" or cons_sim_desc.text.get() == "":
            messagebox.showinfo(
                title='Go-Consequences', message="Simulation Name and Description must be provided for Run Type: Single.")
        else:
            cons_args.sim_name = cons_sim_name.text.get()
            cons_args.sim_description = cons_sim_desc.text.get()

        # Check if Optional Layers are provided.
        if cons_hazard_select.file_path != "":
            cons_args.hazard_layer = cons_hazard_select.file_path
        else:
            cons_args.hazard_layer = None
        if cons_inv_select.file_path != "":
            cons_args.inventory_layer = cons_inv_select.file_path
        else:
            cons_args.inventory_layer = None
        if cons_res_select.file_path != "":
            cons_args.results_layer = cons_res_select.file_path
        else:
            cons_args.results_layer = None

    # Check all Multiple Run specific fields.
    elif cons_args.run_type == 1:  # multiple run
        if cons_runtable_select.file_path == "":
            messagebox.showinfo(
                title='Go-Consequences', message="Run Table File must be provided for Run Type: Multiple.")
        else:
            cons_args.run_table = cons_runtable_select.file_path

    print("\nParsing Go-Consequences..")
    print(cons_args)
    # msg = go_consequences_parser.parse(cons_args)
    go_consequences_parser.parse_consequences(cons_args)
    # print(msg)
    # messagebox.showinfo(title='Go-Consequences', message=msg)


def cons_single_run_type_selected():
    try:

        cons_sim_name.entPath.config(state="normal")
        cons_sim_name.lblName.config(state="normal")

        cons_sim_desc.entPath.config(state="normal")
        cons_sim_desc.lblName.config(state="normal")

        cons_hazard_select.entPath.config(state="normal")
        cons_hazard_select.lblName.config(state="normal")
        cons_hazard_select.btnFind.config(state="normal")

        cons_inv_select.entPath.config(state="normal")
        cons_inv_select.lblName.config(state="normal")
        cons_inv_select.btnFind.config(state="normal")

        cons_res_select.entPath.config(state="normal")
        cons_res_select.lblName.config(state="normal")
        cons_res_select.btnFind.config(state="normal")

        cons_runtable_select.entPath.config(state="disabled")
        cons_runtable_select.lblName.config(state="disabled")
        cons_runtable_select.btnFind.config(state="disabled")
        run_type.set(0)
    except:
        pass


def cons_multi_run_type_selected():
    try:
        cons_runtable_select.entPath.config(state="normal")
        cons_runtable_select.lblName.config(state="normal")
        cons_runtable_select.btnFind.config(state="normal")

        cons_sim_name.entPath.config(state="disabled")
        cons_sim_name.lblName.config(state="disabled")

        cons_sim_desc.entPath.config(state="disabled")
        cons_sim_desc.lblName.config(state="disabled")

        cons_hazard_select.entPath.config(state="disabled")
        cons_hazard_select.lblName.config(state="disabled")
        cons_hazard_select.btnFind.config(state="disabled")

        cons_inv_select.entPath.config(state="disabled")
        cons_inv_select.lblName.config(state="disabled")
        cons_inv_select.btnFind.config(state="disabled")

        cons_res_select.entPath.config(state="disabled")
        cons_res_select.lblName.config(state="disabled")
        cons_res_select.btnFind.config(state="disabled")
        run_type.set(1)
    except:
        pass


print('''

 _______ .-. .-.,---.                                           
|__   __|| | | || .-'                                           
  )| |   | `-' || `-.                                           
 (_) |   | .-. || .-'                                           
   | |   | | |)||  `--.                                         
   `-'   /(  (_)/( __.'                                         
        (__)   (__)                                             
.-.  .-.  .--.  _______ ,---.  ,---.                            
| |/\| | / /\ \|__   __|| .-'  | .-.\                           
| /  \ |/ /__\ \ )| |   | `-.  | `-'/                           
|  /\  ||  __  |(_) |   | .-'  |   (                            
|(/  \ || |  |)|  | |   |  `--.| |\ \                           
(_)   \||_|  (_)  `-'   /( __.'|_| \)\                          
                       (__)        (__)                         
,-..-. .-.   .---.  _______ ,-. _______ .-. .-. _______ ,---.   
|(||  \| |  ( .-._)|__   __||(||__   __|| | | ||__   __|| .-'   
(_)|   | | (_) \     )| |   (_)  )| |   | | | |  )| |   | `-.   
| || |\  | _  \ \   (_) |   | | (_) |   | | | | (_) |   | .-'   
| || | |)|( `-'  )    | |   | |   | |   | `-')|   | |   |  `--. 
`-'/(  (_) `----'     `-'   `-'   `-'   `---(_)   `-'   /( __.' 
  (__)                                                 (__)     

                                                                                                
    ____                                  __          
   / __ \ _____ ___   _____ ___   ____   / /_ _____ _ 
  / /_/ // ___// _ \ / ___// _ \ / __ \ / __// ___/(_)
 / ____// /   /  __/(__  )/  __// / / // /_ (__  )_   
/_/    /_/    \___//____/ \___//_/ /_/ \__//____/(_)  
                                                      
      

███████╗███╗   ██╗██████╗ ███╗   ███╗ ██████╗            ██████╗ ███████╗███████╗██╗  ██╗████████╗ ██████╗ ██████╗ 
██╔════╝████╗  ██║██╔══██╗████╗ ████║██╔════╝            ██╔══██╗██╔════╝██╔════╝██║ ██╔╝╚══██╔══╝██╔═══██╗██╔══██╗
█████╗  ██╔██╗ ██║██║  ██║██╔████╔██║██║                 ██║  ██║█████╗  ███████╗█████╔╝    ██║   ██║   ██║██████╔╝
██╔══╝  ██║╚██╗██║██║  ██║██║╚██╔╝██║██║                 ██║  ██║██╔══╝  ╚════██║██╔═██╗    ██║   ██║   ██║██╔═══╝ 
███████╗██║ ╚████║██████╔╝██║ ╚═╝ ██║╚██████╗            ██████╔╝███████╗███████║██║  ██╗   ██║   ╚██████╔╝██║     
╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝     ╚═╝ ╚═════╝            ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  

Please keep this window open while the program is running.
Additional Output information will be displayed here.
Report any issues via Github: https://github.com/waterinstitute/EnDMC_Desktop/issues\n\n
''')

filePath = StringVar()
row = 0

# Separator object
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.grid(row=0, ipady=10)
row += 1

# Global Keywords
global_label = Label(
    scrollable_frame, text="Global Keywords", font=('Helveticabold', 15))
global_label.grid(row=row, column=0, sticky="we")
row += 1

global_label2 = Label(
    scrollable_frame, text="(Optional. Will be added as keywords to every extracted model.)", font=('Helvetica', 10))
global_label2.grid(row=row, column=0, sticky="we")
row += 1

global_prj_id = TextField(
    scrollable_frame, "Project ID (Internal Organizational Code): ")
global_prj_id.grid(row=row)
row += 1

global_keywords = TextField(
    scrollable_frame, "Additional Keywords (ex: LWI, Region 7):")
global_keywords.grid(row=row)
row += 1

# Separator object
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.grid(row=0, ipady=10)
row += 1

# RAS gui objects
ras_label = Label(scrollable_frame, text="HEC-RAS", font=('Helveticabold', 15))
ras_label.grid(row=row, column=0, sticky="we")
row += 1

ras_prj_select = FileSelect(scrollable_frame, "RAS project file (*.prj): ")
ras_prj_select.grid(row=row)
row += 1

ras_shp_select = FileSelect(
    scrollable_frame, "RAS boundary Polygon shape file (*.shp): ")
ras_shp_select.grid(row=row)
row += 1

c = ttk.Button(scrollable_frame, text="Extract RAS MetaData",
               command=parse_ras)
c.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# HMS scrollable_frame objects
hms_label = Label(scrollable_frame, text="HEC-HMS", font=('Helveticabold', 15))
hms_label.grid(row=row, column=0, sticky="we")
row += 1

hms_prj_select = FileSelect(scrollable_frame, "HMS project file (*.hms): ")
hms_prj_select.grid(row=row)
row += 1

hms_shp_select = FileSelect(
    scrollable_frame, "HMS boundary outline shape file (*.shp): ")
hms_shp_select.grid(row=row)
row += 1

hms_dss_select = FolderSelect(
    scrollable_frame, "Optional. DSS Data Directory: ")
hms_dss_select.grid(row=row)
row += 1

c2 = ttk.Button(scrollable_frame, text="Extract HMS MetaData",
                command=parse_hms)
c2.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# FIA gui objects
fia_label = Label(scrollable_frame, text="HEC-FIA", font=('Helveticabold', 15))
fia_label.grid(row=row, column=0, sticky="we")
row += 1

fia_prj_select = FileSelect(scrollable_frame, "FIA project file (*.prj): ")
fia_prj_select.grid(row=row)
row += 1

fia_shp_select = FileSelect(
    scrollable_frame, "FIA boundary Polygon shape file (*.shp): ")
fia_shp_select.grid(row=row)
row += 1

c3 = ttk.Button(scrollable_frame, text="Extract FIA MetaData",
                command=parse_fia)
c3.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# Go-Consequences scrollable_frame objects
cons_label = Label(scrollable_frame, text="Go-Consequences",
                   font=('Helveticabold', 15))
cons_label.grid(row=row, column=0, sticky="we")
row += 1

run_type = IntVar()

cons_run_type_radio1_row = row
cons_run_type_radio1 = Radiobutton(scrollable_frame, text="Run Type: Single",
                                   value=0, variable="run_type", command=cons_single_run_type_selected)
cons_run_type_radio1.grid(row=row, sticky=W, ipadx=300)
row += 1

cons_run_type_radio2_row = row
cons_run_type_radio2 = Radiobutton(scrollable_frame, text="Run Type: Multiple",
                                   value=1, variable="run_type", command=cons_multi_run_type_selected)
cons_run_type_radio2.grid(row=row, sticky=W, ipadx=300)
row += 1

cons_run_type_radio1.select()


cons_prj_name = TextField(scrollable_frame, "Project Name: ")
cons_prj_name.grid(row=row)
row += 1

cons_prj_desc = TextField(scrollable_frame, "Project Description: ")
cons_prj_desc.grid(row=row)
row += 1

cons_sim_name = TextField(scrollable_frame, "Simulation Name: ")
cons_sim_name.grid(row=row)
row += 1

cons_sim_desc = TextField(scrollable_frame, "Simulation Description: ")
cons_sim_desc.grid(row=row)
row += 1

cons_prj_select = FileSelect(scrollable_frame, "Model Run file (*.go): ")
cons_prj_select.grid(row=row)
row += 1

cons_data_dir_select = FolderSelect(
    scrollable_frame, "Model Input Data Directory: ")
cons_data_dir_select.grid(row=row)
row += 1

cons_results_dir_select = FolderSelect(
    scrollable_frame, "Model Results Directory: ")
cons_results_dir_select.grid(row=row)
row += 1

cons_hazard_select = FileSelect(
    scrollable_frame, "Optional. Specified WSE Hazard Layer (*.tif): ")
cons_hazard_select.grid(row=row)
row += 1

cons_inv_select = FileSelect(
    scrollable_frame, "Optional. Specified Structure Inventory (*.shp): ")
cons_inv_select.grid(row=row)
row += 1

cons_res_select = FileSelect(
    scrollable_frame, "Optional. Specified Results Layer (*.gpkg): ")
cons_res_select.grid(row=row)
row += 1

cons_runtable_select = FileSelect(
    scrollable_frame, "Multiple Run Table Data (*.csv): ")
cons_runtable_select.grid(row=row)
row += 1

cons_runtable_select.entPath.config(state="disabled")
cons_runtable_select.lblName.config(state="disabled")
cons_runtable_select.btnFind.config(state="disabled")

c4 = ttk.Button(scrollable_frame,
                text="Extract Consequences MetaData", command=parse_consequences)
c4.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# Upload To label
upload_label = Label(
    scrollable_frame, text="Upload output to one of the following EnDMC websites:", font=('Helveticabold', 15))
upload_label.grid(row=row, column=0, sticky="we")
row += 1

# LWI website link
link = Label(scrollable_frame, text="Louisiana Watershed Initivative",
             font=('Helveticabold', 13), fg="blue", cursor="hand2")
link.grid(row=row)
row += 1
link.bind("<Button-1>", lambda e: callback("https://lwi.endmc.org/"))

# TWI website link
link = Label(scrollable_frame, text="The Water Institute",
             font=('Helveticabold', 13), fg="blue", cursor="hand2")
link.grid(row=row)
row += 1
link.bind("<Button-1>", lambda e: callback("https://twi.endmc.org/"))

# Github Issues website link
link = Label(scrollable_frame, text="Questions/Comments: Github",
             font=('Helveticabold', 10), fg="blue", cursor="hand2", anchor=SW)
link.grid(row=row, pady=10)
row += 1
link.bind("<Button-1>",
          lambda e: callback("https://github.com/waterinstitute/hec_meta_extract/issues"))


# For testing only, auto input file paths.
# Global Variables
# global_prj_id.text.set("P00813")
# global_keywords.text.set("LWI, Region 7")
# # RAS
# ras_prj_select.filePath.set("V:/projects/p00813_nps_2023_greenbelt_ig/02_analysis/HEC-RAS_MainModel/Greenbelt_RAS.prj")
# ras_shp_select.filePath.set("V:/projects/p00813_nps_2023_greenbelt_ig/02_analysis/HEC-RAS_MainModel/Shapes/2DFlowArea.shp")
# # HMS
# hms_prj_select.filePath.set("C:/py/WestPark_HMS/WestPark_HMS.hms")
# hms_shp_select.filePath.set("C:/py/WestPark_HMS/maps/WestPark_Boundary_3451.shp")
# hms_dss_select.folderPath.set("C:/py/WestPark_HMS/data")
# # FIA
# fia_prj_select.filePath.set("Z:/LWI/FIA Darlington/AmiteWatershed_2016Event_WithDarlingtonReservoir/AmiteWatershed_2016Event.prj")
# fia_shp_select.filePath.set("Z:/LWI/FIA Darlington/AmiteWatershed_2016Event_WithDarlingtonReservoir/maps/AmiteHUC8_NAD83_Albers.shp")
# # Go-Consequences either run type
# cons_prj_name.text.set("Amite")
# cons_prj_desc.text.set("Amite Go-Consequences Model Based on Dewberry Amite River HEC-RAS Model Results and USACE National Structure Inventory Data")
# cons_prj_select.filePath.set("C:/py/hec_meta_extract/dev/go-consequences/main.go")
# cons_data_dir_select.folderPath.set("C:/py/hec_meta_extract/dev/go-consequences/data")
# cons_results_dir_select.folderPath.set("C:/py/hec_meta_extract/dev/go-consequences/output")
# # Go-Consequences single run
# cons_sim_name.text.set("Hurricane Ida 2021")
# cons_sim_desc.text.set("Hurricane Ida 2021 Water Surface Elevation Results from Dewberry Amite River HEC-RAS Model with NSI Data")
# # Go-Consequences single run - optional layers
# cons_hazard_select.filePath.set("C:/py/hec_meta_extract/dev/go-consequences/data/Amite_Katrina2005_AORC_ADCIRC_2021Geometry.tif")
# cons_inv_select.filePath.set("C:/py/hec_meta_extract/dev/go-consequences/data/NSI.shp")
# cons_res_select.filePath.set("C:/py/hec_meta_extract/dev/go-consequences/output/Amite_Isaac2012_AORC_ADCIRC_NoWind_2022Geometry_NSI.gpkg")
# # Go-Consequences multiple run
# cons_runtable_select.filePath.set("C:/py/hec_meta_extract/example/input/go-consequences/run_table.csv")

# run app
gui.mainloop()
