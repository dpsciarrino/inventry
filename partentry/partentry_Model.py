class AppletModel:
    def __init__(self, applet, application):
        self._application = application
        self._applet = applet
        self._databaseOperator = application.databaseOperator

    def processData(self, data):
        invalidCharacters = self._databaseOperator.invalidChars
        _data = data
        for char in invalidCharacters:
            if char in _data:
                _data = _data.replace(char, "\\" + char)
        
        return _data

    def nextAvailablePartID(self):
        self._databaseOperator.openDatabase()
        sql = f"""SELECT MAX(part_id) FROM {self._applet.databaseTableName}"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        data = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        if data[0][0] == None:
            return 1
        
        return int(data[0][0]) + 1
    
    def insertPart(self, part_id, manufacturer, mpn, price):
        self._databaseOperator.openDatabase()
        sql = f"""INSERT INTO "parts" ('part_id', 'manufacturer', 'mpn', 'tier1_price') VALUES ('{str(part_id)}', '{manufacturer}', '{mpn}', {price})"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        self._databaseOperator.closeDatabase()