# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class MyMarker(QtGui.QGraphicsRectItem):
    def __init__(self, rect):
        QtGui.QGraphicsRectItem.__init__(self, rect)
        self.qobject = QtCore.QObject()
        self.graphics_rect = rect

    def rect(self):
        return self.graphics_rect

    def getQObject(self):
        return self.qobject

    def paint(self, painter, option, widget):
        qp = QtGui.QPen()
        qp.setBrush(QtGui.QColor(255, 0, 0))
        painter.setPen(qp)
        drawing_rect = QtCore.QRect(self.graphics_rect.x(), self.graphics_rect.y(),
            self.graphics_rect.width(), self.graphics_rect.height())
        painter.fillRect(drawing_rect, QtGui.QColor(255, 0, 0))
        painter.drawRect(drawing_rect)

    def hoverEnterEvent(self, event):
        QtGui.QGraphicsRectItem.hoverEnterEvent(self, event)
        self.qobject.emit(QtCore.SIGNAL("markerEntered"), self)

    def hoverLeaveEvent(self, event):
        QtGui.QGraphicsRectItem.hoverLeaveEvent(self, event)
        self.qobject.emit(QtCore.SIGNAL("markerLeft"))

    def saveScreenshot(self, pixmap, rect):
        print "Save screenshot ", pixmap.width()
        self.pixmap = pixmap.copy(0, 0, rect.width() - self.graphics_rect.width() * 2, rect.height())

    def getScreenshot(self):
        return self.pixmap
