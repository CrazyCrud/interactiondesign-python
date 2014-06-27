#!/usr/bin/env python
# cod_totaling: utf-8

import sys
from pyqtgraph.flowchart import Flowchart
import pyqtgraph
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
import wiimote
from wiimote_node import *


def main():
    app = QtGui.QApplication(sys.argv)

    demo = Demo()
    demo.show()

    while True:
        demo.update()

    sys.exit(app.exec_())


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Gesture Recognizer")
        self.showFullScreen()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })
        self.layout.addWidget(self.fc.widget(), 0, 0, 2, 1)

        self.path = {'x': [], 'y': []}
        self.threshold = 50
        self.sample_size = 64
        self.default_msg = 'No template matched...'
        self.error_ir_msg = 'No ir-values received'
        self.error_wiimote_msg = 'No wiimote connected'
        self.error_template_msg = 'No template could be created'

        self.pressed_key = None

        self.dollar = dollar.Recognizer()

        self.config_nodes()
        self.config_layout()
        self.setup_templates()

        self.get_wiimote()

    '''
    The command-line argument is parsed and used to establish
    a connection to the wiimote
    '''
    def get_wiimote(self):
        if len(sys.argv) == 1:
            addr, name = wiimote.find()[0]
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
        print("Connecting to %s (%s)" % (name, addr))

        self.wiimoteNode.text.setText(addr)
        self.wiimoteNode.connect_wiimote()

    '''
    A wiimote node and a buffer node are created as well as a
    custom node which returns the position of the most intense
    light source detected by the wiimote
    '''
    def config_nodes(self):
        self.wiimoteNode = self.fc.createNode('Wiimote', pos=(0, 0), )
        self.bufferNode = self.fc.createNode('Buffer', pos=(0, -150))
        self.pointVisNode = self.fc.createNode('Vis2D', pos=(-150, 150))

        self.bufferNode.setBufferSize(128)

        self.fc.connectTerminals(
            self.wiimoteNode['irVals'],
            self.bufferNode['dataIn'])
        self.fc.connectTerminals(
            self.bufferNode['dataOut'],
            self.pointVisNode['irVals'])

    '''
    A scatterplot is used to display the infrafred data and a text label
    should indicate if the user input matches a predefined template
    '''
    def config_layout(self):
        gview = pg.GraphicsLayoutWidget()
        self.layout.addWidget(gview, 0, 1, 2, 1)
        self.templatePlot = gview.addPlot()
        self.templateScatter = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 255, 0, 120))
        self.templatePlot.addItem(self.templateScatter)
        self.templatePlot.setTitle("Template")
        self.setRange(self.templatePlot)

        #self.layout.addWidget(gview, 0, 1, 2, 1)
        self.pathPlot = gview.addPlot()
        self.pathScatter = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        self.pathPlot.addItem(self.pathScatter)
        self.pathPlot.setTitle("Path")
        self.setRange(self.pathPlot)

        self.label = QtGui.QLabel()
        self.label.setText(self.default_msg)
        font = QtGui.QFont("Arial")
        font.setPointSize(32)
        self.label.setFont(font)
        self.layout.addWidget(self.label, 2, 1, 1, 1)

    '''
    Three default templates are added to the recognizer
    '''
    def setup_templates(self):
        circlePoints = [(269, 84), (263, 86), (257, 92), (253, 98), (249, 104), (245, 114), (243, 122), (239, 132), (237, 142), (235, 152), (235, 162), (235, 172), (235, 180), (239, 190), (245, 198), (251, 206), (259, 212), (267, 216), (275, 218), (281, 222), (287, 224), (295, 224), (301, 226), (311, 226), (319, 226), (329, 226), (339, 226), (349, 226), (352, 226), (360, 226), (362, 225), (366, 219), (367, 217), (367, 209), (367, 206), (367, 198), (367, 190), (367, 182), (367, 174), (365, 166), (363, 158), (359, 152), (355, 146), (353, 138), (349, 134), (345, 130), (341, 124), (340, 122), (338, 121), (337, 119), (336, 117), (334, 116), (332, 115), (331, 114), (327, 110), (325, 109), (323, 109), (321, 108), (320, 108), (318, 107), (316, 107), (315, 107), (314, 107), (313, 107), (312, 107), (311, 107), (310, 107), (309, 106), (308, 106), (307, 105), (306, 105), (305, 105), (304, 105), (303, 104), (302, 104), (301, 104), (300, 104), (299, 103), (298, 103), (296, 102), (295, 101), (293, 101), (292, 100), (291, 100), (290, 100), (289, 100), (288, 100), (288, 99), (287, 99), (287, 99)]
        squarePoints = [(193, 123), (193, 131), (193, 139), (195, 151), (197, 161), (199, 175), (201, 187), (205, 201), (207, 213), (209, 225), (213, 235), (213, 243), (215, 251), (215, 254), (217, 262), (217, 264), (217, 266), (217, 267), (218, 267), (219, 267), (221, 267), (224, 267), (227, 267), (237, 267), (247, 265), (259, 263), (273, 261), (287, 261), (303, 259), (317, 257), (331, 255), (347, 255), (361, 253), (375, 253), (385, 253), (395, 251), (403, 249), (406, 249), (408, 249), (408, 248), (409, 248), (409, 246), (409, 245), (409, 242), (409, 234), (409, 226), (409, 216), (407, 204), (407, 194), (405, 182), (403, 172), (403, 160), (401, 150), (399, 140), (399, 130), (397, 122), (397, 119), (397, 116), (396, 114), (396, 112), (396, 111), (396, 110), (396, 109), (396, 108), (396, 107), (396, 106), (396, 105), (394, 105), (392, 105), (384, 105), (376, 105), (364, 105), (350, 107), (334, 109), (318, 111), (306, 113), (294, 115), (286, 117), (278, 117), (272, 119), (269, 119), (263, 121), (260, 121), (254, 123), (251, 123), (245, 125), (243, 125), (242, 125), (241, 126), (240, 126), (238, 127), (236, 127), (232, 128), (231, 128), (231, 129), (230, 129), (228, 129), (227, 129), (226, 129), (225, 129), (224, 129), (223, 129), (222, 129), (221, 130), (221, 130)]
        trianglePoints = [(282, 83), (281, 85), (277, 91), (273, 97), (267, 105), (261, 113), (253, 123), (243, 133), (235, 141), (229, 149), (221, 153), (217, 159), (216, 160), (215, 161), (214, 162), (216, 162), (218, 162), (221, 162), (227, 164), (233, 166), (241, 166), (249, 166), (259, 166), (271, 166), (283, 166), (297, 166), (309, 164), (323, 164), (335, 162), (345, 162), (353, 162), (361, 160), (363, 159), (365, 159), (366, 158), (367, 158), (368, 157), (369, 157), (370, 156), (371, 156), (371, 155), (372, 155), (372, 153), (372, 152), (372, 151), (372, 149), (372, 147), (371, 145), (367, 141), (363, 137), (359, 133), (353, 129), (349, 125), (343, 121), (337, 119), (333, 115), (327, 111), (325, 110), (324, 109), (320, 105), (318, 104), (314, 100), (312, 99), (310, 98), (306, 94), (305, 93), (303, 92), (301, 91), (300, 90), (298, 89), (297, 88), (296, 88), (295, 87), (294, 87), (293, 87), (293, 87)]

        '''
        self.templateScatter.addPoints(
            pos=np.array(circlePoints), brush=pg.mkBrush(0, 255, 0, 120))
        self.templateScatter.addPoints(
            pos=np.array(squarePoints), brush=pg.mkBrush(0, 255, 0, 120))
        self.templateScatter.addPoints(
            pos=np.array(trianglePoints), brush=pg.mkBrush(0, 255, 0, 120))
        '''

        self.dollar.addTemplate('circle', circlePoints)
        self.dollar.addTemplate('square', squarePoints)
        self.dollar.addTemplate('triangle', trianglePoints)

    def update(self):
        # get biggest light's x/y values
        outputValues = self.pointVisNode.outputValues()
        if outputValues['irX'] is not None and outputValues['irY'] is not None:
            if self.wiimoteNode.wiimote is not None:
                if self.wiimoteNode.wiimote.buttons['A']:
                    # collect values and set state
                    self.construct_path(outputValues)
                    self.pressed_key = 'A'
                elif self.wiimoteNode.wiimote.buttons['B']:
                    # collect values and set state
                    self.construct_path(outputValues)
                    self.pressed_key = 'B'
                elif self.path['x'] is not None and len(self.path['x']) > 0:
                    self.draw_path()
            else:
                self.templateScatter.clear()
                self.pathScatter.clear()
                self.display_message(self.error_wiimote_msg)
        else:
            self.templateScatter.clear()
            self.pathScatter.clear()
            self.display_message(self.error_ir_msg)

        # update range to remove old graphics
        self.setRange(self.templatePlot)
        self.setRange(self.pathPlot)

        pyqtgraph.QtGui.QApplication.processEvents()

    '''
    The user input is added as a new template
    '''
    def create_template(self):
        points = []
        # combine x/y path arrays to one point array
        for i in range(0, len(self.path['x'])):
            points.append([self.path['x'][i], self.path['y'][i]])

        # avoid devision by zero
        if len(points) > 3:
            # name and add template
            name = 'tpl_' + str((len(self.dollar.templates) + 1))
            self.dollar.addTemplate(name, points)
        else:
            self.display_message(self.error_template_msg)

    '''
    The user input is compared to all available templates and depending
    on the accordance a text message is displayed
    '''
    def compare_template(self):
        points = self.combineXYPoints()

        # try recognizing points. get name of template that matches most
        # and its amount of matching
        if len(points) < 3:
            self.display_message(self.default_msg)
            self.templateScatter.clear()
            return

        name, score = self.dollar.recognize(points)

        score = score * 100
        if score > self.threshold:
            # template matches good enough
            self.display_message(name)

            # get template by name
            template = [t for t in self.dollar.templates if t.name == name][0]

            tpl_points = []

            # collect and display template points
            for i in range(0, len(template.points)):
                tpl_points.append([template.points[i].x, template.points[i].y])
            # display points
            self.templateScatter.addPoints(
                pos=np.array(tpl_points), brush=pg.mkBrush(0, 255, 0, 120))
        else:
            # template doesn't match good enough
            self.display_message(self.default_msg)
            self.templateScatter.clear()

    '''
    The infrafred values are stored in a dictionary
    '''
    def construct_path(self, irValues):
        self.templateScatter.clear()
        self.pathScatter.clear()
        self.path['x'].append(irValues['irX'])
        self.path['y'].append(irValues['irY'])

    '''
    The stored infrafred values are passed to a scatterplot
    '''
    def draw_path(self):
        path = self.combineXYPoints()
        points = []
        for i in range(0, len(path)):
            points.append(dollar.Point(path[i][0], path[i][1]))

        # display points
        if len(points) >= 3:
            points = dollar.resample(points, self.sample_size)
            if points is not None:
                path = []
                for i in range(0, len(points)):
                    path.append([points[i].x, points[i].y])

                self.pathScatter.addPoints(
                    pos=np.array(path), brush=pg.mkBrush(255, 255, 255, 120))

                # handle pressed keys
                if self.pressed_key is 'A':
                    self.compare_template()
                elif self.pressed_key is 'B':
                    self.create_template()

        self.path['x'] = []
        self.path['y'] = []
        self.pressed_key = None

    '''
    Combine separate x and y point arrays to one nested array
    '''
    def combineXYPoints(self):
        points = []
        for i in range(0, len(self.path['x'])):
            points.append([self.path['x'][i], self.path['y'][i]])
        return points

    '''
    A text message is passed to a ui label widget
    '''
    def display_message(self, msg):
        self.label.setText(msg)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

    def setRange(self, plot):
        plot.enableAutoRange(enable=False)
        plot.enableAutoRange(enable=True)

