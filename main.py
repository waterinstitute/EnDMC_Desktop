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


version = '1.4.0'

gui = Tk()
# gui.geometry("800x50")
gui.title(f"The Water Institute: Metadata Extraction for HEC Models v{version}")
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

canvas.create_window((0,0), window=scrollable_frame, anchor='nw')
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=0, column=0)
scrollbar.grid(row=0, column=1, sticky='ns')



# # Create a frame for the gui with non-zero row&column weights
# frame_canvas = Frame(canvas)
# frame_canvas.grid(row=0, column=0, pady=(5, 0), sticky='nw')
# frame_canvas.grid_rowconfigure(0, weight=1)
# frame_canvas.grid_columnconfigure(0, weight=1)
# # Set grid_propagate to False to allow 5-by-5 buttons resizing later
# frame_canvas.grid_propagate(False)

# # Add a canvas in that frame
# canvas = canvas(frame_canvas, bg="yellow")
# canvas.grid(row=0, column=0, sticky="news")

# v = Scrollbar(frame_canvas, orient='vertical', command=canvas.yview)
# v.grid(row=0, column=1, sticky='ns')
# canvas.configure(yscrollcommand=v.set)

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
    ras_prj = ras_prj_select.file_path
    ras_shp = ras_shp_select.file_path
    print("Parsing RAS..")
    msg = ras_parser.parse(ras_prj, ras_shp)
    print(msg)
    messagebox.showinfo(title='RAS', message=msg)


def parse_hms():
    hms_prj = hms_prj_select.file_path
    hms_shp = hms_shp_select.file_path
    hms_dss = hms_dss_select.folder_path
    print("\nParsing HMS..")
    msg = hms_parser.parse(hms_prj, hms_shp, hms_dss)
    print(msg)
    messagebox.showinfo(title='HMS', message=msg)

def parse_fia():
    fia_prj = fia_prj_select.file_path
    fia_shp = fia_shp_select.file_path
    print("\nParsing FIA..")
    msg = fia_parser.parse(fia_prj, fia_shp)
    print(msg)
    messagebox.showinfo(title='FIA', message=msg)

def parse_consequences():
    cons_args = SimpleNamespace()
    cons_args.run_type = run_type.get()

    
    # Ensure Project Name and Desc are not empty
    if cons_prj_name.text == "" or cons_prj_desc.text == "":
        messagebox.showinfo(title='Go-Consequences', message="Project Name and Description must be provided")
    else:
        cons_args.prj_name = cons_prj_name.text.get()
        cons_args.prj_desc = cons_prj_desc.text.get()
    
    # Ensure Run File is not empty
    if cons_prj_select.file_path == "":
        messagebox.showinfo(title='Go-Consequences', message="Go-Consequences Run File must be provided")
    else:
        cons_args.prj_file = cons_prj_select.file_path
    
    # Ensure Data and Results Directory are not empty
    if cons_data_dir_select.folder_path == "" or cons_results_dir_select.folder_path == "":
        messagebox.showinfo(title='Go-Consequences', message="Go-Consequences Input Data Direcotry and Model Results Directory must be provided.")
    else:
        cons_args._data_dir = cons_data_dir_select.folder_path
        cons_args.results_dir = cons_results_dir_select.folder_path
    
    # Check all Single Run specific fields.
    if cons_args.run_type == 0: # single run
        # Ensure Sim Name and Sim Desc are not empty.
        if cons_sim_name.text.get() == "" or cons_sim_desc.text.get() == "":
            messagebox.showinfo(title='Go-Consequences', message="Simulation Name and Description must be provided for Run Type: Single.")
        else:
            cons_args.sim_name = cons_sim_name.text.get()
            cons_args.sim_description = cons_sim_desc.text.get()
        
        # Check if Optional Layers are provided.
        if cons_hazard_select.file_path != "":
            cons_hazard = cons_hazard_select.file_path
        if cons_inv_select.file_path != "":
            cons_inv = cons_inv_select.file_path
        if cons_res_select.file_path != "":
            cons_res = cons_res_select.file_path
    
    # Check all Multiple Run specific fields.
    elif cons_args.run_type == 1: # multiple run
        if cons_runtable_select.file_path == "":
            messagebox.showinfo(title='Go-Consequences', message="Run Table File must be provided for Run Type: Multiple.")
        else:
            cons_runtable = cons_runtable_select.file_path
    
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
    except:
        pass

