# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore


class MyTextPassage(QtGui.QGraphicsWidget):
    def __init__(self, text, headline, width, font, parent=None):
        QtGui.QGraphicsWidget.__init__(self, parent)
        self.text = text
        self.headline = headline
        self.font = font
        self.label_width = width
        self.label_height = 100

    def sizeHint(self, which, constraint=QtCore.QSizeF()):
        return QtCore.QSizeF(self.label_width, self.label_height)

    def paint(self, painter, option, widget):
        qp = QtGui.QPen()
        qp.setWidth(1)
        qp.setBrush(QtCore.Qt.black)
        painter.setPen(qp)
        text_rect = QtCore.QRect(0, 0,
            self.label_width, self.label_height)
        painter.setFont(self.font)
        painter.drawText(text_rect, QtCore.Qt.TextWordWrap | QtCore.Qt.AlignLeft,
            self.headline + "\n" + self.text)
