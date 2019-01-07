#! /usr/bin/env python3
import sys

left, right, straight = range(3)
next_direction = straight, left, right

def simulate(diagram, cars):
    while len(cars) > 1:
        for y, x in sorted(cars):
            if (y, x) not in cars:
                continue

            dy, dx, dr = cars[y, x]

            del cars[y, x]

            y += dy
            x += dx

            if (y, x) in cars:
                del cars[y, x]
                print(x, y, sep = ',')
                continue

            d = diagram[y][x]

            if d == '\\':
                dy, dx = dx, dy
            elif d == '/':
                dy, dx = -1 * dx, -1 * dy
            elif d == '+':
                dr = next_direction[dr]
                dy, dx = turn(dr, dy, dx)

            cars[y, x] = (dy, dx, dr)

    print('Remaining:')
    for y, x in cars:
        print(x, y, sep = ',')

def read_diagram():
    diagram = [ list(line[:-1]) for line in sys.stdin.readlines() ]

    cars = {}
    direction = {
        '^': (-1,  0),
        'v': ( 1,  0),
        '<': ( 0, -1),
        '>': ( 0,  1)
    }

    for y, row in enumerate(diagram):
        for x, sym in enumerate(row):
            if sym in direction.keys():
                row[x] = '-' if sym in '><' else '|'
                cars[y, x] = (*direction[sym], right)

    return diagram, cars

def turn(dr, dy, dx):
    if dr == left:
        if dy == 0: dy, dx = -dx, dy
        else:       dy, dx =  dx, dy
    elif dr == right:
        if dx == 0: dy, dx = dx, -dy
        else:       dy, dx = dx,  dy

    return dy, dx

simulate(*read_diagram())
