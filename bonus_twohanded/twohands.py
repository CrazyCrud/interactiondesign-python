#!/usr/bin/env python

import time
import sys
import math
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
    pygame.quit()
    sys.exit(app.exec_())
    sys.exit()


class Display:
    def __init__(self):
        # initialize the pygame module
        pygame.init()

        # create a surface on screen that has the size of 240 x 180
        self.screen = pygame.display.set_mode((1200, 700))

        self.initImages()

        self.pointerKeys = [
            ('irX1', 'irY1'), ('irX2', 'irY2'),
            ('irX3', 'irY3'), ('irX4', 'irY4')]

        #self.pointerCombis = [('ir1', 'ir2'), ('ir3', 'ir4')]
        self.pointerCombis = [('', ''), ('', '')]

        self.pointerColors = [(0, 0, 255), (255, 0, 0)]

        self.pinchIds = []
        self.combiRadius = 200

    def initImages(self):
        # load and set the logo
        #logo = pygame.image.load("water.jpg")
        #pygame.display.set_icon(logo)
        pygame.display.set_caption("2HandsInteraction")

        self.bgd_image = pygame.image.load("backgr.jpg")
        self.screen.blit(self.bgd_image, (0, -150))

    def update(self, pointerValues):
        self.screen.blit(self.bgd_image, (0, -150))
        self.smallestDistances = [100000, 100000]
        self.distances = [0, 0, 0]
        self.combiIds = [[-1, -1], [-1, -1]]

        self.distances = []
        self.pinchIds = []
        self.combiIds = []

        pointersCount = len(pointerValues)/2

        self.pointerIds = [x for x in range(1, pointersCount+1)]

        print 'pointersCount'
        print pointersCount
        if pointersCount == 1:
            self.pinchIds = 1
        elif pointersCount >= 2:
            for i in range(2, pointersCount+1):
                # read x/y values
                x1 = pointerValues['irX1']
                x2 = pointerValues['irX' + str(i)]
                y1 = pointerValues['irY1']
                y2 = pointerValues['irY' + str(i)]

                # calculate distance using pythagoras
                a = x1-x2
                b = y1-y2

                self.distances.append(math.sqrt(math.pow(a, 2) + math.pow(b, 2)))

        nearestId = 0
        smallestDist = -1

        print 'self.distances:'
        print self.distances

        for i in range(len(self.distances)):
            print 'get nearestId'
            if smallestDist == -1 or smallestDist > self.distances[i]:
                print 'if check'
                smallestDist = self.distances[i]
                # mark id of nearest pointer, adjust index by adding 2
                nearestId = i+2

        if pointersCount == 4:
            #if smallestDist < combiRadius:
            # define first combi ids
            firstCombi = [1, nearestId]
            # define second combi ids by selecting the remaining ids
            secondCombi = self.getRemainingPointerIds([1, nearestId])

            self.combiIds = [firstCombi, secondCombi]
        elif pointersCount == 3:
            if smallestDist < self.combiRadius:
                # define only one combi
                self.combiIds = [[1, nearestId]]
                self.pinchIds = self.getRemainingPointerIds([1, nearestId])
            elif smallestDist >= self.combiRadius:
                # define only one combi
                self.combiIds = [self.getRemainingPointerIds([1, nearestId])]
                self.pinchIds = [1, nearestId]
        elif pointersCount == 2:
            if smallestDist < self.combiRadius:
                self.combiIds = [[1, nearestId]]
                print '2: if smallestDist < self.combiRadius:'
                print self.combiIds
            else:
                self.pinchIds = [1, nearestId]
                print '2: else:'
                print self.pinchIds
        elif pointersCount == 1:
            self.pinchIds = [1]

        print 'combiIds:'
        print self.combiIds
        print 'pinchIds:'
        print self.pinchIds
        print 'nearestId:'
        print nearestId

        radius = 9
        # check all pointer values for None
        for i in range(1, pointersCount+1):
            color = (0, 0, 0)
            if (len(self.combiIds) > 0 and i in self.combiIds[0]) or \
               (len(self.pinchIds) > 0 and i in self.pinchIds[0]):
                color = self.pointerColors[0]
            else:
                color = self.pointerColors[1]

            if i in self.pinchIds:
                radius = 15
            else:
                radius = 9

            self.drawCircle(
                color,
                pointerValues['irX' + str(i)],
                pointerValues['irY' + str(i)],
                radius)

            #self.drawCircle((255, 0, 0), pointerX2, pointerY2)
        pygame.display.flip()

    # draw circle by color, position and radius parameters
    def drawCircle(self, color, xPos, yPos, radius):
        if xPos is not None and yPos is not None:
            pygame.draw.circle(self.screen, color, (int(xPos), int(yPos)), radius, 0)

    # return pointer ids which are not in the given array usedIds
    def getRemainingPointerIds(self, usedIds):
        return [x for x in self.pointerIds if x not in usedIds]


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

        #self.getWiimote()

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

        self.outputValues = {
            'irX1': 200, 'irY1': 200,
            'irX2': 300, 'irY2': 300#,
            #'irX3': 500, 'irY3': 500#,
            #'irX4': 600, 'irY4': 600
            }

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
