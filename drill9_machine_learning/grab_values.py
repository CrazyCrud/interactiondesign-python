#!/usr/bin/env python
# coding: utf-8

import wiimote
import time
import sys

wm = wiimote.connect(sys.argv[1])

xp = yp = zp = 0

while True:
    if wm.buttons["A"]:
        x, y, z = wm.accelerometer
        if (x != xp) or (y != yp) or (z != zp):
            print("%d,%d,%d") % (x, y, z)
        xp, yp, zp = x,y,z
        time.sleep(0.01)

    if wm.buttons["B"]:
        print
        break

wm.disconnect()
time.sleep(1)
