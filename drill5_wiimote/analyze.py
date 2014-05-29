# import wiimote
import sys
import time
from random import randint
import numpy
import pyqtgraph
from PyQt4 import QtGui, QtCore


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()
    # wm = getWiimote()

    while True:
        demo.add(randint(0, 100), randint(0, 100), randint(0, 100))
        demo.drawPlots()
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


class Demo(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()
        self.node = WiimoteNode()

        self.setWindowTitle("Plotting the Wiimote")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.showFullScreen()
        pyqtgraph.setConfigOptions(antialias=True)

        self.x_plot_raw = self.addPlot()
        self.x_plot_raw.setTitle("The X Accelerometer")
        self.x_plot_raw.setMenuEnabled(False)
        self.x_plot_raw.setClipToView(False)
        self.x_plot_raw.hideAxis('bottom')
        self.x_plot_raw.showGrid(x=True, y=True, alpha=0.5)
        self.nextColumn()
        self.x_plot_filtered = self.addPlot()
        self.x_plot_filtered.setTitle("The X Accelerometer - Filtered")
        self.x_plot_filtered.setMenuEnabled(False)
        self.x_plot_filtered.setClipToView(False)
        self.x_plot_filtered.hideAxis('bottom')
        self.x_plot_filtered.showGrid(x=True, y=True, alpha=0.5)
        self.nextRow()
        self.y_plot_raw = self.addPlot()
        self.y_plot_raw.setTitle("The Y Accelerometer")
        self.y_plot_raw.setMenuEnabled(False)
        self.y_plot_raw.setClipToView(False)
        self.y_plot_raw.hideAxis('bottom')
        self.y_plot_raw.showGrid(x=True, y=True, alpha=0.5)
        self.nextColumn()
        self.y_plot_filtered = self.addPlot()
        self.y_plot_filtered.setTitle("The Y Accelerometer - Filtered")
        self.y_plot_filtered.setMenuEnabled(False)
        self.y_plot_filtered.setClipToView(False)
        self.y_plot_filtered.hideAxis('bottom')
        self.y_plot_filtered.showGrid(x=True, y=True, alpha=0.5)
        self.nextRow()
        self.z_plot_raw = self.addPlot()
        self.z_plot_raw.setTitle("The Z Accelerometer")
        self.z_plot_raw.setMenuEnabled(False)
        self.z_plot_raw.setClipToView(False)
        self.z_plot_raw.hideAxis('bottom')
        self.z_plot_raw.showGrid(x=True, y=True, alpha=0.5)
        self.nextColumn()
        self.z_plot_filtered = self.addPlot()
        self.z_plot_filtered.setTitle("The Z Accelerometer - Filtered")
        self.z_plot_filtered.setMenuEnabled(False)
        self.z_plot_filtered.setClipToView(False)
        self.z_plot_filtered.hideAxis('bottom')
        self.z_plot_filtered.showGrid(x=True, y=True, alpha=0.5)

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

    def get(self):
        if len(self.values['x']) == 0:
            return None
        else:
            return self.values

if __name__ == "__main__":
    main()
