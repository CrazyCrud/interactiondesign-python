#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import csv
import datetime
import random
from circle import Circle
from PyQt4 import QtGui, QtCore


class ClickRecorder(QtGui.QWidget):


	def requestFileName(self):
		if len(sys.argv) < 2:
			#exit(0)
			self.fileName = "user1.txt"
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


		userLines = content.split()

		#split description and comma-separated values, take values and convert to int
		self.userId 	= userLines[0].split(':')[1]
		self.widths 	= map(int, userLines[1].split(':')[1].split(','))
		self.distances 	= map(int, userLines[2].split(':')[1].split(','))

		self.filename = "user" + self.userId

		#randomize width and distance arrays order
		random.shuffle(self.widths)
		random.shuffle(self.distances)


	def __init__(self):
		super(ClickRecorder, self).__init__()
		self.requestFileName()
		self.readTestSetup()
		self.initUI()
		self.initUser()
		self.setupCircles()
		self.setupTimer()
		self.setupLogging()
		self.setupTrial()


	def setupLogging(self):
		if os.path.exists(self.filename + ".csv"):
			return
		else:
			with open(self.filename + ".csv", "a") as logfile:
				output = csv.DictWriter(logfile, ["UserID", "Width", "Distance", "Timestamp", "Movements", "Errors"],
					delimiter=';')
				output.writeheader()


	def setupCircles(self):
		self.circles = []
		self.currentCircle = None

		#height is constant for all tests
		constHeight = 150

		#get circle values for this trial. start at index 0
		width 		= self.widths[self.trialsCount]
		distance 	= self.distances[self.trialsCount]

		marginleft = int((1100 - (distance)) / 2)

		#create circle and add to current two-element circle array
		self.circles.append(Circle(width, marginleft, constHeight))
		self.circles.append(Circle(width, marginleft + distance, constHeight))


	def setupTimer(self):
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.timeUp)


	def setupTrial(self):
		self.movements = 0
		self.errors = 0
		self.isReady = False


	def initUser(self):
		self.trialsCount = 0


	def initUI(self):
		self.setGeometry(0, 0, 1100, 400)
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
		if self.trialsCount > 3:
			pass
		else:
			self.drawCircles(event, qp)
			self.drawState(event, qp)
		qp.end()


	def mousePressEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			if self.isReady == False and not self.timer.isActive():
				return

			if self.timer.isActive() == False:
				print "Start timer"
				self.timer.start(1000 * 60)

			for circle in self.circles:
				if circle.isClicked(event.pos()) == True:
					if self.currentCircle == None:
						print "Start position"
						self.currentCircle = circle
						return
					elif circle != self.currentCircle:
						print "Correct start to target movement"
						self.currentCircle = circle
						self.movements += 1
						return
					else:
						self.currentCircle = circle
						self.errors += 1
						return

			if self.currentCircle != None:
				print "Click out of boundaries"
				self.errors += 1

			self.currentCircle = None


	def drawCircles(self, event, qp):
		for circle in self.circles:
			circle.drawCircle(event, qp)


	def drawState(self, event, qp):
		qp.setPen(QtGui.QColor(80, 80, 80))
		qp.setFont(QtGui.QFont('Decorative', 24))
		if self.isReady:
			qp.drawText(event.rect(), QtCore.Qt.AlignBottom, "Ready")
		else:
			qp.drawText(event.rect(), QtCore.Qt.AlignBottom, "Not ready")


	def keyPressEvent(self, ev):
		if ev.key() == QtCore.Qt.Key_Space:
			if self.timer.isActive():
				return
			else:
				self.isReady = not self.isReady
				self.update()


	def timeUp(self):
		self.timer.stop()
		self.logResults()
		self.resetTrial()


	def resetTrial(self):
		self.isReady = False
		self.movements = 0
		self.errors = 0
		self.trialsCount += 1
		self.setupCircles()
		self.update()


	def logResults(self):
		with open(self.filename + ".csv", "a") as logfile:
			timestamp = datetime.datetime.now().strftime("%I:%M%p")
			data = {
				"UserID": self.userId,
				"Width": self.widths[self.trialsCount],
				"Distance": self.distances[self.trialsCount],
				"Timestamp": timestamp,
				"Movements": self.movements,
				"Errors": self.errors
			}
			output = csv.DictWriter(logfile, ["UserID", "Width", "Distance", "Timestamp", "Movements", "Errors"])
			output.writerow(data)


	def closeEvent(self, event):
		event.accept()


def main():
	app = QtGui.QApplication(sys.argv)
	click = ClickRecorder()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
