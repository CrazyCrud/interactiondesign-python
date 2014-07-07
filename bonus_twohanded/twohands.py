#!/usr/bin/env python

import time
import sys
from pyqtgraph.flowchart import Flowchart
import pyqtgraph
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
import wiimote
from wiimote_node import *
import pygame


def main():
    app = QtGui.QApplication(sys.argv)

    pointer = Pointer()
    display = Display()

    running = True
    while running:
        pointer.update()
        display.update(pointer.outputValues)
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
        time.sleep(0.05)

    sys.exit(app.exec_())


class Display:
    def __init__(self):
        print 'display init'
        # initialize the pygame module
        pygame.init()

        # create a surface on screen that has the size of 240 x 180
        self.screen = pygame.display.set_mode((1200, 700))

        self.initImages()

        self.pointerKeys = [('irX1', 'irY1'), ('irX2', 'irY2')]

    def initImages(self):
        # load and set the logo
        #logo = pygame.image.load("water.jpg")
        #pygame.display.set_icon(logo)
        pygame.display.set_caption("minimal program")

        self.bgd_image = pygame.image.load("backgr.jpg")
        self.screen.blit(self.bgd_image, (0, -150))

    def update(self, pointerValues):
        self.screen.blit(self.bgd_image, (0, -150))

        # check all pointer values for None
        for posKeys in self.pointerKeys:
                self.drawCircle(
                    (0, 0, 255),
                    pointerValues[posKeys[0]],
                    pointerValues[posKeys[1]])
            #else:
                #pointerValues[key] = -pointerValues[key]
                #pointerValues[key] = pointerValues[key] / 600

            #self.drawCircle((255, 0, 0), pointerX2, pointerY2)
        pygame.display.flip()

    def drawCircle(self, color, xPos, yPos):
        if xPos is not None and yPos is not None:
            pygame.draw.circle(self.screen, color, (int(xPos), int(yPos)), 9, 0)


class Pointer(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Pointer, self).__init__()

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
        self.outputValues = self.pointVisNode.outputValues()

        '''
        isX1Valid = self.outputValues['irX1'] is not None
        isY1Valid = self.outputValues['irY1'] is not None
        isX2Valid = self.outputValues['irX2'] is not None
        isY2Valid = self.outputValues['irY2'] is not None

        if isX1Valid and isX2Valid and isY1Valid and isY2Valid:
            self.scatter.setData(
                pos=[[
                    -self.outputValues['irX1'],
                    -self.outputValues['irY1']],
                    [-self.outputValues['irX2'], -self.outputValues['irY2']]],
                size=10, pxMode=True)
        '''
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

    #def drawPoint(self):



if __name__ == "__main__":
    main()
