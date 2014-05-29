# import wiimote
import sys
import time
from random import randint
import numpy
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
import pyqtgraph
from PyQt4 import QtGui, QtCore


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()
    # wm = getWiimote()

    while True:
        demo.updateValues(
            randint(0, 6), randint(0, 6), randint(0, 6))
        time.sleep(0.05)

    sys.exit(app.exec_())


def getWiimote():
    if len(sys.argv) == 1:
        addr, name = wiimote.find()[0]
    elif len(sys.argv) == 2:
        addr = sys.argv[1]
        name = None
    elif len(sys.argv) == 3:
        addr, name = sys.argv[1:3]
    return wiimote.connect(addr, name)


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()
        #self.node = WiimoteNode()

        self.setWindowTitle("Plotting the Wiimote")
        self.showFullScreen()

        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        self.flowchart = Flowchart(terminals={
            'xDataIn': {'io': 'in'},
            'yDataIn': {'io': 'in'},
            'zDataIn': {'io': 'in'},
            'xDataOut': {'io': 'out'},
            'yDataOut': {'io': 'out'},
            'zDataOut': {'io': 'out'}
        })

        layout.addWidget(self.flowchart.widget(), 0, 0, 3, 1)

        self.x_plot_raw = pyqtgraph.PlotWidget()
        self.y_plot_raw = pyqtgraph.PlotWidget()
        self.z_plot_raw = pyqtgraph.PlotWidget()
        self.x_plot_filtered = pyqtgraph.PlotWidget()
        self.y_plot_filtered = pyqtgraph.PlotWidget()
        self.z_plot_filtered = pyqtgraph.PlotWidget()

        #layout.addWidget(self.x_plot_raw, 0, 1, 1, 1)
        layout.addWidget(self.x_plot_filtered, 0, 2, 1, 2)
        #layout.addWidget(self.y_plot_raw, 1, 1, 1, 1)
        layout.addWidget(self.y_plot_filtered, 1, 2, 1, 2)
        #layout.addWidget(self.z_plot_raw, 2, 1, 1, 1)
        layout.addWidget(self.z_plot_filtered, 2, 2, 1, 2)

        pyqtgraph.setConfigOptions(antialias=True)

        self.x_plot_raw.getPlotItem().setTitle("The X Accelerometer")
        self.x_plot_raw.getPlotItem().setMenuEnabled(False)
        self.x_plot_raw.getPlotItem().setClipToView(False)
        self.x_plot_raw.getPlotItem().hideAxis('bottom')
        self.x_plot_raw.getPlotItem().showGrid(x=True, y=True, alpha=0.5)

        self.x_plot_filtered.getPlotItem().setTitle(
            "The X Accelerometer - Filtered")
        self.x_plot_filtered.getPlotItem().setMenuEnabled(False)
        self.x_plot_filtered.getPlotItem().setClipToView(False)
        self.x_plot_filtered.getPlotItem().hideAxis('bottom')
        self.x_plot_filtered.getPlotItem().showGrid(x=True, y=True, alpha=0.5)

        self.y_plot_raw.getPlotItem().setTitle("The Y Accelerometer")
        self.y_plot_raw.getPlotItem().setMenuEnabled(False)
        self.y_plot_raw.getPlotItem().setClipToView(False)
        self.y_plot_raw.getPlotItem().hideAxis('bottom')
        self.y_plot_raw.getPlotItem().showGrid(x=True, y=True, alpha=0.5)

        self.y_plot_filtered.getPlotItem().setTitle(
            "The Y Accelerometer - Filtered")
        self.y_plot_filtered.getPlotItem().setMenuEnabled(False)
        self.y_plot_filtered.getPlotItem().setClipToView(False)
        self.y_plot_filtered.getPlotItem().hideAxis('bottom')
        self.y_plot_filtered.getPlotItem().showGrid(x=True, y=True, alpha=0.5)

        self.z_plot_raw.getPlotItem().setTitle("The Z Accelerometer")
        self.z_plot_raw.getPlotItem().setMenuEnabled(False)
        self.z_plot_raw.getPlotItem().setClipToView(False)
        self.z_plot_raw.getPlotItem().hideAxis('bottom')
        self.z_plot_raw.getPlotItem().showGrid(x=True, y=True, alpha=0.5)

        self.z_plot_filtered.getPlotItem().setTitle(
            "The Z Accelerometer - Filtered")
        self.z_plot_filtered.getPlotItem().setMenuEnabled(False)
        self.z_plot_filtered.getPlotItem().setClipToView(False)
        self.z_plot_filtered.getPlotItem().hideAxis('bottom')
        self.z_plot_filtered.getPlotItem().showGrid(x=True, y=True, alpha=0.5)

        fclib.registerNodeType(WiimoteNode, [('Display',)])
        wii_node = self.flowchart.createNode('Wiimote', pos=(0, 0))

        x_plot_raw_node = self.flowchart.createNode(
            'PlotWidget', pos=(-450, -350))
        x_plot_raw_node.setPlot(self.x_plot_raw)
        x_plot_filtered_node = self.flowchart.createNode(
            'PlotWidget', pos=(-300, -350))
        x_plot_filtered_node.setPlot(self.x_plot_filtered)

        y_plot_raw_node = self.flowchart.createNode(
            'PlotWidget', pos=(-150, -350))
        y_plot_raw_node.setPlot(self.y_plot_raw)
        y_plot_filtered_node = self.flowchart.createNode(
            'PlotWidget', pos=(0, -350))
        y_plot_filtered_node.setPlot(self.y_plot_filtered)

        z_plot_raw_node = self.flowchart.createNode(
            'PlotWidget', pos=(150, -350))
        z_plot_raw_node.setPlot(self.z_plot_raw)
        z_plot_filtered_node = self.flowchart.createNode(
            'PlotWidget', pos=(300, -350))
        z_plot_filtered_node.setPlot(self.z_plot_filtered)

        filter_x_node = self.flowchart.createNode(
            'GaussianFilter', pos=(-375, -150))
        filter_x_node.ctrls['sigma'].setValue(5)
        filter_y_node = self.flowchart.createNode(
            'GaussianFilter', pos=(-75, -150))
        filter_y_node.ctrls['sigma'].setValue(5)
        filter_z_node = self.flowchart.createNode(
            'GaussianFilter', pos=(225, -150))
        filter_z_node.ctrls['sigma'].setValue(5)

        self.flowchart.setInput(xDataIn=0)
        self.flowchart.setInput(yDataIn=0)
        self.flowchart.setInput(zDataIn=0)

        self.flowchart.connectTerminals(
            self.flowchart['xDataIn'], wii_node['xDataIn'])
        self.flowchart.connectTerminals(
            self.flowchart['yDataIn'], wii_node['yDataIn'])
        self.flowchart.connectTerminals(
            self.flowchart['zDataIn'], wii_node['zDataIn'])

        self.flowchart.connectTerminals(
            wii_node['xDataOut'], x_plot_raw_node['In'])
        self.flowchart.connectTerminals(
            wii_node['yDataOut'], y_plot_raw_node['In'])
        self.flowchart.connectTerminals(
            wii_node['zDataOut'], z_plot_raw_node['In'])

        self.flowchart.connectTerminals(
            wii_node['xDataOut'], filter_x_node['In'])
        self.flowchart.connectTerminals(
            wii_node['yDataOut'], filter_y_node['In'])
        self.flowchart.connectTerminals(
            wii_node['zDataOut'], filter_z_node['In'])

        self.flowchart.connectTerminals(
            filter_x_node['Out'], x_plot_filtered_node['In'])
        self.flowchart.connectTerminals(
            filter_y_node['Out'], y_plot_filtered_node['In'])
        self.flowchart.connectTerminals(
            filter_z_node['Out'], z_plot_filtered_node['In'])

        self.flowchart.connectTerminals(
            filter_x_node['Out'], self.flowchart['xDataOut'])
        self.flowchart.connectTerminals(
            filter_y_node['Out'], self.flowchart['yDataOut'])
        self.flowchart.connectTerminals(
            filter_z_node['Out'], self.flowchart['zDataOut'])

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

"""
class WiimoteNode(object):
    def __init__(self, n=100):
        self.values = {'x': [], 'y': [], 'z': []}
        self.limit = n

    def add(self, x, y, z):
        if len(self.values['x']) > self.limit:
            self.values['x'].pop(0)
            self.values['y'].pop(0)
            self.values['z'].pop(0)
        self.values['x'].append(x)
        self.values['y'].append(y)
        self.values['z'].append(z)

    def getX(self):
        return self.values['x']

    def getY(self):
        return self.values['y']

    def getZ(self):
        return self.values['z']
"""
if __name__ == "__main__":
    main()
