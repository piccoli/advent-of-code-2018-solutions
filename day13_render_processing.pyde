#! /usr/bin/env python3
from __future__ import print_function
import sys, time
from heapq import heapify

X       = None
Arrow   = (-1, 1, 0, -1, 1, 1)
Img     = None
Diagram = []
Cars    = {}
Queue   = []

next_direction = {
    'right':    'left',
    'left':     'straight',
    'straight': 'right'
}

def keyPressed():
    if key == 'q':
        exit()

def draw():
    global Arrow, Cars, Diagram, Img, X, Queue
        
    pushMatrix()
    w = len(Diagram[0])
    h = len(Diagram)       
    image(Img, 0, 0)            
    scale(Img.width / w, Img.height / h)
    for (y, x), (dy, dx, dr) in Cars.items():
        pushMatrix()
        pushStyle()

        translate(x + .5, y + .5)
        
        if dx != 0:
            rotate(dx * PI / 2)
        elif dy == 1:
            rotate(PI)

        scale(.0001 * w * h)
        stroke(255, 255, 0)
        fill(255, 255, 0)
        triangle(*Arrow)

        popStyle()
        popMatrix()

    if X is not None:
        pushMatrix()
        pushStyle()
                
        translate(X[1] + .5, X[0] + .5)
        fill(255, 0, 0)
        stroke(255, 0, 0)
        scale(.0001 * w * h)
        ellipse(0, 0, 1, 1)
        
        popStyle()
        popMatrix()
    else:        
        if len(Queue) == 0:        
            Queue = list(Cars.keys())
            heapify(Queue)
            
        update()
        
    popMatrix()

def setup():
    global font
    
    initialize()
    size(600, 600)    
    stroke(0)
    strokeWeight(1)
    strokeJoin(MITER)
    strokeCap(SQUARE)
    rectMode(CORNER)
    textAlign(CENTER, CENTER)
    textMode(MODEL)
    font = createFont('Arial', 12, True)
    textFont(font, 12)
    hint(ENABLE_NATIVE_FONTS)
    #frameRate(1000)
    #noFill()    
    #noLoop()

def turn(dr, dy, dx):
    if dr == 'left':
        if dy == 0: dy, dx = -dx, dy
        else:       dx, dy =  dy, dx
    elif dr == 'right':
        if dy == 0: dy, dx =  dx, dy
        else:       dx, dy = -dy, dx

    return dy, dx

def initialize():
    global Diagram, Cars, Img
    
    Diagram = [ list(line[:-1]) for line in sys.stdin.readlines() ]

    for y, row in enumerate(Diagram):
        for x, sym in enumerate(row):
            if sym in '><^v':
                row[x] = '-' if sym in '><' else '|'

                dx =  1 if sym == '>'\
                else -1 if sym == '<'\
                else  0

                dy =  1 if sym == 'v'\
                else -1 if sym == '^'\
                else  0

                Cars[y, x] = (dy, dx, 'right')
                
    Img = createImage(width, height, RGB)    
    Img.loadPixels()
    w = len(Diagram[0])
    h = len(Diagram)
    for y in range(Img.height):
        for x in range(Img.width):
            i = int(y * h / Img.height)
            j = int(x * w / Img.width)
            sym = Diagram[i][j]
            Img.pixels[y * Img.width + x] = color(0, 189, 255) if sym != ' ' else color(0, 0, 0)
    Img.updatePixels()   
    
    ortho(0, Img.width, Img.height, 0)
    frameRate(20 * w * h / (6 * 6))

def update():
    global Diagram, Cars, X, Queue
    
    y, x = Queue.pop(0)

    dy, dx, dr = Cars[y, x]

    del Cars[y, x]

    y += dy
    x += dx

    if (y, x) in Cars:
        del Cars[y, x]
        Diagram[y][x] = 'X'
        X = (y, x)
        print(x, y)

    d = Diagram[y][x]

    if d == '\\':
        if dy == 0: dy, dx = dx, dy
        else:       dx, dy = dy, dx
    elif d == '/':
        if dy == 0: dy, dx = -dx, dy
        else:       dx, dy = -dy, dx
    elif d == '+':
        dr = next_direction[dr]
        dy, dx = turn(dr, dy, dx)

    Cars[y, x] = (dy, dx, dr)
