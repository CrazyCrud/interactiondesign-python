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
    pygame.quit()
    sys.exit(app.exec_())
    sys.exit()


class Display:
    def __init__(self):
        # initialize the pygame module
        pygame.init()

        # create a surface on screen that has the size of 240 x 180
        self.screen = pygame.display.set_mode((1000, 700))

        self.initImages()

        self.pointerCombis = [('', ''), ('', '')]

        self.pointerColors = [(0, 0, 255), (255, 0, 0)]

        self.pinchIds = []
        self.ignoreIds = []
        self.combiRadius = 200
        self.pinchRadius = 50

        self.lastPinchPositions = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}

        self.myfont = pygame.font.SysFont("monospace", 15)


    def initImages(self):
        # load and set the logo
        pygame.display.set_caption("2HandsInteraction")

        self.bgd_image = pygame.image.load("backgr.jpg")
        self.screen.blit(self.bgd_image, (0, 0))

        self.images = [
            ImageObject('sugar.jpg', 0, (0, 100), self.screen),
            ImageObject('water.jpg', 0, (100, 300), self.screen),
            ImageObject('penguins.jpg', 0, (350, 150), self.screen)
        ]

    def updatePointers(self):
        self.smallestDistances = [100000, 100000]
        self.distances = [0, 0, 0]
        self.combiIds = [[-1, -1], [-1, -1]]

        self.distances = []
        self.pinchIds = []
        self.combiIds = []
        self.ignoreIds = []

        # collect ids of pointers in an array
        self.pointerIds = [x for x in range(0, self.pointersCount)]

        self.checkCombis()

        self.checkPinches()

        # adjust pointer values for displaying on screen
        for key in self.pointerVals:
            if self.pointerVals[key] is not None:
                if 'X' in key:
                    self.pointerVals[key] = (1000-self.pointerVals[key])
                if 'Y' in key:
                    self.pointerVals[key] = (700-self.pointerVals[key])

        radius = 9

        # check all pointer values for None
        for i in range(0, self.pointersCount):
            if i in self.ignoreIds:
                # don't draw circle if it shall be ignored
                print 'ignore' + str(i)
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
        if self.pointersCount == 1:
            self.combiIds = [[0]]
        elif self.pointersCount >= 2:
            # check distance between pointer 1 and the others
            for pointerId in range(1, self.pointersCount):
                distance = self.calcDistance(0, pointerId)
                self.distances.append(distance)

        nearestId = 0
        smallestDist = -1

        for i in range(len(self.distances)):
            #print 'get nearestId'
            if smallestDist == -1 or smallestDist > self.distances[i]:
                #print 'if check'
                smallestDist = self.distances[i]
                # mark id of nearest pointer, adjust index by adding 2
                nearestId = i+1

        if self.pointersCount == 4:
            #if smallestDist < combiRadius:
                # define first combi ids
                firstCombi = [0, nearestId]
                # define second combi ids by selecting the remaining ids
                secondCombi = self.getRemainingPointerIds([0, nearestId])

                self.combiIds = [firstCombi, secondCombi]
        elif self.pointersCount == 3:
            if smallestDist < self.combiRadius:
                # define only one combi
                self.combiIds = [[0, nearestId], self.getRemainingPointerIds([0, nearestId])]
                #self.pinchIds = self.getRemainingPointerIds([1, nearestId])
            elif smallestDist >= self.combiRadius:
                # define only one combi
                self.combiIds = [self.getRemainingPointerIds([1])]
                #self.pinchIds = [0, nearestId]
        #elif self.pointersCount == 2:
        #    if smallestDist < self.combiRadius:
        #       self.combiIds = [[0, nearestId]]

    def checkPinches(self):
        for combiId in self.combiIds:
            distance = self.calcDistance(combiId[0], combiId[1])
            # if distance is small enough combine ids to pinch
            if distance < self.pinchRadius:
                self.pinchIds = [combiId[0], combiId[1]]

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

            #print self.pinchIds
        elif self.pointersCount == 1:
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

    # basic loop method. parameter is the array of pointer x/y values
    def update(self, pointerValues):
        self.pointerVals = pointerValues
        self.pointersCount = len(self.pointerVals)/2

        self.updateImages()

        self.updatePointers()

        pygame.display.flip()

    def getPointerVal(self, axis, pointerId):
        return self.pointerVals['ir' + axis + str(pointerId)]

    def updateImages(self):
        self.screen.blit(self.bgd_image, (0, -150))
        for image in self.images:
            for pinchId in self.pinchIds:
                if self.checkPinchIsOverImg(image, pinchId) is 1:
                    self.checkImgPosition(image, pinchId)
                    self.checkImgRotation(image)
                    self.checkImgScale(image)
            image.draw()
            #pygame.draw.rect(self.screen, (0, 255, 255), image.rect)

        '''
        surface = pygame.Surface((200, 200))
        rect = pygame.Rect(200, 200, 200, 200)
        rect = pygame.draw.rect(self.screen, (0, 255, 0), rect)

        self.drawCircle((0, 255, 255), 250, 250, 4)


        isColliding = rect.collidepoint(250, 250)
        print isColliding'''


    # check if a pinch gesture is done over an image's rectangle
    def checkPinchIsOverImg(self, image, pinchId):
        #print 'checkPinchIsOverImg'
        x = self.getPointerVal('X', pinchId)
        y = self.getPointerVal('Y', pinchId)
        isColliding = 0

        if x is not None and y is not None:
            isColliding = image.rect.collidepoint(x, y)
            #else:
            #    print 'is not Colliding'
        return isColliding

    def printWithNr(self, text, nr):
        print text + str(nr)

    def checkImgRotation(self, image):
        # todo: rotate img if pinches are done over the image (compare with last pinch positions)
        x = 1+1

    def checkImgPosition(self, image, pinchId):
        lastPinchPosX = self.lastPinchPositions[pinchId][0] #200
        lastPinchPosY = self.lastPinchPositions[pinchId][1] #200

        newPinchPosX = self.getPointerVal('X', pinchId) #220
        newPinchPosY = self.getPointerVal('Y', pinchId) #220

        if lastPinchPosX != 0 and lastPinchPosY != 0:
            diffPinchX = lastPinchPosX - newPinchPosX #20
            diffPinchY = lastPinchPosY - newPinchPosY #20

            print 'diffPinchX: ' + str(diffPinchX) + ' ' + str(diffPinchY)
            #newImagePosX = image.pos[0] - diffPinchX
            #newImagePosY = image.pos[1] - diffPinchY

            image.move(diffPinchX, diffPinchY)

        self.lastPinchPositions[pinchId] = (newPinchPosX, newPinchPosY)
        '''
        for pinchId in self.pinchIds:
            lastX = self.getPointerVal('X', pinchId)
            lastX = self.getPointerVal('Y', pinchId)
            self.lastPinchPositions[pinchId] = (x, y)'''

    def checkImgScale(self, image):
        # todo: scale img if pinches are done over the image (compare with last pinch position)
        x = 1+1

    def normalizeDisplayValues(self, values):
        values = values / len(values)
        return values * 700


