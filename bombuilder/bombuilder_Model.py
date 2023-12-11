class AppletModel:
    def __init__(self, applet, application):
        self._application = application
        self._applet = applet
        self._databaseOperator = application.databaseOperator

        self._availableBOMs = self.getBOMs()
    
    @property
    def availableBOMs(self):
        return self._availableBOMs
    
    @property
    def application(self):
        return self._application

    def getBOMs(self):
        """
        Fetches the BOM ID column in database table 'boms'.
        """
        self._databaseOperator.openDatabase()
        sql = f"""SELECT '{self._applet.databaseTableName}'.'bom_id' FROM '{self._applet.databaseTableName}' """
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        data = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        idList = []
        for d in data:
            idList.append(d[0])
        
        return idList
    
    def searchInventory(self, column, searchTerm):
        self._databaseOperator.openDatabase()
        sql = f"""SELECT "parts".'part_id', "parts".'manufacturer', "Parts".'mpn' FROM parts WHERE "{column}" LIKE '%{searchTerm}%'"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        dataArray = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        return dataArray
    
    def processData(self, data):
        invalid_characters = self._databaseOperator.invalidChars
        _data = data
        for char in invalid_characters:
            if char in _data:
                _data = _data.replace(char, "\\" + char)
        
        return _data
    
    def getPartData(self, part_id):
        """
        getPartData(part_id)

        Given the ID of a single part, fetch all columns of the associated part.
        """
        self._databaseOperator.openDatabase()
        sql = f"""SELECT "parts".'part_id', "parts".'manufacturer', "parts".'mpn' FROM "parts" WHERE "parts".'part_id' = '{part_id}' """
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        data = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        _id = data[0][0]
        mfr = data[0][1].replace("\\", "")
        mpn = data[0][2].replace("\\", "")

        return _id, mfr, mpn

    def nextAvailableID(self):
        self._databaseOperator.openDatabase()
        sql = f"""SELECT MAX(bom_id) FROM {self._applet.databaseTableName}"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        data = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        if data[0][0] == None:
            return 1
        
        return int(data[0][0]) + 1
    
    def insertBOM(self, bom_id, bom_name):
        self._databaseOperator.openDatabase()
        sql = f"""INSERT INTO {self._applet.databaseTableName} ('bom_id', 'name') VALUES ('{str(bom_id)}', '{bom_name}')"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        self._databaseOperator.closeDatabase()
    
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
        

