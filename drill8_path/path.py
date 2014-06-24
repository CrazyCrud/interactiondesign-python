#!/usr/bin/env python

import time
import sys
from pyqtgraph.flowchart import Flowchart
import pyqtgraph
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
import wiimote
from wiimote_node import *
import dollar


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

        self.setWindowTitle("Pointing Device")
        self.show()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })
        self.layout.addWidget(self.fc.widget(), 0, 0, 2, 1)

        self.path = {'x': [], 'y': []}
        self.threshold = 50
        self.default_text = 'No template matched...'

        self.pressed_key = None

        self.config_nodes()
        self.config_layout()
        self.setup_templates()

        self.get_wiimote()

    # connect to wiimote and config wiimote node
    def get_wiimote(self):
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

    # create and connect nodes
    def config_nodes(self):
        self.pointVisNode = self.fc.createNode('Vis2D', pos=(-150, 150))
        self.wiimoteNode = self.fc.createNode('Wiimote', pos=(0, 0), )
        self.bufferNode = self.fc.createNode('Buffer', pos=(0, -150))

        self.fc.connectTerminals(
            self.wiimoteNode['irVals'],
            self.bufferNode['dataIn'])
        self.fc.connectTerminals(
            self.bufferNode['dataOut'],
            self.pointVisNode['irVals'])

    # create and config scatter plot item
    def config_layout(self):
        gview = pg.GraphicsLayoutWidget()
        self.layout.addWidget(gview, 0, 1, 2, 1)
        plot = gview.addPlot()
        self.scatter = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        plot.addItem(self.scatter)
        #plot.setXRange(-1000, 200)
        #plot.setYRange(-1000, 200)

        self.label = QtGui.QLabel()
        self.label.setText(self.default_text)
        font = QtGui.QFont("Arial")
        font.setPointSize(32)
        self.label.setFont(font)
        self.layout.addWidget(self.label, 2, 1, 1, 1)

    def setup_templates(self):
        dollar.addTemplate('circle', circle_points)
        dollar.addTemplate('square', square_points)
        dollar.addTemplate('triangle', triangle_points)

    def update(self):
        outputValues = self.pointVisNode.outputValues()
        if outputValues['irX'] is not None and outputValues['irY'] is not None:
            if self.wiimoteNode.wiimote is not None:
                if self.wiimoteNode.wiimote.buttons['A']:
                    self.draw_path(irValues)
                    self.pressed_key = 'A'
                elif self.wiimoteNode.wiimote.buttons['B']:
                    self.draw_path(irValues)
                    self.pressed_key = 'B'
                elif self.path['x'] is not None and len(self.path['x']) > 0:
                    points = []
                    for i in range(0, len(self.path['x'])):
                        points.append([self.path['x'][i], self.path['y'][i]])
                    self.scatter.setData(pos=np.array(points))
                    if self.pressed_key is 'A':
                        self.compare_template()
                    elif self.pressed_key is 'B':
                        self.create_template()
                    self.path['x'] = []
                    self.path['y'] = []
                    self.pressed_key = None

        pyqtgraph.QtGui.QApplication.processEvents()

    def create_template(self):
        points = []
        for i in range(0, len(0, len(self.path['x']))):
            points.append([self.path['x'][i], self.path['y'][i]])
        name = 'tpl_' + (len(dollar.templates) + 1)
        dollar.addTemplate(name, circle_points)

    def compare_template(self):
        points = []
        for i in range(0, len(0, len(self.path['x']))):
            points.append([self.path['x'][i], self.path['y'][i]])
        name, score = dollar.recognize(points)
        score = score * 100
        if score > self.threshold:
            self.label.setText(name)
        else:
            self.label.setText(self.default_text)

    def draw_path(self, irValues):
        self.scatter.clear()
        self.path['x'].append(irValues['irX'])
        self.path['y'].append(irValues['irY'])

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == "__main__":
    main()
