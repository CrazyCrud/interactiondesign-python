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

    demo = Demo()
    demo.show()

    while True:
        demo.update()

    sys.exit(app.exec_())


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Pointing Device")
        self.show()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.buffer_amount = 32

        self.fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })
        self.layout.addWidget(self.fc.widget(), 0, 0, 2, 1)
        self.usePlotWidget()

        self.getWiimote()

    def getWiimote(self):
        if len(sys.argv) == 1:
            addr, name = wiimote.find()[0]
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
        print("Connecting to %s (%s)" % (name, addr))

        self.wiimoteNode.text.setText(addr)
        self.wiimoteNode.connect_wiimote()

    def usePlotWidget(self):
        gview = pg.GraphicsLayoutWidget()
        self.layout.addWidget(gview, 0, 1, 2, 1)
        plot = gview.addPlot()
        self.scatter = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        plot.addItem(self.scatter)

        self.pointVisNode = self.fc.createNode('Vis2D', pos=(-150, 150))
        self.wiimoteNode = self.fc.createNode('Wiimote', pos=(0, 0), )
        self.bufferNode = self.fc.createNode('Buffer', pos=(0, -150))

        self.fc.connectTerminals(
            self.wiimoteNode['irVals'], self.bufferNode['dataIn'])
        self.fc.connectTerminals(
            self.bufferNode['dataOut'], self.pointVisNode['irVals'])

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

    def update(self):
        outputValues = self.pointVisNode.outputValues()

        if outputValues['irX'] is not None and outputValues['irY'] is not None:
            self.scatter.setData(
                pos=[[-outputValues['irX'], -outputValues['irY']]])

        if self.wiimoteNode.wiimote is not None:
            if self.wiimoteNode.wiimote.buttons['Plus']:
                self.buffer_amount += 1
                self.bufferNode.setBufferValue(self.buffer_amount)
            elif self.wiimoteNode.wiimote.buttons['Minus']:
                if self.buffer_amount > 1:
                    self.buffer_amount -= 1
                    self.bufferNode.setBufferValue(self.buffer_amount)

        pyqtgraph.QtGui.QApplication.processEvents()

if __name__ == "__main__":
    main()