numPoints = 64
squareSize = 250.0
halfDiagonal = 0.5 * math.sqrt(250.0 * 250.0 + 250.0 * 250.0)
angleRange = 45.0
anglePrecision = 2.0
phi = 0.5 * (-1.0 + math.sqrt(5.0))  # Golden Ratio


class Recognizer:
    """The $1 gesture recognizer. See http://sleepygeek.org/projects.dollar for more, or http://depts.washington.edu/aimgroup/proj/dollar/ for the original implementation and paper."""
    templates = []

    def recognize(self, points):
        """Determine which gesture template most closely matches the gesture represented by the input points. 'points' is a list of tuples, eg: [(1, 10), (3, 8) ...]. Returns a tuple of the form (name, score) where name is the matching template, and score is a float [0..1] representing the match certainty."""

        points = [Point(point[0], point[1]) for point in points]
        points = resample(points, numPoints)
        if points is None or len(points) < 4:
            return ('', 0)
        points = _rotateToZero(points)
        print len(points)
        points = _scaleToSquare(points, squareSize)
        points = _translateToOrigin(points)

        bestDistance = float("infinity")
        bestTemplate = None
        for template in self.templates:
            distance = _distanceAtBestAngle(points, template, -angleRange, +angleRange, anglePrecision)
            if distance < bestDistance:
                bestDistance = distance
                bestTemplate = template

        score = 1.0 - (bestDistance / halfDiagonal)
        return (bestTemplate.name, score)

    def addTemplate(self, name, points):
        """Add a new template, and assign it a name. Multiple templates can be given the same name, for more accurate matching. Returns an integer representing the number of templates matching this name."""
        self.templates.append(Template(name, points))

        # Return the number of templates with this name.
        return len([t for t in self.templates if t.name == name])

    def deleteTemplates(self, name):
        """Remove all templates matching a given name. Returns an integer representing the new number of templates."""

        self.templates = [t for t in self.templates if t.name != name]
        return len(self.templates)


