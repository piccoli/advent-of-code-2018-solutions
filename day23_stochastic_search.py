#! /usr/bin/env python3
import sys, re, math
from functools import partial

from random import seed, random, randint

#Seed       = None
Seed       = 12345
Iterations = 10000

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

# Part 2: Stochastic search with simulated annealing.
# It only finds approximate solutions at a minimum,
# but I was very pleased/surprised with the accuracy I got!
minx = min(x - r for x, y, z, r in nanobots)
miny = min(y - r for x, y, z, r in nanobots)
minz = min(z - r for x, y, z, r in nanobots)
maxx = max(x + r for x, y, z, r in nanobots)
maxy = max(y + r for x, y, z, r in nanobots)
maxz = max(z + r for x, y, z, r in nanobots)

class State:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
        self.error = self.__error()

    def __error(self):
        x, y, z = self.x, self.y, self.z
        return len(nanobots) - sum(in_range(b, (x, y, z, 0)) for b in nanobots)

    def distance_to_origin(self):
        return self.x + self.y + self.z

    def __str__(self):
        return '({}, {}, {}) -> {}'.format(self.x, self.y, self.z, len(nanobots) - self.error)

    @staticmethod
    def sample():
        x = randint(minx, maxx)
        y = randint(miny, maxy)
        z = randint(minz, maxz)

        return State(x, y, z)

    def sample_neighbor(self):
        while True:
            axis = randint(0, 2)

            d = (1 << randint(0, 25)) * (-1) ** randint(0, 1)

            x, y, z = self.x, self.y, self.z

            if   axis == X: x += d
            elif axis == Y: y += d
            else:           z += d

            if    x < minx or x > maxx\
               or y < miny or y > maxy\
               or z < minz or z > maxz:
                    continue

            if x != self.x or y != self.y or z != self.z:
                return State(x, y, z)

def T(k, t0, tn = .0001, n = Iterations):
    return tn + .5 * (t0 - tn) * (1. + math.cos(k * math.pi / n))

def P(delta, t):
    return math.exp(-delta / t)

def find():
    seed(Seed)

    old = State.sample()
    best = old

    t0 = 1
    for k in range(Iterations):
        t = T(k, t0)

        new = old.sample_neighbor()

        d = new.error - old.error

        print(
            'T: {:10.3f}; Delta: {:12.3f}; Best: {}; New: {};'.format(t, d, best, new),
            ' ' * 10,
            end = '\r',
            file = sys.stderr
        )

        if new.error <= old.error or P(d, t) >= random():
            old = new

            if new.error < best.error\
                or (new.error == best.error and
                        new.distance_to_origin() <
                        best.distance_to_origin()):
                best = new

    print(file = sys.stderr)
    return best.x, best.y, best.z

x, y, z = find()

min_dist = x + y + z
max_bots = sum(in_range(b, (x, y, z, 0)) for b in nanobots)

print(min_dist, '({} nanobots)'.format(max_bots))
