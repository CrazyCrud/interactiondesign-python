# -*- coding: utf-8 -*-
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.flowchart.library.common import CtrlNode, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from random import randint
import sys
import time


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    """
    while True:
        demo.update()
        time.sleep(0.20)
    """
    sys.exit(app.exec_())


class AnalyzeNode(Node):
    nodeName = "AnalyzeNode"

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }

        Node.__init__(self, name, terminals=terminals)

    def process(self, dataIn):
        data_length = len(dataIn)
        frequency_spectrum = np.fft.fft(dataIn) / data_length # fft computing and normalization
        frequency_spectrum = frequency_spectrum[range(data_length / 2)]

        output =  np.abs(frequency_spectrum)

        print output

        return {'dataOut': output}


fclib.registerNodeType(AnalyzeNode, [('Data',)])


class NoiseNode(CtrlNode):
    nodeName = "NoiseNode"
    uiTemplate = [
        ('noise',  'spin', {'value': 5, 'step': 1.0, 'range': [0.0, 128.0]}),
    ]

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }

        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, dataIn):
        size = int(self.ctrls['noise'].value())
        for i in xrange(len(dataIn)):
            dataIn[i] = dataIn[i] + (size * randint(-500, 500))
        output = dataIn
        return {'dataOut': output}

    def setBufferValue(self, value):
        self.ctrls['noise'].setValue(value)


fclib.registerNodeType(NoiseNode, [('Data',)])


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Fourier Transformation")
        self.showFullScreen()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })

        self.layout.addWidget(fc.widget(), 0, 0, 2, 1)

        pw1 = pg.PlotWidget()
        pw2 = pg.PlotWidget()
        pw1.getPlotItem().setLabel('left', text='Amplitude')
        pw1.getPlotItem().setLabel('bottom', text='Time')
        pw2.getPlotItem().setLabel('left', text='Y(freq)')
        pw2.getPlotItem().setLabel('bottom', text='F(Hz)')
        self.layout.addWidget(pw1, 0, 1)
        self.layout.addWidget(pw2, 1, 1)

        sampling_rate = 150.0
        sampling_interval = 1.0 / sampling_rate; # Abtastfrequenz f = (1/t)
        time_vector = np.arange(0, 1, sampling_interval)

        signal_frequency = 10
        data = np.sin(2 * np.pi * signal_frequency * time_vector)

        print data

        fc.setInput(dataIn=data)

        pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
        pw1Node.setPlot(pw1)

        pw2Node = fc.createNode('PlotWidget', pos=(150, -150))
        pw2Node.setPlot(pw2)

        fNode = fc.createNode('AnalyzeNode', pos=(0, 0))

        fc.connectTerminals(fc['dataIn'], fNode['dataIn'])
        fc.connectTerminals(fc['dataIn'], pw1Node['In'])
        fc.connectTerminals(fNode['dataOut'], pw2Node['In'])
        fc.connectTerminals(fNode['dataOut'], fc['dataOut'])

    def update(self):
        pass

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    main()
