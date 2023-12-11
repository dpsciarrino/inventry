import tkinter as tk
from tkinter import ttk
from tkinter import TclError

class AppletMainWindow(tk.Toplevel):
    def __init__(self, applet, application):
        # GLOBAL CLASS VARIABLES
        self._applet = applet
        self._application = application

        # INITIATE TK WINDOW
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().title("Inventry - BOM Viewer")
        self.winfo_toplevel().geometry("1100x580+20+20")
        self.resizable(False, False)
        self.iconbitmap(application.config['icon_path'])

        # INIT MENU
        menubar = AppletMenu(self)

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

        # BOM ID labels
        idLabel = ttk.Label(self, text="ID: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')
        self.idEntry = ttk.Entry(self, width=7, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.idEntry.state(['readonly'])

        # BOM Selection Components
        bomLabel = ttk.Label(self, text="BOM: ", font=('Sans', '8', 'bold'), foreground=application._inventoryStyleBackground, background=application.frameBackground, justify='center')
        self.bomCombo = ttk.Combobox(self, width=50, values = self._parent.applet.model.availableBOMs)
        self.bomCombo.bind('<<ComboboxSelected>>', self.bomSelectionCallback)
        self.bomCombo.state(['readonly'])

        # BUTTONS
        self.addPartBtn = ttk.Button(self, text="Add Part", padding=3, command = lambda : AddPartWindow(self, parent, application))
        self.addPartBtn.state(['disabled'])

        self.removePartBtn = ttk.Button(self, text="Remove Part", padding=3, command = lambda : self.removePart())
        self.removePartBtn.state(['disabled'])

        self.editBomBtn = ttk.Button(self, text="Edit BOM", padding=3, command = lambda : self.editBOMMode())
        self.editBomBtn.state(['disabled'])

        self.cancelEditsBtn = ttk.Button(self, text="Cancel Edits", padding=3, command = lambda : self.cancelEdits())
        self.cancelEditsBtn.state(['disabled'])

        closeButton = ttk.Button(self, text="Close", padding=3, command = lambda : parent.kill())

        # TREE VIEW
        self._tree = ttk.Treeview(self, columns=['column_partID', 'column_mfr', \
			'column_mfrNum', 'column_qty', 'column_price'], \
			height =22)
        self._tree.heading('#0', text='Item #')
        self._tree.heading('column_partID', text='Part ID')
        self._tree.heading('column_mfr', text='Manufacturer')
        self._tree.heading('column_mfrNum', text='MPN')
        self._tree.heading('column_qty', text='Qty')
        self._tree.heading('column_price', text='Unit Price')

        self._tree.column('#0', width=75, anchor='center')
        self._tree.column('column_partID', width=100, anchor='center')
        self._tree.column('column_qty', width=75, anchor='center')
        self._tree.column('column_price', width=75, anchor='center')

        self._tree.bind("<Double-1>", self.onDoubleClick)

        # BOM Cost Components
        self.totalCostLabel = ttk.Label(self, text="Total Cost:", font = ('Sans', '8', 'bold'), foreground=application._inventoryStyleBackground, background = application.frameBackground, justify='center')
        self.buildQuantityLabel = ttk.Label(self, text="Build Qty:", font = ('Sans', '8', 'bold'), foreground=application._inventoryStyleBackground, background = application.frameBackground, justify='center')

        self.buildQuantityEntry = ttk.Entry(self, width=7, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.buildQuantityEntry.config(state = 'normal')
        self.buildQuantityEntry.insert(0, "1")

        self.buildCostCalculateButton = ttk.Button(self, text="Calculate", padding=1, command = lambda : self.update_build_cost())
        self.buildCostCalculateButton.state(['disabled'])

        # COMPONENT PLACEMENT
        idLabel.place(x=10, y=25, anchor='nw')
        self.idEntry.place(x=100, y=25, anchor='nw')

        bomLabel.place(x=10, y=55, anchor='nw')
        self.bomCombo.place(x=100, y=55, anchor='nw')

        self.addPartBtn.place(x=600, y=25, anchor='nw')
        self.removePartBtn.place(x=700, y=25, anchor='nw')
        self.cancelEditsBtn.place(x=800, y=25, anchor='nw')
        self.editBomBtn.place(x=900, y=25, anchor='nw')
        closeButton.place(x=1000, y=25, anchor='nw')

        self._tree.place(x=10, y=85, anchor='nw')

        self.totalCostLabel.place(x=210, y=556, anchor='nw')
        
        self.buildQuantityLabel.place(x=10, y=556, anchor='nw')
        self.buildQuantityEntry.place(x=70, y=555, anchor='nw')
        self.buildCostCalculateButton.place(x=125, y=553, anchor='nw')
    
    @property
    def application(self):
        return self._application
    
    @property
    def tree(self):
        return self._tree
    
    @property
    def itemCount(self):
        return len(self._tree.get_children())
    
    def update_build_cost(self):
        if not self.buildQuantityEntry.get().isnumeric():
            raise TypeError("Enter only numeric values for build quantity.")
        
        quantity_to_build = int(self.buildQuantityEntry.get())
        total_build_cost = self._parent.applet.model.get_build_cost(bom_name = self.bomCombo.get(), quantity=quantity_to_build)

        self.totalCostLabel['text'] = f"Total Cost: ${float(total_build_cost):.2f}"
        
        return False
    
    def onDoubleClick(self, event = None):
        # Should only be able to increment in Edit BOM mode
        # BOM Combo box is disabled in View BOM Mode
        # Using this to determine binding functionality.
        if self.bomCombo.state()[0] == 'readonly':
            return 0
        
        # Get currently selected treeview item ID
        item = self.tree.selection()[0]

        # Get field values of item
        # We only care about the part ID
        partID, mfr, mfrNum, quantity, price = self.tree.item(item, "values")
        part_id_processed = self._parent.applet.model.processData(partID)

        _id, manufacturer, manufacturerPartNum, price = self._parent.applet.model.getPartData(part_id_processed)

        price = f"${float(price):.2f}"

        try:
            self.tree.insert('', "end", text=str(self.itemCount + 1), iid=partID, values=[partID, manufacturer, manufacturerPartNum, quantity, price])
        except TclError as tclErr:
            if f"Item {partID} already exists" in str(tclErr):
                itemValues = list(self.tree.item(partID, "values"))
                bomQty = int(itemValues[3]) # GEt the current quantity of part from the BOM list
                bomQty += 1
                itemValues[3] = str(bomQty)
                self.tree.item(partID, values = itemValues)
        
    
    def bomSelectionCallback(self, event=None):
        # Clear the tree
        self.tree.delete(*self.tree.get_children())

        # Obtain the BOM name and process it for SQL query
        selection = self.bomCombo.get()
        selection_processed = self._parent.applet.model.processData(selection)

        # Obtain BOM id from name
        bom_id = self._parent.applet.model.get_bom_id_from_name(selection_processed)

        # Obtain parts list from BOM name
        bom_parts_list = self._parent.applet.model.get_bom_parts_by_name(selection_processed)

        i = 1
        for part in bom_parts_list:
            part_id = part[0]
            manufacturer = part[1]
            mpn = part[2]
            qty = part[4]
            tiered_pricing = self._parent.applet.model.get_tiered_pricing_for_part(part_id)
            price = self._parent.applet.model.calculate_unit_cost_from_tiered_pricing(tiered_pricing, qty)
            price = f"${float(price):.2f}"  # Round price to nearest cents, add currency symbol

            try:
                self.tree.insert('', 'end', text=str(i), iid=part_id, values=[part_id, manufacturer, mpn, qty, price])
            except TclError as tclerr:
                print(tclerr)

            i += 1
        
        self.idEntry.config(state="normal")
        self.idEntry.delete(0, 'end')
        self.idEntry.insert(0, str(bom_id))
        self.idEntry.config(state = "readonly")

        self.editBomBtn.config(state = "normal")
        self.buildCostCalculateButton.config(state="normal")

        self.update_build_cost()


    def removePart(self):
        selection = self.tree.selection()
        if len(selection) > 0:
            self.tree.delete(self.tree.selection()[0])

    def editBOMMode(self):
        self.addPartBtn.config(state = "normal")
        self.removePartBtn.config(state = "normal")
        self.cancelEditsBtn.config(state = "normal")

        self.bomCombo.config(state = "disabled")

        self.buildCostCalculateButton.config(state = "disabled")

        self.editBomBtn['text'] = "Save Edits"
        self.editBomBtn['command'] = lambda : self.saveEdits()


    def cancelEdits(self):
        # Call original data into the BOM tree
        self.bomSelectionCallback()

        # Set the BOM Selection to read-only
        self.bomCombo.config(state = "readonly")

        # Disable relevant buttons for View BOM Mode
        self.addPartBtn.config(state = "disabled")
        self.removePartBtn.config(state = "disabled")
        self.cancelEditsBtn.config(state = "disabled")

        # Enable BOM Quantity calculation
        self.buildCostCalculateButton.config(state = "normal")

        # Change the state of the Edit BOM button
        self.editBomBtn['text'] = "Edit BOM"
        self.editBomBtn['command'] = lambda : self.editBOMMode()


    def saveEdits(self):
        # Collect the items in the BOM tree
        tree_items = list(self.tree.get_children())

        number_of_bom_items = len(tree_items)

        if number_of_bom_items == 0:
            raise Exception("You need at least 1 part to edit a BOM.")
        
        max_item_number = sorted(list(map(int, tree_items)))[-1]

        part_id = ""
        qty = ""
        part_dict = {}
        bom_items_dict = {}
        for item in tree_items:
            # Get BOM number as string from BOM list
            item_number = self.tree.item(item, "text")

            # Extract relevant values from BOM
            values = list(self.tree.item(item, "values"))
            part_id = values[0]
            qty = values[3]

            # Construct part dictionary for BOM item line
            part_dict['part_id'] = part_id
            part_dict['quantity'] = str(qty)

            # Add BOM items to dictionary
            bom_items_dict[item_number] = part_dict

            # Reset variables
            part_dict = {}
            part_id = ""
            qty = ""
        
        # Grab ID and BOM name
        bom_id = self.idEntry.get()
        bom_name_processed = self._parent.applet.model.processData(self.bomCombo.get())

        # Remove all the parts associated with the current BOM
        self._parent.applet.model.delete_bom_parts(bom_id)

        # Insert the new BOM list/quantities into the database
        self._parent.applet.model.insertPartsIntoBom(max_item_number, str(bom_id), bom_items_dict)

        # Reset the BOM to verify save occurred
        self.bomSelectionCallback()

        # Revert buttons to View BOM state
        self.addPartBtn.config(state = "disabled")
        self.removePartBtn.config(state = "disabled")
        self.cancelEditsBtn.config(state = "disabled")
        self.editBomBtn['text'] = "Edit BOM"
        self.editBomBtn['command'] = lambda : self.editBOMMode()

        # Enable BOM Quantity calculation
        self.buildCostCalculateButton.config(state = "normal")

        self.bomCombo['state'] = 'readonly'


class AddPartWindow(tk.Toplevel):
    def __init__(self, frame, view, application):
        # GLOBAL CLASS VARIABLES
        self._view = view
        self._bomFrame = frame
        self._application = application

        # INITIATE TK WINDOW
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().title("Add Part")
        self.winfo_toplevel().geometry("1000x400+50+100")
        self.iconbitmap(application.config['icon_path'])

        # INIT APPLET FRAME
        self._appletFrame = AddPartFrame(self, application)
        self.columnconfigure(0, minsize=100, weight=1)
        self.rowconfigure(0, minsize=100, weight=1)
        self._appletFrame.grid(row=0, column=0, columnspan=1, rowspan=1, sticky='NEWS')

        self.resizable(0,0)

        self.after(500, lambda : self.focus_force())
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

        _id, manufacturer, manufacturerPartNum, price = self._parent.view.applet.model.getPartData(part_id_processed)

        price = f"${float(price):.2f}"

        quantity = 1
        try:
            self._parent.bomFrame.tree.insert('', "end", text=str(self._parent.bomFrame.itemCount + 1), iid=part_id, values=[part_id, manufacturer, manufacturerPartNum, quantity, price])
        except TclError as tclErr:
            if f"Item {part_id} already exists" in str(tclErr):
                itemValues = list(self._parent.bomFrame.tree.item(part_id, "values"))
                bomQty = int(itemValues[3]) # Get the current quantity of part from the BOM list
                bomQty += 1
                itemValues[3] = str(bomQty)
                self._parent.bomFrame.tree.item(part_id, values = itemValues)

    