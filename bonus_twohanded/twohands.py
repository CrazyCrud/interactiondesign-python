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

    useWiiMote = True

    pointer = Pointer(useWiiMote)
    display = Display()

    running = True
    # main loop
    while running:
        pointer.update()
        display.update(pointer.outputValues)
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
        time.sleep(0.02)

    # quit
    pygame.quit()
    sys.exit(app.exec_())
    sys.exit()


class Display:
    '''
    This class handles drawing of images and circles,
    interpretes all pointers' combinations, pinches,
    gestures and handles transformations.
    '''
    def __init__(self):
        # initialize the pygame module
        pygame.init()

        # create a surface on screen that has the size of 240 x 180
        self.screen = pygame.display.set_mode((1000, 600))

        self.initImages()

        self.pointerCombis = [('', ''), ('', '')]

        self.pointerColors = [(0, 0, 255), (255, 0, 0)]

        self.pinchIds = []
        self.ignoreIds = []
        self.combiRadius = 200
        self.pinchRadius = 50

        self.lastPinchPositions = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}

        self.myfont = pygame.font.SysFont("monospace", 15)

        self.updateCounter = 0

    # load backgr image and image objects
    def initImages(self):
        pygame.display.set_caption("2HandsInteraction")

        self.bgd_image = pygame.image.load("backgr.jpg")
        self.screen.blit(self.bgd_image, (0, 0))

        self.images = [
            ImageObject('sugar.jpg', 0, (20, 100), (260, 260), self.screen),
            ImageObject('water.jpg', 0, (100, 300), (260, 260), self.screen),
            ImageObject('penguins.jpg', 0, (350, 150), (260, 260), self.screen)
        ]

    # basic loop method. parameter is the array of pointer x/y values
    def update(self, pointerValues):
        #print pointerValues
        self.updateCounter += 1

        self.pointerVals = pointerValues

        self.pointersCount = 0
        for key in self.pointerVals:
            if 'X' in key and self.pointerVals[key] is not None:
                self.pointersCount += 1

        self.adjustPointerValues()

        self.updateImages()

        self.updatePointers()

        pygame.display.flip()

    # adjust pointer values for displaying on screen
    def adjustPointerValues(self):
        for key in self.pointerVals:
            if self.pointerVals[key] is not None:
                if 'X' in key:
                    self.pointerVals[key] = (1000-self.pointerVals[key])
                if 'Y' in key:
                    self.pointerVals[key] = (600-self.pointerVals[key])

    # read pointer values and handle actions based on those,
    # including drawing
    def updatePointers(self):
        self.distances = []
        self.pinchIds = []
        self.combiIds = []
        self.ignoreIds = []

        # collect ids of pointers in an array
        self.pointerIds = [x for x in range(0, self.pointersCount)]

        self.checkCombis()

        self.checkPinches()

        radius = 9

        # check all pointer values for None
        for i in range(0, self.pointersCount):
            if i in self.ignoreIds:
                # don't draw circle if it shall be ignored
                continue
            color = (255, 255, 255)
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
                self.getPointerVal('X', i),
                self.getPointerVal('Y', i),
                radius, i)

    # check which combis can be created respecting the distance.
    # check this by comparing pointer 1 with the others and respecting
    # the count of pointers
    def checkCombis(self):
        if self.pointersCount >= 2:
            # check distance between pointer 1 and the others
            for pointerId in range(1, self.pointersCount):
                distance = self.calcDistance(0, pointerId)
                self.distances.append(distance)

        nearestId = 0
        smallestDist = -1

        for i in range(len(self.distances)):
            if smallestDist == -1 or smallestDist > self.distances[i]:
                smallestDist = self.distances[i]
                # mark id of nearest pointer, adjust index by adding 2
                nearestId = i+1

        if self.pointersCount == 4:
            # define first combi ids
            firstCombi = [0, nearestId]
            # define second combi ids by selecting the remaining ids
            secondCombi = self.getRemainingPointerIds([0, nearestId])

            self.combiIds = [firstCombi, secondCombi]
        elif self.pointersCount == 3:
            if smallestDist < self.combiRadius:
                # define only one combi
                self.combiIds = [[0, nearestId]]
            elif smallestDist >= self.combiRadius:
                # define only one combi
                self.combiIds = [self.getRemainingPointerIds([1])]

    # check if pointers are close enough for pinches
    def checkPinches(self):
        if self.pointersCount == 3:
            # interprete the one point that is not in a combination as pinch
            self.pinchIds.append(self.getRemainingPointerIds(self.combiIds)[0])
        elif self.pointersCount == 2:
            distance = self.calcDistance(self.pointerIds[0], self.pointerIds[1])
            # if the two pointers are very near to another interprete
            # them as one pinch and ignore one of both pointers
            if distance < self.pinchRadius:
                self.pinchIds = [self.pointerIds[0]]
                self.ignoreIds = [self.pointerIds[1]]
            # if the two pointers aren't near enough interprete them as separate
            # pinches
            else:
                self.pinchIds = [self.pointerIds[0], self.pointerIds[1]]
        elif self.pointersCount == 1:
            # only one pointer -> pinch
            self.pinchIds = [0]

    # calculate distance between points using pythagoras
    def calcDistance(self, firstPointerId, secondPointerId):
        # read x/y values
        x1 = self.getPointerVal('X', firstPointerId)
        x2 = self.getPointerVal('X', secondPointerId)
        y1 = self.getPointerVal('Y', firstPointerId)
        y2 = self.getPointerVal('Y', secondPointerId)

        # pseudo distance which will be overwritten or ignored
        a = b = 100000

        if x1 is not None and x2 is not None and \
           y1 is not None and y2 is not None:
            a = x1-x2
            b = y1-y2

        distance = math.sqrt(math.pow(a, 2) + math.pow(b, 2))

        return distance

    # draw circle by color, position and radius parameters
    def drawCircle(self, color, xPos, yPos, radius, nr):
        if xPos is not None and yPos is not None:
            pygame.draw.circle(self.screen, color, (int(xPos), int(yPos)), radius, 0)

            # render text
            label = self.myfont.render(str(nr), 3, (255, 255, 255))
            self.screen.blit(label, (xPos-5, yPos-5))

    # return pointer ids which are not in the given array usedIds
    def getRemainingPointerIds(self, usedIds):
        return [x for x in self.pointerIds if x not in usedIds]

    # return pointer coordinate for one axis
    def getPointerVal(self, axis, pointerId):
        return self.pointerVals['ir' + axis + str(pointerId)]

    # transform and draw images due to pinch gestures
    def updateImages(self):
        self.screen.blit(self.bgd_image, (0, -150))

        for image in self.images:
            # with two pinches enable rotation and scaling
            if len(self.pinchIds) == 2:
                id1 = self.pinchIds[0]
                id2 = self.pinchIds[1]
                if self.checkPinchIsOverImg(image, id1) is 1 and \
                   self.checkPinchIsOverImg(image, id2) is 1:
                    self.calcMultiPinchDiff(id1, id2)
                    self.checkImgRotozoom(image)
            # with only one pinch enable only movement
            elif len(self.pinchIds) == 1:
                if self.checkPinchIsOverImg(image, self.pinchIds[0]) is 1:
                    self.calcSinglePinchDiff(self.pinchIds[0])
                    self.checkImgPosition(image, self.pinchIds[0])
            image.draw()

    # check if a pinch gesture is done over an image's rectangle
    def checkPinchIsOverImg(self, image, pinchId):
        x = self.getPointerVal('X', pinchId)
        y = self.getPointerVal('Y', pinchId)
        isColliding = 0

        if x is not None and y is not None:
            isColliding = image.rect.collidepoint(x, y)
        return isColliding

    # print helper method
    def printWithNr(self, text, nr):
        x = 1
        #print text + str(nr)

    # calc difference between old and new pinch positions
    def calcMultiPinchDiff(self, pinchId1, pinchId2):
        self.diffNewX = 0
        self.diffNewY = 0
        self.diffLastX = 0
        self.diffLastY = 0

        lastPinchPosX1 = self.lastPinchPositions[pinchId1][0]
        lastPinchPosY1 = self.lastPinchPositions[pinchId1][1]
        lastPinchPosX2 = self.lastPinchPositions[pinchId2][0]
        lastPinchPosY2 = self.lastPinchPositions[pinchId2][1]

        newPinchPosX1 = self.getPointerVal('X', pinchId1)
        newPinchPosY1 = self.getPointerVal('Y', pinchId1)
        newPinchPosX2 = self.getPointerVal('X', pinchId2)
        newPinchPosY2 = self.getPointerVal('Y', pinchId2)

        # update 'last' positions for next call
        self.lastPinchPositions[pinchId1] = (newPinchPosX1, newPinchPosY1)
        self.lastPinchPositions[pinchId2] = (newPinchPosX2, newPinchPosY2)

        self.diffNewX = newPinchPosX1 - newPinchPosX2
        self.diffNewY = newPinchPosY1 - newPinchPosY2
        self.diffLastX = lastPinchPosX1 - lastPinchPosX2
        self.diffLastY = lastPinchPosY1 - lastPinchPosY2

    # calc difference between old and new pinch position
    def calcSinglePinchDiff(self, pinchId):
        lastPinchPosX = self.lastPinchPositions[pinchId][0]
        lastPinchPosY = self.lastPinchPositions[pinchId][1]

        newPinchPosX = self.getPointerVal('X', pinchId)
        newPinchPosY = self.getPointerVal('Y', pinchId)

        self.diffPinch = (0, 0)

        # calc diff only if pointers are't out of the screen
        if lastPinchPosX != 0 and lastPinchPosY != 0 and \
           newPinchPosX < 1000 and newPinchPosY < 600:
            self.diffPinch = (lastPinchPosX - newPinchPosX, lastPinchPosY - newPinchPosY)

        self.lastPinchPositions[pinchId] = (newPinchPosX, newPinchPosY)

    # move image by difference
    def checkImgPosition(self, image, pinchId):
        image.move(-self.diffPinch[0], -self.diffPinch[1])

    # rotate and scale image
    # src for forms: http://mmi.capira.de/?p=102
    def checkImgRotozoom(self, image):
        # scale img if pinches are done over the image
        scaleDiff = 1.0

        topSum = (self.diffNewX**2+self.diffNewY**2)
        lowSum = (self.diffLastX**2+self.diffLastY**2)

        # scale
        if lowSum > 0:
            scaleDiff = math.sqrt(topSum/float(lowSum))
            #scaleDiff = 1.0
            #scale = image.rect.width - (image.rect.width - scaleDiff)

        # rotate
        angleDiff = 0.0
        if self.diffNewX > 0:
            angleDiff = math.atan2(self.diffNewY, self.diffNewX) -\
                math.atan2(self.diffLastY, self.diffLastX)
            angleDiff = angleDiff * 180.0 / math.pi

        image.rotozoom(angleDiff, scaleDiff)

    def normalizeDisplayValues(self, values):
        values = values / len(values)
        return values * 600


