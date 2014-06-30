# -*- coding: utf-8 -*-
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
import wiimote
from wiimote_node import *
import scipy
import math
import os
import csv

'''
The demo application identifies three different states:
it detects when the person - who holds the wiimote in one
of his hands - stands still, when the person walks and when
the person runs
'''


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    while True:
        demo.update()

    sys.exit(app.exec_())


class ActivityNode(CtrlNode):
    '''
    This node reads accelerometer data of a wiimote and tries
    to identify the activities walking, lying or running by
    analyzing this data using FFT. Using heuristics
    the activities can be recognized.
    '''

    nodeName = "ActivityNode"

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='in'),
            'accelY': dict(io='in'),
            'accelZ': dict(io='in'),
            'activity': dict(io='out'),
        }

        self.logCounter = 0
        self.fileName = 'walk'
        self.setupLogging()

        self.activities = {
            'walking': 'You\'re walking',
            'running': 'You\'re running', 'none': 'No activity yet...',
            'standing': 'You\'re standing',
            'nodata': 'Computing data...'}

        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, accelX, accelY, accelZ):
        if accelX is None or accelY is None or accelZ is None:
            return

        data_length = len(accelX)

        self.accelX = accelX
        self.accelY = accelY
        self.accelZ = accelZ

        self.logResults()

        '''
        filteredX, filteredY, filteredZ = \
            self.filterData(
                accelX, accelY, accelZ)


        frequencySum = []
        for i in range(0, data_length):
            filteredX[i] = math.pow(filteredX[i], 2)
            filteredY[i] = math.pow(filteredY[i], 2)
            filteredZ[i] = math.pow(filteredZ[i], 2)
            frequencySum.append(math.sqrt(filteredX[i] +
                                filteredY[i] + filteredZ[i]))
        '''

        '''
        frequency_spectrum = scipy.fft(frequencySum) / data_length

        frequency_spectrum = frequency_spectrum[range(data_length / 2)]
        frequency_spectrum[0] = 0
        frequency_spectrum = np.abs(frequency_spectrum)

        output = self.computeFrequencies(frequency_spectrum)
        '''
        output = 'Collecting'
        return {'activity': output}

    #setup log csv file
    def setupLogging(self):
        self.logColumnHeaders = [
            "WalkId",
            "AccelX",
            "AccelY",
            "AccelZ",
            "Timestamp"]

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
        with open(self.filename + self.logCounter + ".csv", "ab") as logfile:
            timestamp = datetime.now()
            data = {
                "WalkId": self.logCounter,
                "AccelX": self.accelX,
                "AccelY": self.accelY,
                "AccelZ": self.accelZ,
                "Timestamp": timestamp,
            }
            print data
            output = csv.DictWriter(
                logfile, self.logColumnHeaders, delimiter=';')
            output.writerow(data)

    '''
    def filterData(self, data_x, data_y, data_z):
        kernelX = [0 for i in range(0, len(data_x))]
        kernelY = [0 for i in range(0, len(data_y))]
        kernelZ = [0 for i in range(0, len(data_z))]

        for i in range((len(data_x) / 2) - 5, (len(data_x) / 2) + 5):
            kernelX[i] = 0.1

        for i in range((len(data_y) / 2) - 5, (len(data_y) / 2) + 5):
            kernelY[i] = 0.1

        for i in range((len(data_z) / 2) - 5, (len(data_z) / 2) + 5):
            kernelZ[i] = 0.1

        data_x = np.convolve(data_x, kernelX, 'same')
        data_y = np.convolve(data_y, kernelY, 'same')
        data_z = np.convolve(data_z, kernelZ, 'same')
        return data_x, data_y, data_z
    '''
    def computeFrequencies(self, fspec):
        activity = self.activities['none']

        if fspec is None or len(fspec) < 150:
            return self.activities['nodata']

        # get most dominant frequencies
        dominantIndices = sorted(
            range(len(fspec)), key=lambda i: fspec[i], reverse=True)
        dominantFrequencies = []

        for i in range(0, 12):
            dominantFrequencies.append(dominantIndices[i])

        # calculate deviation
        mean = sum(dominantFrequencies) / \
            float(len(dominantFrequencies))

        value_sum = 0
        for value in dominantFrequencies:
            value_sum += math.pow(value - mean, 2)

        dev = math.sqrt(value_sum / mean)

        # check for activities
        runningFrequency = 8.5
        walkingFrequency = 6.5
        standingFrequency = 6.0

        if mean >= runningFrequency:
            activity = self.activities['running']
            return activity

        if mean <= standingFrequency or dev < 5.0:
            activity = self.activities['standing']
            return activity

        if mean > walkingFrequency - (walkingFrequency - standingFrequency) \
                and mean < runningFrequency:
            activity = self.activities['walking']
            return activity

        return activity

