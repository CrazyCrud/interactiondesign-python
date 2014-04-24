#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import csv
import time
from datetime import datetime
import random
import itertools
from circle import Circle
from PyQt4 import QtGui, QtCore


class ClickRecorder(QtGui.QWidget):

    def requestFileName(self):
        if len(sys.argv) < 2:
            sys.exit(0)
        else:
            self.fileName = sys.argv[1]

    #read content of test setup file and calculate random
    def readTestSetup(self):
        #read input
        with open(self.fileName) as f:
            content = f.read()

        if not content:
            #print "File is empty"
            sys.exit(0)

        userLines = content.split()

        #split description and comma-separated values, take values
        #and convert to int
        self.userId = userLines[0].split(':')[1]
        widths = map(int, userLines[1].split(':')[1].split(','))
        distances = map(int, userLines[2].split(':')[1].split(','))

        self.filename = "user" + self.userId

        #calculate possible combinations of distances and widths
        self.distWidthCombis = list(itertools.product(distances, widths))

        #randomize order of combinations of distance and width
        random.shuffle(self.distWidthCombis)

    def __init__(self):
        super(ClickRecorder, self).__init__()
        self.requestFileName()
        self.readTestSetup()
        self.initUI()
        self.setupStartRect()
        self.setupTrial()
        self.setupLogging()

    def setupStartRect(self):
        self.marginTop = self.res.height() / 3
        self.marginLeft = 100
        self.startCircle = Circle(50, self.marginLeft, self.marginTop)

    def setupCircle(self):
        width = self.distWidthCombis[self.trialsCount][1]
        distance = self.distWidthCombis[self.trialsCount][0]
        marginLeft = self.marginLeft + self.startCircle.diameter + distance
        self.circle = Circle(width, marginLeft - width / 2, self.marginTop)
        self.update()

    def setupTrial(self):
        self.circle = None
        self.errors = 0
        self.maxTrialsRepetition = 4
        self.maxTrialsCount = 16
        self.experimentOver = False
        self.trialsRepetition = 0
        self.trialsCount = 0

    def initUI(self):
        self.setWindowTitle("A Study about Fitts's Law")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.showFullScreen()
        self.show()
        self.res = QtGui.QDesktopWidget().screenGeometry()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(qp.Antialiasing)
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(event.rect())
        self.drawState(event, qp)
        if self.experimentOver is True:
            pass
        else:
            self.drawCircles(event, qp)
        qp.end()

    #handle mouse press event
    def mousePressEvent(self, event):
        #check only left buton click
        if event.button() == QtCore.Qt.LeftButton:
            #start circle is hit and there's no target circle right now
            if self.startCircle.isClicked(event.pos()) and self.circle is None:
                self.setupCircle()
                self.initPosX = event.pos().x()
                self.initPosY = event.pos().y()
                self.targetPosX = self.circle.x()
                self.targetPosY = self.circle.y()
                self.start = int(round(time.time() * 1000))
            #there's a target circle
            elif self.circle is not None:
                self.clickPosX = event.pos().x()
                self.clickPosY = event.pos().y()

                if self.circle.isClicked(event.pos()) is True:
                    self.isCircleHit = True
                else:
                    self.isCircleHit = False
                    self.addError()
                self.logResults()
                self.resetTrial()

    def addError(self):
        self.errors += 1

    def drawCircles(self, event, qp):
        if self.circle is not None:
            self.circle.drawCircle(event, qp)
        self.startCircle.drawCircle(event, qp)

    #draw hints for the different states
    def drawState(self, event, qp):
        qp.setPen(QtGui.QColor(80, 80, 80))
        qp.setFont(QtGui.QFont('Decorative', 24))
        if self.experimentOver is True:
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter,
                        "Danke für die Teilnahme!")
        else:
            qp.drawText(
                event.rect(), QtCore.Qt.AlignCenter,
                str(self.trialsCount
                    + (self.trialsRepetition * self.maxTrialsCount))
                + "/" + str(self.maxTrialsCount * self.maxTrialsRepetition))

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

    #reset variables for a new trial
    def resetTrial(self):
        self.trialsCount += 1
        if self.trialsCount > 0 and self.trialsCount % 16 == 0:
            self.trialsRepetition += 1
            self.trialsCount = 0

        count = (self.trialsRepetition * self.maxTrialsCount)
        count += self.trialsCount
        if (count) >= (self.maxTrialsCount * self.maxTrialsRepetition):
            self.experimentOver = True
        self.circle = None
        self.start = -1
        self.update()

    #setup log csv file
    def setupLogging(self):
        self.logColumnHeaders = [
            "UserID",
            "Trial",
            "Width",
            "Distance",
            "Timestamp",
            "MovementTime (ms)",
            "InitPosX",
            "InitPosY",
            "TargetPosX",
            "TargetPosY",
            "ClickPosX",
            "ClickPosY",
            "IsTargetHit",
            "Errors"]

        if os.path.exists(self.filename + ".csv"):
            return
        else:
            with open(self.filename + ".csv", "ab") as logfile:
                output = csv.DictWriter(
                    logfile, self.logColumnHeaders, delimiter=';')
                output.writeheader()

    #log results in a csv file
    def logResults(self):
        #append data
        with open(self.filename + ".csv", "ab") as logfile:
            timestamp = datetime.now()
            data = {
                "UserID": self.userId,
                "Trial": (self.trialsCount + 1)
                + (self.trialsRepetition * self.maxTrialsCount),
                "Width": self.distWidthCombis[self.trialsCount][1],
                "Distance": self.distWidthCombis[self.trialsCount][0],
                "Timestamp": timestamp,
                "MovementTime (ms)": (
                    int(round(time.time() * 1000)) - self.start),
                "InitPosX": self.initPosX,
                "InitPosY": self.initPosY,
                "TargetPosX": self.targetPosX,
                "TargetPosY": self.targetPosY,
                "ClickPosX": self.clickPosX,
                "ClickPosY": self.clickPosY,
                "IsTargetHit": self.isCircleHit,
                "Errors": self.errors
            }
            output = csv.DictWriter(
                logfile, self.logColumnHeaders, delimiter=';')
            output.writerow(data)


def main():
    app = QtGui.QApplication(sys.argv)
    sys.click = ClickRecorder()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
