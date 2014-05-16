# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class MyMarker(QtGui.QGraphicsRectItem):
    def __init__(self, rect):
        QtGui.QGraphicsRectItem.__init__(self)

        self.graphics_rect = rect

    def rect(self):
        return self.graphics_rect
