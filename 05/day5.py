#! /usr/bin/env python3
from string import ascii_lowercase

polymer = list(map(ord, input().strip()))

def polarized(p, i):
    return abs(p[i] - p[i - 1]) == 32

def tolower(c):
    return c + 32 if c < 97 else c

def collapsed(remove_unit = None):
    p = [ u for u in polymer if tolower(u) != remove_unit ]
    i = 1
    while i < len(p):
        while 0 < i < len(p) and polarized(p, i):
            p[i - 1:] = p[i + 1:]
            i -= 1
        i += 1

    return p

polymer = collapsed()

print(len(collapsed()))

shortest_len = min(len(collapsed(u)) for u in map(ord, ascii_lowercase))

print(shortest_len)
