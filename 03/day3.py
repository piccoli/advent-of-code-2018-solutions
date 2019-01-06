#! /usr/bin/env python3
import sys, re
from functools import partial
from itertools import product

fabric = {}
claims = []

parse_record = partial(re.match, r'#(\d+) @ (\d+),(\d+): (\d+)x(\d+)')

records = map(parse_record, sys.stdin.readlines())

for record in records:
    c, x, y, w, h = map(int, record.groups())

    claims.append((c, x, y, w, h))

    for i, j in product(range(y, y + h), range(x, x + w)):
        fabric[i, j] = int((i, j) in fabric)

print(sum(fabric.values()))

for c, x, y, w, h in claims:
    intact = 0 == sum(
        fabric[i, j]
            for i, j in product(
                range(y, y + h),
                range(x, x + w)
            )
    )

    if intact:
        print(c)
        break
