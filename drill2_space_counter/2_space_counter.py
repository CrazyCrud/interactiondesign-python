#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore

class ClickRecorder(QtGui.QWidget):
    
    def __init__(self):
        super(ClickRecorder, self).__init__()
        self.counter = 0
        self.initUI()
        
    def initUI(self):      
        self.text = "Please press 'space' repeatedly."
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('ClickRecorder')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Space:
            self.counter += 1
            self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        self.drawRect(event, qp) 
        qp.end()
        
    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        if self.counter > 0:
             self.text = str(self.counter)
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)        
    
    def drawRect(self, event, qp):
        if (self.counter % 2) == 0:
             rect = QtCore.QRect(10,10, 30,30)
             qp.setBrush(QtGui.QColor(34, 34, 200))
        else:
             rect = QtCore.QRect(40,10, 30,30)
             qp.setBrush(QtGui.QColor(200, 34, 34))
        qp.drawRoundRect(rect)        
        
def main():
    app = QtGui.QApplication(sys.argv)
    click = ClickRecorder()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
