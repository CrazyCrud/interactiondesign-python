import sys
import time
from random import randint
from PyQt4 import QtGui, QtCore
from MyScrollbar import MyScrollbar
from MyTextPassage import MyTextPassage

class PositionTest(QtGui.QWidget):
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

        #enable mouse tracking
        self.setMouseTracking(True)

        self.setContentsMargins(0, 0, 0, 0)

        #create container scene for graphic items
        self.scene = QtGui.QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.window_width, 700)

        #create view which a vertical scroll bar
        self.view = QtGui.QGraphicsView(self.scene)

        #add panel to scene
        self.panel = QtGui.QGraphicsWidget()
        self.scene.addItem(self.panel)

        self.initMarker()

    def initMarker(self):
    	marker = 20
    	y_absolute = marker + 40
        y_relative = 40

        print "Relative y position: ", y_relative
        print "Absolute y position: ", y_absolute

        rect_marker = QtCore.QRectF(100,
            y_absolute, 50,
            50)
        
        self.scene.addItem(rect_marker)
        self.update()


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
        print "Repaint marker"
        qp = QtGui.QPen()
        qp.setBrush(QtGui.QColor(255, 0, 0))
        painter.setPen(qp)

        drawing_rect = QtCore.QRect(self.graphics_rect.x(), self.graphics_rect.y(),
            self.graphics_rect.width(), self.graphics_rect.height())
        """
        painter.fillRect(drawing_rect, QtGui.QColor(255, 0, 0))
        painter.drawRect(drawing_rect)
        """
        painter.drawPixmap(drawing_rect, self.icon)

def main():
    app = QtGui.QApplication(sys.argv)
    positionTest = PositionTest()
    positionTest.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
