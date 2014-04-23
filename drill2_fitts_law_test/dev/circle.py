import math
from PyQt4 import QtGui
from PyQt4.QtCore import QPoint


class Circle():

	def __init__(self, diameter, x, y):
		self.diameter = diameter
		self.radius = math.floor(diameter / 2.0)
		self.center = QPoint(x, y)


	def drawCircle(self, event, qp):
		qp.setBrush(QtGui.QColor(34, 34, 200))
		qp.drawEllipse(self.center, self.radius, self.radius)


	def isClicked(self, pos):
		result = math.pow((pos.x() - self.center.x()), 2) + math.pow((pos.y() - self.center.y()), 2)
		if result <= math.pow(self.radius, 2):
			return True
		else:
			return False

	def x(self):
		return self.center.x()

	def y(self):
		return self.center.y()
