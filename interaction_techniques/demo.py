# -*- coding: utf-8 -*-

import sys
from random import randint
from PyQt4 import QtGui, QtCore


class Demo(QtGui.QWidget):
    def __init__(self, parent=None, items=20):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(100, 100, 300, 300)
        self.setWindowTitle('Your Scrollbar Helper')
        self.placeholders = [
            u"""Am Anfang wurde das Universum erschaffen.
        Das machte viele Leute sehr wütend und wurde allenthalben als
        Schritt in die falsche Richtung angesehen.
        """,
            u"""Der beste Drink, den es gibt, ist der pangalaktische Donnergurgler.
        Die Wirkung ist so, als werde einem mit einem riesigen Goldbarren,
        der in Zitronenscheiben gehüllt ist, das Gehirn aus dem Kopf gedroschen.
        """]
        box_layout = QtGui.QVBoxLayout(self)
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(0)

        scroll_area = QtGui.QScrollArea()

        inline_widget = QtGui.QWidget(self)
        inline_box = QtGui.QVBoxLayout(inline_widget)

        for i in range(1, (items + 1)):
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

        scroll_area.setWidget(inline_widget)
        box_layout.addWidget(scroll_area)


def main():
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
