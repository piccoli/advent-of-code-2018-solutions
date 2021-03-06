#! /usr/bin/env python3
import sys

from itertools import product
import colorsys
import numpy as np
import cv2

X, Y = range(2)

DistanceThreshold = 32 if len(sys.argv) > 1 and sys.argv[1] == '--test'\
               else 10000

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

def distance(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)

def read_areas():
    seeds = []
    for line in sys.stdin.readlines():
        x, y = map(int, line.split(','))

        seeds.append((x, y))

    x1 = min(s[X] for s in seeds)
    y1 = min(s[Y] for s in seeds)
    x2 = max(s[X] for s in seeds)
    y2 = max(s[Y] for s in seeds)

    return seeds, x1, y1, x2, y2

def render(seeds, labels):
    out = np.zeros((y2 - y1 + 1, x2 - x1 + 1, 3), np.uint8)

    for i, j in product(
            range(y1, y2 + 1),
            range(x1, x2 + 1)):
        if labels[i, j] < 0:
            out[i - y1, j - x1, :] = np.array([ 0, 0, 0 ])
        else:
            hue = float(labels[i, j]) / float(len(seeds) - 1)

            r, g, b = (int(255 * c) for c in colorsys.hsv_to_rgb(hue, .5, 1))

            out[i - y1, j - x1, :] = np.array([ b, g, r ])

    cv2.imwrite('output.png', out)

seeds, x1, y1, x2, y2 = read_areas()

labels = assign_labels(seeds, x1, y1, x2, y2)

render(seeds, labels)

print(max_area(seeds, labels))
print(closest_area(seeds))
