#! /usr/bin/env python3
import sys
from string import ascii_lowercase

def find_off_by_one_id(ids):
    seen = set()

    for s in ids:
        for i, c in enumerate(s):
            left, right = s[:i], s[i + 1:]
            if (left, right) in seen:
                return left + right

            seen.add((left, right))

def count_two_and_three_occurrences(ids):
    twos   = 0
    threes = 0

    for s in ids:
        d = {}

        for c in s:
            d[c] = d.get(c, 0) + 1

        twos   += int(any([ d[c] == 2 for c in s ]))
        threes += int(any([ d[c] == 3 for c in s ]))

    return twos * threes

ids = [ s.strip() for s in sys.stdin.read().split() ]

print(count_two_and_three_occurrences(ids))
print(find_off_by_one_id(ids))
