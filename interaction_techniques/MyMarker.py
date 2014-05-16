# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class MyMarker(QtGui.QGraphicsRectItem):
    def __init__(self, rect):
        QtGui.QGraphicsRectItem.__init__(self, rect)

        self.graphics_rect = rect

    def rect(self):
        return self.graphics_rect

    def paint(self, painter, option, widget):
        print "Paint Marker"
        qp = QtGui.QPen()
        qp.setBrush(QtGui.QColor(255, 0, 0))
        painter.setPen(qp)
        drawing_rect = QtCore.QRect(self.graphics_rect.x(), self.graphics_rect.y(),
            self.graphics_rect.width(), self.graphics_rect.height())
        painter.fillRect(drawing_rect, QtGui.QColor(255, 0, 0))
        painter.drawRect(drawing_rect)

    def hoverEnterEvent(self, event):
        QtGui.QGraphicsRectItem.hoverEnterEvent(self, event)
        print "Hover enter..."

    def hoverLeaveEvent(self, event):
        QtGui.QGraphicsRectItem.hoverLeaveEvent(self, event)
        print "Hover leave..."

    def saveScreenshot(self):
        pass

    def getScreenshot(self):
        pass
