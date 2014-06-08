#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import pdb

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
            'irX': dict(io='out'),
            'irY': dict(io='out')
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
        self.btaddr = "B8:AE:6E:50:05:32" # for ease of use
        self.text.setText(self.btaddr)
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)

        Node.__init__(self, name, terminals=terminals)

    def print_ir(self, ir_data):
        #print''
        #print len(ir_data)
        #asd = 1#!!
        testaX = self._ir_vals
        #print testaX
        #if len(testaX) == 1:
        #    print testaX[0]
        #elif len(testaX) > 1:
        #    print testaX[-1]
        #print testaX[len(testaX)-1]['x']
        #print testaX[len(testaX)-1]
        #for ir_obj in ir_data:
            #print "%4d %4d %2d" % (ir_obj["x"],ir_obj["y"],ir_obj["size"]),
        #print ir_data[-1]
        #print "%4d %4d %2d" % (ir_data[-1]["x"],ir_data[-1]["y"],ir_data[-1]["size"])

    def update_all_sensors(self):
        if self.wiimote == None:
            return
        self._acc_vals = self.wiimote.accelerometer
        # todo: other sensors...
        self._ir_vals = self.wiimote.ir
        self.update()

    def update_accel(self, acc_vals):
        self._acc_vals = acc_vals
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
        if len(self.btaddr) == 17 :
            self.connect_button.setText("connecting...")
            self.wiimote = wiimote.connect(self.btaddr)
            if self.wiimote == None:
                self.connect_button.setText("try again")
            else:
                self.connect_button.setText("disconnect")
                self.set_update_rate(self.update_rate_input.value())
                self.wiimote.ir.register_callback(self.print_ir)

    def set_update_rate(self, rate):
        if rate == 0: # use callbacks for max. update rate
            self.wiimote.accelerometer.register_callback(self.update_accel)
            self.update_timer.stop()
        else:
            self.wiimote.accelerometer.unregister_callback(self.update_accel)
            self.update_timer.start(1000.0/rate)

    def process(self, **kwdargs):
        x,y,z = self._acc_vals
        
        irXValue = self._ir_vals[len(self._ir_vals)-1]['x']
        irYValue = self._ir_vals[len(self._ir_vals)-1]['y']

        return {'accelX': np.array([x]), 'accelY': np.array([y]), 'accelZ': np.array([z]),
                'irX': np.array([irXValue]), 'irY': np.array([irYValue])}

fclib.registerNodeType(WiimoteNode, [('Sensor',)])

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('WiimoteNode demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    ## Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
        'dataIn': {'io': 'in'},
        'dataOut': {'io': 'out'}
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    pw1 = pg.PlotWidget()
    layout.addWidget(pw1, 0, 1)
    pw1.setYRange(0,1024)

    pw2 = pg.PlotWidget()
    layout.addWidget(pw2, 1, 1)
    pw2.setYRange(0,1024)

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)

    pw2Node = fc.createNode('PlotWidget', pos=(0, 150))    
    pw2Node.setPlot(pw2)

    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
    #bufferNode = fc.createNode('Buffer', pos=(150, 0))
    bufferNodeX = fc.createNode('Buffer', pos=(150, 0))
    bufferNodeY = fc.createNode('Buffer', pos=(300, 0))

    #fc.connectTerminals(wiimoteNode['accelX'], bufferNode['dataIn'])
    #fc.connectTerminals(wiimoteNode['irX'], bufferNode['dataIn'])
    fc.connectTerminals(wiimoteNode['irX'], bufferNodeX['dataIn'])
    fc.connectTerminals(wiimoteNode['irY'], bufferNodeY['dataIn'])
    #fc.connectTerminals(bufferNode['dataOut'], pw1Node['In'])
    fc.connectTerminals(bufferNodeX['dataOut'], pw1Node['In'])
    fc.connectTerminals(bufferNodeY['dataOut'], pw2Node['In'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
