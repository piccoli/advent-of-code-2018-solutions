#! /usr/bin/env python3
import sys, math

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

def iterate(area, size, num_iterations = 10):
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
    totals = { Ground: 0, Lumberyard: 0, Trees: 0 }

    for acre in area:
        totals[acre] += 1

    return totals[Trees] * totals[Lumberyard]

def read_area():
    area = list(sys.stdin.read().replace('\n', '').replace(' ', ''))
    size = int(math.sqrt(len(area)))

    return area, size

initial_area, size = read_area()

area = iterate(initial_area, size)
print(total_value(area))

area = iterate(initial_area, size, 1000000000)
print(total_value(area))
