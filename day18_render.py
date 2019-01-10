#! /usr/bin/env python3
import sys, math

import cv2
import numpy as np

Ground, Trees, Lumberyard = '.|#'

next_state_given = {
    Ground: lambda count: (Ground, Trees)[
        count[Trees] > 2
    ],

    Trees: lambda count: (Trees, Lumberyard)[
        count[Lumberyard] > 2
    ],

    Lumberyard:  lambda count: (Ground, Lumberyard)[
        count[Lumberyard] > 0 and count[Trees] > 0
    ]
}

def iterate(area, size, num_iterations = 10, should_render = True):
    if should_render:
        four_cc = cv2.VideoWriter_fourcc(*'MP42')
        video  = cv2.VideoWriter('output.avi', four_cc, 50.0, (size * 8, size * 8))

    color = {
        Ground:     np.array([ 0  , 81 , 140 ]),
        Lumberyard: np.array([ 255, 116, 42  ]),
        Trees:      np.array([ 0  , 210, 0   ])
    }

    def render_frame():
        im = np.zeros((size * 8, size * 8, 3), np.uint8)

        k = 0
        for y in range(size):
            for x in range(size):
                acre = area[k]
                im[y * 8:(y + 1) * 8, x * 8:(x + 1) * 8] = color[acre]
                k += 1

        video.write(im)

    area = area[:]
    nexta = list(Ground * size * size)
    sequence = [ ''.join(area) ]
    cache = { sequence[0]: 0 }

    for i in range(num_iterations):
        for y in range(size):
            for x in range(size):
                acre = area[y * size + x]

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

                count = { Ground: 0, Lumberyard: 0, Trees: 0 }

                for yn, xn in neighbors:
                    count[area[yn * size + xn]] += 1

                nexta[y * size + x] = next_state_given[acre](count)

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
    totals = { Ground: 0, Lumberyard: 0, Trees: 0 }

    for acre in area:
        totals[acre] += 1

    return totals[Trees] * totals[Lumberyard]

def read_area():
    area = list(sys.stdin.read().replace('\n', '').replace(' ', ''))
    size = int(math.sqrt(len(area)))

    return area, size

initial_area, size = read_area()

area = iterate(initial_area, size, should_render = False)
print(total_value(area))

area = iterate(initial_area, size, 1000000000, should_render = True)
print(total_value(area))
