# import wiimote
import sys
import time
from random import randint
import numpy
from pyqtgraph.flowchart import Flowchart
import pyqtgraph
from PyQt4 import QtGui, QtCore


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()
    # wm = getWiimote()

    """
    while True:
        demo.add(randint(0, 100), randint(0, 100), randint(0, 100))
        #demo.drawPlots()
        time.sleep(0.05)
    """
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
        self.node = WiimoteNode()

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

        layout.addWidget(self.x_plot_raw, 0, 1, 1, 1)
        layout.addWidget(self.x_plot_filtered, 0, 2, 1, 1)
        layout.addWidget(self.y_plot_raw, 1, 1, 1, 1)
        layout.addWidget(self.y_plot_filtered, 1, 2, 1, 1)
        layout.addWidget(self.z_plot_raw, 2, 1, 1, 1)
        layout.addWidget(self.z_plot_filtered, 2, 2, 1, 1)

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

        # placeholder data
        data = numpy.random.normal(size=1000)
        data[200:300] += 1
        data += numpy.sin(numpy.linspace(0, 100, 1000))

        self.flowchart.setInput(xDataIn=data)
        self.flowchart.setInput(yDataIn=data)
        self.flowchart.setInput(zDataIn=data)

        self.flowchart.connectTerminals(
            self.flowchart['xDataIn'], x_plot_raw_node['In'])
        self.flowchart.connectTerminals(
            self.flowchart['yDataIn'], y_plot_raw_node['In'])
        self.flowchart.connectTerminals(
            self.flowchart['zDataIn'], z_plot_raw_node['In'])

        self.flowchart.connectTerminals(
            self.flowchart['xDataIn'], filter_x_node['In'])
        self.flowchart.connectTerminals(
            self.flowchart['yDataIn'], filter_y_node['In'])
        self.flowchart.connectTerminals(
            self.flowchart['zDataIn'], filter_z_node['In'])

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

    def add(self, x, y, z):
        self.node.add(x, y, z)

    def drawPlots(self):
        values = self.node.get()
        if values is None:
            return
        else:
            self.x_plot_raw.plot(values['x'], clear=True)
            self.y_plot_raw.plot(values['y'], clear=True)
            self.z_plot_raw.plot(values['z'], clear=True)
            pyqtgraph.QtGui.QApplication.processEvents()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()


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

if __name__ == "__main__":
    main()
