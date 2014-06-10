#!/usr/bin/env python

import time
import sys
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
import pyqtgraph
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
        self.setWindowTitle("Pointing Device")
        self.showFullScreen()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        pw1 = pg.PlotWidget()
        layout.addWidget(pw1, 0, 1)
        pw1.setYRange(0,1024)

        pw2 = pg.PlotWidget()
        layout.addWidget(pw2, 1, 1)
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

        self.getWiimote()

    def getWiimote():
        addr = ""
        if len(sys.argv) == 1:
            addr, name = wiimote.find()[0]
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
        self.wiimoteNode.text.setText(addr)
        self.wiimoteNode.connect_wiimote()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

    def update(self):
        if self.wiimoteNode.wiimote is None:
            return
        if self.wiimoteNode.wiimote.buttons['Plus']:
            pass
        elif self.wiimoteNode.wiimote.buttons['Minus']:
            pass
        else:
            pass
        pyqtgraph.QtGui.QApplication.processEvents()

if __name__ == "__main__":
    main()
