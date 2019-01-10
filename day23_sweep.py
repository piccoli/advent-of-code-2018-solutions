#! /usr/bin/env python3
import sys, re
from functools import partial

X, Y, Z, R = range(4)

def find_position(nanobots):
    sweep_plane    = set()
    leaving        = set()
    best_positions = {}
    events         = []
    scan           = None

    for b in nanobots:
        x, y, z, r = b

        events += [
            (x - r, y    , z    , b),
            (x    , y - r, z    , b),
            (x    , y    , z - r, b),
            (x    , y    , z    , b),
            (x    , y    , z + r, b),
            (x    , y + r, z    , b),
            (x + r, y    , z    , b)
        ]

    for x, y, z, b in sorted(events):
        r, xb, yb, zb = b

        if scan is not None and x != scan and leaving:
            sweep_plane.difference_update(leaving)
            leaving.clear()

        sweep_plane.add(b)

        if x == xb + r:
            leaving.add(b)

        best_positions[x, y, z] = sum(
            in_range(b, (x, y, z, 0)) for b in sweep_plane
        )

        scan = x

    max_bots = max(best_positions.values())

    best_positions = {
        k: v for k, v in best_positions.items() if v == max_bots
    }

    min_dist = min(x + y + z for x, y, z in best_positions)

    return min_dist, max_bots

def in_range(reference, bot):
    return sum(abs(bot[i] - reference[i]) for i in (X, Y, Z)) <= reference[R]

def read():
    bots = []
    for record in map(partial(re.match, r'pos=<(-?\d+),(-?\d+),(-?\d+)>, *r=(\d+)'), sys.stdin.readlines()):
        x, y, z, r = map(int, record.groups())

        bots.append((x, y, z, r))

    return sorted(bots, reverse = True, key = lambda b: (b[R], b[X], b[Y], b[Z]))

# Part 1
nanobots = read()

bot_with_largest_radius = nanobots[0]

print(sum(in_range(bot_with_largest_radius, b) for b in nanobots))

# Part 2: Sweep plane scan, assuming the answer must strictly lie
# on a nanobot vertex. This is not true, of course, but we could
# probably resolve this by considering bot-to-bot intersection vertices
# as well.
min_dist, max_bots = find_position(nanobots)

#print(min_dist, '({} nanobots)'.format(max_bots))
print(min_dist)
