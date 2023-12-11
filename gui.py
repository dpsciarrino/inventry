import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

###############################################################################################################
###############################################################################################################

# Main Application tk Window

###############################################################################################################
###############################################################################################################

class ApplicationWindow(tk.Tk):
    def __init__(self, application):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Inventry")
        self.iconbitmap(application.config['icon_path'])

        menubar = ApplicationMenu(self)

        self._frame = None
        # self.switch_frame(HomeFrame)
        self._appletFrame = AppletFrame(self, application)

        img = ImageTk.PhotoImage(Image.open("img/inventry.jpg").resize((240,240)))

        image_label = ttk.Label(self, image=img)
        image_label.place(x=0, y=0, anchor='nw')

        self.columnconfigure(0, minsize=50, weight=1)
        self.columnconfigure(1, minsize=200, weight=2)
        self.rowconfigure(0, minsize=250, weight=1)
        self._appletFrame.grid(row=0, column=0, columnspan=2, rowspan=1, sticky="NEWS")
		
        self.winfo_toplevel().geometry("460x250+50+10")
        self.resizable(0,0)

        self.mainloop()
    
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
    
    def kill(self):
        self.winfo_toplevel().destroy()
    
###############################################################################################################
###############################################################################################################

#   Main Application Window

#   Main Menu Bar

###############################################################################################################
###############################################################################################################

class ApplicationMenu(tk.Menu):
    def __init__(self, parent):
        self._menubar = tk.Menu(parent)
        parent.config(menu=self._menubar)

        self._fileMenu = tk.Menu(self._menubar, tearoff=0)
        self._fileMenu.add_command(label="Close", command=parent.kill)

        self._menubar.add_cascade(label="File", menu = self._fileMenu)


###############################################################################################################
###############################################################################################################

# Home Frame

###############################################################################################################
###############################################################################################################

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg='white', width="750")
        self.winfo_toplevel().geometry("550x500")

        self.place(relx=0.5, rely=0.5, anchor='center')

###############################################################################################################
###############################################################################################################

# Applet Frame

###############################################################################################################
###############################################################################################################

class AppletFrame(tk.Frame):
    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent, width="180", bg=app.frameBackground)
        self.winfo_toplevel().geometry("170x500")

        # Part Management Components
        partMgmtLabel = ttk.Label(text="PART MANAGEMENT", anchor="center", background=app.frameBackground)
        partEntryBtn = ttk.Button(text="Part Entry", command = lambda : app.partentry)
        partViewerBtn = ttk.Button(text="Part Viewer", command = lambda: app.partviewer)
        partMgmtLabel.place(x=250, y=8, width=200, anchor='nw')
        partEntryBtn.place(x=250, y=30, width=200, height=40, anchor='nw')
        partViewerBtn.place(x=250, y=75, width=200, height=40, anchor='nw')

        # BOM Management Components
        bomMgmtLabel = ttk.Label(text="BOM MANAGEMENT", anchor="center", background=app.frameBackground)
        bomBuilderBtn = ttk.Button(text="BOM Builder", command = lambda: app.bombuilder)
        bomViewerBtn = ttk.Button(text="BOM Viewer", command = lambda : app.bomviewer)
        bomMgmtLabel.place(x=250, y=125, width=200, anchor='nw')
        bomBuilderBtn.place(x=250, y=147, width=200, height=40, anchor='nw')
        bomViewerBtn.place(x=250, y=190, width=200, height=40, anchor='nw')