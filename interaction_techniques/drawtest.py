#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

This example draws three rectangles in three
different colors. 

author: Jan Bodnar
website: zetcode.com 
last edited: September 2011
"""

import sys
from PyQt4 import QtGui, QtCore
from threading import Timer


class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        self.setGeometry(300, 300, 350, 100)
        self.setWindowTitle('Colors')
        self.show()
        #arguments: 
        #how long to wait (in seconds), 
        #what function to call, 
        #what gets passed in
        r = Timer(1.0, self.twoArgs, ("arg1","arg2"))
        #s = Timer(2.0, self.nArgs, ("OWLS","OWLS","OWLS"))

        r.start()
        #s.start()
        self.width = 250

    def paintEvent(self, e):
        print "paintEvent"
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()
        
    def drawRectangles(self, qp):
        print "drawRectangles"

        self.icon = QtGui.QPixmap("icon.png")

        qp.setBrush(QtGui.QColor(255, 0, 0))
        #painter.setPen(qp)

        drawing_rect = QtCore.QRect(20, 20,
            self.width, 100)
        """
        painter.fillRect(drawing_rect, QtGui.QColor(255, 0, 0))
        painter.drawRect(drawing_rect)
        """
        #painter.drawPixmap(drawing_rect, self.icon)
        qp.drawPixmap(drawing_rect, self.icon)

    def twoArgs(self,arg1,arg2):
        print "update"
        self.width = 90
        self.update()

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



