class AppletModel:
    def __init__(self, applet, application):
        self._application = application
        self._applet = applet
        self._databaseOperator = application.databaseOperator

        self._availableBOMs = self.getBOMList()
    
    @property
    def availableBOMs(self):
        return self._availableBOMs
    
    @property
    def application(self):
        return self._application
    
    def getBOMList(self):
        """
        Fetches the BOM ID column in database table 'boms'.
        """
        self._databaseOperator.openDatabase()
        sql = f"""SELECT '{self._applet.databaseTableName}'.'name' FROM '{self._applet.databaseTableName}' """
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        data = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        idList = []
        for d in data:
            idList.append(d[0])
        
        return idList
    
    def processData(self, data):
        invalidCharacters = self._databaseOperator.invalidChars
        _data = data
        for char in invalidCharacters:
            if char in _data:
                _data = _data.replace(char, "\\" + char)

        return _data
    
    def get_bom_id_from_name(self, bom_name):
        self._databaseOperator.openDatabase()
        bom_id_sql = f"""\
            SELECT 'boms'.'bom_id' \
            FROM 'boms'\
            WHERE 'boms'.'name' = '{bom_name}';"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(bom_id_sql)
        self._databaseOperator.commit()
        bom_id = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        return bom_id[0][0]
    
    def get_bom_parts_by_name(self, bom_name):
        """
        get_bom_data_by_name(bom_name)

        Returns the parts list for a given BOM name in format:
        0 = Part ID
        1 = Manufacturer
        2 = MPN
        3 = Tiered Price
        4 = Quantity on BOM
        """
        self._databaseOperator.openDatabase()
        bom_parts_sql = f"""\
            SELECT  'parts'.'part_id', 'parts'.'manufacturer', \
                    'parts'.'mpn', 'parts'.'tier1_price', \
                    'bom_parts'.'bom_quantity' \
            FROM 'bom_parts' \
                INNER JOIN 'parts' ON 'bom_parts'.'part_id' = 'parts'.'part_id'\
            WHERE 'bom_parts'.'bom_id' = (\
                SELECT 'boms'.'bom_id' \
                FROM 'boms' \
                WHERE 'boms'.'name' = '{bom_name}');"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(bom_parts_sql)
        self._databaseOperator.commit()
        parts_list = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        return parts_list
    
    def getPartData(self, part_id):
        """
        getPartData(part_id)

        Given the ID of a single part, fetch all columns of the associated part.
        """
        self._databaseOperator.openDatabase()
        sql = f"""SELECT "parts".'part_id', "parts".'manufacturer', "parts".'mpn', "parts".'tier1_price' FROM "parts" WHERE "parts".'part_id' = '{part_id}' """
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        data = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        _id = data[0][0]
        mfr = data[0][1].replace("\\", "")
        mpn = data[0][2].replace("\\", "")
        price = str(data[0][3]).replace("\\", "")

        return _id, mfr, mpn, price
    
    def searchInventory(self, column, searchTerm):
        self._databaseOperator.openDatabase()
        sql = f"""SELECT "parts".'part_id', "parts".'manufacturer', "Parts".'mpn' FROM parts WHERE "{column}" LIKE '%{searchTerm}%'"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        dataArray = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        return dataArray
    
    def insertPartsIntoBom(self, max_item_number: int, bom_id: str, bom_items_dictionary: dict):
        base_sql = f"""INSERT INTO "bom_parts" ('bom_id', 'part_id', 'bom_quantity') VALUES ("""
        sql_inserts = []
        for i in range(0, max_item_number):
            try:
                item_part_id = bom_items_dictionary[str(i+1)]['part_id']
                item_quantity = bom_items_dictionary[str(i+1)]['quantity']

                s = str(bom_id) + ", " + str(item_part_id) + ", " + str(item_quantity) + ");"
                sql_inserts.append(base_sql + s)
            except KeyError as e:
                continue
        
        self._databaseOperator.openDatabase()
        for query in sql_inserts:
            self._databaseOperator.setCursor()
            self._databaseOperator.execute(query)
            self._databaseOperator.commit()
        
        self._databaseOperator.closeDatabase()
    
    def delete_bom_parts(self, bom_id):
        self._databaseOperator.openDatabase()
        sql = f"""DELETE FROM 'bom_parts' WHERE 'bom_parts'.'bom_id' = {bom_id}"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        self._databaseOperator.closeDatabase()
        
    
    def get_single_build_cost(self, bom_name):
        bom_line_items = self.get_bom_parts_by_name(bom_name)
        total_single_build_cost = 0
        for line in bom_line_items:
            price = line[3]
            qty = line[4]

            total_for_line = float(price) * int(qty)
            total_single_build_cost += total_for_line
        
        return round(total_single_build_cost, 2)
    
    def get_build_cost(self, bom_name, quantity):
        bom_line_items = self.get_bom_parts_by_name(bom_name)
        total_build_cost = 0
        quantity_to_build = quantity

        for line in bom_line_items:
            part_id = line[0]
            part_bom_qty = line[4]
            actual_parts_needed =  int(quantity_to_build) * int(part_bom_qty)

            line_cost = self.get_total_part_cost_at_quantity(part_id, actual_parts_needed)

            total_build_cost += line_cost

        return round(total_build_cost, 2)
    
    def get_total_part_cost_at_quantity(self, part_id, quantity):
        """
        Retrieves the total part cost of a tiered-priced part at a specified quantity
        """
        # Get part pricing data
        tiered_pricing_data = self.get_tiered_pricing_for_part(part_id)

        # calculate unit cost based on tiered pricing model
        unit_cost = self.calculate_unit_cost_from_tiered_pricing(tiered_pricing_data, quantity)

        # calculate total cost based on quantity
        total_cost_at_quantity = quantity * unit_cost

        return total_cost_at_quantity
    
    def get_tiered_pricing_for_part(self, part_id):
        """
        get_tiered_pricing_for_part

        Returns pricing data in the form of a list of key-value pairs, one pair per pricing tier
        """
        self._databaseOperator.openDatabase()
        sql = f"""SELECT "parts".'number_of_tiers' FROM 'parts' WHERE "part_id"="{part_id}";"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        data = self._databaseOperator.fetchone()
        self._databaseOperator.closeDatabase()

        number_of_tiers = data[0]
        tier_pricing_list = []

        for tier_idx in range(0, number_of_tiers):
            tier = tier_idx+1
            sql = f"""SELECT "parts".'tier{int(tier)}_quantity', "parts".'tier{int(tier)}_price' FROM 'parts' WHERE "part_id" = "{part_id}";"""
            self._databaseOperator.openDatabase()
            self._databaseOperator.setCursor()
            self._databaseOperator.execute(sql)
            data = self._databaseOperator.fetchone()
            self._databaseOperator.closeDatabase()

            tier_pricing_list.append((f"{data[0]}", f"{data[1]}"))
        
        return tier_pricing_list
    
    def calculate_unit_cost_from_tiered_pricing(self, tiered_pricing_data, quantity):
        """
        Calculates the unit cost of a tiered priced part from supplied tiered_pricing_data

        Generate tiered pricing data from 'get_tiered_pricing_for_part()' function.
        """
        price = 0.0
        for i in range(0, len(tiered_pricing_data)):
            tier_tuple = tiered_pricing_data[i]
            tier_quantity = int(tier_tuple[0])
            tier_price = float(tier_tuple[1])

            if int(quantity) >= tier_quantity:
                price = tier_price
        
        return price
