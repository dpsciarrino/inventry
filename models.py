######################################################################################################################
######################################################################################################################

#	BOM Model

######################################################################################################################
######################################################################################################################

class BOM:
	def __init__(self):
		self._bomID = ""

		#A dictionary representing the BOM items
		self._items = {}

	@property
	def bomID(self):
		return self._bomID

	@property
	def items(self):
		return self._items	
	
	@bomID.setter
	def bomID(self, value):
		self._bomID = value

	@items.setter
	def items(self, value):
		self._items = value