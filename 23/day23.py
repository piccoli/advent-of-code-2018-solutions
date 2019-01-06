#! /usr/bin/env python3
import sys, re, math
from functools import partial
from collections import namedtuple

from heapq import *

X, Y, Z, R = range(4)

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

# Part 2: Octree space partitioning search to the rescue!
def bots_in_cube(x0, y0, z0, size):
    '''
    Count how many nanobots are inside or intersect the cube
    defined by (x0, y0, size).
    '''
    s = size - 1
    cube_vertices = [
        (x0    , y0    , z0    ),
        (x0    , y0    , z0 + s),
        (x0    , y0 + s, z0    ),
        (x0    , y0 + s, z0 + s),
        (x0 + s, y0    , z0    ),
        (x0 + s, y0    , z0 + s),
        (x0 + s, y0 + s, z0    ),
        (x0 + s, y0 + s, z0 + s)
    ]

    # TODO: I seem to be missing the case where a nanobot
    # intersects one the faces of the cube, but is not entirely
    # inside of it. However, this produces the correct results, at
    # least for my input and the sample cases. Why?
    # Of course, once the octree cubes start to get small enough,
    # this won't matter, because the bots have huge radii and will
    # thus either contain the entire cube or be outside of it
    # (remember, we're working with integer coordinates here).
    return sum(
        # We consider a nanobot as part of the cube, if:
        int(
            # it is completely inside the volume...
            (
                    x - r >= x0 and x + r < x0 + size
                and y - r >= y0 and y + r < y0 + size
                and z - r >= z0 and z + r < z0 + size
            )
            # ...or at least contains one of the vertices
            # of the cube.
            or any(
                in_range((x, y, z, r), (xc, yc, zc, 0))
                    for (xc, yc, zc) in cube_vertices
            )
        )
        for x, y, z, r in nanobots
    )

Cube = namedtuple('Cube', 'bots_missing size x0 y0 z0')

minx = min(x - r for x, y, z, r in nanobots)
miny = min(y - r for x, y, z, r in nanobots)
minz = min(z - r for x, y, z, r in nanobots)
maxx = max(x + r for x, y, z, r in nanobots)
maxy = max(y + r for x, y, z, r in nanobots)
maxz = max(z + r for x, y, z, r in nanobots)

rangex = maxx - minx
rangey = maxy - miny
rangez = maxz - minz

# Smallest power of two large enough to cover all nanobots.
size = int(math.ceil(math.log2(max(rangex, rangey, rangez))))
n = len(nanobots)

queue = [ Cube(0, size, minx, miny, minz) ]

while queue:
    missing, size, x, y, z = heappop(queue)

    #in_cube = n - missing
    #print(size, in_cube)

    if size == 0:
        max_bots = sum(in_range(b, (x, y, z, 0)) for b in nanobots)
        min_dist = x + y + z
        break

    size -= 1

    s = 2 ** size

    for x0, y0, z0, in (
        (x    , y    , z    ),
        (x    , y    , z + s),
        (x    , y + s, z    ),
        (x    , y + s, z + s),
        (x + s, y    , z    ),
        (x + s, y    , z + s),
        (x + s, y + s, z    ),
        (x + s, y + s, z + s)
        ):
        cube = Cube(n - bots_in_cube(x0, y0, z0, s), size, x0, y0, z0)
        heappush(queue, cube)

#print(min_dist, '({} nanobots)'.format(max_bots))
print(min_dist)
