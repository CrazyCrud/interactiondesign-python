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

    useWiiMote = False
    pointer = Pointer(useWiiMote)
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

        self.pointerCombis = [('', ''), ('', '')]

        self.pointerColors = [(0, 0, 255), (255, 0, 0)]

        self.pinchIds = []
        self.combiRadius = 200
        self.pinchRadius = 50


    def initImages(self):
        # load and set the logo
        pygame.display.set_caption("2HandsInteraction")

        self.bgd_image = pygame.image.load("backgr.jpg")
        self.screen.blit(self.bgd_image, (0, -150))

        self.images = {
            0: {'obj': None, 'img': pygame.image.load("sugar.jpg"), 'posX': 200,
                'posY': 100, 'angle': 0.0, 'scale': 1.0},
            1: {'obj': None, 'img': pygame.image.load("water.jpg"), 'posX': 500,
                'posY': 300, 'angle': 0.0, 'scale': 1.0},
            2: {'obj': None, 'img': pygame.image.load("penguins.jpg"), 'posX': 800,
                'posY': 150, 'angle': 0.0, 'scale': 1.0}
        }

        for image in self.images.values():
            image['obj'] = ImageObject(image)

    def normalizeDisplayValues(self, values):
        values = values / len(values)
        return values * 700


    def updatePointers(self, pointerValues, pointersCount):
        self.smallestDistances = [100000, 100000]
        self.distances = [0, 0, 0]
        self.combiIds = [[-1, -1], [-1, -1]]

        self.distances = []
        self.pinchIds = []
        self.combiIds = []

        # collect ids of pointers in an array
        self.pointerIds = [x for x in range(1, pointersCount+1)]

        self.checkCombis(pointerValues, pointersCount)

        self.checkPinches(pointerValues, pointersCount)

        # adjust pointer values for displaying on screen
        for key in pointerValues:
            if pointerValues[key] is not None:
                if 'X' in key:
                    pointerValues[key] = (1200-pointerValues[key])
                if 'Y' in key:
                    pointerValues[key] = (700-pointerValues[key])

        radius = 9

        # check all pointer values for None
        for i in range(1, pointersCount+1):
            color = (0, 0, 0)
            if (len(self.combiIds) > 0 and i in self.combiIds[0]):
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



    # check which combis can be created respecting the distance.
    # check this by comparing pointer 1 with the others and respecting
    # the count of pointers
    def checkCombis(self, pointerValues, pointersCount):
        if pointersCount == 1:
            self.combiIds = [[1]]
        elif pointersCount >= 2:
            # check distance between pointer 1 and the others
            for pointerId in range(2, pointersCount+1):
                distance = self.calcDistance(pointerValues, 1, pointerId)
                self.distances.append(distance)

        nearestId = 0
        smallestDist = -1

        for i in range(len(self.distances)):
            #print 'get nearestId'
            if smallestDist == -1 or smallestDist > self.distances[i]:
                #print 'if check'
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
                self.combiIds = [[1, nearestId], self.getRemainingPointerIds([1, nearestId])]
                #self.pinchIds = self.getRemainingPointerIds([1, nearestId])
            elif smallestDist >= self.combiRadius:
                # define only one combi
                self.combiIds = [self.getRemainingPointerIds([1])]
                #self.pinchIds = [1, nearestId]
        elif pointersCount == 2:
            #if smallestDist < self.combiRadius:
            self.combiIds = [[1, nearestId]]
            #else:
                #self.pinchIds = [1, nearestId]

    def checkPinches(self, pointerValues, pointersCount):
        for combiId in self.combiIds:
            distance = self.calcDistance(pointerValues, combiId[0], combiId[1])
            # if distance is small enough combine ids to pinch
            if distance < self.pinchRadius:
                self.pinchIds = [combiId[0], combiId[1]]

        if pointersCount == 3:
            # interprete the one point that is not in a combination as pinch
            self.pinchIds.append(self.getRemainingPointerIds(self.combiIds)[0])
        elif pointersCount == 2:
            # check if the two pointers are in combination and if not interprete them
            # as pinch
            uncombinedPointerIds = self.getRemainingPointerIds(self.combiIds)
            for pointerId in uncombinedPointerIds:
                self.pinchIds.append(pointerId)
        elif pointersCount == 1:
            self.pinchIds = [1]

    # calculate distance between points using pythagoras
    def calcDistance(self, pointerValues, firstPointerId, secondPointerId):
        # read x/y values
        x1 = pointerValues['irX' + str(firstPointerId)]
        x2 = pointerValues['irX' + str(secondPointerId)]
        y1 = pointerValues['irY' + str(firstPointerId)]
        y2 = pointerValues['irY' + str(secondPointerId)]

        # pseudo distance which will be overwritten or ignored
        a = b = 100000

        if x1 is not None and x2 is not None and \
           y1 is not None and y2 is not None:
            a = x1-x2
            b = y1-y2

        distance = math.sqrt(math.pow(a, 2) + math.pow(b, 2))

        return distance

    # draw circle by color, position and radius parameters
    def drawCircle(self, color, xPos, yPos, radius):
        if xPos is not None and yPos is not None:
            pygame.draw.circle(self.screen, color, (int(xPos), int(yPos)), radius, 0)

    # return pointer ids which are not in the given array usedIds
    def getRemainingPointerIds(self, usedIds):
        return [x for x in self.pointerIds if x not in usedIds]


    def update(self, pointerValues):
        pointersCount = len(pointerValues)/2

        self.updatePointers(pointerValues, pointersCount)

        self.updateImages(pointerValues, pointersCount)

        pygame.display.flip()

    def updateImages(self, pointerValues, pointersCount):
        self.screen.blit(self.bgd_image, (0, -150))
        for image in self.images.values():
            self.checkImgRotation(pointerValues, pointersCount, image)
            self.checkImgPosition(pointerValues, pointersCount, image)
            self.checkImgScale(pointerValues, pointersCount, image)
            self.screen.blit(image['img'], (image['posX'], image['posY']))

    def checkImgRotation(self, pointerValues, pointersCount, image):
        # todo: rotate img if pinches are done over the image (compare with last pinch positions)
        x = 1+1

    def checkImgPosition(self, pointerValues, pointersCount, image):
        # todo: move positions if pinches are done over the image (compare with last pinch positions)
        image['posX'] = image['posX'] + 2
        image['obj'].move()

    def checkImgScale(self, pointerValues, pointersCount, image):
        # todo: scale img if pinches are done over the image (compare with last pinch position)
        x = 1+1

class ImageObject:
    def __init__(self, image):
        self.pos = image['img'].get_rect().move(image['posX'], image['posY'])

    def move(self):
        self.pos = self.pos.move(0, 20)
        if self.pos.right > 600:
            self.pos.left = 0

class Pointer(QtGui.QWidget):
    def __init__(self, useWiiMote, parent=None):
        super(Pointer, self).__init__()

        self.useWiiMote = useWiiMote

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.buffer_amount = 20

        self.fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })
        self.layout.addWidget(self.fc.widget(), 0, 0, 2, 1)

        self.configNodes()

        if self.useWiiMote:
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
        #print 'self.outputValues'
        #print self.outputValues

        if self.useWiiMote is False:
            self.outputValues = {
                'irX1': 200, 'irY1': 200,
                'irX2': 220, 'irY2': 220,
                'irX3': 500, 'irY3': 500,
                'irX4': 600, 'irY4': 600
                }

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



if __name__ == "__main__":
    main()
