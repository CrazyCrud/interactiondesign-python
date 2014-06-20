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


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    while True:
        demo.update()
        #time.sleep(0.20)

    sys.exit(app.exec_())

class AnalyzeNode(Node):
    nodeName = "AnalyzeNode"

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }

        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.sampling_rate_input = QtGui.QSpinBox()
        self.sampling_rate_input.setMinimum(0)
        self.sampling_rate_input.setMaximum(80)
        self.sampling_rate_input.setValue(60)
        self.sampling_rate_input.valueChanged.connect(self.update_sampling_rate)
        self.layout.addWidget(self.sampling_rate_input)
        self.ui.setLayout(self.layout)

        self.callback = None

        Node.__init__(self, name, terminals=terminals)

    def process(self, dataIn):
        sampling_rate = int(self.sampling_rate_input.value())
        #data_length = len(dataIn)
        #dataIn = dataIn / float(max(dataIn)) # Scaling
        frequency_spectrum = np.fft.fft(dataIn, n=sampling_rate) / sampling_rate
        frequency_spectrum = frequency_spectrum[range(sampling_rate / 2)]

        output = np.abs(frequency_spectrum)

        return {'dataOut': output}

    def update_sampling_rate(self, rate):
        if self.callback is not None:
            self.callback(self.sampling_rate_input.value())

    def set_sampling_rate(self, rate):
        self.sampling_rate_input.setValue(rate)

    def register_callback(self, callback):
        self.callback = callback

fclib.registerNodeType(AnalyzeNode, [('Data',)])


class ActivityNode(CtrlNode):
    nodeName = "ActivityNode"

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='in'),
            'accelY': dict(io='in'),
            'accelZ': dict(io='in'),
            'activity': dict(io='out'),
        }

        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.sampling_rate_input = QtGui.QSpinBox()
        self.sampling_rate_input.setMinimum(0)
        self.sampling_rate_input.setMaximum(80)
        self.sampling_rate_input.setValue(60)
        self.sampling_rate_input.valueChanged.connect(self.update_sampling_rate)
        self.layout.addWidget(self.sampling_rate_input)
        self.ui.setLayout(self.layout)

        self.callback = None

        self.activities = {
            'walking': 'You\'re walking', 'lying': 'You\'re lying',
            'running': 'You\'re running', 'none': 'No activity yet...'}
        CtrlNode.__init__(self, name, terminals=terminals)

    def update_sampling_rate(self, rate):
        if self.callback is not None:
            self.callback(self.sampling_rate_input.value())

    def set_sampling_rate(self, rate):
        self.sampling_rate_input.setValue(rate)

    def register_callback(self, callback):
        self.callback = callback

    def process(self, accelX, accelY, accelZ):
        sampling_rate = int(self.sampling_rate_input.value())
        data_x_length = len(accelX)
        data_y_length = len(accelY)
        data_z_length = len(accelZ)

        frequency_spectrum_x = np.fft.fft(accelX, n=sampling_rate) / sampling_rate
        frequency_spectrum_x = frequency_spectrum_x[range(sampling_rate / 2)]
        frequency_spectrum_y = np.fft.fft(accelY, n=sampling_rate) / sampling_rate
        frequency_spectrum_y = frequency_spectrum_y[range(sampling_rate / 2)]
        frequency_spectrum_z = np.fft.fft(accelZ, n=sampling_rate) / sampling_rate
        frequency_spectrum_z = frequency_spectrum_z[range(sampling_rate / 2)]

        frequency_spectrum_x = np.abs(frequency_spectrum_x)
        frequency_spectrum_y = np.abs(frequency_spectrum_y)
        frequency_spectrum_z = np.abs(frequency_spectrum_z)

        frequency_spectrum_x, frequency_spectrum_y, frequency_spectrum_z = \
            self.filterData(
                frequency_spectrum_x, frequency_spectrum_y, frequency_spectrum_z)

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

        self.fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })

        self.layout.addWidget(self.fc.widget(), 0, 0, 4, 1)

        self.createNodes()
        self.createCompareNode()

        sampling_rate = 60.0
        self.activityNode.set_update_rate(sampling_rate)
        self.analyzeXNode.set_update_rate(sampling_rate)
        self.analyzeYNode.set_update_rate(sampling_rate)
        self.analyzeZNode.set_update_rate(sampling_rate)
        #self.updateRate(self.sampling_rate)

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

    def updateRate(self, rate):
        self.wiimoteNode.set_update_rate(rate)
        self.bufferXNode.set_buffersize(rate)
        self.bufferYNode.set_buffersize(rate)
        self.bufferZNode.set_buffersize(rate)
        self.compBufferXNode.set_buffersize(rate)
        self.compBufferYNode.set_buffersize(rate)
        self.compBufferZNode.set_buffersize(rate)

    def update(self):
        outputValues = self.activityNode.outputValues()
        if outputValues['activity'] is not None:
            self.label.setText(outputValues['activity'])
        pg.QtGui.QApplication.processEvents()

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
        self.activityNode.register_callback(self.updateRate)

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
            bufferXNode['dataOut'], self.activityNode['accelX'])
        self.fc.connectTerminals(
            bufferYNode['dataOut'], self.activityNode['accelY'])
        self.fc.connectTerminals(
            bufferZNode['dataOut'], self.activityNode['accelZ'])

    def createCompareNode(self):
        compPwX = pg.PlotWidget()
        compPwY = pg.PlotWidget()
        compPwZ = pg.PlotWidget()

        self.layout.addWidget(compPwX, 3, 1)
        self.layout.addWidget(compPwY, 4, 1)
        self.layout.addWidget(compPwZ, 5, 1)

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

        self.analyzeXNode.register_callback(self.updateRate)
        self.analyzeYNode.register_callback(self.updateRate)
        self.analyzeZNode.register_callback(self.updateRate)

        self.fc.connectTerminals(self.wiimoteNode['accelX'], self.compBufferXNode['dataIn'])
        self.fc.connectTerminals(self.wiimoteNode['accelY'], self.compBufferYNode['dataIn'])
        self.fc.connectTerminals(self.wiimoteNode['accelZ'], self.compBufferZNode['dataIn'])

        self.fc.connectTerminals(self.compBufferXNode['dataOut'], analyzeXNode['dataIn'])
        self.fc.connectTerminals(self.compBufferYNode['dataOut'], analyzeYNode['dataIn'])
        self.fc.connectTerminals(self.compBufferZNode['dataOut'], analyzeZNode['dataIn'])

        self.fc.connectTerminals(
            analyzeXNode['dataOut'], pwXNode['In'])
        self.fc.connectTerminals(
            analyzeYNode['dataOut'], pwYNode['In'])
        self.fc.connectTerminals(
            analyzeZNode['dataOut'], pwZNode['In'])

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    main()
