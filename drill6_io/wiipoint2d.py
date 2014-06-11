#!/usr/bin/env python

import time
import sys
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
import pyqtgraph
import pyqtgraph as pg
import numpy as np
from PyQt4 import QtGui, QtCore

import wiimote
import wiimote_node


def main():
    app = QtGui.QApplication(sys.argv)

    #wm = getWiimote()
    demo = Demo()
    demo.show()

    while True:
        demo.update()
        time.sleep(0.20)

    sys.exit(app.exec_())


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Pointing Device")
        self.show()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })
        self.layout.addWidget(self.fc.widget(), 0, 0, 2, 1)

        wm = self.getWiimote()

        self.usePlotWidget()

    def getWiimote(self):
        if len(sys.argv) == 1:
            addr, name = wiimote.find()[0]
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
        print("Connecting to %s (%s)" % (name, addr))
        self.wiimote_address = addr
        return wiimote.connect(addr, name)


    def usePlotWidget(self):
        pw1 = pg.PlotWidget()
        self.layout.addWidget(pw1, 0, 1)
        pw1.setYRange(0,1024)

        pw2 = pg.PlotWidget()
        self.layout.addWidget(pw2, 1, 1)
        pw2.setYRange(0,1024)

        pw1Node = self.fc.createNode('PlotWidget', pos=(0, -150))
        pw1Node.setPlot(pw1)

        pw2Node = self.fc.createNode('PlotWidget', pos=(0, 150))
        pw2Node.setPlot(pw2)

        self.wiimoteNode = self.fc.createNode('Wiimote', pos=(0, 0), )
        self.wiimoteNode.btaddr = self.wiimote_address
        self.wiimoteNode.text.setText(self.wiimote_address)

        bufferNodeX = self.fc.createNode('Buffer', pos=(150, 0))
        bufferNodeY = self.fc.createNode('Buffer', pos=(300, 0))

        self.fc.connectTerminals(self.wiimoteNode['irX'], bufferNodeX['dataIn'])
        self.fc.connectTerminals(self.wiimoteNode['irY'], bufferNodeY['dataIn'])
        self.fc.connectTerminals(bufferNodeX['dataOut'], pw1Node['In'])
        self.fc.connectTerminals(bufferNodeY['dataOut'], pw2Node['In'])

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

    def update(self):
        if self.wiimoteNode.wiimote is not None:
            print 'Not None'
            #return
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
