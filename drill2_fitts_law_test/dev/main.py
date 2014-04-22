#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import csv
from datetime import datetime
import random
import itertools
from circle import Circle
from PyQt4 import QtGui, QtCore


class ClickRecorder(QtGui.QWidget):

    def requestFileName(self):
        if len(sys.argv) < 2:
        #exit(0)
            self.fileName = "user1.txt"
        else:
            self.fileName = sys.argv[1]

    #read content of test setup file and calculate random
    def readTestSetup(self):
        #read input
        with open(self.fileName) as f:
        #with open(self.fileName) as f:
            content = f.read()

        if not content:
            print 'File is empty'
            exit(0)

        userLines = content.split()

        #split description and comma-separated values, take values
        #and convert to int
        self.userId = userLines[0].split(':')[1]
        widths = map(int, userLines[1].split(':')[1].split(','))
        distances = map(int, userLines[2].split(':')[1].split(','))

        self.filename = "user" + self.userId

        #calculate possible combinations of distances and widths
        self.distWidthCombis = list(itertools.product(distances, widths))
        print ",".join(map(str, self.distWidthCombis))

        #randomize order of combinations of distance and width
        random.shuffle(self.distWidthCombis)
        print ",".join(map(str, self.distWidthCombis))

    def __init__(self):
        super(ClickRecorder, self).__init__()
        self.requestFileName()
        self.readTestSetup()
        self.initUI()
        self.initUser()
        self.setupCircles()
        self.setupTimer()
        self.setupTrial()
        self.setupLogging()

    def setupCircles(self):
        self.circles = []
        self.currentCircle = None

        #height is constant for all tests
        constHeight = 150

        #get circle values for this trial. start at index 0
        width = self.distWidthCombis[self.trialsCount][1]
        distance = self.distWidthCombis[self.trialsCount][0]

        marginleft = int((1100 - (distance + width)) / 2)

        #create circle and add to current two-element circle array
        self.circles.append(Circle(width, marginleft, constHeight))

        #append width to distance so that the distance is related to the boundaries of the circles
        self.circles.append(Circle(width, marginleft + distance + width, constHeight))


    def setupTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timeUp)


    def setupTrial(self):
        self.movements = 0
        self.errors = 0
        self.isReady = False
        self.initPosX = 0
        self.initPosY = 0
        self.targetPosX = 0
        self.targetPosY = 0

    def initUser(self):
        self.trialsCount = 0


    def initUI(self):
        self.setGeometry(0, 0, 1100, 400)
        self.setWindowTitle("A Study about Fitts's Law")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.center()
        self.show()


    def center(self):
        res = QtGui.QDesktopWidget().screenGeometry()
        self.move((res.width() / 2) - (self.frameSize().width() / 2),
            (res.height() / 2) - (self.frameSize().height() / 2))


    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(qp.Antialiasing)
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(event.rect())
        if self.trialsCount > 3:
            pass
        else:
            self.drawCircles(event, qp)
            self.drawState(event, qp)
        qp.end()


    def mousePressEvent(self, event):       

        self.isCircleHit = False

        if event.button() == QtCore.Qt.LeftButton:

            if self.isReady == False and not self.timer.isActive():
                return

            if self.timer.isActive() == False:
                print "Start timer"
                self.timer.start(1000 * 5)#!!

            for i in range(len(self.circles)):
                circle = self.circles[i]
                #click is not inside a circle
                if circle.isClicked(event.pos()) == True:
                    self.isCircleHit = True

                    if self.currentCircle == None:
                        print "Start position"
                        self.currentCircle = circle
                    elif circle != self.currentCircle:
                        print "Correct start to target movement"
                        self.currentCircle = circle
                        self.movements += 1
                    else:
                        self.currentCircle = circle
                        self.addError()

                    self.initPosX = circle.center.x()
                    self.initPosY = circle.center.y()

                    self.targetPosX = circle.center.x()
                    self.targetPosY = circle.center.y()
                    print "self.initPosX : %d" % self.initPosX
                    print "self.initPosY : %d" % self.initPosY

            self.clickPosX = event.pos().x()
            self.clickPosY = event.pos().y()
            print "self.clickPosX : %d" % self.clickPosX
            print "self.clickPosY : %d" % self.clickPosY

            if self.isCircleHit == False:# and self.currentCircle != None:
                print "Click out of boundaries"
                self.addError()
                #self.currentCircle = None

            self.logResults()

    def addError(self):
        self.errors += 1
        print "errors +=1"

    def drawCircles(self, event, qp):
        for circle in self.circles:
            circle.drawCircle(event, qp)


    def drawState(self, event, qp):
        qp.setPen(QtGui.QColor(80, 80, 80))
        qp.setFont(QtGui.QFont('Decorative', 24))
        if self.isReady:
            qp.drawText(event.rect(), QtCore.Qt.AlignBottom, "Ready")
        else:
            qp.drawText(event.rect(), QtCore.Qt.AlignBottom, "Not ready")


    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Space:
            if self.timer.isActive():
                return
            else:
                self.isReady = not self.isReady
                self.lastTimestamp = datetime.now()
                self.update()


    def timeUp(self):
        self.timer.stop()
        #self.logResults()
        self.resetTrial()


    def resetTrial(self):
        self.isReady = False
        self.movements = 0
        self.errors = 0
        self.trialsCount += 1
        self.setupCircles()
        self.update()


    def setupLogging(self):

        self.logColumnHeaders = [
            "UserID",
            "TrialNr",
            "Width",
            "Distance",
            "Timestamp",
            "Movements",
            "MovementTime (h:m:s.ms)",
            "InitPosX",
            "InitPosY",
            "TargetPosX",
            "TargetPosY",
            "ClickPosX",
            "ClickPosY",
            "IsCircleHit",
            "Errors"]

        self.lastTimestamp = datetime.now()

        if os.path.exists(self.filename + ".csv"):
            return
        else:
            with open(self.filename + ".csv", "ab") as logfile:
                output = csv.DictWriter(logfile, self.logColumnHeaders,
                    delimiter=';')
                output.writeheader()

    def logResults(self):

        with open(self.filename + ".csv", "ab") as logfile:
            timestamp = datetime.now()
            timestampStr = timestamp
            data = {
                "UserID": self.userId,
                "TrialNr": self.trialsCount,
                "Width": self.distWidthCombis[self.trialsCount][1],
                "Distance": self.distWidthCombis[self.trialsCount][0],
                "Timestamp": timestampStr,
                "Movements": self.movements,
                "MovementTime (h:m:s.ms)": (timestamp-self.lastTimestamp),
                "InitPosX": self.initPosX,
                "InitPosY": self.initPosY,
                "TargetPosX": self.targetPosX,
                "TargetPosY": self.targetPosY,
                "ClickPosX": self.clickPosX,
                "ClickPosY": self.clickPosY,
                "IsCircleHit": self.isCircleHit,
                "Errors": self.errors
            }
            output = csv.DictWriter(logfile, self.logColumnHeaders, delimiter=';')
            output.writerow(data)

            self.lastTimestamp = timestamp;


    def closeEvent(self, event):
        event.accept()


def main():
    app = QtGui.QApplication(sys.argv)
    click = ClickRecorder()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
