import tkinter as tk
from tkinter import ttk
import os.path
from tkinter import TclError
from datetime import datetime
import json

class AppletMainWindow(tk.Toplevel):
    def __init__(self, applet, application):
        # GLOBAL CLASS VARIABLES
        self._applet = applet
        self._application = application

        # INITIATE TK WINDOW
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().title("Inventry BOM Builder")
        self.winfo_toplevel().geometry("1000x575+20+20")
        self.iconbitmap(application.config['icon_path'])

        # INIT MENU
        menubar = AppletMenu(self)

        # INIT APPLET FRAME
        self._appletFrame = AppletFrame(self, application)

        self.columnconfigure(0, minsize=100, weight=1)
        self.rowconfigure(0, minsize=100, weight=1)
        self._appletFrame.grid(row=0, column=0, columnspan=1, rowspan=1, sticky="NEWS")

        self.resizable(0,0)

        # TAKE FOCUS AND START APPLET WINDOW
        self.after(500, lambda: self.focus_force())
        self.grab_set()
    
    def kill(self):
        self.winfo_toplevel().destroy()
    
    @property
    def applet(self):
        return self._applet

    @property
    def application(self):
        return self._application



class AppletMenu(tk.Menu):
    def __init__(self, parent):
        self._menubar = tk.Menu(parent)
        parent.config(menu=self._menubar)

        self._fileMenu = tk.Menu(self._menubar, tearoff=0)
        self._fileMenu.add_command(label="Close", command = parent.kill)

        self._menubar.add_cascade(label="File", menu = self._fileMenu)

