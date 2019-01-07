#! /usr/bin/env python3
'''
Solution by Justin Le: https://blog.jle.im/entry/shifting-the-stars.html
'''
import sys, re
from functools import partial

pv = 0
vv = 0
for record in map(partial(re.match, r'position=<( *-?\d+), ( *-?\d+)> velocity=<( *-?\d+), ( *-?\d+)>'), sys.stdin.readlines()):
    px, py, vx, vy = map(int, record.groups())
    pv += px * vx + py * vy
    vv += vx * vx + vy * vy

print(int(-pv / vv))
