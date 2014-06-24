#!/usr/bin/env python

import sys
from pyqtgraph.flowchart import Flowchart
import pyqtgraph
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
import wiimote
from wiimote_node import *
import dollar


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

        self.setWindowTitle("Pointing Device")
        self.showFullScreen()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })
        self.layout.addWidget(self.fc.widget(), 0, 0, 2, 1)

        self.path = {'x': [], 'y': []}
        self.threshold = 20
        self.default_msg = 'No template matched...'
        self.error_ir_msg = 'No ir-values received'
        self.error_wiimote_msg = 'No wiimote connected'

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
        self.pointVisNode = self.fc.createNode('Vis2D', pos=(-150, 150))
        self.wiimoteNode = self.fc.createNode('Wiimote', pos=(0, 0), )
        self.bufferNode = self.fc.createNode('Buffer', pos=(0, -150))
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
        plot = gview.addPlot()
        self.scatter = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
        plot.addItem(self.scatter)
        #plot.enableAutoRange()
        plot.setXRange(-400, 1400)
        plot.setYRange(-400, 1400)

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
        self.dollar.addTemplate('circle', circlePoints)
        self.dollar.addTemplate('square', squarePoints)
        self.dollar.addTemplate('triangle', trianglePoints)

    def update(self):
        outputValues = self.pointVisNode.outputValues()
        if outputValues['irX'] is not None and outputValues['irY'] is not None:
            if self.wiimoteNode.wiimote is not None:
                if self.wiimoteNode.wiimote.buttons['A']:
                    self.construct_path(outputValues)
                    self.pressed_key = 'A'
                elif self.wiimoteNode.wiimote.buttons['B']:
                    self.construct_path(outputValues)
                    self.pressed_key = 'B'
                elif self.path['x'] is not None and len(self.path['x']) > 0:
                    self.draw_path()
            else:
                self.scatter.clear()
                self.display_message(self.error_wiimote_msg)
        else:
            self.scatter.clear()
            self.display_message(self.error_ir_msg)
        pyqtgraph.QtGui.QApplication.processEvents()

    '''
    The user input is added as a new template
    '''
    def create_template(self):
        points = []
        for i in range(0, len(self.path['x'])):
            points.append([self.path['x'][i], self.path['y'][i]])
        name = 'tpl_' + str((len(self.dollar.templates) + 1))
        self.dollar.addTemplate(name, circle_points)

    '''
    The user input is compared to all available templates and depending
    on the accordance a text message is displayed
    '''
    def compare_template(self):
        points = []
        for i in range(0, len(self.path['x'])):
            points.append([self.path['x'][i], self.path['y'][i]])
        name, score = self.dollar.recognize(points)
        score = score * 100
        if score > self.threshold:
            self.display_message(name)
            template = [t for t in self.dollar.templates if t.name == name][0]
            tpl_points = []
            for i in range(0, len(template.points)):
                tpl_points.append([template.points[i].x, template.points[i].y])
            self.scatter.addPoints(pos=np.array(tpl_points), brush=pg.mkBrush(0, 255, 0, 120))
        else:
            self.display_message(self.default_msg)

    '''
    The infrafred values are stored in a dictionary
    '''
    def construct_path(self, irValues):
        self.scatter.clear()
        self.path['x'].append(irValues['irX'])
        self.path['y'].append(irValues['irY'])

    '''
    The stored infrafred values are passed to a scatterplot
    '''
    def draw_path(self):
        points = []
        for i in range(0, len(self.path['x'])):
            points.append([self.path['x'][i], self.path['y'][i]])
        #self.scatter.setData(pos=np.array(points))
        self.scatter.addPoints(pos=np.array(points), brush=pg.mkBrush(255, 255, 255, 120))
        if self.pressed_key is 'A':
            self.compare_template()
        elif self.pressed_key is 'B':
            self.create_template()
        self.path['x'] = []
        self.path['y'] = []
        self.pressed_key = None

    '''
    A text message is passed to a ui label widget
    '''
    def display_message(self, msg):
        self.label.setText(msg)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()

if __name__ == "__main__":
    main()
