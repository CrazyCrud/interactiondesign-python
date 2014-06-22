# -*- coding: utf-8 -*-
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.flowchart.library.common import CtrlNode, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
import time
import wiimote
import wiimote_node
import scipy
import math

def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    while True:
        demo.update()

    sys.exit(app.exec_())


class AnalyzeNode(Node):
    '''
    This node processes incoming data with FFT and outputs
    the resulting array.
    '''

    nodeName = "AnalyzeNode"

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }

        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()

        # add spinner for sampling rate selection
        self.sampling_rate_input = QtGui.QSpinBox()
        self.sampling_rate_input.setMinimum(0)
        self.sampling_rate_input.setMaximum(20)
        self.sampling_rate_input.setValue(20)
        self.sampling_rate_input.valueChanged.connect(self.update_sampling_rate)
        self.layout.addWidget(self.sampling_rate_input)
        self.ui.setLayout(self.layout)

        self.callback = None

        Node.__init__(self, name, terminals=terminals)

    def process(self, dataIn):
        sampling_rate = int(self.sampling_rate_input.value())

        dataIn = self.filterData(dataIn)

        frequency_spectrum = scipy.fft(dataIn) / len(dataIn)
        frequency_spectrum = frequency_spectrum[range(len(dataIn) / 2)]

        frequency_spectrum[0] = 0

        frequency_spectrum = np.abs(frequency_spectrum)
        output = frequency_spectrum / float(max(frequency_spectrum)) # Scaling

        return {'dataOut': output}

    def filterData(self, data):
        kernel = [0 for i in range(0, len(data))]

        for i in range((len(data) / 2) - 5, (len(data) / 2) + 5):
            kernel[i] = 0.1

        data = np.convolve(data, kernel, 'same')
        return data

    def update_sampling_rate(self, rate):
        if self.callback is not None:
            #print 'not None'
            self.callback(self.sampling_rate_input.value())

    def set_sampling_rate(self, rate):
        #print 'set_sampling_rate'
        self.sampling_rate_input.setValue(rate)

    def register_callback(self, callback):
        #print 'register_callback'
        self.callback = callback

fclib.registerNodeType(AnalyzeNode, [('Data',)])


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

        filteredX, filteredY, filteredZ = \
            self.filterData(
                accelX, accelY, accelZ)
        frequencySum = []
        for i in range(0, data_length):
            filteredX[i] = math.pow(filteredX[i], 2)
            filteredY[i] = math.pow(filteredY[i], 2)
            filteredZ[i] = math.pow(filteredZ[i], 2)
            frequencySum.append(math.sqrt(filteredX[i] + filteredY[i] + filteredZ[i]))

        frequency_spectrum = scipy.fft(frequencySum) / data_length

        frequency_spectrum = frequency_spectrum[range(data_length / 2)]

        frequency_spectrum = np.abs(frequency_spectrum)

        output = self.computeFrequencies(frequency_spectrum)

        return {'activity': output}

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

    def computeFrequencies(self, fspec):
        activity = self.activities['none']

        if fspec is None or len(fspec) < 150:
            return self.activities['nodata']

        dominantIndices = sorted(range(len(fspec)), key=lambda i: fspec[i], reverse=True)
        dominantFrequencies = []

        for i in range(0, 8):
            dominantFrequencies.append(dominantIndices[i])

        dominantFrequency = sum(dominantFrequencies) / float(len(dominantFrequencies))

        print 'dominantFrequency'
        print dominantFrequency

        runningFrequency = 7.0
        walkingFrequency = 5.0
        standingFrequency = 4.75

        if dominantFrequency > runningFrequency:
            activity = self.activities['running']

        if dominantFrequency > walkingFrequency - (walkingFrequency - standingFrequency) \
            and dominantFrequency < runningFrequency:
            activity = self.activities['walking']

        if dominantFrequency <= standingFrequency:
            activity = self.activities['standing']

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
        self.createCompareNode()

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

        self.fc.connectTerminals(self.wiimoteNode['accelX'], self.bufferXNode['dataIn'])
        self.fc.connectTerminals(self.wiimoteNode['accelY'], self.bufferYNode['dataIn'])
        self.fc.connectTerminals(self.wiimoteNode['accelZ'], self.bufferZNode['dataIn'])
        self.fc.connectTerminals(self.bufferXNode['dataOut'], pwXNode['In'])
        self.fc.connectTerminals(self.bufferYNode['dataOut'], pwYNode['In'])
        self.fc.connectTerminals(self.bufferZNode['dataOut'], pwZNode['In'])
        self.fc.connectTerminals(
            self.bufferXNode['dataOut'], self.activityNode['accelX'])
        self.fc.connectTerminals(
            self.bufferYNode['dataOut'], self.activityNode['accelY'])
        self.fc.connectTerminals(
            self.bufferZNode['dataOut'], self.activityNode['accelZ'])

    # create compare nodes and plots which help with analyzing data during development
    def createCompareNode(self):
        compPwX = pg.PlotWidget()
        compPwY = pg.PlotWidget()
        compPwZ = pg.PlotWidget()

        compPwX.setXRange(0, 25)
        compPwY.setXRange(0, 25)
        compPwZ.setXRange(0, 25)

        self.layout.addWidget(compPwX, 4, 1)
        self.layout.addWidget(compPwY, 5, 1)
        self.layout.addWidget(compPwZ, 6, 1)

        pwXNode = self.fc.createNode('PlotWidget', pos=(-150, -150))
        pwXNode.setPlot(compPwX)

        pwYNode = self.fc.createNode('PlotWidget', pos=(0, -150))
        pwYNode.setPlot(compPwY)

        pwZNode = self.fc.createNode('PlotWidget', pos=(150, -150))
        pwZNode.setPlot(compPwZ)

        self.compBufferXNode = self.fc.createNode('Buffer', pos=(-150, -300))
        self.compBufferYNode = self.fc.createNode('Buffer', pos=(0, -300))
        self.compBufferZNode = self.fc.createNode('Buffer', pos=(150, -300))

        self.analyzeXNode = self.fc.createNode('AnalyzeNode', pos=(0, 300))
        self.analyzeYNode = self.fc.createNode('AnalyzeNode', pos=(100, 300))
        self.analyzeZNode = self.fc.createNode('AnalyzeNode', pos=(200, 300))

        self.fc.connectTerminals(self.wiimoteNode['accelX'], self.compBufferXNode['dataIn'])
        self.fc.connectTerminals(self.wiimoteNode['accelY'], self.compBufferYNode['dataIn'])
        self.fc.connectTerminals(self.wiimoteNode['accelZ'], self.compBufferZNode['dataIn'])

        self.fc.connectTerminals(self.compBufferXNode['dataOut'], self.analyzeXNode['dataIn'])
        self.fc.connectTerminals(self.compBufferYNode['dataOut'], self.analyzeYNode['dataIn'])
        self.fc.connectTerminals(self.compBufferZNode['dataOut'], self.analyzeZNode['dataIn'])

        self.fc.connectTerminals(
            self.analyzeXNode['dataOut'], pwXNode['In'])
        self.fc.connectTerminals(
            self.analyzeYNode['dataOut'], pwYNode['In'])
        self.fc.connectTerminals(
            self.analyzeZNode['dataOut'], pwZNode['In'])

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    main()
