#! /usr/bin/env python3
import sys

from collections import deque

class Constellations:
    def __init__(self, points):
        self.id = { p: p for p in points }
        self.sz = { p: 1 for p in points }

    def root(self, r):
        rid = self.id
        while r != rid[r]:
            rid[r] = rid[rid[r]]
            r = rid[r]
        return r

    def size(self):
        return len({ self.root(p) for p in self.id })

    def union(self, r, s):
        i = self.root(r)
        j = self.root(s)

        if self.sz[i] < self.sz[j]:
            self.id[i] = j
            self.sz[j] += self.sz[i]
        else:
            self.id[j] = i
            self.sz[i] += self.sz[j]

def read_input():
    spacetime = set()

    for line in sys.stdin.readlines():
        x, y, z, w = map(int, line.strip().split(','))
        spacetime.add((x, y, z, w))

    return spacetime

def connect_to_close_neighbors(p):
    dist  = 0
    queue = deque([ (dist, *p) ])
    seen  = set()

    while queue:
        dist, x, y, z, w = queue.popleft()

        seen.add((x, y, z, w))

        if dist == 3:
            continue

        neighbors = (
            q for q in (
                (x - 1, y, z, w), (x + 1, y, z, w),
                (x, y - 1, z, w), (x, y + 1, z, w),
                (x, y, z - 1, w), (x, y, z + 1, w),
                (x, y, z, w - 1), (x, y, z, w + 1)
            )
            if q not in seen
        )

        for q in neighbors:
            if q in spacetime:
                constellations.union(p, q)
            if dist < 3:
                queue.append((dist + 1, *q))

spacetime      = read_input()
constellations = Constellations(spacetime)

for p in spacetime:
    connect_to_close_neighbors(p)

print(constellations.size())
