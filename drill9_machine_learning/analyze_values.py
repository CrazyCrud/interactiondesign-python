# -*- coding: utf-8 -*-
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import sys
import wiimote
from wiimote_node import *
import scipy
import math
import os
import csv
from sklearn.preprocessing import scale, StandardScaler, MinMaxScaler

'''
The demo application identifies three different states:
it detects when the person - who holds the wiimote in one
of his hands - stands still, when the person walks and when
the person runs
'''


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

        self.setWindowTitle("Wiimote Activity")
        self.showFullScreen()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.xData = []
        self.yData = []
        self.zData = []
        self.readData()

    def readData(self):
        f = open('walk1.txt', 'r')

        for line in f:
            stripped = [x.strip() for x in line.split(',')]
            self.xData.append(stripped[0])
            self.yData.append(stripped[1])
            self.zData.append(stripped[2])

        #s = MinMaxScaler()
        #s.fit(zip(self.xData))

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    main()
