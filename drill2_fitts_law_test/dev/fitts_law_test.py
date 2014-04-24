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
            exit(0)
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
        self.rect = QtCore.QRect(self.marginLeft, self.marginTop, 50, 50)


    def setupCircle(self):
        width = self.distWidthCombis[self.trialsCount][1]
        distance = self.distWidthCombis[self.trialsCount][0]
        marginLeft = self.marginLeft + self.rect.width() + distance
        self.circle = Circle(width, marginLeft - width / 2, self.marginTop + self.rect.height() / 2)
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
        if self.experimentOver == True:
            pass
        else:
            self.drawCircle(event, qp)
            self.drawStartRect(event, qp)
        qp.end()


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.rect.contains(event.pos(), True) and self.circle == None:
                self.setupCircle()
                self.initPosX = event.pos().x()
                self.initPosY = event.pos().y()
                self.targetPosX = self.circle.x()
                self.targetPosY = self.circle.y()
                self.start = int(round(time.time() * 1000))
            elif self.circle != None:
                self.clickPosX = event.pos().x()
                self.clickPosY = event.pos().y()
                if self.circle.isClicked(event.pos()) == True:
                    self.isCircleHit = True
                else:
                    self.isCircleHit = False
                    self.addError()
                self.logResults()
                self.resetTrial()


    def addError(self):
        self.errors += 1


    def drawCircle(self, event, qp):
        if self.circle != None:
            self.circle.drawCircle(event, qp)


    def drawStartRect(self, event, qp):
        qp.setBrush(QtGui.QColor(200, 200, 200))
        qp.drawRect(self.rect)


    def drawState(self, event, qp):
        qp.setPen(QtGui.QColor(80, 80, 80))
        qp.setFont(QtGui.QFont('Decorative', 24))
        if self.experimentOver == True:
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, u"Danke für die Teilnahme!")
        else:
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, str(self.trialsCount + (self.trialsRepetition * self.maxTrialsCount)) +
                "/" + str(self.maxTrialsCount * self.maxTrialsRepetition))


    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()


    def resetTrial(self):
        self.trialsCount += 1
        if self.trialsCount > 0 and self.trialsCount % 16 == 0:
            self.trialsRepetition += 1
            self.trialsCount = 0
        if (self.trialsCount + (self.trialsRepetition * self.maxTrialsCount)) >= (self.maxTrialsCount * self.maxTrialsRepetition):
            self.experimentOver = True
        self.circle = None
        self.start = -1
        self.update()


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
                output = csv.DictWriter(logfile, self.logColumnHeaders,
                    delimiter=';')
                output.writeheader()


    def logResults(self):
        with open(self.filename + ".csv", "ab") as logfile:
            timestamp = datetime.now()
            data = {
                "UserID": self.userId,
                "Trial": (self.trialsCount + 1) + (self.trialsRepetition * self.maxTrialsCount),
                "Width": self.distWidthCombis[self.trialsCount][1],
                "Distance": self.distWidthCombis[self.trialsCount][0],
                "Timestamp": timestamp,
                "MovementTime (ms)": (int(round(time.time() * 1000)) - self.start),
                "InitPosX": self.initPosX,
                "InitPosY": self.initPosY,
                "TargetPosX": self.targetPosX,
                "TargetPosY": self.targetPosY,
                "ClickPosX": self.clickPosX,
                "ClickPosY": self.clickPosY,
                "IsTargetHit": self.isCircleHit,
                "Errors": self.errors
            }
            output = csv.DictWriter(logfile, self.logColumnHeaders, delimiter=';')
            output.writerow(data)


def main():
    app = QtGui.QApplication(sys.argv)
    click = ClickRecorder()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