class ImageObject:
    def __init__(self, fileName, myId, pos, screen):
        '''
        self.images = {
            0: {'obj': None, 'img': pygame.image.load("sugar.jpg"), 'posX': 200,
                'posY': 100, 'angle': 0.0, 'scale': 1.0},
            1: {'obj': None, 'img': pygame.image.load("water.jpg"), 'posX': 500,
                'posY': 300, 'angle': 0.0, 'scale': 1.0},
            2: {'obj': None, 'img': pygame.image.load("penguins.jpg"), 'posX': 800,
                'posY': 150, 'angle': 0.0, 'scale': 1.0}
        }'''

        self.id = myId
        self.image = pygame.image.load(fileName)
        self.rect = self.image.get_rect()
        self.pos = pos
        #self.surface = self.image.convert()
        #self.rect.move_ip(pos[0], pos[1])
        self.scale = 1.0
        self.angle = 1.0
        self.src = pygame.image.load(fileName)
        self.screen = screen
        self.move(pos[0], pos[1])

    def draw(self):
        self.screen.blit(self.src, (self.pos[0], self.pos[1]))

    def move(self, posX, posY):
        self.rect.move_ip(posX, posY)
        self.pos = (self.rect.left, self.rect.top)

    def rotate(self):
        #self.
        x = 2

    def scale(self):
        x=1

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
                'irX0': 500, 'irY0': 200,
                'irX1': 550, 'irY1': 220,
                'irX2': 500, 'irY2': 500,
                'irX3': 600, 'irY3': 600
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
