#! /usr/bin/env python3
import sys, re
import numpy as np
import cv2

from functools import partial
from collections import namedtuple

Area = namedtuple('Area', 'x0 y0 x1 y1')

CLAY_COLOR   = np.array([ 0  , 114, 255 ])
FLOW_COLOR   = np.array([ 255, 231, 212 ])
SOURCE_COLOR = np.array([ 255, 0  , 0   ])
WATER_COLOR  = np.array([ 255, 115, 0   ])

def read():
    reservoir = set()
    parse_record = partial(re.match, r'([xy])=(\d+),\s*([xy])=(\d+)\.\.(\d+)')

    records = map(parse_record, sys.stdin.readlines())

    for record in records:
        vertical = record.group(1) == 'x'

        x, y1, y2 = map(int, map(record.group, (2, 4, 5)))

        if vertical:
            reservoir.update((x, y) for y in range(y1, y2 + 1))
        else:
            reservoir.update((y, x) for y in range(y1, y2 + 1))

    area = Area(
        x0 = min(x for x, y in reservoir),
        y0 = min(y for x, y in reservoir),
        x1 = max(x for x, y in reservoir),
        y1 = max(y for x, y in reservoir)
    )

    return reservoir, area

def render_set(im, window, point_set, color):
    if not point_set:
        return

    xs, ys = map(np.int32, zip(*point_set))

    bounds = (window.y0 <= ys) & (ys < window.y1)\
           & (window.x0 <= xs) & (xs < window.x1)

    xs = xs[bounds] - window.x0
    ys = ys[bounds] - window.y0

    im[ys, xs, :] = color

def render_frame():
    if not water_sources:
        return

    y1 = min(y for x, y in water_sources) + size // 2 - 1
    y0 = y1 - size

    window = Area(
        x0 = scan.x0,
        y0 = y0,
        x1 = scan.x1,
        y1 = y1
    )

    im = np.zeros((size, size, 3), np.uint8)

    im[:, :, 0] = 0
    im[:, :, 1] = 49
    im[:, :, 2] = 109

    render_set(im, window, reservoir    , CLAY_COLOR  )
    render_set(im, window, settled_water, WATER_COLOR )
    render_set(im, window, flowing      , FLOW_COLOR  )
    render_set(im, window, water_sources, SOURCE_COLOR)

    video.write(im)

reservoir, scan = read()
water_sources   = { (500, 0) }
flowing         = set()
settled_water   = set()
parent          = { (500, 0): (None, None) }

size = scan.x1 - scan.x0 + 1

four_cc = cv2.VideoWriter_fourcc(*'MP42')
video   = cv2.VideoWriter('output.avi', four_cc, 60.0, (size, size))

while water_sources:
    solids  = reservoir | settled_water
    sources = sorted(water_sources, reverse = True)

    water_sources.clear()

    for x, y in sources:
        if y == scan.y1:
            flowing.add((x, y))
            continue

        if (x, y + 1) not in solids:
            flowing.add((x, y))
            water_sources.add((x, y + 1))
            parent[x, y + 1] = x, y
            continue

        x0 = x1 = x
        while (x0, y + 1) in solids and (x0, y) not in solids:
            x0 -= 1
        while (x1, y + 1) in solids and (x1, y) not in solids:
            x1 += 1

        if (x0, y) in solids and (x1, y) in solids:
            settled_water.update((xi, y) for xi in range(x0 + 1, x1))
            flowing.difference_update((xi, y) for xi in range(x0 + 1, x1))

            water_sources.add(parent[x, y])
        else:
            if (x0, y) not in solids:
                water_sources.add((x0, y))
                parent[x0, y] = x, y

            if (x1, y) not in solids:
                water_sources.add((x1, y))
                parent[x1, y] = x, y

            flowing.update((x, y) for x in range(x0 + 1, x1))

    render_frame()

video.release()

total         = list(filter(lambda p: p[1] >= scan.y0, settled_water | flowing))
total_settled = list(filter(lambda p: p[1] >= scan.y0, settled_water))

print(len(total))
print(len(total_settled))