filePath = StringVar()
row = 0

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

ras_shp_select = FileSelect(scrollable_frame, "RAS boundary Polygon shape file (*.shp): ")
ras_shp_select.grid(row=row)
row += 1

c = ttk.Button(scrollable_frame, text="Extract RAS MetaData", command=parse_ras)
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

hms_shp_select = FileSelect(scrollable_frame, "HMS boundary outline shape file (*.shp): ")
hms_shp_select.grid(row=row)
row += 1

hms_dss_select = FolderSelect(scrollable_frame, "Optional. DSS Data Directory: ")
hms_dss_select.grid(row=row)
row += 1

c2 = ttk.Button(scrollable_frame, text="Extract HMS MetaData", command=parse_hms)
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

fia_shp_select = FileSelect(scrollable_frame, "FIA boundary Polygon shape file (*.shp): ")
fia_shp_select.grid(row=row)
row += 1

c3 = ttk.Button(scrollable_frame, text="Extract FIA MetaData", command=parse_fia)
c3.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# Go-Consequences scrollable_frame objects
cons_label = Label(scrollable_frame, text="Go-Consequences", font=('Helveticabold', 15))
cons_label.grid(row=row, column=0, sticky="we")
row += 1

run_type = IntVar()

cons_run_type_radio1_row = row
cons_run_type_radio1 = Radiobutton(scrollable_frame, text="Run Type: Single", value=0, variable="run_type", command=cons_single_run_type_selected)
cons_run_type_radio1.grid(row=row, sticky=W, ipadx=300)
row += 1

cons_run_type_radio2_row = row
cons_run_type_radio2 = Radiobutton(scrollable_frame, text="Run Type: Multiple", value=1, variable="run_type", command=cons_multi_run_type_selected)
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

cons_data_dir_select = FolderSelect(scrollable_frame, "Model Input Data Directory: ")
cons_data_dir_select.grid(row=row)
row += 1

cons_results_dir_select = FolderSelect(scrollable_frame, "Model Results Directory: ")
cons_results_dir_select.grid(row=row)
row += 1

cons_hazard_select = FileSelect(scrollable_frame, "Optional. Specified WSE Hazard Layer (*.tif): ")
cons_hazard_select.grid(row=row)
row += 1

cons_inv_select = FileSelect(scrollable_frame, "Optional. Specified Structure Inventory (*.shp): ")
cons_inv_select.grid(row=row)
row += 1

cons_res_select = FileSelect(scrollable_frame, "Optional. Specified Results Layer (*.gpkg): ")
cons_res_select.grid(row=row)
row += 1

cons_runtable_select = FileSelect(scrollable_frame, "Multiple Run Table Data (*.csv): ")
cons_runtable_select.grid(row=row)
row += 1

cons_runtable_select.entPath.config(state="disabled")
cons_runtable_select.lblName.config(state="disabled")
cons_runtable_select.btnFind.config(state="disabled")

c4 = ttk.Button(scrollable_frame, text="Extract Consequences MetaData", command=parse_consequences)
c4.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(scrollable_frame, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# Metadata website link
link = Label(scrollable_frame, text="Upload Output to: The Water Institute Model Repository",font=('Helveticabold', 15), fg="blue", cursor="hand2")
link.grid(row=row, pady=10)
row += 1
link.bind("<Button-1>", lambda e: callback("https://metadata-creation-tool.herokuapp.com/signup"))

# Metadata website link
link = Label(scrollable_frame, text="Questions/Comments: Github",font=('Helveticabold', 10), fg="blue", cursor="hand2", anchor=SW)
link.grid(row=row)
row += 1
link.bind("<Button-1>", lambda e: callback("https://github.com/waterinstitute/hec_meta_extract/issues"))

# run app
gui.mainloop()