fclib.registerNodeType(ActivityNode, [('Data',)])


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Wiimote Activity")
        self.showFullScreen()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })

        self.layout.addWidget(self.fc.widget(), 0, 0, 4, 1)

        self.createNodes()

        self.getWiimote()

    # connect to wiimote with an address given as argument
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

    def update(self):
        outputValues = self.activityNode.outputValues()
        if outputValues['activity'] is not None:
            self.label.setText(outputValues['activity'])
        pg.QtGui.QApplication.processEvents()

    # create and config the nodes needed to recognize activities
    def createNodes(self):
        pwX = pg.PlotWidget()
        pwY = pg.PlotWidget()
        pwZ = pg.PlotWidget()
        pwX.getPlotItem().hideAxis('bottom')
        pwX.setYRange(300, 700)
        pwY.getPlotItem().hideAxis('bottom')
        pwY.setYRange(300, 700)
        pwZ.getPlotItem().hideAxis('bottom')
        pwZ.setYRange(300, 700)

        self.label = QtGui.QLabel()
        self.label.setText("No activity yet...")
        font = QtGui.QFont("Arial")
        font.setPointSize(32)
        self.label.setFont(font)

        self.layout.addWidget(pwX, 0, 1)
        self.layout.addWidget(pwY, 1, 1)
        self.layout.addWidget(pwZ, 2, 1)
        self.layout.addWidget(self.label, 3, 1)

        pwXNode = self.fc.createNode('PlotWidget', pos=(-150, -150))
        pwXNode.setPlot(pwX)

        pwYNode = self.fc.createNode('PlotWidget', pos=(0, -150))
        pwYNode.setPlot(pwY)

        pwZNode = self.fc.createNode('PlotWidget', pos=(150, -150))
        pwZNode.setPlot(pwZ)

        self.activityNode = self.fc.createNode('ActivityNode', pos=(0, 150))

        self.wiimoteNode = self.fc.createNode('Wiimote', pos=(-300, 0))
        self.bufferXNode = self.fc.createNode('Buffer', pos=(-150, -300))
        self.bufferYNode = self.fc.createNode('Buffer', pos=(0, -300))
        self.bufferZNode = self.fc.createNode('Buffer', pos=(150, -300))

        self.fc.connectTerminals(
            self.wiimoteNode['accelX'], self.bufferXNode['dataIn'])
        self.fc.connectTerminals(
            self.wiimoteNode['accelY'], self.bufferYNode['dataIn'])
        self.fc.connectTerminals(
            self.wiimoteNode['accelZ'], self.bufferZNode['dataIn'])
        self.fc.connectTerminals(self.bufferXNode['dataOut'], pwXNode['In'])
        self.fc.connectTerminals(self.bufferYNode['dataOut'], pwYNode['In'])
        self.fc.connectTerminals(self.bufferZNode['dataOut'], pwZNode['In'])
        self.fc.connectTerminals(
            self.bufferXNode['dataOut'], self.activityNode['accelX'])
        self.fc.connectTerminals(
            self.bufferYNode['dataOut'], self.activityNode['accelY'])
        self.fc.connectTerminals(
            self.bufferZNode['dataOut'], self.activityNode['accelZ'])

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    main()
