# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class MyMarker(QtGui.QGraphicsRectItem):
    def __init__(self, rect, y_absolute):
        QtGui.QGraphicsRectItem.__init__(self, rect)
        self.qobject = QtCore.QObject()
        self.graphics_rect = rect
        self.y_absolute = y_absolute
        self.icon = QtGui.QPixmap("icon.png")

    def rect(self):
        return self.graphics_rect

    def getQObject(self):
        return self.qobject

    def paint(self, painter, option, widget):
        drawing_rect = QtCore.QRect(
            self.graphics_rect.x(), self.graphics_rect.y(),
            self.graphics_rect.width(), self.graphics_rect.height())
        painter.drawPixmap(drawing_rect, self.icon)

    def hoverEnterEvent(self, event):
        QtGui.QGraphicsRectItem.hoverEnterEvent(self, event)
        self.qobject.emit(QtCore.SIGNAL("markerEntered"), self)

    def hoverLeaveEvent(self, event):
        QtGui.QGraphicsRectItem.hoverLeaveEvent(self, event)
        self.qobject.emit(QtCore.SIGNAL("markerLeft"))

    def saveScreenshot(self, pixmap, rect):
        self.pixmap = pixmap.copy(0, 0, rect.width() / 2, rect.height())

    def getScreenshot(self):
        return self.pixmap
