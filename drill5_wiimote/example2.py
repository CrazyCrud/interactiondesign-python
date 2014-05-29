import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np

print np.random.normal(size=100)
plt = pg.plot(np.random.normal(size=100), title="Simplest possible plotting example")

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1 or not hasattr(pg.QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.exec_()
