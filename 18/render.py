#! /usr/bin/env python3
import sys, math

import cv2
import numpy as np

def iterate(area, size, num_iterations = 10, should_render = True):
    if should_render:
        four_cc = cv2.VideoWriter_fourcc(*'MP42')
        video  = cv2.VideoWriter('output.avi', four_cc, 50.0, (size * 8, size * 8))

    color = {
        '.': np.array([ 0  , 81 , 140 ]),
        '#': np.array([ 255, 116, 42  ]),
        '|': np.array([ 0  , 210, 0   ])
    }

    def render_frame():
        im = np.zeros((size * 8, size * 8, 3), np.uint8)

        k = 0
        for y in range(size):
            for x in range(size):
                sym = area[k]
                im[y * 8:(y + 1) * 8, x * 8:(x + 1) * 8] = color[sym]
                k += 1

        video.write(im)

    area     = area[:]
    nexta    = list('.' * size * size)
    sequence = [ ''.join(area) ]
    cache    = { sequence[-1]: 0 }

    for i in range(num_iterations):
        for y in range(size):
            for x in range(size):
                sym = area[y * size + x]
                neighbors = (
                    (yn, xn) for (yn, xn) in (
                        (y - 1, x - 1),
                        (y - 1, x    ),
                        (y - 1, x + 1),
                        (y    , x - 1),
                        (y    , x + 1),
                        (y + 1, x - 1),
                        (y + 1, x    ),
                        (y + 1, x + 1)
                    )
                    if      yn >= 0 and yn < size\
                        and xn >= 0 and xn < size
                )
                count = { '.': 0, '#': 0, '|': 0 }

                for yn, xn in neighbors:
                    count[area[yn * size + xn]] += 1

                if sym == '.':
                    nexta[y * size + x] = '|' if count['|'] > 2 else '.'
                elif sym == '|':
                    nexta[y * size + x] = '#' if count['#'] > 2 else '|'
                else:
                    nexta[y * size + x] = '#' if count['#'] > 0 and count['|'] > 0 else '.'

        if should_render:
            render_frame()
        area, nexta = nexta, area

        key = ''.join(area)

        if key in cache:
            index = cache[key]
            loop = sequence[index:]
            remaining = num_iterations - (i + 1)

            area = loop[remaining % len(loop)]

            if should_render:
                render_frame()
                video.release()

            return area

        cache[key] = i + 1
        sequence.append(key)

    if should_render:
        render_frame()
        video.release()

    return area

def total_value(area):
    totals = { '.': 0, '#': 0, '|': 0 }

    for sym in area:
        totals[sym] += 1

    return totals['|'] * totals['#']

def read_area():
    area = list(sys.stdin.read().replace('\n', '').replace(' ', ''))
    size = int(math.sqrt(len(area)))

    return area, size

initial_area, size = read_area()

area = iterate(initial_area, size, should_render = False)
print(total_value(area))

area = iterate(initial_area, size, 1000000000, should_render = True)
print(total_value(area))