class Point:
    """Simple representation of a point."""
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangle:
    """Simple representation of a rectangle."""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Template:
    """A gesture template. Used internally by Recognizer."""
    def __init__(self, name, points):
        """'name' is a label identifying this gesture, and 'points' is a list of tuple co-ordinates representing the gesture positions. Example: [(1, 10), (3, 8) ...]"""
        self.name = name
        self.points = [Point(point[0], point[1]) for point in points]
        self.points = resample(self.points, numPoints)
        if self.points is None or len(self.points) < 4:
            self.points = [Point(0, 0)]
        self.points = _rotateToZero(self.points)
        self.points = _scaleToSquare(self.points, squareSize)
        self.points = _translateToOrigin(self.points)


def resample(points, n):
    """Resample a set of points to a roughly equivalent, evenly-spaced set of points."""
    I = _pathLength(points) / (n - 1)  # interval length
    D = 0.0
    newpoints = [points[0]]
    i = 1
    while i < len(points) - 1:
        try:
            d = _distance(points[i - 1], points[i])
        except Exception:
            return None

    if d > 0:
        if (D + d) >= I:
            qx = points[i - 1].x + ((I - D) / d) * (points[i].x - points[i - 1].x)
            qy = points[i - 1].y + ((I - D) / d) * (points[i].y - points[i - 1].y)
            q = Point(qx, qy)
            newpoints.append(q)
            # Insert 'q' at position i in points s.t. 'q' will be the next i
            points.insert(i, q)
            D = 0.0
        else:
            D += d
    i += 1

    # Sometimes we fall a rounding-error short of adding the last point, so add it if so.
    if len(newpoints) == n - 1:
        newpoints.append(points[-1])
    return newpoints


