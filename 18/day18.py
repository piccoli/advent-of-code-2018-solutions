#! /usr/bin/env python3
import sys, math

def iterate(area, size, num_iterations = 10):
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

        area, nexta = nexta, area

        key = ''.join(area)

        if key in cache:
            index = cache[key]
            loop = sequence[index:]
            remaining = num_iterations - (i + 1)

            return loop[remaining % len(loop)]

        cache[key] = i + 1
        sequence.append(key)

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

area = iterate(initial_area, size)
print(total_value(area))

area = iterate(initial_area, size, 1000000000)
print(total_value(area))
