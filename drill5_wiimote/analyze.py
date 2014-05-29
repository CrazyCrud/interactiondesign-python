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

        self.x_plot = self.addPlot()
        self.x_plot.setTitle("The X Accelerometer")
        self.x_plot.setMenuEnabled(False)
        self.x_plot.setClipToView(True)
        self.x_plot.hideAxis('bottom')
        self.nextRow()
        self.y_plot = self.addPlot()
        self.y_plot.setTitle("The Y Accelerometer")
        self.y_plot.setMenuEnabled(False)
        self.y_plot.setClipToView(True)
        self.y_plot.hideAxis('bottom')
        self.nextRow()
        self.z_plot = self.addPlot()
        self.z_plot.setTitle("The Z Accelerometer")
        self.z_plot.setMenuEnabled(False)
        self.z_plot.setClipToView(True)
        self.z_plot.hideAxis('bottom')

    def add(self, x, y, z):
        self.node.add(x, y, z)

    def drawPlots(self):
        values = self.node.get()
        if values is None:
            return
        else:
            self.x_plot.plot(numpy.random.normal(size=100), clear=True)
            self.y_plot.plot(numpy.random.normal(size=100), clear=True)
            self.z_plot.plot(numpy.random.normal(size=100), clear=True)
            #self.x_plot.plot(values['x'], clear=True)
            #self.y_plot.plot(values['y'], clear=True)
            #self.z_plot.plot(values['z'], clear=True)
            pyqtgraph.QtGui.QApplication.processEvents()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()


class WiimoteNode(object):
    def __init__(self, n=100):
        self.coordinates = {'x': [], 'y': [], 'z': []}
        self.limit = n

    def add(self, x, y, z):
        if len(self.coordinates['x']) > self.limit:
            self.coordinates['x'].pop(0)
            self.coordinates['y'].pop(0)
            self.coordinates['z'].pop(0)
        self.coordinates['x'].append(x)
        self.coordinates['y'].append(y)
        self.coordinates['z'].append(z)

    def get(self):
        if len(self.coordinates['x']) == 0:
            return None
        else:
            x = self.coordinates['x'][len(self.coordinates['x']) - 1]
            y = self.coordinates['y'][len(self.coordinates['y']) - 1]
            z = self.coordinates['z'][len(self.coordinates['z']) - 1]
            return {'x': x, 'y': y, 'z': z}

if __name__ == "__main__":
    main()
