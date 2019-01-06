#! /usr/bin/env python3
import numpy as np
import scipy.signal as signal

from collections import namedtuple

Square = namedtuple('Square', 'x y size total_power')

serial_number = int(input().strip())
n = 300

power_level = np.arange(n * n, dtype = np.int32).reshape((n, n))

x = power_level %  n + 1
y = power_level // n + 1

rack_id = x + 10

power_level = (((rack_id * y + serial_number) * rack_id) // 100) % 10 - 5

total_power_kernel = np.array([
    [ 1, 1, 1 ],
    [ 1, 1, 1 ],
    [ 1, 1, 1 ]
])

total_power = signal.convolve2d(
    power_level,
    total_power_kernel, mode = 'valid'
)

maximum_power_fuel_cell = np.unravel_index(
    np.argmax(total_power, axis = None),
    total_power.shape
)

print(','.join(map(str,
    np.flip(maximum_power_fuel_cell) + np.array([ 1, 1 ])
)))

def largest_power_square(power_level):
    accum_power = np.concatenate((
        np.zeros((1, n)),
        power_level
    )).cumsum(axis = 0)

    max_square = Square(1, 1, 0, 0)

    for y0 in range(1, n + 1):
        for y1 in range(y0, n + 1):
            start = 0
            end   = y1 - y0 + 1

            sum_here = np.sum(
                  accum_power[y1    , start:end]
                - accum_power[y0 - 1, start:end]
           )

            max_in_row = max(0, sum_here)
            x0 = 0

            while end < n:
                sum_here += (accum_power[y1, end  ] - accum_power[y0 - 1, end  ])\
                          - (accum_power[y1, start] - accum_power[y0 - 1, start])

                start += 1
                end   += 1

                if sum_here > max_in_row:
                    max_in_row = sum_here
                    x0 = start

            if max_in_row > max_square.total_power:
                max_square = Square(
                    x           = x0 + 1,
                    y           = y0,
                    size        = y1 - y0 + 1,
                    total_power = max_in_row
                )

    return max_square

square = largest_power_square(power_level)

print(','.join(map(str,
    (square.x, square.y, square.size)
)))
