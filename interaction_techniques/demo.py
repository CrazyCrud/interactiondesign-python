# -*- coding: utf-8 -*-

import sys
import time
from random import randint
from PyQt4 import QtGui, QtCore
from MyScrollbar import MyScrollbar
from MyTextPassage import MyTextPassage


class Demo(QtGui.QWidget):
    def __init__(self, parent=None, items=7):
        #construct widget as child of parent
        QtGui.QWidget.__init__(self, parent)

        self.window_width = 600
        self.window_height = 300
        self.scrollbar_offset = 20

        #define window size and position
        self.setGeometry(100, 100, self.window_width,
            self.window_height)

        self.setFixedSize(self.window_width + self.scrollbar_offset,
            self.window_height)


        self.setWindowTitle('Your Scrollbar Helper')

        self.last_timestamp = None
        self.threshold = 600

        s1 = (
            u"Am Anfang wurde das Universum erschaffen. "
            u"Das machte viele Leute sehr wütend und wurde allenthalben "
            u"als Schritt in die falsche Richtung angesehen."
        )

        s2 = (
            u"Der beste Drink, den es gibt, ist der "
            u"pangalaktische Donnergurgler. Die Wirkung ist so, "
            u"als werde einem mit einem riesigen Goldbarren, "
            u"der in Zitronenscheiben gehüllt ist, das Gehirn "
            u"aus dem Kopf gedroschen."
        )

        self.placeholders = [s1, s2]

        #enable mouse tracking
        self.setMouseTracking(True)

        self.setContentsMargins(0, 0, 0, 0)

        #create container scene for graphic items
        self.scene = QtGui.QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.window_width, 700)

        #create view which a vertical scroll bar
        self.view = QtGui.QGraphicsView(self.scene)
        self.scroll_bar = MyScrollbar(self)
        self.view.setVerticalScrollBar(self.scroll_bar)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        #connect signals(triggers) to slots(bindings)
        self.connect(self.scroll_bar, QtCore.SIGNAL(
            "sliderPressed()"), self.sliderPressed)
        self.connect(self.scroll_bar, QtCore.SIGNAL(
            "valueChanged(int)"), self.sliderPositionChanged)

        #add panel to scene
        self.panel = QtGui.QGraphicsWidget()
        self.scene.addItem(self.panel)

        #create vertical box
        box_layout = QtGui.QVBoxLayout()
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(0)

        #create vertical inlinebox
        inline_box = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        inline_box.setContentsMargins(10, 10, 10, 10)
        inline_box.setSpacing(0)
        self.panel.setLayout(inline_box)

        font = QtGui.QFont('White Rabbit')
        font.setPointSize(12)

        #add texts randomly
        for i in range(0, items):
            text_passage = MyTextPassage(self.placeholders[randint(
                0, len(self.placeholders) - 1)],
                "#" + str(i + 1), self.window_width, font)

            inline_box.addItem(text_passage)

            self.scene.setSceneRect(0, 0, self.window_width,
                (i + 1) * text_passage.label_height)

            self.update()

        #assemble widgets
        box_layout.addWidget(self.view)
        self.setLayout(box_layout)

    def sliderPressed(self):
        current_stamp = int(round(time.time() * 1000))
        if self.last_timestamp is None:
            #first click
            self.last_timestamp = current_stamp
            return
        elif (current_stamp - self.last_timestamp) < self.threshold:
            #doubleclick
            self.scroll_bar.setMarker()
            self.update()
            self.last_timestamp = None
            return
        else:
            #too long, no doubleclick
            self.last_timestamp = current_stamp

    def sliderPositionChanged(self, value):
        self.scroll_bar.updatePosition(value)

    def keyPressEvent(self, event):
        key = event.key()
        value = None
        if key == QtCore.Qt.Key_Space:
            value = self.scroll_bar.getNextMaker()
        elif key == QtCore.Qt.Key_1:
            value = self.scroll_bar.getNextMaker(1)
        elif key == QtCore.Qt.Key_2:
            value = self.scroll_bar.getNextMaker(2)
        elif key == QtCore.Qt.Key_3:
            value = self.scroll_bar.getNextMaker(3)
        elif key == QtCore.Qt.Key_4:
            value = self.scroll_bar.getNextMaker(4)
        elif key == QtCore.Qt.Key_5:
            value = self.scroll_bar.getNextMaker(5)
        elif key == QtCore.Qt.Key_6:
            value = self.scroll_bar.getNextMaker(6)
        elif key == QtCore.Qt.Key_7:
            value = self.scroll_bar.getNextMaker(7)
        elif key == QtCore.Qt.Key_8:
            value = self.scroll_bar.getNextMaker(8)
        elif key == QtCore.Qt.Key_9:
            value = self.scroll_bar.getNextMaker(9)
        if value is not None:
            self.scroll_bar.setValue(value)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            absolute_pos = event.pos()
            absolute_pos.setY(self.scroll_bar.value() + absolute_pos.y())
            value = self.scroll_bar.isMarkerClicked(absolute_pos)
            if value is not None:
                self.scroll_bar.setValue(value)


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
