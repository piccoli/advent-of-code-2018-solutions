#! /usr/bin/env python3
from functools import lru_cache
from itertools import product
from collections import namedtuple
from heapq import *

memoized = lru_cache(maxsize = None)

State = namedtuple('State', 'x y tool')

Rocky, Wet, Narrow = range(3)

Torch, ClimbingGear, Neither = range(3)

AllowedToolsForRegion = {
    Rocky:   frozenset((ClimbingGear, Torch)),
    Wet:     frozenset((ClimbingGear, Neither)),
    Narrow:  frozenset((Torch       , Neither))
}

def read_input():
    def get_field():
        _, f = input().strip().split()

        return f

    depth = int(get_field())
    x, y = map(int, get_field().split(','))

    return depth, x, y

def min_cost(x, y):
    start = State(0, 0, Torch)
    goal  = State(x, y, Torch)

    q = [ (0, start) ]
    open_set = { start: 0 }

    closed_set = set()

    while q:
        _, state = heappop(q)

        if state not in open_set:
            continue

        closed_set.add(state)

        if state == goal:
            return open_set[goal]

        for action_cost, next_state in possible_actions_from(state):
            if next_state not in closed_set\
                and (next_state not in open_set\
                    or open_set[next_state] > open_set[state] + action_cost):

                open_set[next_state] = open_set[state] + action_cost

                cost_estimate = open_set[next_state] + lower_bound_to_goal(next_state, goal)

                heappush(q, (cost_estimate, next_state))

        del open_set[state]

def possible_actions_from(state):
    x, y, tool = state

    neighbors = (
        (xn, yn) for xn, yn in (
            (x    , y - 1),
            (x - 1, y    ),
            (x + 1, y    ),
            (x    , y + 1)
        )
        if xn >= 0 and yn >= 0\
            and tool in AllowedToolsForRegion[region_type(xn, yn)]
    )

    other_tools = [
        t for t in { ClimbingGear, Torch, Neither } - { tool }
        if t in AllowedToolsForRegion[region_type(x, y)]
    ]

    for xn, yn in neighbors:
        yield 1, State(xn, yn, tool)

    for next_tool in other_tools:
        yield 7, State(x, y, next_tool)

def lower_bound_to_goal(state, goal):
    return abs(goal.x - state.x) + abs(goal.y - state.y) + 7 * (state.tool != goal.tool)

@memoized
def risk_level():
    return sum(region_type(x, y) for x, y in product(range(X + 1), range(Y + 1)))

@memoized
def region_type(x, y):
    return erosion_level(geologic_index(x, y)) % 3

@memoized
def geologic_index(x, y):
    if x == X and y == Y:
        return 0

    if y == 0:
        return x * 16807

    if x == 0:
        return y * 48271

    level_above = erosion_level(geologic_index(x, y - 1))
    level_left  = erosion_level(geologic_index(x - 1, y))

    return level_above * level_left

@memoized
def erosion_level(geologic_index):
    return (geologic_index + Depth) % 20183

Depth, X, Y = read_input()

print(risk_level())
print(min_cost(X, Y))