class AppletFrame(tk.Frame):
    def __init__(self, parent, application):
        self._parent = parent
        self._application = application
        self.storedEntry = ""
        tk.Frame.__init__(self, parent, width="500", bg=application.frameBackground)

        ############################################################
		#					      LABELS						   #
		############################################################
        idLabel = ttk.Label(self, text="ID: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')
        nameLabel = ttk.Label(self, text="BOM Name: ", font = ('Sans', '8','bold'), foreground = application._inventoryStyleBackground, background=application.frameBackground, justify='right')

        self.idEntry = ttk.Entry(self, width=7, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        nextAvailableID = str(parent.applet.model.nextAvailableID())
        self.idEntry.insert(0, nextAvailableID)
        self.idEntry.state(['disabled'])

        self.nameEntry = ttk.Entry(self, width=50, text="", font=('Sans', '8', 'bold'), background= '#FFFFFF', foreground='#000000', justify='left')
        self.nameEntry.insert(0, f"BOM #{nextAvailableID}")

        ############################################################
		#					      BUTTONS						   #
		############################################################
        self.addPartBtn = ttk.Button(self, text="Add Part", padding=3, command=lambda: AddPartWindow(self, parent, application))
        self.removePartBtn = ttk.Button(self, text="Remove Part", padding=3, command = lambda : self.removePart())
        self.createBtn = ttk.Button(self, text="Create BOM", padding=3, command = lambda : self.createBOM())
        closeButton = ttk.Button(self, text="Close", padding=3, command = lambda : parent.kill())

        ############################################################
		#					      TREEVIEW						   #
		############################################################

        self._tree = ttk.Treeview(self, columns=['column_partID', 'column_mfr', \
                                                 'column_mfrNum', 'column_qty'], height=22)
        self._tree.heading('#0', text='Item #')
        self._tree.heading('column_partID', text='Part ID')
        self._tree.heading('column_mfr', text='Manufacturer')
        self._tree.heading('column_mfrNum', text='MPN')
        self._tree.heading('column_qty', text='Qty')

        self._tree.column('#0', width=75, anchor='center')
        self._tree.column('column_partID', width=100, anchor='center')
        self._tree.column('column_qty', width=75, anchor='center')

        # PLACE COMPONENTS
        idLabel.place(x=10, y=25, anchor='nw')
        self.idEntry.place(x=100, y=25, anchor='nw')

        nameLabel.place(x=10, y=55, anchor='nw')
        self.nameEntry.place(x=100, y=55, anchor='nw')

        self._tree.place(x=10, y=85, anchor='nw')
        
        self.addPartBtn.place(x=600, y=25, anchor='nw')
        self.removePartBtn.place(x=700, y=25, anchor='nw')
        self.createBtn.place(x=800, y=25, anchor='nw')
        closeButton.place(x=900, y=25, anchor='nw')

    @property
    def tree(self):
        return self._tree

    @property
    def itemCount(self):
        return len(self._tree.get_children())

    @property
    def application(self):
        return self._application
    
    def removePart(self):
        selection = self._tree.selection()
        if len(selection) > 0:
            self._tree.delete(self._tree.selection()[0])
    
    def createBOM(self):
        treeItems = list(self.tree.get_children())

        number_of_bom_items = len(treeItems)

        if number_of_bom_items == 0:
            raise Exception("You need at least 1 part to build a BOM.")
        
        max_item_number = sorted(list(map(int, treeItems)))[-1]

        part_id = ""
        qty = ""
        part_dict = {}
        bom_items_dict = {}
        for item in treeItems:
            # Get BOM number as string from BOM list
            item_number = self.tree.item(item, "text")

            # Extract relevant values from BOM
            values = list(self.tree.item(item, "values"))
            part_id = values[0]
            qty = values[3]

            # Construct part dictionary for BOM item line                
            part_dict["part_id"] = part_id
            part_dict["quantity"] = str(qty)

            # Add BOM items to dictionary
            bom_items_dict[item_number] = part_dict

            # Reset variables
            part_dict = {}
            part_id = ""
            qty = ""
        
        # Grab ID and BOM name
        bom_id = self.idEntry.get()
        bom_name_processed = self._parent.applet.model.processData(self.nameEntry.get())

        # Insert into database
        self._parent.applet.model.insertBOM(bom_id, bom_name_processed)

        # Insert parts into BOM
        self._parent.applet.model.insertPartsIntoBom(max_item_number, str(bom_id), bom_items_dict)

        # Reset the BOM fields and clear the tree
        self.resetForm()

    def resetForm(self):
        # Clear the tree
        self.tree.delete(*self.tree.get_children())

        # Set the next available ID field
        nextAvailableID = str(self._parent.applet.model.nextAvailableID())
        self.idEntry.config(state='enabled')
        self.idEntry.delete(0, 'end')
        self.idEntry.insert(0, nextAvailableID)
        self.idEntry.state(['readonly'])
        
        # Clear the name entry
        self.nameEntry.delete(0, 'end')
        self.nameEntry.insert(0, "BOM #" + str(nextAvailableID))

        
        
        







############################################################
#					      ADD PART WINDOW				   #
############################################################

class AddPartWindow(tk.Toplevel):
    def __init__(self, frame, view, application):
        # GLOBAL CLASS VARIABLES
        self._view = view
        self._bomFrame = frame
        self._application = application

        # INITIATE TK WINDOW
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().title('Add Part to BOM')
        self.winfo_toplevel().geometry("1000x400+50+100")
        self.iconbitmap(application.config['icon_path'])

        # INIT APPLET FRAME
        self._appletFrame = AddPartFrame(self, application)
        self.columnconfigure(0, minsize=100, weight=1)
        self.rowconfigure(0, minsize=100, weight=1)
        self._appletFrame.grid(row=0, column=0, columnspan=1, rowspan=1, sticky='NEWS')

        self.resizable(0,0)

        # TAKE FOCUS AND START APPLET WINDOW
        self.after(500, lambda: self.focus_force())
        self.grab_set()

    @property
    def view(self):
        return self._view

    @property
    def bomFrame(self):
        return self._bomFrame
    
    def kill(self):
        self.winfo_toplevel().destroy()

class AddPartFrame(tk.Frame):
    def __init__(self, parent, application):
        self._parent = parent
        tk.Frame.__init__(self, parent, width="500", bg=application.frameBackground)

        # Instantiate AddPartFrame Components
        searchByLabel = ttk.Label(self, text="Search By: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        searchBoxLabel = ttk.Label(self, text="Search Term: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self.searchByDropdown = ttk.Combobox(self, width=20, values = ["Part ID", "Manufacturer", "MPN"])
        self.searchByDropdown.insert(0, "Part ID")
        self.searchEntryBox = ttk.Entry(self, width=25, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.searchButton = ttk.Button(self, text="Search", padding=3, command = lambda : self.search(self))

        # Results Tree Creation and Heading Definitions
        self._resultsTree = ttk.Treeview(self, columns=['column_partID', 'column_mfr', 'column_mpn'], height=15)
        self._resultsTree.heading('#0', text='Result #')
        self._resultsTree.heading('column_partID', text='Part ID')
        self._resultsTree.heading('column_mfr', text='Manufacturer')
        self._resultsTree.heading('column_mpn', text='MPN')

        # Results Tree Column Sizing
        self._resultsTree.column('#0', width=75)
        self._resultsTree.column('column_partID', width=100)

        # Bindings
        self._resultsTree.bind("<Double-1>", self.onDoubleClick)

        # Place Components
        searchByLabel.place(x=10, y=25, anchor='nw')
        self.searchByDropdown.place(x=85, y=25, anchor='nw')
        searchBoxLabel.place(x=240, y=25, anchor='nw')
        self.searchEntryBox.place(x=320, y=25, anchor='nw')
        self.searchButton.place(x=500, y=20, anchor='nw')
        self._resultsTree.place(x=10, y=55, anchor='nw')

    @property
    def resultsTree(self):
        return self._resultsTree

    def search(self, frame):
        frame.resultsTree.delete(*frame.resultsTree.get_children())
        searchTerm = self.searchEntryBox.get()
        searchColumn = self.searchByDropdown.get()
        column = ""
        if searchColumn == "Part ID":
            column = "part_id"
        elif searchColumn == "Manufacturer":
            column = "manufacturer"
        elif searchColumn == "MPN":
            column = "mpn"
        else:
            column = ""
        
        itemNumber = 0
        if column != "":
            data = self._parent.view.applet.model.searchInventory(column, searchTerm)

            if len(data) != 0:
                itemNumber = 0
                for line in data:
                    partID = str(line[0]).replace("\\", "")
                    mfr = str(line[1]).replace("\\", "")
                    mfrNum = str(line[2]).replace("\\", "")
                    frame.resultsTree.insert('', "end", text = str(itemNumber+1), iid=itemNumber, values = [partID, mfr, mfrNum])
                    itemNumber += 1

    def onDoubleClick(self, event = None):
        # Get selected TreeView Item ID
        item = self.resultsTree.selection()[0]

        # Get the field values of the item (we only care about the part ID in this case)
        part_id, mfr, mpn = self.resultsTree.item(item, "values")
        part_id_processed = self._parent.view.applet.model.processData(part_id)

        _id, manufacturer, manufacturerPartNum = self._parent.view.applet.model.getPartData(part_id_processed)

        quantity = 1
        try:
            self._parent.bomFrame.tree.insert('', "end", text=str(self._parent.bomFrame.itemCount + 1), iid=part_id, values=[part_id, manufacturer, manufacturerPartNum, quantity])
        except TclError as tclErr:
            if f"Item {part_id} already exists" in str(tclErr):
                itemValues = list(self._parent.bomFrame.tree.item(part_id, "values"))
                bomQty = int(itemValues[3]) # Get the current quantity of part from the BOM list
                bomQty += 1
                itemValues[3] = str(bomQty)
                self._parent.bomFrame.tree.item(part_id, values = itemValues)