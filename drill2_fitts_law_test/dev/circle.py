import math
from PyQt4 import QtGui, QtCore


class Circle():


	def __init__(self, diameter, x, y):
		self.diameter = diameter;
		self.x = x;
		self.y = y;
		self.drawCircle()


	def drawCircle(self):
		qp = QtGui.QPainter()
		qp.begin(self)
		rect = QtCore.QRect(10,10, 30,30)
		qp.setBrush(QtGui.QColor(34, 34, 200))
		qp.drawRoundRect(rect)
		qp.end()
		print('drawnCircle')


	def isClicked(self, x, y):
		result = math.pow((x - self.x), 2) + math.pow((y - self.y), 2)
		if result <= math.pow(self.diamter / 2.0, 2):
			return True
		else:
			return False

'''
	def drawText(self, event, qp):
		qp.setPen(QtGui.QColor(168, 34, 3))
		qp.setFont(QtGui.QFont('Decorative', 32))
		if self.counter > 0:
			 self.text = str(self.counter)
		qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)
'''
