from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import hms_parser
import ras_parser
import os
import webbrowser

gui = Tk()
gui.geometry("400x400")
gui.title("The Water Institute: LWI Metadata Extraction")

#Define a callback function
def callback(url):
   webbrowser.open_new_tab(url)

class FileSelect(Frame):
    def __init__(self, parent=None, fileDescription="", **kw):
        Frame.__init__(self, master=parent, **kw)
        self.filePath = StringVar()
        self.lblName = Label(self, text=fileDescription)
        self.lblName.grid(row=0, column=0)
        self.entPath = Entry(self, textvariable=self.filePath)
        self.entPath.grid(row=0, column=1)
        self.btnFind = ttk.Button(
            self, text="Browse...", command=self.setFilePath)
        self.btnFind.grid(row=0, column=2)

    def setFilePath(self):
        file_selected = filedialog.askopenfilename(
            # filetypes=[("Excel files", ".xlsx .xls")]
            filetypes=[("File Types", ".dss .hms .prj .shp .geojson .json")])
        self.filePath.set(file_selected)

    @property
    def file_path(self):
        return self.filePath.get()


class FolderSelect(Frame):
    def __init__(self, parent=None, folderDescription="", **kw):
        Frame.__init__(self, master=parent, **kw)
        self.folderPath = StringVar()
        self.lblName = Label(self, text=folderDescription)
        self.lblName.grid(row=0, column=0)
        self.entPath = Entry(self, textvariable=self.folderPath)
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
    ras_parser.parse(ras_prj, ras_shp)
    output_dir = os.path.join(os.getcwd(), 'output', 'ras')
    print(f"\nRAS Parsing Complete. Output files located at: {output_dir}")


def parse_hms():
    hms_prj = hms_prj_select.file_path
    hms_shp = hms_shp_select.file_path
    hms_dss = hms_dss_select.folder_path
    print("\nParsing HMS..")
    hms_parser.parse(hms_prj, hms_shp, hms_dss)
    print(f"RAS Parsing Complete. Output files located at: {output_dir}")
    

filePath = StringVar()

# RAS gui objects

ras_prj_select = FileSelect(gui, "RAS project file (.prj)")
ras_prj_select.grid(row=0, ipady=10)

ras_shp_select = FileSelect(gui, "RAS boundary shape file (*.shp) ")
ras_shp_select.grid(row=1)


c = ttk.Button(gui, text="Extract RAS MetaData", command=parse_ras)
c.grid(row=4, column=0)

# Separator object
separator = ttk.Separator(gui, orient='horizontal')
separator.grid(row=5, ipady=10)

# HMS gui objects

hms_prj_select = FileSelect(gui, "HMS project file (.prj)")
hms_prj_select.grid(row=6)

hms_shp_select = FileSelect(gui, "HMS boundary shape file (*.shp) ")
hms_shp_select.grid(row=7)

hms_dss_select = FolderSelect(gui, "Optional. DSS Data Directory.")
hms_dss_select.grid(row=8)

c2 = ttk.Button(gui, text="Extract HMS MetaData", command=parse_hms)
c2.grid(row=9, column=0)

# Separator object
separator = ttk.Separator(gui, orient='horizontal')
separator.grid(row=10, ipady=10)

# Metadata website link
link = Label(gui, text="The Water Institute Model Repository",font=('Helveticabold', 15), fg="blue", cursor="hand2")
link.grid(row=11)
link.bind("<Button-1>", lambda e: callback("https://metadata-creation-tool.herokuapp.com/signup"))

# run app
gui.mainloop()
