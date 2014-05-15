# -*- coding: utf-8 -*-

import sys
import time
from random import randint
from PyQt4 import QtGui, QtCore
from MyScrollbar import MyScrollbar


class Demo(QtGui.QWidget):
    def __init__(self, parent=None, items=6):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(100, 100, 300, 300)
        self.setFixedSize(500, 300)
        self.setWindowTitle('Your Scrollbar Helper')
        self.last_timestamp = None
        self.threshold = 600
        self.placeholders = [
            u"""Am Anfang wurde das Universum erschaffen.
        Das machte viele Leute sehr wütend und wurde allenthalben als
        Schritt in die falsche Richtung angesehen.
        """,
            u"""Der beste Drink, den es gibt, ist der pangalaktische Donnergurgler.
        Die Wirkung ist so, als werde einem mit einem riesigen Goldbarren,
        der in Zitronenscheiben gehüllt ist, das Gehirn aus dem Kopf gedroschen.
        """]

        self.scene = QtGui.QGraphicsScene()
        self.scene.setSceneRect(0, 0, 500, 800)
        self.view = QtGui.QGraphicsView(self.scene)

        box_layout = QtGui.QVBoxLayout()
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(0)

        #scroll_area = QtGui.QScrollArea()

        self.scroll_bar = MyScrollbar()

        #scroll_area.setVerticalScrollBar(self.scroll_bar)
        self.view.setVerticalScrollBar(self.scroll_bar)

        self.connect(self.scroll_bar, QtCore.SIGNAL(
            "sliderPressed()"), self.sliderPressed)
        self.connect(self.scroll_bar, QtCore.SIGNAL(
            "valueChanged(int)"), self.sliderPositionChanged)

        #inline_widget = QtGui.QWidget(self)

        #inline_box = QtGui.QVBoxLayout(inline_widget)
        #inline_box.addWidget(self.view)

        font = QtGui.QFont('White Rabbit')
        font.setPointSize(12)

        for i in range(0, items - 1):
            text_passage = QtGui.QGraphicsTextItem(self.placeholders[randint(
                0, len(self.placeholders) - 1)])
            text_passage.setFont(font)
            text_passage.setPos(0, i * 200)
            self.scene.addItem(text_passage)

            """
            horizontal_layout_header = QtGui.QHBoxLayout()
            horizontal_layout_quote = QtGui.QHBoxLayout()
            horizontal_layout_header.addWidget(QtGui.QLabel(
                "Quote #%d" % i, self))
            horizontal_layout_quote.addWidget(QtGui.QTextEdit(
                self.placeholders[randint(0, len(self.placeholders) - 1)], self))
            horizontal_layout_header.addStretch(1)
            horizontal_layout_quote.addStretch(1)
            inline_box.addLayout(horizontal_layout_header)
            inline_box.addLayout(horizontal_layout_quote)
            """

        #scroll_area.setWidget(inline_widget)

        #box_layout.addWidget(scroll_area)
        box_layout.addWidget(self.view)
        self.setLayout(box_layout)

    def sliderPressed(self):
        current_stamp = int(round(time.time() * 1000))
        if self.last_timestamp is None:
            self.last_timestamp = current_stamp
            return
        elif (current_stamp - self.last_timestamp) < self.threshold:
            self.scroll_bar.setMarker(self)
            self.update()
            self.last_timestamp = None
            return
        else:
            self.last_timestamp = current_stamp

    def sliderPositionChanged(self, value):
        self.scroll_bar.updatePosition(value)
        print "Value ", value

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            value = self.scroll_bar.getNextMaker()
            if value is not None:
                print "Jump to mark ", value
                self.scroll_bar.setValue(value)


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
