#! /usr/bin/env python3
import sys

from itertools import product

X, Y = range(2)

DistanceThreshold = 32 if len(sys.argv) > 1 and sys.argv[1] == '--test'\
               else 10000

def read():
    seeds = []
    for line in sys.stdin.readlines():
        x, y = map(int, line.split(','))

        seeds.append((x, y))

    x1 = min(s[X] for s in seeds)
    y1 = min(s[Y] for s in seeds)
    x2 = max(s[X] for s in seeds)
    y2 = max(s[Y] for s in seeds)

    return seeds, x1, y1, x2, y2

def distance(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)

def assign_labels(seeds, x1, y1, x2, y2):
    dist = {
        (y, x): float("+inf")
            for y, x in product(
                range(y1, y2 + 1),
                range(x1, x2 + 1)
            )
    }

    labels = {
        (y, x): 0
            for y, x in product(
                range(y1, y2 + 1),
                range(x1, x2 + 1)
            )
    }

    for k, (x, y) in enumerate(seeds):
        for i, j in product(
                range(y1, y2 + 1),
                range(x1, x2 + 1)):
            d = distance(x, y, j, i)

            if d < dist[i, j]:
                dist[i, j] = d
                labels[i, j] = k

            elif d == dist[i, j]:
                labels[i, j] = -1

    return labels

def max_area(seeds, labels):
    count = { l: 0 for l in range(len(seeds)) }
    infinite = set()

    for j in range(x1, x2 + 1):
        infinite.add(labels[y1, j])
        infinite.add(labels[y2, j])

    for i in range(y1, y2 + 1):
        infinite.add(labels[i, x1])
        infinite.add(labels[i, x2])

    for i, j in product(
            range(y1, y2 + 1),
            range(x1, x2 + 1)):
        l = labels[i, j]
        if l not in infinite:
            count[l] += 1

    return max(count.values())

def closest_area(seeds):
    return sum(
        sum(distance(x, y, i, j) for x, y in seeds) < DistanceThreshold

        for i, j in product(
            range(y1, y2 + 1),
            range(x1, x2 + 1)
        )
    )

seeds, x1, y1, x2, y2 = read()

labels = assign_labels(seeds, x1, y1, x2, y2)

print(max_area(seeds, labels))
print(closest_area(seeds))
