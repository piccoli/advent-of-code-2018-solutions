#! /usr/bin/env python3
import sys, re

import numpy as np
import cv2

from functools import partial
from collections import namedtuple, defaultdict

X, Y = range(2)

class VideoRecorder:
    def __init__(self, scan, source):
        self.width  = scan.x1 - scan.x0 + 1
        self.height = 16 * self.width // 9

        four_cc = cv2.VideoWriter_fourcc(*'MP42')

        self.video = cv2.VideoWriter('output.avi', four_cc, 60.0, (self.width, self.height))

        self.velocity = [ 0, 0 ]

        self.position = [
            source[X] - self.width  // 2,
            source[Y] - self.height // 2
        ]

    def render_frame(self, x, y):
        self.__accelerate_towards(x, y)

        im = np.zeros((self.height, self.width, 3), np.uint8)
        im[:, :] = EmptyColor

        for object_type, color in zip(
            (Clay     , Settled     , Flowing  ),
            (ClayColor, SettledColor, FlowColor)):

            objects = self.__objects_by_window(object_type)
            self.__render_object(im, objects, color)

        self.video.write(im)

    def __accelerate_towards(self, x, y):
        vx, vy = self.velocity

        if x < self.position[X] + self.width // 3:
            self.velocity[X] = max(-5, vx - 2)
        elif x >= self.position[X] + 2 * self.width // 3:
            self.velocity[X] = min(5, vx + 2)

        if y < self.position[Y] + self.height // 3:
            self.velocity[Y] = max(-5, vy - 2)
        elif y >= self.position[Y] + 2 * self.height // 3:
            self.velocity[Y] = min(5, vy + 2)

        self.position[X] += int(vx)
        self.position[Y] += int(vy)

        self.velocity[X] *= .9
        self.velocity[Y] *= .9

    def __objects_by_window(self, object_type):
        return [
            (x, y) for (x, y), t in reservoir.items()
                if t == object_type
                    and self.position[X] <= x < self.position[X] + self.width
                    and self.position[Y] <= y < self.position[Y] + self.height
        ]

    def __render_object(self, im, obj, color):
        if not obj:
            return

        xs, ys = map(np.int32, zip(*obj))

        bounds = (self.position[Y] <= ys) & (ys < self.position[Y] + self.height)\
               & (self.position[X] <= xs) & (xs < self.position[X] + self.width )

        xs = xs[bounds] - self.position[X]
        ys = ys[bounds] - self.position[Y]

        im[ys, xs, :] = color

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.video.release()

Source = 500, 0

Area = namedtuple('Area', 'x0 y0 x1 y1')

Empty, Clay, Flowing, Settled = ' #|~'
Solids = Clay + Settled

ClayColor    = np.array([ 0  , 114, 255 ])
FlowColor    = np.array([ 255, 231, 212 ])
SettledColor = np.array([ 255, 115, 0   ])
EmptyColor   = np.array([ 0  , 49 , 109 ])

def flood(x, y):
    y, stop = flood_down(x, y)

    while not stop:
        x0, leak_left  = flood_side(x, y, -1)
        x1, leak_right = flood_side(x, y,  1)

        if leak_left:  flood(x0, y)
        if leak_right: flood(x1, y)

        stop  = reservoir[x0, y] not in Solids\
             or reservoir[x1, y] not in Solids

        if not stop:
            reservoir.update({
                (x, y): Settled for x in range(x0 + 1, x1)
            })

            recorder.render_frame(x, y)

            y -= 1

def flood_down(x, y):
    reservoir[x, y] = Flowing
    recorder.render_frame(x, y)

    while y < scan.y1 and reservoir[x, y + 1] == Empty:
        y += 1
        reservoir[x, y] = Flowing

    recorder.render_frame(x, y)

    return y, y == scan.y1 or reservoir[x, y + 1] == Flowing

def flood_side(x, y, dx):
    xi = x
    while reservoir[xi, y + 1] in Solids and reservoir[xi, y] not in Solids:
        reservoir[xi, y] = Flowing
        xi += dx

    return xi, reservoir[xi, y] == Empty

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

reservoir, scan = read()

with VideoRecorder(scan, Source) as recorder:
    flood(*Source)

reservoir = {
    (x, y): reservoir[x, y]
        for x, y in reservoir
            if y >= scan.y0
}

total_settled = sum(r == Settled for r in reservoir.values())
total_flowing = sum(r == Flowing for r in reservoir.values())

print(total_settled + total_flowing)
print(total_settled)
