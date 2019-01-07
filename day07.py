#! /usr/bin/env python3
import sys
from collections import deque

from heapq import *

if len(sys.argv) > 1 and sys.argv[1] == '--test':
    NumberOfWorkers = 2
    MinimumCompletionTime = 0
else:
    NumberOfWorkers = 5
    MinimumCompletionTime = 60

def read_step_dependencies():
    before = {}
    after  = {}

    for line in sys.stdin.readlines():
        record = line.split()

        u, v = record[1], record[7]

        if u not in after: after[u] = set()
        if v not in after: after[v] = set()
        after[u].add(v)

        if u not in before: before[u] = set()
        if v not in before: before[v] = set()
        before[v].add(u)

    return before, after

def ordered_steps(after):
    steps_in_order = deque()
    placed = set()

    def place(step):
        if step in placed:
            return

        for dependency in sorted(after[step], reverse = True):
            place(dependency)

        steps_in_order.appendleft(step)
        placed.add(step)

    for step in sorted(after.keys(), reverse = True):
        place(step)

    return ''.join(steps_in_order)

before, after = read_step_dependencies()

print(ordered_steps(after))

current_time = 0
available_steps = [ b for b in before if not before[b] ]
available_workers = NumberOfWorkers
schedule = []

heapify(available_steps)

def completion_time(step):
    return MinimumCompletionTime + ord(step) - ord('A') + 1

def next_task():
    step = heappop(available_steps)
    finish_by = current_time + completion_time(step)

    return (finish_by, step)

def allocate_workers():
    global available_workers

    while available_steps and available_workers:
        available_workers -= 1
        heappush(schedule, next_task())

def execute_tasks():
    global current_time, available_workers

    allocate_workers()

    while schedule:
        current_time, step = heappop(schedule)

        available_workers += 1
        for s in after[step]:
            before[s].remove(step)
            if not before[s]:
                heappush(available_steps, s)

        allocate_workers()

execute_tasks()

print(current_time)
