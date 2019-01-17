#! /usr/bin/env python3
import sys, re

from functools import partial
from collections import namedtuple, defaultdict

Source = 500, 0

Area = namedtuple('Area', 'x0 y0 x1 y1')

Empty, Clay, Flowing, Settled = ' #|~'
Solids = Clay + Settled

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

            y -= 1

def flood_down(x, y):
    reservoir[x, y] = Flowing

    while y < scan.y1 and reservoir[x, y + 1] == Empty:
        y += 1
        reservoir[x, y] = Flowing

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
