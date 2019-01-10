#! /usr/bin/env python3
import sys, re

import numpy as np
import cv2

from functools import partial
from collections import namedtuple, defaultdict

Area = namedtuple('Area', 'x0 y0 x1 y1')

Empty, Clay, Flowing, Settled = ' #|~'
Solids = Clay + Settled

ClayColor   = np.array([ 0  , 114, 255 ])
FlowColor   = np.array([ 255, 231, 212 ])
WaterColor  = np.array([ 255, 115, 0   ])
EmptyColor  = np.array([ 0  , 49 , 109 ])

def fill(x, y):
    reservoir[x, y] = Flowing
    render_frame(x, y)

    if y == scan.y1:
        return

    if reservoir[x, y + 1] == Empty:
        fill(x, y + 1)

    if reservoir[x, y + 1] == Flowing:
        return

    x0 = x - 1
    while reservoir[x0, y + 1] in Solids\
        and reservoir[x0, y] not in Solids:
        reservoir[x0, y] = Flowing
        x0 -= 1

    x1 = x + 1
    while reservoir[x1, y + 1] in Solids\
        and reservoir[x1, y] not in Solids:
        reservoir[x1, y] = Flowing
        x1 += 1

    if reservoir[x0, y] == Empty:
        fill(x0, y)

    if reservoir[x1, y] == Empty:
        fill(x1, y)

    if reservoir[x0, y] in Solids and reservoir[x1, y] in Solids:
        reservoir.update({
            (x, y): Settled for x in range(x0 + 1, x1)
        })
        render_frame(x, y)

def read():
    reservoir = defaultdict(lambda: Empty)
    parse_record = partial(re.match, r'([xy])=(\d+),\s*([xy])=(\d+)\.\.(\d+)')

    records = map(parse_record, sys.stdin.readlines())

    for record in records:
        vertical = record.group(1) == 'x'

        x, y1, y2 = map(int, map(record.group, (2, 4, 5)))

        r    = { (x, y): Clay for y in range(y1, y2 + 1) } if vertical\
          else { (y, x): Clay for y in range(y1, y2 + 1) }

        reservoir.update(r)

    area = Area(
        x0 = min(x for x, y in reservoir),
        y0 = min(y for x, y in reservoir),
        x1 = max(x for x, y in reservoir),
        y1 = max(y for x, y in reservoir)
    )

    return reservoir, area

def render_frame(x, y):
    clay    = [ (x, y) for (x, y), t in reservoir.items() if t == Clay    ]
    settled = [ (x, y) for (x, y), t in reservoir.items() if t == Settled ]
    flowing = [ (x, y) for (x, y), t in reservoir.items() if t == Flowing ]


    x1 = x + size // 2 - 1
    x0 = x1 - size
    y1 = y + size // 10 - 1
    y0 = y1 - size

    window = Area(
        x0 = x0,
        y0 = y0,
        x1 = x1,
        y1 = y1
    )

    im = np.zeros((size, size, 3), np.uint8)
    im[:, :] = EmptyColor

    render_object(im, window, clay   , ClayColor )
    render_object(im, window, settled, WaterColor)
    render_object(im, window, flowing, FlowColor )

    video.write(im)

def render_object(im, window, obj, color):
    if not obj:
        return

    xs, ys = map(np.int32, zip(*obj))

    bounds = (window.y0 <= ys) & (ys < window.y1)\
           & (window.x0 <= xs) & (xs < window.x1)

    xs = xs[bounds] - window.x0
    ys = ys[bounds] - window.y0

    im[ys, xs, :] = color

reservoir, scan = read()

max_water = (scan.y1 - scan.y0 + 1) * (scan.x1 - scan.x0 + 1)
sys.setrecursionlimit(max_water)

size    = scan.x1 - scan.x0 + 1
four_cc = cv2.VideoWriter_fourcc(*'MP42')
video   = cv2.VideoWriter('output.avi', four_cc, 60.0, (size, size))

fill(500, 0)

video.release()

reservoir = {
    (x, y): reservoir[x, y]
        for x, y in reservoir
            if y >= scan.y0
}

total_settled = sum(reservoir[x, y] == Settled for x, y in reservoir)
total_flowing = sum(reservoir[x, y] == Flowing for x, y in reservoir)

print(total_settled + total_flowing)
print(total_settled)
