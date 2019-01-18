#! /usr/bin/env python3
from functools import lru_cache
from itertools import product
from collections import namedtuple
from heapq import *

import time, curses

memoized = lru_cache(maxsize = None)

State = namedtuple('State', 'x y tool')

Rocky, Wet, Narrow = range(3)

Torch, ClimbingGear, Neither = range(3)

SymbolFor = '.=|'

AllowedToolsForRegion = {
    Rocky:   frozenset((ClimbingGear, Torch)),
    Wet:     frozenset((ClimbingGear, Neither)),
    Narrow:  frozenset((Torch       , Neither))
}

Wait = .02
Sleep = True

def main(screen):
    global Depth, X, Y

    curses.init_pair(1, curses.COLOR_RED    , curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN  , curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW , curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE   , curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN   , curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE  , curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK  , curses.COLOR_BLACK)

    curses.curs_set(False)
    Depth, X, Y = read_input()

    screen.clear()
    screen.move(0, 0)
    screen.addstr(1, 0, 'Computing minimal-cost path. This may take a few seconds...')
    screen.refresh()

    mincost = min_cost(screen, X, Y)

    screen.clear()
    screen.move(0, 0)
    screen.addstr(1, 0, 'Risk level: {}'.format(risk_level()))
    screen.addstr(2, 0, 'Minimum cost to reach target: {}'.format(mincost))
    screen.refresh()
    time.sleep(3)

def read_input():
    def get_field():
        _, f = input().strip().split()

        return f

    depth = int(get_field())
    x, y = map(int, get_field().split(','))

    return depth, x, y

def min_cost(screen, x, y):
    start = State(0, 0, Torch)
    goal  = State(x, y, Torch)

    q = [ (0, start) ]
    open_set = { start: 0 }
    parent = { start: None }

    closed_set = set()

    while q:
        _, state = heappop(q)

        if state not in open_set:
            continue

        closed_set.add(state)

        if state == goal:
            path = []
            while state:
                path.append(state)
                state = parent[state]
            path.reverse()

            print_plan(screen, path)

            return open_set[goal]

        for action_cost, next_state in possible_actions_from(state):
            if next_state not in closed_set\
                and (next_state not in open_set\
                    or open_set[next_state] > open_set[state] + action_cost):

                parent[next_state] = state

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

    for xn, yn in neighbors:
        yield 1, State(xn, yn, tool)

    other_tools = AllowedToolsForRegion[region_type(x, y)] - { tool }

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

def print_plan(screen, path, window_width = 40, window_height = 20):
    previous = None

    screen.clear()
    for state in path:
        x0 = state.x - window_width  // 2
        y0 = state.y - window_height // 2
        x1 = state.x + window_width  // 2
        y1 = state.y + window_height // 2

        screen.move(0, 0)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                char = '?'
                if x == X and y == Y:
                    char = 't'
                elif x == state.x and y == state.y:
                    char = 'TCN'[state.tool]
                elif x >= 0 and y >= 0:
                    char = SymbolFor[region_type(x, y)]

                screen.addstr(y - y0, x - x0, char, color(char))

        screen.addstr(
            y1 - y0 + 1,
            0,
                'Begin at ({}, {}) carrying {}         '.format(
                    state.x, state.y, tool_name[state.tool]
                ) if not previous
            else
                'Change tool to {}                     '.format(
                    tool_name[state.tool]
                ) if previous.tool != state.tool
            else
                'Move to ({}, {})                      '.format(
                    state.x, state.y
                )
        )
        screen.refresh()

        if Sleep:
            time.sleep(Wait)

        previous = state

    if Sleep:
        time.sleep(3)

tool_name = 'torch', 'climbing gear', 'neither'
color_map = {
    '?': (8, 0),
    '.': (8, curses.A_BOLD),
    '=': (4, curses.A_BOLD | curses.A_ITALIC),
    '|': (3, 0),
    'C': (2, curses.A_BOLD),
    'T': (3, curses.A_BOLD | curses.A_STANDOUT | curses.A_BLINK),
    't': (5, curses.A_BOLD | curses.A_BLINK | curses.A_STANDOUT),
    'N': (7, 0)
}

def color(k):
    pair, attr = color_map[k]

    return curses.color_pair(pair) | attr

curses.wrapper(main)
