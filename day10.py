#! /usr/bin/env python3
import sys, re
from functools import partial

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

    def map(self, time, size):
        pt = self.positions + self.velocities * time
        x  = pt[:, X]
        y  = pt[:, Y]

        pmin = np.array([ x.min(), y.min() ])
        pmax = np.array([ x.max(), y.max() ])

        maxrange = np.max(pmax - pmin) + 1

        return np.int32(np.round(
            size * (pt - pmin) / maxrange
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

points = Points()

time_when_aligned = points.find_time()

points.render_text(time_when_aligned)

print(time_when_aligned)
