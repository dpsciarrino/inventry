import tkinter as tk
from tkinter import ttk
from decimal import *

class AppletMainWindow(tk.Toplevel):
    def __init__(self, applet, application):
        # GLOBAL CLASS VARIABLES
        self._applet = applet
		
        # INITIATE WINDOW
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().title("Inventry - Part Viewer")
        self.winfo_toplevel().geometry("450x300+25+25")
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
        self._application = application
        tk.Frame.__init__(self, parent, width = "500", bg = application.frameBackground)

        ############################################################
        #						PART INFO						   #
        ############################################################

        # BASIC PART INFO LABELS
        idLabel = ttk.Label(self, text = "Part ID:", font=('Sans', '8', 'bold'), foreground= application._inventoryStyleBackground, background=application.frameBackground, justify='center')
        manufacturerLabel = ttk.Label(self, text="Manufacturer: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')
        mpnLabel = ttk.Label(self, text="MPN: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')

        self.idEntry = ttk.Entry(self, width=7, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.idEntry.state(['disabled'])

        self.manufacturerEntry = ttk.Entry(self, width=50, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.manufacturerEntry.state(['disabled'])

        self.mpnEntry = ttk.Entry(self, width=50, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.mpnEntry.state(['disabled'])

        ############################################################
        #						PRICING/COST INFO			       #
        ############################################################
        unitPriceLabel = ttk.Label(self, text="Pricing: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='center')

        self._tieredPricingTree = ttk.Treeview(self, columns=['column_qty', 'column_price'], height=5)
        self._tieredPricingTree.heading('column_qty', text="Quantity")
        self._tieredPricingTree.heading('column_price', text="Price")

        self._tieredPricingTree.column('#0', minwidth=0)
        self._tieredPricingTree.column('#0', width = 0)
        self._tieredPricingTree.column('column_qty', width=150, anchor="center")
        self._tieredPricingTree.column('column_price', width=150, anchor="center")

        self._tieredPricingTree.bind("<Double-1>", self.onDoubleClick)

        self.searchButton = ttk.Button(self, text="Search", padding=3, command = lambda : SearchPartWindow(self, parent, application))
        self.editModeButton = ttk.Button(self, text="Edit Part", padding=3, command = lambda : self.editMode())
        self.editModeButton.state(['disabled'])
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
        self._tieredPricingTree.place(x=120, y=115, anchor='nw')

        self.searchButton.place(x=75, y=250, anchor='nw')
        self.editModeButton.place(x=175, y=250, anchor='nw')
        closeButton.place(x=275, y=250, anchor='nw')
    
    @property
    def tree(self):
        return self._tieredPricingTree
    
    @property
    def itemCount(self):
        return len(self._tieredPricingTree.get_children())
    
    def editMode(self):
        # Disable the search button when editing
        self.searchButton.config(state = 'disabled')

        # Enable entries
        self.manufacturerEntry.config(state = 'normal')
        self.mpnEntry.config(state = 'normal')

        self.editModeButton['text'] = "Save Edits"
        self.editModeButton['command'] = lambda : self.saveEdits()
    
    def saveEdits(self):
        # Enable the search button
        self.searchButton.config(state = 'enabled')

        # Get the ID for the edited part
        part_id = self.idEntry.get()
        manufacturer = self.manufacturerEntry.get()
        mpn = self.mpnEntry.get()

        # Process the data associated with the part data update
        _manufacturer = self._parent.applet.model.processData(manufacturer)
        _mpn = self._parent.applet.model.processData(mpn)

        # Edit the part in the database
        self._parent.applet.model.editPart(part_id, manufacturer, mpn)

        # Lock the field entries
        self.manufacturerEntry.config(state = 'readonly')
        self.mpnEntry.config(state = 'readonly')

        self.editModeButton['text'] = "Edit Part"
        self.editModeButton['command'] = lambda : self.editMode()

        self.viewPart(part_id)


    def viewPart(self, part_id):
        # Get part data from part_id
        _id, manufacturer, mpn, price = self._parent.applet.model.getPartData(part_id)

        # Clear out all pricing information from pricing tree
        self.tree.delete(*self.tree.get_children())

        # Get relevant pricing data and add it to the tree
        tier_pricing = self._parent.applet.model.getPricingData(part_id)
        for tier_idx in range(0, len(tier_pricing)):
            tier_tuple = tier_pricing[tier_idx]

            tier_quantity = tier_tuple[0]
            tier_price = tier_tuple[1]

            price = f"${float(tier_price):.2f}"

            # Place tier pricing in tree
            self.tree.insert('', 'end', iid=str(tier_idx), values=(tier_quantity, price))
            
        self.idEntry.config(state = 'normal')
        self.manufacturerEntry.config(state = 'normal')
        self.mpnEntry.config(state = 'normal')

        self.idEntry.delete(0, 'end')
        self.manufacturerEntry.delete(0, 'end')
        self.mpnEntry.delete(0, 'end')

        self.idEntry.insert(0, _id)
        self.manufacturerEntry.insert(0, manufacturer)
        self.mpnEntry.insert(0, mpn)

        self.idEntry.config(state = 'readonly')
        self.manufacturerEntry.config(state = 'readonly')
        self.mpnEntry.config(state = 'readonly')

        self.editModeButton.config(state = 'enabled')
    
    def onDoubleClick(self, event=None):
        if self.idEntry.get() != None and self.idEntry.get() != "":
            PartPricingWindow(self, self._parent, self._application, part_id = self.idEntry.get())
    
    def update_tier_pricing_tree(self):
        self.tree.delete(*self.tree.get_children())
        tier_pricing = self._parent.applet.model.getPricingData(self.idEntry.get())

        for tier_idx in range(0, len(tier_pricing)):
            tier_tuple = tier_pricing[tier_idx]

            tier_quantity = tier_tuple[0]
            tier_price = tier_tuple[1]

            price = f"${float(tier_price):.2f}"

            # Place tier pricing in tree
            self.tree.insert('', 'end', iid=str(tier_idx), values=(tier_quantity, price))



class SearchPartWindow(tk.Toplevel):
    def __init__(self, frame, view, application):
        # GLOBAL CLASS VARIABLES
        self._view = view
        self._partFrame = frame
        self._application = application

        # INITIATE TK WINDOW
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().title("Search Part")
        self.winfo_toplevel().geometry("595x450+50+100")
        self.iconbitmap(application.config['icon_path'])

        # INIT APPLET FRAME
        self._appletFrame = SearchPartFrame(self, application)
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
    def partFrame(self):
        return self._partFrame
    
    def kill(self):
        self.winfo_toplevel().destroy()

class SearchPartFrame(tk.Frame):
    def __init__(self, parent, application):
        self._parent = parent
        tk.Frame.__init__(self, parent, width="500", bg=application.frameBackground)

        searchByLabel = ttk.Label(self, text="Search: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        searchBoxLabel = ttk.Label(self, text="Search Term: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self.searchByDropdown = ttk.Combobox(self, width=20, values = ["Part ID", "Manufacturer", "MPN"])
        self.searchByDropdown.insert(0, "Part ID")
        self.searchEntryBox = ttk.Entry(self, width=25, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self.searchButton = ttk.Button(self, text="Search", padding=3, command = lambda : self.search(self))

        self.enterButton = ttk.Button(self, text="Enter", padding = 3, command = lambda : self.enter(self))

        # Results Tree Creation and Heading Definitions
        self._resultsTree = ttk.Treeview(self, columns=['column_partID', 'column_mfr', 'column_mpn'], height=15)
        # self._resultsTree.heading('#0', text='Result #')
        self._resultsTree.heading('column_partID', text='Part ID')
        self._resultsTree.heading('column_mfr', text='Manufacturer')
        self._resultsTree.heading('column_mpn', text='MPN')

        # Results Tree Column Sizing
        self._resultsTree.column('column_partID', width=100, anchor='center')
        self._resultsTree.column('#0', minwidth=0)
        self._resultsTree.column('#0', width = 0)
        self._resultsTree.column('column_partID', minwidth=70, width=70)
        self._resultsTree.column('column_mfr', minwidth=200, width=200)
        self._resultsTree.column('column_mpn', minwidth=250, width=300)

        self._resultsTree.bind("<Double-1>", self.onDoubleClick)

        # Place Components
        searchByLabel.place(x=10, y=25, anchor='nw')
        self.searchByDropdown.place(x=85, y=25, anchor='nw')
        searchBoxLabel.place(x=240, y=25, anchor='nw')
        self.searchEntryBox.place(x=320, y=25, anchor='nw')
        self.searchButton.place(x=500, y=20, anchor='nw')
        self._resultsTree.place(x=10, y=55, anchor='nw')

        self.enterButton.place(x = 260, y = 395, anchor='nw')

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
    
    def enter(self, frame):
        try:
            # Get selected TreeView Item ID
            item = self.resultsTree.selection()[0]
        except IndexError as e:
            return -1

        part_id, mfr, mpn = self.resultsTree.item(item, "values")
        part_id_processed = self._parent.view.applet.model.processData(part_id)

        self._parent.partFrame.viewPart(part_id_processed)

        self._parent.kill()
    
    def onDoubleClick(self, event = None):
        try:
            # Get selected TreeView Item ID
            item = self.resultsTree.selection()[0]
        except IndexError as e:
            return -1

        part_id, mfr, mpn = self.resultsTree.item(item, "values")
        part_id_processed = self._parent.view.applet.model.processData(part_id)

        self._parent.partFrame.viewPart(part_id_processed)

        self.after(100, lambda : self.winfo_toplevel().destroy())





class PartPricingWindow(tk.Toplevel):
    def __init__(self, frame, view, application, part_id):
        # GLOBAL CLASS VARIABLES
        self._view = view
        self._partFrame = frame
        self._application = application
        self._part_id = part_id

        # INITIATE TK WINDOW
        tk.Toplevel.__init__(self)
        self.winfo_toplevel().title("Part Pricing")
        self.winfo_toplevel().geometry("370x260+50+100")
        self.iconbitmap(application.config['icon_path'])

        # INIT APPLET FRAME
        self._appletFrame = PartPricingFrame(self, application)
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
    def partFrame(self):
        return self._partFrame
    
    @property
    def part_id(self):
        return self._part_id
    
    def kill(self):
        self.winfo_toplevel().destroy()

class PartPricingFrame(tk.Frame):
    def __init__(self, parent, application):
        self._parent = parent
        tk.Frame.__init__(self, parent, width="500", bg=application.frameBackground)

        # Get tier pricing information for part
        tiered_pricing_data = self._parent.view.applet.model.getTierPricing(self._parent.part_id)

        # Part ID Components
        self._partidLabel = ttk.Label(self, text="Part ID: ", font = ('Sans', '8', 'bold'), foreground=application._inventoryStyleBackground, background=application.frameBackground, justify='right')
        self._partidEntry = ttk.Entry(self, width=5, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self._partidEntry.insert(0, self._parent.part_id)
        self._partidEntry.config(state='readonly')

        # Number of Tiers Components
        self._numberOfTiersLabel = ttk.Label(self, text="Number of Pricing Tiers: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self._numberOfTiersEntry = ttk.Entry(self, width=5, text="1", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='left')
        self._numberOfTiersEntry.delete(0, 'end')
        self._numberOfTiersEntry.insert(0, tiered_pricing_data["number_of_tiers"])
        self._numberOfTiersEntry.config(state = 'readonly')

        self._incrementTiersButton = ttk.Button(self, text="Add", command=lambda: self.add_tier())
        if tiered_pricing_data["number_of_tiers"] == 5:
            self._incrementTiersButton.config(state = 'disabled')
        self._decrementTiersButton = ttk.Button(self, text="Remove", command=lambda: self.remove_tier())
        if tiered_pricing_data["number_of_tiers"] == 1:
            self._decrementTiersButton.config(state = 'disabled')
        
        self._saveTieredPricingButton = ttk.Button(self, text="Save", command=lambda: self.save())
        self._cancelButton = ttk.Button(self, text="Cancel", command=lambda:self.kill())

        self._errorLabel = ttk.Label(self, text="", foreground='red', background='white')

        # Tier Pricing Table Headings
        self._tierQtyLabel = ttk.Label(self, text="Quantity", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self._tierPriceLabel = ttk.Label(self, text="Price", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')

        # Tier Row Labels
        self._tier1Label = ttk.Label(self, text="Tier 1: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self._tier2Label = ttk.Label(self, text="Tier 2: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self._tier3Label = ttk.Label(self, text="Tier 3: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self._tier4Label = ttk.Label(self, text="Tier 4: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self._tier5Label = ttk.Label(self, text="Tier 5: ", font = ('Sans', '8', 'bold'), foreground = application._inventoryStyleBackground, background = application.frameBackground, justify='right')
        self._tier_row_labels = [self._tier1Label, self._tier2Label, self._tier3Label, self._tier4Label, self._tier5Label]

        # Tier Quantity Entries
        self._tier1QtyEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier1QtyEntry.delete(0, 'end')
        self._tier1QtyEntry.insert(0, tiered_pricing_data['tier1_quantity'])
        self._tier2QtyEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier2QtyEntry.delete(0, 'end')
        self._tier2QtyEntry.insert(0, tiered_pricing_data['tier2_quantity'])
        self._tier3QtyEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier3QtyEntry.delete(0, 'end')
        self._tier3QtyEntry.insert(0, tiered_pricing_data['tier3_quantity'])
        self._tier4QtyEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier4QtyEntry.delete(0, 'end')
        self._tier4QtyEntry.insert(0, tiered_pricing_data['tier4_quantity'])
        self._tier5QtyEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier5QtyEntry.delete(0, 'end')
        self._tier5QtyEntry.insert(0, tiered_pricing_data['tier5_quantity'])
        self._tier_qty_entries = [self._tier1QtyEntry, self._tier2QtyEntry, self._tier3QtyEntry, self._tier4QtyEntry, self._tier5QtyEntry]

        # Tier Price Entries
        self._tier1PriceEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier1PriceEntry.delete(0, 'end')
        self._tier1PriceEntry.insert(0, tiered_pricing_data['tier1_price'])
        self._tier2PriceEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier2PriceEntry.delete(0, 'end')
        self._tier2PriceEntry.insert(0, tiered_pricing_data['tier2_price'])
        self._tier3PriceEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier3PriceEntry.delete(0, 'end')
        self._tier3PriceEntry.insert(0, tiered_pricing_data['tier3_price'])
        self._tier4PriceEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier4PriceEntry.delete(0, 'end')
        self._tier4PriceEntry.insert(0, tiered_pricing_data['tier4_price'])
        self._tier5PriceEntry = ttk.Entry(self, width = 10, text="", font = ('Sans', '8', 'bold'), background = '#FFFFFF', foreground = '#000000', justify='center')
        self._tier5PriceEntry.delete(0, 'end')
        self._tier5PriceEntry.insert(0, tiered_pricing_data['tier5_price'])
        self._tier_price_entries = [self._tier1PriceEntry, self._tier2PriceEntry, self._tier3PriceEntry, self._tier4PriceEntry, self._tier5PriceEntry]

        # Place Components
        self._partidLabel.place(x=10, y=10, anchor='nw')
        self._partidEntry.place(x=100, y=10, anchor='nw')
        self._errorLabel.place(x=155, y=10, anchor='nw')
        self._numberOfTiersLabel.place(x=10, y=50, anchor='nw')
        self._numberOfTiersEntry.place(x=155, y=50, anchor='nw')

        self._decrementTiersButton.place(x=200, y=50, anchor='nw')
        self._incrementTiersButton.place(x=280, y=50, anchor='nw')

        self._tierQtyLabel.place(x=90, y=100, anchor='nw')
        self._tierPriceLabel.place(x=200, y=100, anchor='nw')

        for tier in range(1, tiered_pricing_data["number_of_tiers"]+1):
            self.show_tier(tier)
        
        self._saveTieredPricingButton.place(x=280, y=150, anchor='nw')
        self._cancelButton.place(x=280, y=200, anchor='nw')
    
    def kill(self):
        self.winfo_toplevel().destroy()

    def show_tier(self, tier_number):
        # Place Tier Row Labels
        row_label_x = 10
        y = 125 + (tier_number-1)*25
        self._tier_row_labels[tier_number-1].place(x=row_label_x, y=y, anchor='nw')

        # Place Tier quantity entries
        row_qty_x = 80
        self._tier_qty_entries[tier_number-1].place(x=row_qty_x, y=y, anchor='nw')

        # Place Tier price entries
        row_price_x = 180
        self._tier_price_entries[tier_number-1].place(x=row_price_x, y=y, anchor='nw')
    
    def add_tier(self):
        current_number_of_tiers = int(self._numberOfTiersEntry.get())
        new_number_of_tiers = current_number_of_tiers + 1

        # Make sure we don't get price errors when removing a tier
        self._tier_price_entries[new_number_of_tiers-1].delete(0, 'end')
        self._tier_price_entries[new_number_of_tiers-1].insert(0, self._tier_price_entries[current_number_of_tiers-1].get())

        # Make sure we don't get quantity errors when removing a tier
        self._tier_qty_entries[new_number_of_tiers-1].delete(0, 'end')
        if new_number_of_tiers == 2:
            self._tier_qty_entries[new_number_of_tiers-1].insert(0, "10")
        elif new_number_of_tiers == 3:
            self._tier_qty_entries[new_number_of_tiers-1].insert(0, "50")
        elif new_number_of_tiers == 4:
            self._tier_qty_entries[new_number_of_tiers-1].insert(0, "100")
        elif new_number_of_tiers == 5:
            self._tier_qty_entries[new_number_of_tiers-1].insert(0, "200")

        # Reveal the tier row
        self.show_tier(new_number_of_tiers)
        self._numberOfTiersEntry.config(state = 'enabled')
        self._numberOfTiersEntry.delete(0, 'end')
        self._numberOfTiersEntry.insert(0, str(new_number_of_tiers))
        self._numberOfTiersEntry.config(state = 'readonly')

        # Enable the decrement tier count button
        self._decrementTiersButton.config(state = 'enabled')

        # We've hit the limit -> Disable the increment button
        if new_number_of_tiers == 5:
            self._incrementTiersButton.config(state = 'disabled')
        

    def remove_tier(self):
        # Determine tier values
        current_number_of_tiers = int(self._numberOfTiersEntry.get())
        new_number_of_tiers = current_number_of_tiers - 1

        # Make sure we don't get price errors when removing a tier
        self._tier_price_entries[current_number_of_tiers-1].delete(0, 'end')
        self._tier_price_entries[current_number_of_tiers-1].insert(0, self._tier_price_entries[new_number_of_tiers-1].get())

        # Make sure we don't get quantity errors when removing a tier
        self._tier_qty_entries[current_number_of_tiers-1].delete(0, 'end')
        self._tier_qty_entries[current_number_of_tiers-1].insert(0, self._tier_qty_entries[new_number_of_tiers-1].get())
        
        # Hide the removed tier
        self.hide_tier(current_number_of_tiers)
        self._numberOfTiersEntry.config(state = 'enabled')
        self._numberOfTiersEntry.delete(0, 'end')
        self._numberOfTiersEntry.insert(0, str(new_number_of_tiers))
        self._numberOfTiersEntry.config(state = 'readonly')

        # Enable the increment tier button
        self._incrementTiersButton.config(state = 'enabled')

        # We've hit the limit, disable the decrement tier button
        if new_number_of_tiers == 1:
            self._decrementTiersButton.config(state = 'disabled')


    
    def save(self):
        self._errorLabel.config(text= "")
        number_of_tiers = int(self._numberOfTiersEntry.get())

        # Check for quantities
        qty = 0
        tier = 1
        for qty_entry in self._tier_qty_entries:
            if tier >= number_of_tiers:
                break
            temp_qty = int(qty_entry.get())
            if temp_qty <= 0:
                self._errorLabel.config(text = "Quantities must be positive & non-zero.")
                return -1
            if temp_qty < qty:
                self._errorLabel.config(text= "Quantities must increase.")
                return -1
            qty = temp_qty
            tier += 1
        
        # Check for prices
        price = 999999999999.0
        tier = 1
        for price_entry in self._tier_price_entries:
            if tier >= number_of_tiers:
                break
            temp_price = float(price_entry.get())
            if temp_price > price:
                self._errorLabel.config(text = "Prices must decrease.")
                return -1
            price = temp_price
            tier += 1
        
        part_id = self._partidEntry.get()

        # Collect quantity and price information
        tier_pricing = []
        for i in range(0, 5):
            tier_qty = int(self._tier_qty_entries[i].get())
            tier_price = float(self._tier_price_entries[i].get())

            tier_pricing.append((tier_qty, tier_price))

        self._parent.view.applet.model.updateTierPricing(part_id, tier_pricing, number_of_tiers)

        self._parent.partFrame.update_tier_pricing_tree()
        
        self.kill()
        return 0

    def hide_tier(self, tier_number):
        self._tier_row_labels[tier_number-1].place_forget()
        self._tier_qty_entries[tier_number-1].place_forget()
        self._tier_price_entries[tier_number-1].place_forget()

