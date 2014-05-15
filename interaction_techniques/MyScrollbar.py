# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class MyScrollbar(QtGui.QScrollBar):
    def __init__(self):
        QtGui.QScrollBar.__init__(self)
        self.current_position = 0
        self.current_marker = 0
        self.rect_visualization_w = 28
        self.rect_visualization_h = 6
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

    def setMarker(self, ui):
        index = None
        try:
            index = self.markers.index(self.current_position)
        except ValueError:
            index = None
        if index is None:
            print "Set marker at ", self.current_position
            self.markers.append(self.current_position)
            self.sortMarkers()
            self.visualizeMarker(ui, self.current_position)

    def sortMarkers(self):
        self.markers.sort(key=int, reverse=True)

    def visualizeMarker(self, ui, marker):
        if (ui is not None) and (ui.scene is not None):
            ui.scene.addRect(QtCore.QRectF(ui.width() - self.rect_visualization_w,
                marker, self.rect_visualization_w,
                self.rect_visualization_h), QtGui.QPen(QtCore.Qt.red),
                QtGui.QBrush(QtGui.QColor(255, 0, 0)))
            print "Draw rect at ", ui.width() - self.rect_visualization_w, marker

    def getNextMaker(self):
        next_marker = None
        if len(self.markers) > 0:
            for i in range(0, len(self.markers)):
                if self.markers[i] < self.current_position:
                    next_marker = self.markers[i]
                    return next_marker
            next_marker = self.markers[0]
        return next_marker
