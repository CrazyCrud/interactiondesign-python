from PyQt4 import QtGui, QtCore

class Circle():

	def __init__(self, size, distance):
		self.size = size;
		self.distance = distance;
		self.drawCircle()
		print ("init circle")


	def drawCircle(self):
		qp = QtGui.QPainter()
		qp.begin(self)
		rect = QtCore.QRect(10,10, 30,30)
		qp.setBrush(QtGui.QColor(34, 34, 200))
		qp.drawRoundRect(rect)
		qp.end()
		print('drawnCircle')

'''
	def drawText(self, event, qp):
		qp.setPen(QtGui.QColor(168, 34, 3))
		qp.setFont(QtGui.QFont('Decorative', 32))
		if self.counter > 0:
			 self.text = str(self.counter)
		qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)      
'''


circle1 = Circle(20, 40)