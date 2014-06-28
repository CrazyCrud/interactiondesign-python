#!/usr/bin/env python
# cod_totaling: utf-8

import sys
from pyqtgraph.flowchart import Flowchart
import pyqtgraph
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
import wiimote
from wiimote_node import *
import math

# disable warning for deprecated npy versio
# define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
import scipy


def main():
    app = QtGui.QApplication(sys.argv)

    demo = Demo()
    #demo.show()

    w = pg.GraphicsView()
    w.show()
    w.resize(400,400)
    w.setWindowTitle('pyqtgraph example: Draw')

    view = pg.ViewBox()
    w.setCentralItem(view)

    # lock the aspect ratio
    #view.setAspectLocked(True)

    imgFile = scipy.misc.imread("/home/michl/Desktop/sf_SharedLinuxFolder/Git/interactiondesign-python/bonus_twohanded/sugar.jpg")

    ## Create image item
    img = pg.ImageItem(imgFile, border='w')
    view.addItem(img)

    ## Set initial view bounds
    view.setRange(QtCore.QRectF(0, 0, 200, 200))

    #while True:
    #    demo.update()

    sys.exit(app.exec_())


# Recognize predefined and custom gestures with the WiiMote using $1 Recognizer
class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        #self.setWindowTitle("Gesture Recognizer")
        #self.show()
        #self.resize(400, 400)

        #w = pg.GraphicsView()
        #w.showFullScreen()
        #w.resize(800,800)
        '''
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.view = pg.ViewBox()
        #self.layout.addWidget(self.view., 0, 0, 2, 1)
        #self..setCentralItem(self.view)


        #view = pg.ViewBox()
        #.setCentralItem(view)
        self.imagesData = []

        self.imagesData.append(self.loadImage())
        self.imageItem = pg.ImageItem(np.array(self.imagesData))
        '''
        #self.view.addItem(self.imageItem)
        #self.layout.addItem(self.imageItem)
        #self.view.setRange(QtCore.QRectF(0, 0, 200, 200))
        #self.imageItem.setRange(QtCore.QRectF(0, 0, 200, 200))

        #...

    def loadImage(self):
        # todo: load image from file
        imageData = np.array([(20, 10), (30, 40), (50, 60)])
        return imageData

    def update(self):
        pyqtgraph.QtGui.QApplication.processEvents()


if __name__ == "__main__":
    main()
