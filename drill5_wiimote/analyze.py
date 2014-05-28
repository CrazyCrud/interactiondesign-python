#import wiimote
import sys
import numpy
import pyqtgraph
from PyQt4 import QtGui, QtCore


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())


class Demo(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()
        self.node = WiimoteNode()

        self.setWindowTitle("Plotting the Wiimote")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.showFullScreen()

        self.x_plot = self.addPlot()
        self.x_plot.setTitle("The X Accelerometer")
        self.nextRow()
        self.y_plot = self.addPlot()
        self.y_plot.setTitle("The Y Accelerometer")
        self.nextRow()
        self.z_plot = self.addPlot()
        self.z_plot.setTitle("The Z Accelerometer")

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()


class WiimoteNode(object):
    def __init__(self, n=20):
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
            x = self.coordinates['x'][len(self.coordinates['x'] - 1)]
            y = self.coordinates['y'][len(self.coordinates['y'] - 1)]
            z = self.coordinates['z'][len(self.coordinates['z'] - 1)]
            return {'x': x, 'y': y, 'z': z}

if __name__ == "__main__":
    main()
