import sys
import turtle
import math


turtle = turtle.Turtle()
turtle.up()
turtle.speed(0)
turtle.pensize(2)
turtle.down()
turtle.color("red")


def draw_roundcircle(radius):
    #distance fo 1 degree
    degreecount = 0
    degreestep = 2 * math.pi * radius / 360.0

    while True:
        turtle.forward(degreestep)
        #turn right 1 degree
        turtle.right(1.0)


def draw_circle(radius):
    degreecount = 0
    spokescount = 5
    #distance of 1 degree
    degreestep = (2 * math.pi * radius / 360.0)/spokescount

    while True:
        degreecount = degreecount + 1
        turtle.forward(degreestep)
        
        if degreecount < 180:
            turtle.right(1.0)
        else:
            turtle.left(1.0)
        if degreecount >= 360-(360/spokescount):
            degreecount = 0

#read radius given as argument
rad = float(sys.argv[1])

#start drawing
draw_circle(rad)
#draw_roundcircle(rad)
