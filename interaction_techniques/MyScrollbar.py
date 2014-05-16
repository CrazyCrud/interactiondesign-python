# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class MyScrollbar(QtGui.QScrollBar):
    def __init__(self, ui):
        QtGui.QScrollBar.__init__(self)
        self.setMouseTracking(True)
        self.current_position = 0
        self.current_marker = 0
        self.cursor_pos = 0
        self.rect_visualization_w = 12
        self.rect_visualization_h = 6
        self.markers = []
        self.visualizations = {}
        self.ui = ui


    def mousePressEvent(self, event):
        QtGui.QScrollBar.mousePressEvent(self, event)
        self.cursor_pos = event.pos()
        """
        if event.button() == QtCore.Qt.RightButton:
            self.emit(QtCore.SIGNAL("scrollbarPressed"))
        else:
            QtGui.QScrollBar.mousePressEvent(self, event)
        """

    def updatePosition(self, value):
        self.current_position = value

    def setMarker(self):
        index = None
        try:
            index = self.markers.index(self.current_position)
            self.removeMarkers(index)
        except ValueError:
            index = None
        if index is None:
            self.markers.append(self.current_position)
            self.sortMarkers()
            self.visualizeMarker(self.current_position)

    def sortMarkers(self):
        self.markers.sort(key=int, reverse=True)

    def removeMarkers(self, index):
        marker = self.markers.pop(index)
        self.ui.scene.removeItem(self.visualizations[marker])
        del self.visualizations[marker]
        self.sortMarkers()
        self.ui.update()

    def visualizeMarker(self, marker):
        if (self.ui is not None) and (self.ui.scene is not None):
            rect_marker = QtCore.QRectF(self.ui.window_width - self.rect_visualization_w,
                marker + self.cursor_pos.y(), self.rect_visualization_w,
                self.rect_visualization_h)

            self.visualizations[marker] = self.ui.scene.addRect(
                rect_marker, QtGui.QPen(QtCore.Qt.red),
                QtGui.QBrush(QtGui.QColor(255, 0, 0)))
            self.visualizations[marker].setCursor(QtCore.Qt.PointingHandCursor)
            self.visualizations[marker].setAcceptHoverEvents(True)

    def getNextMaker(self):
        next_marker = None
        if len(self.markers) > 0:
            for i in range(0, len(self.markers)):
                if self.markers[i] < self.current_position:
                    next_marker = self.markers[i]
                    return next_marker
            next_marker = self.markers[0]
        return next_marker

    def isMarkerClicked(self, pos):
        value = None
        for k, v in self.visualizations.iteritems():
            if v.contains(pos) is True:
                value = k
                break
        return value
