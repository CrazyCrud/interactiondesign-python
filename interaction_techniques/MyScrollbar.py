# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class MyScrollbar(QtGui.QScrollBar):
    def __init__(self):
        QtGui.QScrollBar.__init__(self)
        self.current_position = 0
        self.current_marker = 0
        self.markers = []

    def mousePressEvent(self, event):
        QtGui.QScrollBar.mousePressEvent(self, event)
        """
        if event.button() == QtCore.Qt.RightButton:
            self.emit(QtCore.SIGNAL("scrollbarPressed"))
        else:
            QtGui.QScrollBar.mousePressEvent(self, event)
        """

    def updatePosition(self, value):
        self.current_position = value

    def setMarker(self):
        self.markers.append(self.current_position)

    def getNextMaker(self):
        if len(self.markers) > 0 and self.current_marker < len(self.markers):
            return self.markers[self.current_marker]
