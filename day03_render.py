#! /usr/bin/env python3
import sys, re

import cv2
import numpy as np

from functools import partial

FabricSize     = 1000
EmptyColor     = 255
RectangleColor = np.array([ 0, 128, 0   ])
OverlapColor   = np.array([ 0, 0  , 192 ])

parse_record = partial(re.match, r'#(\d+) @ (\d+),(\d+): (\d+)x(\d+)')

records = map(parse_record, sys.stdin.readlines())

fabric     = np.full((FabricSize, FabricSize, 3), EmptyColor, np.uint8)
fabric_map = np.zeros((FabricSize, FabricSize), np.int32)

for record in records:
    _, x, y, w, h = map(int, record.groups())
    fabric_map[y:y + h, x:x + w] += 1

fabric[fabric_map >  1] = OverlapColor
fabric[fabric_map == 1] = RectangleColor

cv2.imwrite('output.png', fabric)
