import wiimote
import sys
import time
import math


class Level(object):

    def __init__(self):
        raw_input(
            "Press the 'sync' button on the back of your Wiimote Plus " +
            "or buttons (1) and (2) on your classic Wiimote.\n" +
            "Press <return> once the Wiimote's LEDs start blinking.")

        self.axis = None
        self.straightAngle = 500
        self.treshold = 50

        if len(sys.argv) == 1:
            addr, name = wiimote.find()[0]
        elif len(sys.argv) == 2:
            addr = sys.argv[1]
            name = None
        elif len(sys.argv) == 3:
            addr, name = sys.argv[1:3]
        print("Connecting to %s (%s)" % (name, addr))
        self.wm = wiimote.connect(addr, name)

        while True:
            if self.wm.buttons["Up"] or self.wm.buttons["Down"]:
                print "Use y-axis"
                self.axis = 1
            elif self.wm.buttons["Right"] or self.wm.buttons["Left"]:
                print "Use x-axis"
                self.axis = 0
            else:
                pass

            if self.axis is not None:
                self.checkAngle()

            time.sleep(0.05)

    def checkAngle(self):
        leds = []
        angle = self.wm.accelerometer._state[self.axis]
        if angle == self.straightAngle:
            self.wm.rumble()
            leds = [True, True, True, True]
        elif angle - self.straightAngle > 0:
            if math.fabs(angle - self.straightAngle) > self.treshold:
                leds = [False, False, True, True]
            else:
                leds = [False, False, True, False]
        elif angle - self.straightAngle < 0:
            if math.fabs(angle - self.straightAngle) > self.treshold:
                leds = [True, True, False, False]
            else:
                leds = [False, True, False, False]
        self.wm.set_leds(leds)


def main():
    level = Level()

if __name__ == '__main__':
    main()
