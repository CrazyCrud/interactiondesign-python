import math
from PyQt4 import QtGui, QtCore


class Circle():

	def __init__(self, diameter, x, y):
		self.diameter = diameter
		self.x = x
		self.y = y


	def drawCircle(self, event, qp):
		rect = QtCore.QRect(self.x, self.y, self.diameter, self.diameter)
		qp.setBrush(QtGui.QColor(34, 34, 200))
		qp.drawRoundRect(rect)


	def isClicked(self, x, y):
		result = math.pow((x - self.x), 2) + math.pow((y - self.y), 2)
		if result <= math.pow(self.diameter / 2.0, 2):
			return True
		else:
			return False
