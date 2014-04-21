#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from circle import Circle
from PyQt4 import QtGui, QtCore


class ClickRecorder(QtGui.QWidget):


	def requestFileName(self):
		if len(sys.argv) < 2:
			exit(0)
		else:
			self.fileName = sys.argv[1]


	def readTestSetup(self):

		#read input
		with open(self.fileName) as f:
		#with open(self.fileName) as f:
			content = f.read()

		if not content:
			print 'File is empty'
			exit(0)
		#split array of form
		#USER:1
		#WIDTHS:10,20,30,40
		#DISTANCES:100,200,300,400
		#USER:2...
		#to structure
		#{1 : { widths : [10,20,30,40] }, { distances: [100,200..] } }

		#split content into array with infos of the user
		usersData = content.split('(User)')

		self.setupData = {}

		for userData in usersData:
			userLines = userData.split()
			userId = userLines[0].split(':')[1]
			widths = map(int, userLines[1].split(':')[1].split(','))
			distances = map(int, userLines[2].split(':')[1].split(','))

			self.setupData.update(
			{   userId :
				{
					"widths" : widths,
					"distances" : distances
				}
			})
		print "setup data: " % self.setupData


	def __init__(self):
		super(ClickRecorder, self).__init__()
		self.requestFileName()
		#self.readTestSetup()
		self.initUI()
		self.setupCircles()
		self.setupTimer()
		self.setupLogging()
		self.setupTrial()


	def setupTrial(self):
		self.movements = 0
		self.errors = 0


	def initUI(self):
		self.setGeometry(0, 0, 500, 300)
		self.setWindowTitle("A Study about Fitts's Law")
		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		self.center()
		self.show()


	def center(self):
		res = QtGui.QDesktopWidget().screenGeometry()
		self.move((res.width() / 2) - (self.frameSize().width() / 2),
			(res.height() / 2) - (self.frameSize().height() / 2))


	def paintEvent(self, event):
		qp = QtGui.QPainter()
		qp.begin(self)
		qp.setRenderHint(qp.Antialiasing)
		qp.setBrush(QtGui.QColor(255, 255, 255))
		qp.drawRect(event.rect())
		self.drawCircles(event, qp)
		qp.end()


	def mousePressEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			if self.timer.isActive == False:
				self.timer.start(1000 * 60)

			for circle in self.circles:
				if circle.isClicked(event.pos()) == True:
					if self.currentCircle == None:
						self.currentCircle = circle
						return
					elif circle != self.currentCircle:
						self.currentCircle = circle
						self.movements += 1
						return
					else:
						self.errors += 1
						return

			if self.currentCircle != None:
				self.errors += 1

			self.currentCircle = None


	def setupLoggin(self):
		pass


	def setupCircles(self):
		self.circles = []
		self.currentCircle = None
		self.circles.append(Circle(20, 50, 150))
		self.circles.append(Circle(20, 450, 150))


	def setupTimer(self):
		self.timer = QtCore.QtTimer()
		self.timer.timeout.connect(self.timeUp)


	def drawCircles(self, event, qp):
		for circle in self.circles:
			circle.drawCircle(event, qp)


	def timeUp(self):
		self.timer.stop()
		self.logResults()


	def logResults(self):
		pass


def main():
	app = QtGui.QApplication(sys.argv)
	click = ClickRecorder()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
