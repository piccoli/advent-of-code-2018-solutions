#! /usr/bin/env python3

from collections import deque

import colorsys
import numpy as np
import cv2

WallColor = (255, 255, 255)
DoorColor = (105, 173, 255)
RoomSize  = 8
WallGap   = 2

def longest_paths(floorplan, root):
    x0 = min(x for y, x in floorplan)
    y0 = min(y for y, x in floorplan)
    x1 = max(x for y, x in floorplan)
    y1 = max(y for y, x in floorplan)

    w, h = x1 - x0 + 2, y1 - y0 + 2

    four_cc = cv2.VideoWriter_fourcc(*'MP42')
    video = cv2.VideoWriter('output.avi', four_cc, 120.0, (w * RoomSize, h * RoomSize))

    distance = { root: 0 }

    q = deque([ root ])

    while q:
        node = q.popleft()

        for adjacent in floorplan[node]:
            if adjacent not in distance:
                distance[adjacent] = distance[node] + 1
                q.append(adjacent)

        video.write(render_frame(floorplan, distance, x0, y0, w, h))

    video.release()

    return max(distance.values()),\
           sum(d >= 1000 for d in distance.values())

def render_frame(floorplan, distance, x0, y0, w, h):
    im = np.zeros((h * RoomSize, w * RoomSize, 3), np.uint8)

    #max_dist = max(distance.values())
    max_dist = 3527

    map_x = lambda x: (x - x0) * RoomSize
    map_y = lambda y: (y - y0) * RoomSize

    def draw_wall(x, y, dx = 0, dy = 0):
        x, y = map_x(x), map_y(y)
        dx, dy = (d * RoomSize for d in (dx, dy))

        cv2.line(im, (y, x), (y + dy, x + dx), WallColor, 2)

    def draw_door(x, y, dx = 0, dy = 0):
        if (y, x) in distance:
            return

        x, y = map_x(x), map_y(y)

        s = (
            y + WallGap * dy,
            x + WallGap * dx
        )
        t = (
            y + (RoomSize - WallGap) * dy,
            x + (RoomSize - WallGap) * dx
        )
        cv2.line(im, s, t, DoorColor, 1)

    def draw_cost(x, y):
        hue = .3 * (1. - distance[y, x] / max_dist)

        x, y = map_x(x), map_y(y)

        r, g, b = colorsys.hsv_to_rgb(hue, .8, .8)
        r, g, b = (255 * c for c in (r, g, b))

        s = (y, x)
        t = (
            y + RoomSize,
            x + RoomSize
        )
        cv2.rectangle(im, s, t, (b, g, r), -1)

    draw_object_given = [ draw_wall, draw_door ]

    for (y, x), edges in floorplan.items():
        if (y, x) in distance:
            draw_cost(x, y)

        draw_object_given[(y - 1, x    ) in edges](x    , y    , dx = 1)
        draw_object_given[(y + 1, x    ) in edges](x    , y + 1, dx = 1)
        draw_object_given[(y    , x - 1) in edges](x    , y    , dy = 1)
        draw_object_given[(y    , x + 1) in edges](x + 1, y    , dy = 1)

    return im

stack     = []
floorplan = {}

for token in input().strip():
    if token == '^':
        root = 0, 0
        floorplan[root] = set()
        stack.append(root)

    if token in 'NEWS':
        y, x = root

        child =  (y - 1, x    ) if token == 'N'\
            else (y    , x - 1) if token == 'W'\
            else (y    , x + 1) if token == 'E'\
            else (y + 1, x    )

        if child not in floorplan:
            floorplan[child] = set()

        floorplan[root].add(child)
        floorplan[child].add(root)
        root = child

    elif token == '(': stack.append(root)
    elif token == '|': root = stack[-1]
    elif token == ')': stack.pop()
    elif token == '$': root = stack.pop()

longest, large_count = longest_paths(floorplan, root)

print(longest)
print(large_count)
