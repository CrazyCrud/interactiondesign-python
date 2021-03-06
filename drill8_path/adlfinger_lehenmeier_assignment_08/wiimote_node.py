#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

import wiimote


class BufferNode(CtrlNode):
    """
    Buffers the last n samples provided on input and provides them as a list of
    length n on output.
    A spinbox widget allows for setting the size of the buffer.
    Default size is 32 samples.
    """
    nodeName = "Buffer"
    uiTemplate = [
        ('size',  'spin', {'value': 32.0, 'step': 1.0, 'range': [0.0, 128.0]}),
    ]

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }
        self._buffer = np.array([])

        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        size = int(self.ctrls['size'].value())
        self._buffer = np.append(self._buffer, kwds['dataIn'])
        self._buffer = self._buffer[-size:]
        output = self._buffer
        return {'dataOut': output}

    def setBufferSize(self, value):
        self.ctrls['size'].setValue(value)

    def getBufferSize(self):
        size = int(self.ctrls['size'].value())
        return size


fclib.registerNodeType(BufferNode, [('Data',)])


class WiimoteNode(Node):
    """
    Outputs sensor data from a Wiimote.

    Supported sensors: accelerometer (3 axis)
    Text input box allows for setting a Bluetooth MAC address.
    Pressing the "connect" button tries connecting to the Wiimote.
    Update rate can be changed via a spinbox widget. Setting it to "0"
    activates callbacks everytime a new sensor value arrives (which is
    quite often -> performance hit)
    """
    nodeName = "Wiimote"

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='out'),
            'accelY': dict(io='out'),
            'accelZ': dict(io='out'),
            'irVals': dict(io='out')
        }
        self.wiimote = None
        self._acc_vals = []
        self._ir_vals = []
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()

        label = QtGui.QLabel("Bluetooth MAC address:")
        self.layout.addWidget(label)
        self.text = QtGui.QLineEdit()
        self.layout.addWidget(self.text)
        label2 = QtGui.QLabel("Update rate (Hz)")
        self.layout.addWidget(label2)
        self.update_rate_input = QtGui.QSpinBox()
        self.update_rate_input.setMinimum(0)
        self.update_rate_input.setMaximum(60)
        self.update_rate_input.setValue(20)
        self.update_rate_input.valueChanged.connect(self.set_update_rate)
        self.layout.addWidget(self.update_rate_input)

        self.connect_button = QtGui.QPushButton("connect")
        self.layout.addWidget(self.connect_button)
        self.ui.setLayout(self.layout)
        self.connect_button.clicked.connect(self.connect_wiimote)

        # for ease of use
        self.btaddr = "B8:AE:6E:50:05:32"

        self.text.setText(self.btaddr)
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)

        Node.__init__(self, name, terminals=terminals)

    def update_all_sensors(self):
        if self.wiimote is None:
            return
        self._acc_vals = self.wiimote.accelerometer
        self._ir_vals = self.wiimote.ir
        self.update()

    def update_accel(self, acc_vals):
        self._acc_vals = acc_vals
        self.update()

    def update_ir(self, ir_vals):
        self._ir_vals = ir_vals
        self.update()

    def ctrlWidget(self):
        return self.ui

    def connect_wiimote(self):
        self.btaddr = str(self.text.text()).strip()
        if self.wiimote is not None:
            self.wiimote.disconnect()
            self.wiimote = None
            self.connect_button.setText("connect")
            return
        if len(self.btaddr) == 17:
            self.connect_button.setText("connecting...")
            self.wiimote = wiimote.connect(self.btaddr)
            if self.wiimote is None:
                self.connect_button.setText("try again")
            else:
                self.connect_button.setText("disconnect")
                self.set_update_rate(self.update_rate_input.value())

    def set_update_rate(self, rate):
        if rate == 0:
            # use callbacks for max. update rate
            self.wiimote.accelerometer.register_callback(self.update_accel)
            self.wiimote.ir.register_callback(self.update_ir)
            self.update_timer.stop()
        else:
            self.wiimote.accelerometer.unregister_callback(self.update_accel)
            self.wiimote.ir.unregister_callback(self.update_ir)
            self.update_timer.start(1000.0/rate)

    def process(self, **kwdargs):
        x, y, z = self._acc_vals

        return {
            'accelX': np.array([x]),
            'accelY': np.array([y]),
            'accelZ': np.array([z]),
            'irVals': np.array(self._ir_vals)}

fclib.registerNodeType(WiimoteNode, [('Sensor',)])