class ImageObject:
    '''
    This class represents the images as objects and provides
    transformation methods for that. It also stores all
    relevant image values.
    '''
    def __init__(self, fileName, myId, pos, size, screen):
        self.id = myId
        self.image = pygame.image.load(fileName)
        self.fileName = fileName
        self.surface = self.image.convert_alpha()
        self.rect = self.surface.get_rect()
        self.pos = pos
        self.scale = 1.0
        self.angle = 0.0
        self.size = size
        self.screen = screen
        self.move(pos[0], pos[1])

    def draw(self):
        self.screen.blit(self.surface, (self.rect.left, self.rect.top))

    def move(self, diffX, diffY):
        self.rect.move_ip(diffX, diffY)
        self.pos = (self.rect.left, self.rect.top)

    # rotate and scale an image while keeping its center and size
    def rotozoom(self, angleDiff, scaleDiff):
        self.scale *= scaleDiff
        self.angle -= angleDiff

        oldSurfaceX = self.surface.get_width()
        oldSurfaceY = self.surface.get_height()

        cachedImage = pygame.transform.rotozoom(
            self.image,
            self.angle,
            self.scale)

        self.surface = cachedImage.convert_alpha()

        newSurfaceX = self.surface.get_width()
        newSurfaceY = self.surface.get_height()

        diffSurfaceX = newSurfaceX - oldSurfaceX
        diffSurfaceY = newSurfaceY - oldSurfaceY

        self.rect = self.surface.get_rect()

        # take only half
        newPosX = self.pos[0]-diffSurfaceX/2.0
        newPosY = self.pos[1]-diffSurfaceY/2.0

        self.move(newPosX, newPosY)


class Pointer(QtGui.QWidget):
    '''
    This class reads WiiMote IR data and provides
    them on output.
    '''
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

        self.outputCounter = 0

    # connect to wiimoet
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

        if self.useWiiMote is False:
            # use simulated data if WiiMote shall not
            # be used
            self.outputValues = {
                'irX0': 30, 'irY0': 120,
                'irX1': 40, 'irY1': 130,
                'irX2': 400, 'irY2': 400,
                'irX3': 410, 'irY3': 410
                }

            self.outputCounter = self.outputCounter + 2

            for key in self.outputValues:
                if 'X' in key:
                    self.outputValues[key] = self.outputValues[key] + self.outputCounter
                else:
                    self.outputValues[key] = self.outputValues[key] + self.outputCounter

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