def _rotateToZero(points):
    """Rotate a set of points such that the angle between the first point and the centre point is 0."""
    c = _centroid(points)
    theta = math.atan2(c.y - points[0].y, c.x - points[0].x)
    return _rotateBy(points, -theta)


def _rotateBy(points, theta):
    """Rotate a set of points by a given angle."""
    c = _centroid(points)
    cos = math.cos(theta)
    sin = math.sin(theta)

    newpoints = []
    for point in points:
        qx = (point.x - c.x) * cos - (point.y - c.y) * sin + c.x
        qy = (point.x - c.x) * sin + (point.y - c.y) * cos + c.y
        newpoints.append(Point(qx, qy))
    return newpoints


def _scaleToSquare(points, size):
    """Scale a scale of points to fit a given bounding box."""
    B = _boundingBox(points)
    newpoints = []
    for point in points:
        qx = point.x * (size / B.width)
        qy = point.y * (size / B.height)
        newpoints.append(Point(qx, qy))
    return newpoints


def _translateToOrigin(points):
    """Translate a set of points, placing the centre point at the origin."""
    c = _centroid(points)
    newpoints = []
    for point in points:
        qx = point.x - c.x
        qy = point.y - c.y
        newpoints.append(Point(qx, qy))
    return newpoints


def _distanceAtBestAngle(points, T, a, b, threshold):
    """Search for the best match between a set of points and a template, using a set of tolerances. Returns a float representing this minimum distance."""
    x1 = phi * a + (1.0 - phi) * b
    f1 = _distanceAtAngle(points, T, x1)
    x2 = (1.0 - phi) * a + phi * b
    f2 = _distanceAtAngle(points, T, x2)

    while abs(b - a) > threshold:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = phi * a + (1.0 - phi) * b
            f1 = _distanceAtAngle(points, T, x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = (1.0 - phi) * a + phi * b
            f2 = _distanceAtAngle(points, T, x2)
    return min(f1, f2)


def _distanceAtAngle(points, T, theta):
    """Returns the distance by which a set of points differs from a template when rotated by theta."""
    newpoints = _rotateBy(points, theta)
    return _pathDistance(newpoints, T.points)


def _centroid(points):
    """Returns the centre of a given set of points."""
    x = 0.0
    y = 0.0
    for point in points:
        x += point.x
        y += point.y
    x /= len(points)
    y /= len(points)
    return Point(x, y)


def _boundingBox(points):
    """Returns a Rectangle representing the bounding box that contains the given set of points."""
    minX = float("+Infinity")
    maxX = float("-Infinity")
    minY = float("+Infinity")
    maxY = float("-Infinity")

    for point in points:
        if point.x < minX:
            minX = point.x
        if point.x > maxX:
            maxX = point.x
        if point.y < minY:
            minY = point.y
        if point.y > maxY:
            maxY = point.y

    return Rectangle(minX, minY, maxX - minX, maxY - minY)


def _pathDistance(pts1, pts2):
    """'Distance' between two paths."""
    d = 0.0
    for index in range(len(pts1)):  # assumes pts1.length == pts2.length
        d += _distance(pts1[index], pts2[index])
    return d / len(pts1)


def _pathLength(points):
    """Sum of distance between each point, or, length of the path represented by a set of points."""
    d = 0.0
    for index in range(1, len(points)):
        d += _distance(points[index - 1], points[index])
    return d


def _distance(p1, p2):
    """Distance between two points."""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.sqrt(dx * dx + dy * dy)

if __name__ == "__main__":
    main()
