#!/usr/bin/env python

import time
import sys
from pyqtgraph.flowchart import Flowchart
import pyqtgraph
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
import wiimote
from wiimote_node import *
import math


def main():
    app = QtGui.QApplication(sys.argv)

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

        self.configNodes()
        self.configScatterPlot()

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

    # create and connect nodes
    def configNodes(self):
        self.pointVisNode = self.fc.createNode('Vis3D', pos=(-150, 150))
        self.wiimoteNode = self.fc.createNode('Wiimote', pos=(0, 0), )
        self.bufferNode = self.fc.createNode('Buffer', pos=(0, -150))

        self.buffer_amount = self.bufferNode.getBufferSize()

        self.fc.connectTerminals(
            self.wiimoteNode['irVals'],
            self.bufferNode['dataIn'])
        self.fc.connectTerminals(
            self.bufferNode['dataOut'],
            self.pointVisNode['irVals'])

    # create and config scatter plot item
    def configScatterPlot(self):
        gview = pg.GraphicsLayoutWidget()
        self.layout.addWidget(gview, 0, 1, 2, 1)

        plot = gview.addPlot()
        self.scatter = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        plot.addItem(self.scatter)
        plot.setXRange(-1000, 200)
        plot.setYRange(-1000, 200)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

    # do actions in loop
    def update(self):
        outputValues = self.pointVisNode.outputValues()

        isX1Valid = outputValues['irX1'] is not None
        isY1Valid = outputValues['irY1'] is not None
        isX2Valid = outputValues['irX2'] is not None
        isY2Valid = outputValues['irY2'] is not None

        if isX1Valid and isX2Valid and isY1Valid and isY2Valid:
            distance = self.calcDistance(outputValues)
            if distance > 0:
                size = 3000 * (1 / distance * 2)

                self.scatter.setData(
                    pos=[[
                        -outputValues['irX1'],
                        -outputValues['irY1']],
                        [-outputValues['irX2'], -outputValues['irY2']]],
                    size=size, pxMode=True)

        # raise or lower buffer amount with +/- keys
        if self.wiimoteNode.wiimote is not None:
            if self.wiimoteNode.wiimote.buttons['Plus']:
                self.buffer_amount += 1
                self.bufferNode.setBufferSize(self.buffer_amount)
            elif self.wiimoteNode.wiimote.buttons['Minus']:
                if self.buffer_amount > 1:
                    self.buffer_amount -= 1
                    self.bufferNode.setBufferSize(self.buffer_amount)

        pyqtgraph.QtGui.QApplication.processEvents()

    # calc distance from wiimote to the two lights
    # reference: http://wiiphysics.site88.net/physics.html
    def calcDistance(self, outputValues):
        x1 = outputValues['irX1']
        y1 = outputValues['irY1']
        x2 = outputValues['irX2']
        y2 = outputValues['irY2']

        # init wiimote's camera angles
        hfov = 41
        vfov = 31

        # set constant distance between the two lights
        lightDistance = 30

        fov = ((hfov / 1024.0) + (vfov / 768.0)) / 2.0

        r = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

        alpha = (fov * r) / 4.0

        tan = math.tan(math.radians(alpha))

        try:
            camDistance = lightDistance / (2 * tan)
        except:
            camDistance = 0
        return camDistance

if __name__ == "__main__":
    main()