# node filtering the one ir object with the biggest size and
# calculating x/y average
class Vis2DNode(Node):
    """

    """
    nodeName = "Vis2D"

    def __init__(self, name):
        terminals = {
            'irVals': dict(io='in'),
            'irX': dict(io='out'),
            'irY': dict(io='out')
        }
        self._ir_vals = []

        Node.__init__(self, name, terminals=terminals)

    def update_all_sensors(self):
        self.update()

    def update_ir(self, ir_vals):
        self._ir_vals = ir_vals
        self.update()

    def process(self, irVals):
        ir_id = -1
        biggest_size = -1
        rtu_values = {}

        for ir in irVals:
            # get id of the biggest light
            if ir['size'] > biggest_size:
                ir_id = ir['id']
            # append x/y values to list
            if ir['id'] in rtu_values:
                rtu_values[ir['id']]['x'].append(ir['x'])
                rtu_values[ir['id']]['y'].append(ir['y'])
            else:
                rtu_values[ir['id']] = {'x': [ir['x']], 'y': [ir['y']]}

        avgX = 0
        avgY = 0

        # calc average x/y of biggest light
        if ir_id > -1:
            xVals = rtu_values[ir_id]['x']
            yVals = rtu_values[ir_id]['y']

            if len(xVals) > 0:
                avgX = float(sum(xVals))/len(xVals)
            else:
                avgX = float('nan')

            if len(yVals) > 0:
                avgY = float(sum(yVals))/len(yVals)
            else:
                avgY = float('nan')

        return {'irX': avgX, 'irY': avgY}

fclib.registerNodeType(Vis2DNode, [('Sensor',)])


# node filtering the two ir objects with the biggest size and
# calculating x/y average
class Vis3DNode(Node):
    """

    """
    nodeName = "Vis3D"

    def __init__(self, name):
        terminals = {
            'irVals': dict(io='in'),
            'irX1': dict(io='out'),
            'irY1': dict(io='out'),
            'irX2': dict(io='out'),
            'irY2': dict(io='out')
        }
        self._ir_vals = []

        Node.__init__(self, name, terminals=terminals)

    def update_all_sensors(self):
        self.update()

    def update_ir(self, ir_vals):
        self._ir_vals = ir_vals
        self.update()

    def process(self, irVals):
        ir_id1 = -1
        ir_id2 = -1
        rtu_values = {}

        # sort irVals by size
        irVals = sorted(irVals, key=lambda irVal: irVal['size'], reverse=True)

        for ir in irVals:
            if ir_id1 == -1:
                # take id of first element with the biggest size
                ir_id1 = ir['id']
            if ir_id2 == -1 and ir_id1 != ir['id']:
                # take id of element with the second biggest size
                ir_id2 = ir['id']
            # append x/y values to list
            if ir['id'] in rtu_values:
                rtu_values[ir['id']]['x'].append(ir['x'])
                rtu_values[ir['id']]['y'].append(ir['y'])
            else:
                rtu_values[ir['id']] = {'x': [ir['x']], 'y': [ir['y']]}

        avgX1 = 0
        avgY1 = 0
        avgX2 = 0
        avgY2 = 0

        # calc average x/y of the two biggest lights
        if ir_id1 > -1 and ir_id2 > -1:
            xVals1 = rtu_values[ir_id1]['x']
            yVals1 = rtu_values[ir_id1]['y']

            if len(xVals1) > 0:
                avgX1 = float(sum(xVals1))/len(xVals1)
            else:
                avgX1 = 0

            if len(yVals1) > 0:
                avgY1 = float(sum(yVals1))/len(yVals1)
            else:
                avgY1 = 0

            xVals2 = rtu_values[ir_id2]['x']
            yVals2 = rtu_values[ir_id2]['y']

            if len(xVals2) > 0:
                avgX2 = float(sum(xVals2))/len(xVals2)
            else:
                avgX2 = 0

            if len(yVals2) > 0:
                avgY2 = float(sum(yVals2))/len(yVals2)
            else:
                avgY2 = 0

        return {'irX1': avgX1, 'irY1': avgY1, 'irX2': avgX2, 'irY2': avgY2}

fclib.registerNodeType(Vis3DNode, [('Sensor',)])


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('WiimoteNode demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
        'dataIn': {'io': 'in'},
        'dataOut': {'io': 'out'}
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    pw1 = pg.PlotWidget()
    layout.addWidget(pw1, 0, 1)
    pw1.setYRange(0, 1024)

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)

    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
    bufferNode = fc.createNode('Buffer', pos=(150, 0))

    fc.connectTerminals(wiimoteNode['accelX'], bufferNode['dataIn'])
    fc.connectTerminals(bufferNode['dataOut'], pw1Node['In'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
