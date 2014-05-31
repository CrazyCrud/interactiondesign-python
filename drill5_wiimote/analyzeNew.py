import wiimote
import sys
import time
#from random import randint
#import numpy
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
import pyqtgraph
from PyQt4 import QtGui, QtCore


def main():
    wm = getWiimote()
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    while True:
        demo.updateValues(
            wm.accelerometer._state[0], wm.accelerometer._state[1], wm.accelerometer._state[2])
        time.sleep(0.10)

    sys.exit(app.exec_())


def getWiimote():
    '''raw_input(
        "Press the 'sync' button on the back of your Wiimote Plus " +
        "or buttons (1) and (2) on your classic Wiimote.\n" +
        "Press <return> once the Wiimote's LEDs start blinking.")'''
    if len(sys.argv) == 1:
        addr, name = wiimote.find()[0]
    elif len(sys.argv) == 2:
        addr = sys.argv[1]
        name = None
    elif len(sys.argv) == 3:
        addr, name = sys.argv[1:3]
    print("Connecting to %s (%s)" % (name, addr))
    return wiimote.connect(addr, name)


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Plotting the Wiimote")
        self.showFullScreen()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.flowchart = Flowchart(terminals={
            'xDataIn': {'io': 'in'},
            'yDataIn': {'io': 'in'},
            'zDataIn': {'io': 'in'},
            'xDataOut': {'io': 'out'},
            'yDataOut': {'io': 'out'},
            'zDataOut': {'io': 'out'}
        })

        self.layout.addWidget(self.flowchart.widget(), 0, 0, 3, 1)

        fclib.registerNodeType(WiimoteNode, [('Display',)])
        self.wii_node = self.flowchart.createNode('Wiimote', pos=(0, 0))

        self.axes = ['x', 'y', 'z']
        self.positions = {
            'x': [-450, -350, -300, -350, -375, -150],
            'y': [-150, -350, 0, -350, -75, -150],
            'z': [150, -350, -300, -350, 225, -150],
        }

        # create, style, config and connect the elements for every axis
        for axis in self.axes:
            index = self.axes.index(axis)

            plot_raw = pyqtgraph.PlotWidget()
            plot_filtered = pyqtgraph.PlotWidget()

            # add widget for this axis in next row
            self.layout.addWidget(plot_filtered, index, 2, 1, 2)

            self.configPlotItems(axis, plot_raw, plot_filtered)

            self.createNodes(axis, plot_raw, plot_filtered)

            self.connectNodes(axis)

        pyqtgraph.setConfigOptions(antialias=True)

        self.flowchart.setInput(xDataIn=0)
        self.flowchart.setInput(yDataIn=0)
        self.flowchart.setInput(zDataIn=0)

    # create raw, filter and filtered node
    def createNodes(self, axis, plot_raw, plot_filtered):
        # create raw node
        self.plot_raw_node = self.flowchart.createNode(
            'PlotWidget', pos=(self.positions[axis][0], self.positions[axis][1]))
        self.plot_raw_node.setPlot(plot_raw)

        # create filtered node
        self.plot_filtered_node = self.flowchart.createNode(
            'PlotWidget', pos=(self.positions[axis][2], self.positions[axis][3]))
        self.plot_filtered_node.setPlot(plot_filtered)

        # create gaussian filter
        self.filter_node = self.flowchart.createNode(
            'GaussianFilter', pos=(self.positions[axis][4], self.positions[axis][5]))
        self.filter_node.ctrls['sigma'].setValue(5)

    # connect nodes: flowchart -> wiinode -> plot_raw +  filter_node -> filtered_node
    def connectNodes(self, axis):
        self.flowchart.connectTerminals(
            self.flowchart[axis + 'DataIn'], self.wii_node[axis + 'DataIn'])

        self.flowchart.connectTerminals(
            self.wii_node[axis + 'DataOut'], self.plot_raw_node['In'])

        self.flowchart.connectTerminals(
            self.wii_node[axis + 'DataOut'], self.filter_node['In'])

        self.flowchart.connectTerminals(
            self.filter_node['Out'], self.plot_filtered_node['In'])

        self.flowchart.connectTerminals(
            self.filter_node['Out'], self.flowchart[axis + 'DataOut'])

    # config plot items
    def configPlotItems(self, axis, plot_raw, plot_filtered):
        plot_raw.getPlotItem().setTitle("The " + axis + " Accelerometer")
        plot_raw.getPlotItem().setMenuEnabled(False)
        plot_raw.getPlotItem().setClipToView(False)
        plot_raw.getPlotItem().hideAxis('bottom')
        plot_raw.getPlotItem().showGrid(x=True, y=True, alpha=0.5)

        plot_filtered.getPlotItem().setTitle(
            "The " + axis + " Accelerometer - Filtered")
        plot_filtered.getPlotItem().setMenuEnabled(False)
        plot_filtered.getPlotItem().setClipToView(False)
        plot_filtered.getPlotItem().hideAxis('bottom')
        plot_filtered.getPlotItem().showGrid(x=True, y=True, alpha=0.5)

    def updateValues(self, x, y, z):
        self.flowchart.setInput(xDataIn=x)
        self.flowchart.setInput(yDataIn=y)
        self.flowchart.setInput(zDataIn=z)
        pyqtgraph.QtGui.QApplication.processEvents()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()


class WiimoteNode(Node):
    nodeName = 'Wiimote'

    def __init__(self, name, n=100):
        Node.__init__(self, name, terminals={
            'xDataIn': {'io': 'in'},
            'yDataIn': {'io': 'in'},
            'zDataIn': {'io': 'in'},
            'xDataOut': {'io': 'out'},
            'yDataOut': {'io': 'out'},
            'zDataOut': {'io': 'out'}
        })
        self.values = {'x': [], 'y': [], 'z': []}
        self.limit = n

    def process(self, xDataIn, yDataIn, zDataIn, display=True):
        if xDataIn is not None:
            self.add(
                xDataIn, yDataIn, zDataIn)
        return {'xDataOut': self.values['x'],
                'yDataOut': self.values['y'],
                'zDataOut': self.values['z']}

    def add(self, x, y, z):
        if len(self.values['x']) > self.limit:
            self.values['x'].pop(0)
            self.values['y'].pop(0)
            self.values['z'].pop(0)
        self.values['x'].append(x)
        self.values['y'].append(y)
        self.values['z'].append(z)

if __name__ == "__main__":
    main()
