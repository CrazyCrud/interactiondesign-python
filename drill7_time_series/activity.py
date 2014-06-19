# -*- coding: utf-8 -*-
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
import time
import wiimote
import wiimote_node


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    while True:
        demo.update()
        time.sleep(0.20)

    sys.exit(app.exec_())


class ActivityNode(CtrlNode):
    nodeName = "ActivityNode"
    uiTemplate = [
        ('rate', 'spin', {
            'value': 150.0, 'step': 1.0, 'range': [0.0, 1000.0]}),
    ]

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='in'),
            'accelY': dict(io='in'),
            'accelZ': dict(io='in'),
            'activity': dict(io='out'),
        }

        self.activities = {
            'walking': 'You\'re walking', 'lying': 'You\'re lying',
            'running': 'You\'re running', 'none': 'No activity yet...'}
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, accelX, accelY, accelZ):
        data_x_length = len(accelX)
        data_y_length = len(accelY)
        data_z_length = len(accelZ)

        """
        interval = np.arange(data_x_length)
        sampling_rate = int(self.ctrls['rate'].value())
        step = data_x_length / sampling_rate
        frequency_range = interval / step
        frequency_range = frequency_range[range(data_x_length / 2)]
        """

        """
        sampling_rate = int(self.ctrls['rate'].value())
        sampling_interval = 1.0 / sampling_rate
        time_vector = np.arange(0, 1, sampling_interval)

        accelX = np.sin(accelX * time_vector)
        accelY = np.sin(accelY * time_vector)
        accelZ = np.sin(accelZ * time_vector)
        """

        accelX, accelY, accelZ = self.filterData(accelX, accelY, accelZ)

        frequency_spectrum_x = np.fft.fft(accelX) / data_x_length
        frequency_spectrum_x = frequency_spectrum_x[range(data_x_length / 2)]
        frequency_spectrum_y = np.fft.fft(accelY) / data_y_length
        frequency_spectrum_y = frequency_spectrum_y[range(data_y_length / 2)]
        frequency_spectrum_z = np.fft.fft(accelZ) / data_z_length
        frequency_spectrum_z = frequency_spectrum_z[range(data_z_length / 2)]

        frequency_spectrum_x = np.abs(frequency_spectrum_x)
        frequency_spectrum_y = np.abs(frequency_spectrum_y)
        frequency_spectrum_z = np.abs(frequency_spectrum_z)

        output = self.computeFrequencies(
            frequency_spectrum_x, frequency_spectrum_y, frequency_spectrum_z)
        return {'activity': output}

    def filterData(self, data_x, data_y, data_z):
        kernel = [0 for i in range(0, len(data_x))]
        for i in range(45, 55):
            kernel[i] = 0.1
        data_x = np.convolve(data_x, kernel, 'same')
        data_y = np.convolve(data_y, kernel, 'same')
        data_z = np.convolve(data_z, kernel, 'same')
        return data_x, data_y, data_z

    def computeFrequencies(self, fspec_x, fspec_y, fspec_z):
        activity = self.activities['none']
        return activity

fclib.registerNodeType(ActivityNode, [('Data',)])


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Wiimote Activity")
        self.showFullScreen()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })

        self.layout.addWidget(fc.widget(), 0, 0, 4, 1)

        pwX = pg.PlotWidget()
        pwY = pg.PlotWidget()
        pwZ = pg.PlotWidget()
        pwX.getPlotItem().hideAxis('bottom')
        # pwX.setYRange(0, 1024)
        pwY.getPlotItem().hideAxis('bottom')
        # pwY.setYRange(0, 1024)
        pwZ.getPlotItem().hideAxis('bottom')
        # pwZ.setYRange(0, 1024)

        self.label = QtGui.QLabel()
        self.label.setText("No activity yet...")
        font = QtGui.QFont("Arial")
        font.setPointSize(32)
        self.label.setFont(font)

        self.layout.addWidget(pwX, 0, 1)
        self.layout.addWidget(pwY, 1, 1)
        self.layout.addWidget(pwZ, 2, 1)
        self.layout.addWidget(self.label, 3, 1)

        sampling_rate = 150.0
        sampling_interval = 1.0 / sampling_rate  # Abtastfrequenz f = (1/t)
        time_vector = np.arange(0, 1, sampling_interval)
        signal_frequency = 10
        data = np.sin(2 * np.pi * signal_frequency * time_vector)
        fc.setInput(dataIn=data)

        pwXNode = fc.createNode('PlotWidget', pos=(-150, -150))
        pwXNode.setPlot(pwX)

        pwYNode = fc.createNode('PlotWidget', pos=(0, -150))
        pwYNode.setPlot(pwY)

        pwZNode = fc.createNode('PlotWidget', pos=(150, -150))
        pwZNode.setPlot(pwZ)

        self.activityNode = fc.createNode('ActivityNode', pos=(0, 150))

        # Einkommentieren falls mit Wii gearbeitet wird
        #"""
        self.wiimoteNode = fc.createNode('Wiimote', pos=(-300, 0))
        bufferXNode = fc.createNode('Buffer', pos=(-150, -300))
        bufferYNode = fc.createNode('Buffer', pos=(0, -300))
        bufferZNode = fc.createNode('Buffer', pos=(150, -300))
        #"""

        # Auskommentieren falls mit Wii gearbeitet wird
        '''
        fc.connectTerminals(fc['dataIn'], pwXNode['In'])
        fc.connectTerminals(fc['dataIn'], pwYNode['In'])
        fc.connectTerminals(fc['dataIn'], pwZNode['In'])
        fc.connectTerminals(fc['dataIn'], self.activityNode['accelX'])
        fc.connectTerminals(fc['dataIn'], self.activityNode['accelY'])
        fc.connectTerminals(fc['dataIn'], self.activityNode['accelZ'])
        '''
        # Einkommentieren falls mit Wii gearbeitet wird
        #"""
        fc.connectTerminals(self.wiimoteNode['accelX'], bufferXNode['dataIn'])
        fc.connectTerminals(self.wiimoteNode['accelY'], bufferYNode['dataIn'])
        fc.connectTerminals(self.wiimoteNode['accelZ'], bufferZNode['dataIn'])
        fc.connectTerminals(bufferXNode['dataOut'], pwXNode['In'])
        fc.connectTerminals(bufferYNode['dataOut'], pwYNode['In'])
        fc.connectTerminals(bufferZNode['dataOut'], pwZNode['In'])
        fc.connectTerminals(
            bufferXNode['dataOut'], self.activityNode['accelX'])
        fc.connectTerminals(
            bufferYNode['dataOut'], self.activityNode['accelY'])
        fc.connectTerminals(
            bufferZNode['dataOut'], self.activityNode['accelZ'])
        #"""

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

    def update(self):
        outputValues = self.activityNode.outputValues()

        if outputValues['activity'] is not None:
            self.label.setText(outputValues['activity'])
        pg.QtGui.QApplication.processEvents()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    main()
