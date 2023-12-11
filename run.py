import os
import sys
import sqlite3

from gui import ApplicationWindow

from partentry.applet import Applet as PartEntryApp
from partviewer.applet import Applet as PartViewerApp

from bombuilder.applet import Applet as BOMBuilderApp
from bomviewer.applet import Applet as BOMViewerApp

class DatabaseOperator:
    def __init__(self):
        self._databaseName = 'inventry.db'

        if getattr(sys, 'frozen', False):
            self._databasePath = os.path.join(sys._MEIPASS, f"{self._databaseName}")
        else:
            self._databasePath = os.path.join(os.path.dirname(__file__), self._databaseName)
        
        self._connection = None
        self._connected = False
        self._cursor = None
        self._invalidChars = ["|", "'", ".", "-", "*", "/", "<", ";", ">", ",", "=", "~", "!", "^", "(", ")"]

    @property
    def invalidChars(self):
        return self._invalidChars
    
    def openDatabase(self):
        if self._connected == False:
            self._connection = sqlite3.connect(self._databasePath)
            self._connected = True

    def closeDatabase(self):
        if self._connected:
            self._connection.close()
            self._connected = False
    
    def setCursor(self):
        self._cursor = self._connection.cursor()
    
    def fetchall(self):
        if self._cursor != None:
            return self._cursor.fetchall()
        else:
            return None
    
    def fetchone(self):
        if self._cursor != None:
            return self._cursor.fetchone()
        else:
            return None
    
    def execute(self, sql):
        self._cursor.execute(sql)

    def commit(self):
        if self._connected:
            if self._connection != None:
                self._connection.commit()

class Application:
    def __init__(self):
        print("Initializing Inventry...")
        self._databaseName = "inventry.db"
        self._icon = os.path.abspath('img/inventry.ico')

        self._databaseOperator = DatabaseOperator()

        # DIRECTORY SETUP
        self._srcDirectory = None
        if getattr(sys, 'frozen', False):
            self._srcDirectory = sys._MEIPASS
        else:
            self._srcDirectory = os.path.dirname(os.path.abspath(__file__))

        # APPLICATION COLORS
        self._frameBackground = '#ffffff' #dark-grey
        self._inventoryStyleBackground = '#070707' # Blue

        self._config = {
            "icon_path":self._icon,
            "database_operator":self._databaseOperator,
            "database_name":self._databaseName,
            "src_dir":self._srcDirectory
        }

        self._theme = {
            "frame_background": self._frameBackground,
            "inventry_background": self._inventoryStyleBackground
        }

        self._currentWindow = ApplicationWindow(self)
    
    @property
    def config(self):
        return self._config

    @property
    def databaseName(self):
        return self._databaseName
    
    @property
    def databaseOperator(self):
        return self._databaseOperator
    
    @property
    def srcDirectory(self):
        return self._srcDirectory
    
    @property
    def partentry(self):
        return PartEntryApp(self)
    
    @property
    def partviewer(self):
        return PartViewerApp(self)
    
    @property
    def bombuilder(self):
        return BOMBuilderApp(self)
    
    @property
    def bomviewer(self):
        return BOMViewerApp(self)
    
    @property
    def frameBackground(self):
        return self._frameBackground
    
    @property
    def inventoryStyleBackground(self):
        return self._inventoryStyleBackground




if __name__ == '__main__':
    app = Application()
