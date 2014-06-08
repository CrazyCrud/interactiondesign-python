#!/usr/bin/env python

import wiimote
import time
import sys
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
import pyqtgraph
from PyQt4 import QtGui, QtCore

def main():
    wm = getWiimote()
    app = QtGui.QApplication(sys.argv)
    demo = Demo()
    demo.show()

    #wm.ir.register_callback(demo.print_ir)

    # update wiimote data every few milliseconds
    while True:
        demo.update()
        '''demo.updateValues(
            wm.accelerometer._state[0],
            wm.accelerometer._state[1],
            wm.accelerometer._state[2])'''

        time.sleep(0.20)

    sys.exit(app.exec_())

def getWiimote():
    raw_input(
        "Press the 'sync' button on the back of your Wiimote Plus " +
        "or buttons (1) and (2) on your classic Wiimote.\n" +
        "Press <return> once the Wiimote's LEDs start blinking.")
    if len(sys.argv) == 1:
        addr, name = wiimote.find()[0]
    elif len(sys.argv) == 2:
        addr = sys.argv[1]
        name = None
    elif len(sys.argv) == 3:
        addr, name = sys.argv[1:3]
    print("Connecting to %s (%s)" % (name, addr))
    return wiimote.connect(addr, name)


class Demo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Demo, self).__init__()

        self.setWindowTitle("Plotting the Wiimote")
        #self.showFullScreen()
        self.show()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

    def print_ir(self, ir_data):
        print'print_ir'
        print len(ir_data)
        for ir_obj in ir_data:
            #print "%4d %4d %2d" % (ir_obj["x"],ir_obj["y"],ir_obj["size"]),
            a=1

    def update(self):
        pyqtgraph.QtGui.QApplication.processEvents()

if __name__ == "__main__":
    main()
