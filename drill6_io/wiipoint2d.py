#!/usr/bin/env python

import time
import sys
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
import pyqtgraph
import pyqtgraph as pg
import numpy as np
from PyQt4 import QtGui, QtCore

import wiimote_node

def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    while True:
        demo.update()

        time.sleep(0.20)

    sys.exit(app.exec_())


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()
        print 'super'
        self.setWindowTitle("Pointing Device")
        self.show()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        fc = Flowchart(terminals={
        	'dataIn': {'io': 'in'},
        	'dataOut': {'io': 'out'}
    	})
    	#w = fc.widget()

    	self.layout.addWidget(fc.widget(), 0, 0, 2, 1)

        pw1 = pg.PlotWidget()
        self.layout.addWidget(pw1, 0, 1)
        pw1.setYRange(0,1024)

        pw2 = pg.PlotWidget()
        self.layout.addWidget(pw2, 1, 1)
        pw2.setYRange(0,1024)

        pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
        pw1Node.setPlot(pw1)

        pw2Node = fc.createNode('PlotWidget', pos=(0, 150))
        pw2Node.setPlot(pw2)

        self.wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
        bufferNodeX = fc.createNode('Buffer', pos=(150, 0))
        bufferNodeY = fc.createNode('Buffer', pos=(300, 0))

        fc.connectTerminals(self.wiimoteNode['irX'], bufferNodeX['dataIn'])
        fc.connectTerminals(self.wiimoteNode['irY'], bufferNodeY['dataIn'])
        fc.connectTerminals(bufferNodeX['dataOut'], pw1Node['In'])
        fc.connectTerminals(bufferNodeY['dataOut'], pw2Node['In'])
        print 'connected'

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

    def update(self):
    	print 'update'
        if self.wiimoteNode.wiimote is None:
        	#print 'None'
            return
        if self.wiimoteNode.wiimote.buttons['Plus']:
        	print 'Plus'
            #pass
        elif self.wiimoteNode.wiimote.buttons['Minus']:
        	print 'Minus'
            #pass
        else:
        	print 'else'
            #pass
        pyqtgraph.QtGui.QApplication.processEvents()

if __name__ == "__main__":
    main()
