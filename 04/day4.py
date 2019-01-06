#! /usr/bin/env python3
import sys, re

from functools import partial

match        = None
current_gid  = None
start        = 0
slept_for    = {}
slept_during = {}

def in_event(pattern, log):
    global match
    match = re.match(pattern, log)

    return match

def sleepiest_guard_minute(table):
    guard  = max(table,     key = lambda k: max(table[k]))
    minute = max(range(60), key = lambda m: slept_during[guard][m])

    return guard * minute

parse_record = partial(re.match, r'\[(\d+)-(\d+)-(\d+) (\d+):(\d+)\] ([^\n]+)')

records = []

for record in map(parse_record, sys.stdin.readlines()):
    *time, log = record.groups()
    year, month, day, hour, minute = map(int, time)

    records.append((year, month, day, hour, minute, log))

for year, month, day, hour, minute, log in sorted(records):
    if in_event(r'wakes up', log):
        slept_for[current_gid][0] += minute - start

        for m in range(start, minute):
            slept_during[current_gid][m] += 1

    elif in_event(r'falls asleep', log):
        start = minute

    elif in_event(r'Guard #(\d+) begins shift', log):
        current_gid = int(match.group(1))

        if current_gid not in slept_during:
            slept_for[current_gid] = [ 0 ]
            slept_during[current_gid] = [ 0 for _ in range(60) ]

for strategy in slept_for, slept_during:
    print(sleepiest_guard_minute(strategy))
