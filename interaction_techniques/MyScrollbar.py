# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from MyMarker import MyMarker


class MyScrollbar(QtGui.QScrollBar):
    def __init__(self, ui):
        QtGui.QScrollBar.__init__(self)
        self.pixmap = QtGui.QLabel()
        self.setMouseTracking(True)
        self.current_position = 0
        self.current_marker = 0
        self.cursor_pos = 0
        self.rect_visualization_w = 35
        self.rect_visualization_h = 35
        self.markers = []
        self.visualizations = {}
        self.ui = ui
        self.counter = 0

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
        print "slider current position", self.current_position
        #print "self.visualizations.iteritems()", len(self.visualizations)
        for k, v in self.visualizations.iteritems():
            y_relative = self.value() + v.y_absolute * self.ui.height() / self.ui.scene.sceneRect().height()
            #v.graphics_rect.setY(y_relative)

            #rect_marker = QtCore.QRectF(self.ui.window_width - self.rect_visualization_w,
            #    y_relative, self.rect_visualization_w,
            #    self.rect_visualization_h)

            self.counter += 1
            absoluteY = self.visualizations.itervalues().next().y_absolute
            print self.counter
            rect_marker = QtCore.QRectF(self.ui.window_width - self.rect_visualization_w,
                absoluteY, self.rect_visualization_w,
                self.counter)

            print "nextItem", self.visualizations.itervalues().next().y_absolute
            #self.ui.scene.removeItem(self.visualizations.itervalues().next())
            #self.ui.update()
            #self.ui.scene.addItem(self.visualizations.itervalues().next())
            #rect_marker.update()
            self.ui.update()
            v.update(rect_marker)
            print "y_relative", y_relative
            print "rect_marker", rect_marker

        self.update()
        self.ui.update()

    def setMarker(self):
        index = None
        try:
            index = self.markers.index(self.current_position)
            self.removeMarkers(index)
        except ValueError:
            index = None
        if index is None:
            self.markers.append(self.current_position)
            #self.sortMarkers()
            self.visualizeMarker(self.current_position)

    def sortMarkers(self):
        #self.markers.sort(key=int, reverse=True)
        return sorted(self.markers, key=int, reverse=True)

    def removeMarkers(self, index):
        marker = self.markers.pop(index)
        self.ui.scene.removeItem(self.visualizations[marker])
        del self.visualizations[marker]
        #self.sortMarkers()
        self.ui.update()

    def visualizeMarker(self, marker):
        if (self.ui is not None) and (self.ui.scene is not None):
            y_absolute = marker + self.cursor_pos.y()
            y_relative = self.value() + y_absolute * self.ui.height() / self.ui.scene.sceneRect().height()

            print "Relative y position: ", y_relative
            print "Absolute y position: ", y_absolute

            rect_marker = QtCore.QRectF(self.ui.window_width - self.rect_visualization_w,
                y_absolute, self.rect_visualization_w,
                self.rect_visualization_h)

            tmp_rect = MyMarker(rect_marker, y_absolute)
            tmp_rect.saveScreenshot(self.makeScreenshot(), self.ui.scene.sceneRect())
            tmp_rect.setCursor(QtCore.Qt.PointingHandCursor)
            tmp_rect.setAcceptHoverEvents(True)
            tmp_rect.setZValue(1)
            self.visualizations[marker] = tmp_rect

            qobject = self.visualizations[marker].getQObject()
            self.connect(qobject, QtCore.SIGNAL(
            "markerEntered"), self.markerEntered)
            self.connect(qobject, QtCore.SIGNAL(
            "markerLeft"), self.markerLeft)

            self.ui.scene.addItem(self.visualizations[marker])
            self.ui.update()

    def makeScreenshot(self):
        return QtGui.QPixmap.grabWindow(self.ui.winId())

    def getNextMaker(self, index=None):
        next_marker = None
        if index is None:
            markers_asc = self.sortMarkers()
            if len(markers_asc) > 0:
                for i in range(0, len(markers_asc)):
                    if markers_asc[i] < self.current_position:
                        next_marker = markers_asc[i]
                        return next_marker
                next_marker = markers_asc[0]
        else:
            index -= 1
            if index < len(self.markers):
                next_marker = self.markers[index]
        return next_marker

    def isMarkerClicked(self, pos):
        value = None
        for k, v in self.visualizations.iteritems():
            if v.rect().contains(pos) is True:
                self.markerLeft()
                value = k
                break
        return value

    def markerEntered(self, marker):
        screenshot = marker.getScreenshot()
        self.pixmap = self.ui.scene.addPixmap(screenshot)
        self.pixmap.setOffset(self.ui.width() / 2, self.value())
        self.ui.update()

    def markerLeft(self):
        self.ui.scene.removeItem(self.pixmap)
        self.ui.update()
