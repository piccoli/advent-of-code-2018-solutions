#! /usr/bin/env python3
import sys, re

from functools import partial

parse_record = partial(re.match, r'\[(\d+)-(\d+)-(\d+) (\d+):(\d+)\] ([^\n]+)')

def get_stats_from(records):
    start        = 0
    slept_for    = {}
    slept_during = {}
    current_gid  = None
    match        = None

    def in_event(pattern, log):
        nonlocal match
        match = re.match(pattern, log)

        return match

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

    return slept_for, slept_during

def parse_records():
    records = []

    for record in map(parse_record, sys.stdin.readlines()):
        *time, log = record.groups()
        year, month, day, hour, minute = map(int, time)

        records.append((year, month, day, hour, minute, log))

    return records

def sleepiest_guard_minute(table):
    guard  = max(table,     key = lambda k: max(table[k]))
    minute = max(range(60), key = lambda m: slept_during[guard][m])

    return guard * minute

records = parse_records()

slept_for, slept_during = get_stats_from(records)

for strategy in slept_for, slept_during:
    print(sleepiest_guard_minute(strategy))
