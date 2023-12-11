import tkinter as tk
from tkinter import ttk

class AppletMainWindow(tk.Toplevel):
    def __init__(self, applet, application):
        # GLOBAL CLASS VARIABLES
        self._applet = applet

        # INITIATE WINDOW
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().title("Inventry - Part Entry")
        self.winfo_toplevel().geometry("450x200+25+25")
        self.iconbitmap(application.config['icon_path'])

        # INITIALIZE MENU
        menubar = AppletMenu(self)

        self._appletFrame = AppletFrame(self, application)
        self.columnconfigure(0, minsize=100, weight=1)
        self.rowconfigure(0, minsize=100, weight=1)
        self._appletFrame.grid(row=0, column=0, columnspan=1, rowspan = 1, sticky="NEWS")

        self.resizable(0,0)

        self.after(500, lambda: self.focus_force())
        self.grab_set()
    
    def kill(self):
        self.winfo_toplevel().destroy()
    
    @property
    def applet(self):
        return self._applet
    
class AppletMenu(tk.Menu):
    def __init__(self, parent):
        self._menubar = tk.Menu(parent)
        parent.config(menu = self._menubar)

        self._fileMenu = tk.Menu(self._menubar, tearoff=0)
        self._fileMenu.add_command(label = "Close", command = parent.kill)

        self._menubar.add_cascade(label="File", menu = self._fileMenu)

class AppletFrame(tk.Frame):
    def __init__(self, parent, application):
        self._parent = parent
        tk.Frame.__init__(self, parent, width = "500", bg = application.frameBackground)

        ############################################################
        #						PART INFO						   #
        ############################################################

        # BASIC PART INFO LABELS
        idLabel = ttk.Label(self, text = "Part ID:", font=('Sans', '8', 'bold'), foreground= application._inventoryStyleBackground, background=application.frameBackground, justify='center')
        manufacturerLabel = ttk.Label(self, text="Manufacturer: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')
        mpnLabel = ttk.Label(self, text="MPN: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')

        # Choose the Part ID to be the next avaialable unique part ID
        next_part_id = self._parent.applet.model.nextAvailablePartID()
        self.idEntry = ttk.Entry(self, width=7, font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.idEntry.insert(0, str(next_part_id))
        self.idEntry.config(state = 'readonly')

        self.manufacturerEntry = ttk.Entry(self, width=50, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.manufacturerEntry.config(state = 'enabled')

        self.mpnEntry = ttk.Entry(self, width=50, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.mpnEntry.config(state = 'enabled')

        ############################################################
        #						PRICING/COST INFO			       #
        ############################################################
        unitPriceLabel = ttk.Label(self, text="Unit Price: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')
        self.unitPriceEntry = ttk.Entry(self, width=12, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.unitPriceEntry.config(state = 'enabled')
        self.uomForUnitPriceLabel = ttk.Label(self, text="EA", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')

        ############################################################
        #						BUTTONS INFO	    		       #
        ############################################################
        self.addPartButton = ttk.Button(self, text="Add Part", padding=3, command = lambda : self.add_part())
        closeButton = ttk.Button(self, text="Close", padding=3, command = lambda : parent.kill())

        ############################################################
        #						PLACEMENT       			       #
        ############################################################
        
        idLabel.place(x=10, y=25, anchor='nw')
        manufacturerLabel.place(x=10, y=55, anchor='nw')
        mpnLabel.place(x=10, y=85, anchor='nw')

        self.idEntry.place(x=120, y=25, anchor='nw')
        self.manufacturerEntry.place(x=120, y=55, anchor='nw')
        self.mpnEntry.place(x=120, y=85, anchor='nw')

        unitPriceLabel.place(x=10, y=115, anchor='nw')
        self.unitPriceEntry.place(x=120, y=115, anchor='nw')
        self.uomForUnitPriceLabel.place(x=200, y=115, anchor='nw')

        self.addPartButton.place(x=75, y=150, anchor='nw')
        closeButton.place(x=275, y=150, anchor='nw')

    def add_part(self):
        # Get the new part ID
        part_id = self.idEntry.get()

        # Get the new part field values
        manufacturer = self.manufacturerEntry.get()
        mpn = self.mpnEntry.get()
        price = self.unitPriceEntry.get()

        # Process the field values for the database
        _manufacturer = self._parent.applet.model.processData(manufacturer)
        _mpn = self._parent.applet.model.processData(mpn)
        _price = price

        # Insert the new part into the database
        self._parent.applet.model.insertPart(part_id, _manufacturer, _mpn, _price)

        # Reset/Clear the form fields
        self.resetForm()
    
    def resetForm(self):
        # Set the next available ID field
        nextAvailableID = str(self._parent.applet.model.nextAvailablePartID())
        self.idEntry.config(state='enabled')
        self.idEntry.delete(0, 'end')
        self.idEntry.insert(0, nextAvailableID)
        self.idEntry.state(['readonly'])

        # Clear the relevant entries
        self.manufacturerEntry.delete(0, 'end')
        self.mpnEntry.delete(0, 'end')
        self.unitPriceEntry.delete(0, 'end')
        
        


