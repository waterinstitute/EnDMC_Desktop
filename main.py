from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox, Radiobutton, Label

import hms_parser
import ras_parser
import fia_parser
import go_consequences_parser
import os
import webbrowser


version = '1.4.0'

gui = Tk()
gui.geometry("800x800")
gui.title(f"The Water Institute: Metadata Extraction for HEC Models v{version}")

# Set Column Weight
gui.columnconfigure(0, weight=1)
gui.columnconfigure(1, weight=1)

img = PhotoImage(file=os.path.join(os.getcwd(), 'icon.png'))
gui.tk.call('wm', 'iconphoto', gui._w, img)
# gui.wm_iconbitmap('icon.ico')


# Define a callback function
def callback(url):
   webbrowser.open_new_tab(url)

class FileSelect(Frame):
    def __init__(self, parent=None, fileDescription="", **kw):
        Frame.__init__(self, master=parent, **kw)
        self.filePath = StringVar()
        self.lblName = Label(self, text=fileDescription, width=37, anchor=E)
        self.lblName.grid(row=0, column=0)
        self.entPath = Entry(self, textvariable=self.filePath, width=50)
        self.entPath.grid(row=0, column=1)
        self.btnFind = ttk.Button(
            self, text="Browse...", command=self.setFilePath)
        self.btnFind.grid(row=0, column=2)

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
        self.lblName.grid(row=0, column=0)
        self.entPath = Entry(self, textvariable=self.folderPath, width=50)
        self.entPath.grid(row=0, column=1)
        self.btnFind = ttk.Button(
            self, text="Browse...", command=self.setFolderPath)
        self.btnFind.grid(row=0, column=2)

    def setFolderPath(self):
        folder_selected = filedialog.askdirectory()
        self.folderPath.set(folder_selected)

    @property
    def folder_path(self):
        return self.folderPath.get()


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
    cons_prj = cons_prj_select.file_path
    cons_shp = cons_shp_select.file_path
    print("\nParsing cons..")
    msg = go_consequences_parser.parse(cons_prj, cons_shp)
    print(msg)
    messagebox.showinfo(title='Go-Consequences', message=msg)

def cons_single_run_type_selected():
    try:
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

# RAS gui objects
ras_label = Label(gui, text="HEC-RAS", font=('Helveticabold', 15))
ras_label.grid(row=0, column=0, sticky="we")

row = 0

ras_prj_select = FileSelect(gui, "RAS project file (*.prj): ")
ras_prj_select.grid(row=row)
row += 1

ras_shp_select = FileSelect(gui, "RAS boundary Polygon shape file (*.shp): ")
ras_shp_select.grid(row=row)
row += 1

c = ttk.Button(gui, text="Extract RAS MetaData", command=parse_ras)
c.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(gui, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# HMS gui objects
hms_label = Label(gui, text="HEC-HMS", font=('Helveticabold', 15))
hms_label.grid(row=row, column=0, sticky="we")
row += 1

hms_prj_select = FileSelect(gui, "HMS project file (*.hms): ")
hms_prj_select.grid(row=row)
row += 1

hms_shp_select = FileSelect(gui, "HMS boundary outline shape file (*.shp): ")
hms_shp_select.grid(row=row)
row += 1

hms_dss_select = FolderSelect(gui, "Optional. DSS Data Directory: ")
hms_dss_select.grid(row=row)
row += 1

c2 = ttk.Button(gui, text="Extract HMS MetaData", command=parse_hms)
c2.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(gui, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# FIA gui objects
fia_label = Label(gui, text="HEC-FIA", font=('Helveticabold', 15))
fia_label.grid(row=row, column=0, sticky="we")
row += 1

fia_prj_select = FileSelect(gui, "FIA project file (*.prj): ")
fia_prj_select.grid(row=row)
row += 1

fia_shp_select = FileSelect(gui, "FIA boundary Polygon shape file (*.shp): ")
fia_shp_select.grid(row=row)
row += 1

c3 = ttk.Button(gui, text="Extract FIA MetaData", command=parse_fia)
c3.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(gui, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# Go-Consequences gui objects
cons_label = Label(gui, text="Go-Consequences", font=('Helveticabold', 15))
cons_label.grid(row=row, column=0, sticky="we")
row += 1

cons_run_type_radio1_row = row
cons_run_type_radio1 = Radiobutton(gui, text="Run Type: Single", value=0, variable="run_type", command=cons_single_run_type_selected)
cons_run_type_radio1.grid(row=row, sticky=W, ipadx=300)
row += 1

cons_run_type_radio2_row = row
cons_run_type_radio2 = Radiobutton(gui, text="Run Type: Multiple", value=1, variable="run_type", command=cons_multi_run_type_selected)
cons_run_type_radio2.grid(row=row, sticky=W, ipadx=300)
row += 1

cons_run_type_radio1.select()

cons_prj_select = FileSelect(gui, "Go-Consequences Run file (*.go): ")
cons_prj_select.grid(row=row)
row += 1

cons_data_dir_select = FolderSelect(gui, "Go-Consequences Input Data Directory: ")
cons_data_dir_select.grid(row=row)
row += 1

cons_results_dir_select = FolderSelect(gui, "Go-Consequences Model Results Directory: ")
cons_results_dir_select.grid(row=row)
row += 1

cons_hazard_select = FileSelect(gui, "Optional. Specified WSE Hazard Layer (*.tif): ")
cons_hazard_select.grid(row=row)
row += 1

cons_inv_select = FileSelect(gui, "Optional. Specified Structure Inventory (*.shp): ")
cons_inv_select.grid(row=row)
row += 1

cons_res_select = FileSelect(gui, "Optional. Specified Results Layer (*.gpkg): ")
cons_res_select.grid(row=row)
row += 1

cons_runtable_select = FileSelect(gui, "Multiple Run Table Data (*.csv): ")
cons_runtable_select.grid(row=row)
row += 1

cons_runtable_select.entPath.config(state="disabled")
cons_runtable_select.lblName.config(state="disabled")
cons_runtable_select.btnFind.config(state="disabled")

c4 = ttk.Button(gui, text="Extract Consequences MetaData", command=parse_consequences)
c4.grid(row=row, column=0)
row += 1

# Separator object
separator = ttk.Separator(gui, orient='horizontal')
separator.grid(row=row, ipady=10)
row += 1

# Metadata website link
link = Label(gui, text="Upload Output to: The Water Institute Model Repository",font=('Helveticabold', 15), fg="blue", cursor="hand2")
link.grid(row=row, pady=10)
row += 1
link.bind("<Button-1>", lambda e: callback("https://metadata-creation-tool.herokuapp.com/signup"))

# Metadata website link
link = Label(gui, text="Questions/Comments: Github",font=('Helveticabold', 10), fg="blue", cursor="hand2", anchor=SW)
link.grid(row=row)
row += 1
link.bind("<Button-1>", lambda e: callback("https://github.com/waterinstitute/hec_meta_extract/issues"))

# run app
gui.mainloop()
