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

    def getPartData(self, part_id):
        self._databaseOperator.openDatabase()
        sql = f"""SELECT "parts".'part_id', \
                        "parts".'manufacturer', \
                        "parts".'mpn', \
                        "parts".'tier1_price'
                FROM 'parts'\
                WHERE "part_id" = '{part_id}'"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        data = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()
    
        _id = data[0][0]
        mfr = data[0][1].replace("\\", "")
        mpn = data[0][2].replace("\\", "")
        price = data[0][3]

        return _id, mfr, mpn, price
    
    def getPricingData(self, part_id):
        """
        getPricingData

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
        
    def editPart(self,  part_id, \
                        manufacturer, \
                        mpn):
        self._databaseOperator.openDatabase()

        sql = f"""UPDATE 'parts' SET \
            "part_id" = '{part_id}',\
            "manufacturer" = '{manufacturer}',\
            "mpn" = '{mpn}'
            WHERE "part_id" = '{part_id}'"""
        
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        self._databaseOperator.closeDatabase()
    
    def searchInventory(self, column, searchTerm):
        self._databaseOperator.openDatabase()
        sql = f"""SELECT "parts".'part_id', "parts".'manufacturer', "Parts".'mpn' FROM parts WHERE "{column}" LIKE '%{searchTerm}%'"""
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        dataArray = self._databaseOperator.fetchall()
        self._databaseOperator.closeDatabase()

        return dataArray

    def getTierPricing(self, part_id):
        sql = f"""SELECT "parts"."number_of_tiers", \
                        "parts"."tier1_quantity", "parts"."tier1_price", \
                        "parts"."tier2_quantity", "parts"."tier2_price",\
                        "parts"."tier3_quantity", "parts"."tier3_price",\
                        "parts"."tier4_quantity", "parts"."tier4_price",\
                        "parts"."tier5_quantity", "parts"."tier5_price"\
                FROM "parts" \
                WHERE "parts"."part_id" = '{part_id}';"""
        
        self._databaseOperator.openDatabase()
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        data = self._databaseOperator.fetchone()
        self._databaseOperator.closeDatabase()

        return_data = {
            "number_of_tiers": data[0],
            "tier1_quantity": data[1],
            "tier1_price": data[2],
            "tier2_quantity": data[3],
            "tier2_price": data[4],
            "tier3_quantity": data[5],
            "tier3_price": data[6],
            "tier4_quantity": data[7],
            "tier4_price": data[8],
            "tier5_quantity": data[9],
            "tier5_price": data[10],
        }

        return return_data

    def updateTierPricing(self, part_id, tier_pricing_list, number_of_tiers):
        sql = f"""UPDATE parts SET \
            "number_of_tiers" = {number_of_tiers},\
            "tier1_quantity" = {tier_pricing_list[0][0]},\
            "tier1_price" = {tier_pricing_list[0][1]},\
            "tier2_quantity" = {tier_pricing_list[1][0]},\
            "tier2_price" = {tier_pricing_list[1][1]},\
            "tier3_quantity" = {tier_pricing_list[2][0]},\
            "tier3_price" = {tier_pricing_list[2][1]},\
            "tier4_quantity" = {tier_pricing_list[3][0]},\
            "tier4_price" = {tier_pricing_list[3][1]},\
            "tier5_quantity" = {tier_pricing_list[4][0]},\
            "tier5_price" = {tier_pricing_list[4][1]}\
            WHERE "part_id" = {part_id}
            """
        
        self._databaseOperator.openDatabase()
        self._databaseOperator.setCursor()
        self._databaseOperator.execute(sql)
        self._databaseOperator.commit()
        self._databaseOperator.closeDatabase()
        