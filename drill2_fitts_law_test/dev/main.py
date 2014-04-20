#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from circle import Circle
from PyQt4 import QtGui, QtCore

class ClickRecorder(QtGui.QWidget):

	def requestFileName(self):
		#self.fileName = raw_input("Please enter the file name including path containing descriptions for this test.")
		self.fileName = "../test/test_setup.txt"

	def readTestSetup(self):

		#read input
		with open(self.fileName) as f:
		#with open(self.fileName) as f:
			content = f.read()

		if not content:
			print 'File is empty'
		
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
		self.testCounter = 0
		self.clickCounter = 0
		self.initUI()
		self.requestFileName()
		self.readTestSetup()
	
		
	def initUI(self):
		self.text = "Click test"
		#set window size
		self.setGeometry(0, 0, 500, 300)
		self.setWindowTitle('Click test')
		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		self.show()

		circle1 = Circle()
		circle1.drawCircle()
'''
	def keyPressEvent(self, ev):
		if ev.key() == QtCore.Qt.Key_Space:
			self.counter += 1
			self.update()  
''' 
		
def main():
	app = QtGui.QApplication(sys.argv)
	click = ClickRecorder()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
