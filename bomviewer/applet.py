import sys
import os.path
from .bomviewer_GUI import AppletMainWindow
from .bomviewer_Model import AppletModel

sourceDir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(sourceDir)

import models

sys.path.remove(sourceDir)

class Applet:
	def __init__(self, application):
		self._prefix = "BOM"
		self._databaseTableName = "boms"

		self._model = AppletModel(self, application)
		self._view = AppletMainWindow(self, application)

	@property
	def controller(self):
		return self._controller
	
	@property
	def model(self):
		return self._model
	
	@property
	def view(self):
		return self._view

	@property
	def prefix(self):
		return self._prefix
	
	@property
	def databaseTableName(self):
		return self._databaseTableName