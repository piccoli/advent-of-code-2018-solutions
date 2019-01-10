#! /usr/bin/env python3
import sys, re, math
from functools import partial

from random import seed, random, randint

verbose = len(sys.argv) > 1 and sys.argv[1] == '--verbose'
log = partial(print, flush = True, file = sys.stderr) if verbose\
    else (lambda *a, **k: None)

#Seed       = None
Seed       = 12345
Iterations = 10000

X, Y, Z, R = range(4)

class State:
    def __init__(self, nanobots, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
        self.nanobots = nanobots
        self.error = self.__error()

    def distance_to_origin(self):
        return self.x + self.y + self.z

    def sample_neighbor(self, rangex, rangey, rangez):
        while True:
            axis = randint(0, 2)

            d = (1 << randint(0, 25)) * (-1) ** randint(0, 1)

            x, y, z = self.x, self.y, self.z

            if   axis == X: x += d
            elif axis == Y: y += d
            else:           z += d

            if    x < rangex[0] or x > rangex[1]\
               or y < rangey[0] or y > rangey[1]\
               or z < rangez[0] or z > rangez[1]:
                    continue

            if x != self.x or y != self.y or z != self.z:
                return State(self.nanobots, x, y, z)

    @staticmethod
    def sample(nanobots, rangex, rangey, rangez):
        x = randint(rangex[0], rangex[1])
        y = randint(rangey[0], rangey[1])
        z = randint(rangez[0], rangez[1])

        return State(nanobots, x, y, z)

    def __error(self):
        x, y, z = self.x, self.y, self.z
        return len(self.nanobots) - sum(in_range(b, (x, y, z, 0)) for b in self.nanobots)

    def __str__(self):
        return '({}, {}, {}) -> {}'.format(self.x, self.y, self.z, len(self.nanobots) - self.error)

def find_position(nanobots):
    minx = min(x - r for x, y, z, r in nanobots)
    miny = min(y - r for x, y, z, r in nanobots)
    minz = min(z - r for x, y, z, r in nanobots)
    maxx = max(x + r for x, y, z, r in nanobots)
    maxy = max(y + r for x, y, z, r in nanobots)
    maxz = max(z + r for x, y, z, r in nanobots)

    rangex = minx, maxx
    rangey = miny, maxy
    rangez = minz, maxz

    ranges = rangex, rangey, rangez

    seed(Seed)

    old = State.sample(nanobots, *ranges)
    best = old

    t0 = 1
    for k in range(Iterations):
        t = T(k, t0)

        new = old.sample_neighbor(*ranges)

        d = new.error - old.error

        log(
            'T: {:10.3f}; Delta: {:12.3f}; Best: {}; New: {};'.format(t, d, best, new),
            ' ' * 10,
            end = '\r'
        )

        if new.error <= old.error or P(d, t) >= random():
            old = new

            if new.error < best.error\
                or (new.error == best.error and
                        new.distance_to_origin() <
                        best.distance_to_origin()):
                best = new

    log()

    min_dist = best.x + best.y + best.z
    max_bots = sum(in_range(b, (best.x, best.y, best.z, 0)) for b in nanobots)

    return min_dist, max_bots

def T(k, t0, tn = .0001, n = Iterations):
    return tn + .5 * (t0 - tn) * (1. + math.cos(k * math.pi / n))

def P(delta, t):
    return math.exp(-delta / t)

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

# Part 2: Stochastic search with simulated annealing.
# It only finds approximate solutions at a minimum,
# but I was very pleased/surprised with the accuracy I got!
min_dist, max_bots = find_position(nanobots)

#print(min_dist, '({} nanobots)'.format(max_bots))
print(min_dist)
