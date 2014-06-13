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
import math


def main():
    app = QtGui.QApplication(sys.argv)

    #wm = getWiimote()
    demo = Demo()
    demo.show()

    while True:
        demo.update()
        time.sleep(0.05)

    sys.exit(app.exec_())


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Pointing Device")
        self.show()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.buffer_amount = 20

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
        gview = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
        self.layout.addWidget(gview, 0, 1, 2, 1)

        plot = gview.addPlot()
        self.scatter = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        plot.addItem(self.scatter)
        plot.setXRange(-1000, 200)
        plot.setYRange(-1000, 200)

        self.pointVisNode = self.fc.createNode('Vis3D', pos=(-150, 150))
        self.wiimoteNode = self.fc.createNode('Wiimote', pos=(0, 0), )
        self.bufferNode = self.fc.createNode('Buffer', pos=(0, -150))

        self.fc.connectTerminals(self.wiimoteNode['irVals'], self.bufferNode['dataIn'])
        self.fc.connectTerminals(self.bufferNode['dataOut'], self.pointVisNode['irVals'])

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

    def update(self):
        outputValues =  self.pointVisNode.outputValues()

        if outputValues['irX1'] is not None and outputValues['irY1'] is not None:
            if outputValues['irX2'] is not None and outputValues['irY2'] is not None:
                distance = self.calcDistance(outputValues)
                #
                if distance > 0:
                    print distance
                    size = 1000 * (1 / distance)
                    print size
                    self.scatter.setData(pos=[[-outputValues['irX1'], -outputValues['irY1']], [-outputValues['irX2'], -outputValues['irY2']]],
                    size=size, pxMode=True)

        # raise or lower buffer amount with +/- keys
        if self.wiimoteNode.wiimote is not None:
            if self.wiimoteNode.wiimote.buttons['Plus']:
                self.buffer_amount += 1
                self.bufferNode.setBufferValue(self.buffer_amount)
                print 'plus'
            elif self.wiimoteNode.wiimote.buttons['Minus']:
                if self.buffer_amount > 1:
                    self.buffer_amount -= 1
                    self.bufferNode.setBufferValue(self.buffer_amount)
                    print'minus'

        pyqtgraph.QtGui.QApplication.processEvents()

    def calcDistance(self, outputValues):
        x1 = outputValues['irX1']
        y1 = outputValues['irY1']
        x2 = outputValues['irX2']
        y2 = outputValues['irY2']

        #print "(%d, %d, %d, %d)"%(x1, y1, x2, y2)
        hfov = 41
        vfov = 31
        lightDistance = 30#cm
        fov = ((hfov/1024.0) + (vfov/768.0)) / 2.0

        r = math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))

        alpha = (fov * r) / 4.0

        tan = math.tan(math.radians(alpha))

        try:
            camDistance = lightDistance / (2 * tan)
        except:
            camDistance = 0 
        return camDistance

if __name__ == "__main__":
    main()
