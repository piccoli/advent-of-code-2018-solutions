#! /usr/bin/env python3
import sys, re

from functools import partial, reduce
from itertools import product

print(sum(
    reduce(lambda fabric, claim:
        (lambda fabric, x, y, w, h: {
            **fabric,
            **dict(zip(
                product(
                    range(y, y + h),
                    range(x, x + w)
                ),
                map(
                    lambda p: int(p in fabric),
                    product(
                        range(y, y + h),
                        range(x, x + w)
                    )
                )
            ))
        })(fabric, *map(int, claim.groups())),
        map(
            partial(re.match, r'#\d+ @ (\d+),(\d+): (\d+)x(\d+)'),
            sys.stdin.readlines()
        ), {}
    ).values()
))
