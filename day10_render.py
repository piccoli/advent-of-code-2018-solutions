#! /usr/bin/env python3
import sys, re
from functools import partial

import cv2
import numpy as np

parse_record = partial(re.match, r'position=<( *-?\d+), *( *-?\d+)> velocity=<( *-?\d+), *( *-?\d+)>')

X, Y = 0, 1

class Points:
    def __init__(self, input_file = sys.stdin):
        records = map(parse_record, input_file.readlines())

        p = []
        v = []
        for record in records:
            px, py, vx, vy = map(int, record.groups())
            p.append([ px, py ])
            v.append([ vx, vy ])

        self.positions  = np.array(p)
        self.velocities = np.array(v)

    def height(self, time):
        y = (self.positions + self.velocities * time)[:, Y]

        return y.max() - y.min() + 1

    def diff_at(self, time):
        return self.height(time + 1) - self.height(time)

    def find_time(self):
        l, u = 0, 1
        time = 0

        while self.diff_at(time) < 0:
            l, u = u, u * 2
            time = (l + u) // 2

        u = time

        while l <= u:
            time = (l + u) // 2

            if self.diff_at(time) < 0:
                l = time + 1
            else:
                u = time - 1

        return l

    def map(self, time, size, margin = 0):
        pt = self.positions + self.velocities * time
        x  = pt[:, X]
        y  = pt[:, Y]

        pmin = np.array([ x.min(), y.min() ])
        pmax = np.array([ x.max(), y.max() ])

        maxrange = np.max(pmax - pmin) + 1

        return np.int32(np.round(
            margin + (size - 2 * margin) * (pt - pmin) / maxrange
        ))

    def render_text(self, time, size = 60):
        p  = self.map(time, size)
        py = p[:, Y]

        miny = py.min()
        maxy = py.max()

        sky = { (x, y) for (x, y) in p }

        for y in range(miny, maxy + 1):
            print(''.join(
                ' #'[(x, y) in sky]
                for x in range(size)
            ))

    def render_video(self, time_when_aligned, size = 600, margin = 30, frames = 180, fps = 60):
        four_cc = cv2.VideoWriter_fourcc(*'MP42')
        video = cv2.VideoWriter('output.avi', four_cc, fps, (size, size))

        for t in range(frames + 1):
            tf = np.tanh(20 * t / frames) * time_when_aligned
            video.write(self.render_frame(tf, size, margin))

        video.release()

    def render_frame(self, time, size, margin):
        p = self.map(time, size, margin)
        
        canvas = np.zeros((size, size, 3), np.uint8)

        for x, y in p:
            cv2.circle(canvas, (x, y), 3, (255, 255, 255), thickness = 5)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        canvas = cv2.dilate(canvas, kernel, iterations = 3)
        canvas = cv2.blur(canvas, (3, 3))
        canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

        return canvas

points = Points()

time_when_aligned = points.find_time()

points.render_text(time_when_aligned)

print(time_when_aligned)

points.render_video(time_when_aligned)
