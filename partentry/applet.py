import sys
import os.path
from .partentry_GUI import AppletMainWindow
from .partentry_Model import AppletModel

sourceDir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(sourceDir)

import models

sys.path.remove(sourceDir)

class Applet:
	def __init__(self, application):
		self._databaseTableName = "parts"

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
	def databaseTableName(self):
		return self._databaseTableName