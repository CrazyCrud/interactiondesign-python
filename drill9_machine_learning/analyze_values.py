# -*- coding: utf-8 -*-
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
#import wiimote
#from wiimote_node import *
import scipy
import math
import os
import csv
from sklearn import svm
from sklearn import datasets
from sklearn.preprocessing import scale, StandardScaler, MinMaxScaler

'''
The demo application identifies three different states:
it detects when the person - who holds the wiimote in one
of his hands - stands still, when the person walks and when
the person runs
'''

class ClassifierNode(CtrlNode):
    '''
    This node reads accelerometer data of a wiimote and tries
    to identify the activities walking, lying or running by
    analyzing this data using FFT. Using heuristics
    the activities can be recognized.
    '''

    nodeName = "ClassifierNode"

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

        self.classes = ['stand', 'walk', 'hop']

        self.classifier = svm.SVC()

        self.sample_data = {}

        self.sample_data['walk'] = self._read_data('walk')
        self.sample_data['stand'] = self._read_data('stand')
        self.sample_data['hop'] = self._read_data('hop')

        self._transform_data()
        self._train_data()

        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, accelX, accelY, accelZ):
        if accelX is None or accelY is None or accelZ is None:
            return

        output = self._compute_input(accelX, accelY, accelZ)

        return {'activity': output}

    def _read_data(self, which):
        x = y = z = []
        i = 0
        while True:
            i += 1
            try:
                sample_file = open(which + "_" + str(i) + ".csv", 'r')
                for line in sample_file:
                    values = line.strip().split(',')
                    if len(values) is 3:
                        x.append(int(values[0]))
                        y.append(int(values[1]))
                        z.append(int(values[2]))
                sample_file.close()
            except IOError:
                break
        return (x, y, z)

    def _transform_data(self):
        for action in self.sample_data:
            x_data = self.sample_data[action][0]
            data_length = len(x_data)
            x_frequencies = scipy.fft(x_data) / data_length
            x_frequencies = x_frequencies[range(data_length / 2)]
            x_frequencies[0] = 0
            x_frequencies = np.abs(x_frequencies)
            x_frequencies = x_frequencies[:50]

            y_data = self.sample_data[action][1]
            data_length = len(y_data)
            y_frequencies = scipy.fft(y_data) / data_length
            y_frequencies = y_frequencies[range(data_length / 2)]
            y_frequencies[0] = 0
            y_frequencies = np.abs(y_frequencies)
            y_frequencies = y_frequencies[:50]

            z_data = self.sample_data[action][2]
            data_length = len(z_data)
            z_frequencies = scipy.fft(z_data) / data_length
            z_frequencies = z_frequencies[range(data_length / 2)]
            z_frequencies[0] = 0
            z_frequencies = np.abs(z_frequencies)
            z_frequencies = z_frequencies[:50]

            self.sample_data[action] = zip(
                x_frequencies, y_frequencies, z_frequencies)

    def _train_data(self):
        sample = [
            self.sample_data['stand'], self.sample_data['walk'],
            self.sample_data['hop']]
        print sample
        self.classifier.fit(sample, self.classes)

    def _compute_input(self, accelX, accelY, accelZ):
        return self.activities['nodata']


fclib.registerNodeType(ClassifierNode, [('Data',)])


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    while True:
        demo.update()

    sys.exit(app.exec_())


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
        #self.getWiimote()

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

        self.activityNode = self.fc.createNode('ClassifierNode', pos=(0, 150))

        """
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
        """

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    main()
