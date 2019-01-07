#! /usr/bin/env python3
import re, sys

import time, curses

Expected = '''...#..#.#..##......###...###...........
              ...#...#....#.....#..#..#..#...........
              ...##..##...##....#..#..#..##..........
              ..#.#...#..#.#....#..#..#...#..........
              ...#.#..#...#.#...#..#..##..##.........
              ....#...##...#.#..#..#...#...#.........
              ....##.#.#....#...#..##..##..##........
              ...#..###.#...##..#...#...#...#........
              ...#....##.#.#.#..##..##..##..##.......
              ...##..#..#####....#...#...#...#.......
              ..#.#..#...#.##....##..##..##..##......
              ...#...##...#.#...#.#...#...#...#......
              ...##.#.#....#.#...#.#..##..##..##.....
              ..#..###.#....#.#...#....#...#...#.....
              ..#....##.#....#.#..##...##..##..##....
              ..##..#..#.#....#....#..#.#...#...#....
              .#.#..#...#.#...##...#...#.#..##..##...
              ..#...##...#.#.#.#...##...#....#...#...
              ..##.#.#....#####.#.#.#...##...##..##..
              .#..###.#..#.#.#######.#.#.#..#.#...#..
              .#....##....#####...#######....#.#..##.'''\
            .replace(' ', '').split('\n')

def read_input():
    initial_state = ''
    patterns      = {}

    match = None
    def in_event(pattern, line):
        nonlocal match
        match = re.match(pattern, line)
        return match

    with open('test') as f:
        for line in f.readlines():
            if in_event(r'initial state: (.*)', line):
                initial_state = match.group(1)
            elif in_event(r'([.#]+) => ([.#])', line):
                pat, subst = match.groups()
                patterns[pat] = subst

    return initial_state, patterns

def compute_total(state, indices):
    return sum(index for i, index in enumerate(indices) if state[i] == '#')

def trim(state):
    return re.sub(r'^\.+(.*?)\.+$', r'\1', state)

def evolve(initial_state, patterns, num_generations, screen):
    assert trim(initial_state) == trim(Expected[0])

    indices       = list(range(len(initial_state)))
    current_state = initial_state
    next_state    = ''

    prev_total = 0
    for generation in range(num_generations):
        if current_state[:5] != '.....':
            current_state = '.....' + current_state
            indices = [ indices[0] - i for i in range(5, 0, -1) ] + indices

        if current_state[-5:] != '.....':
            current_state = current_state + '.....'
            indices += [ indices[-1] + i for i in range(1, 6) ]

        next_state = list('.' * len(current_state))

        for i in range(2, len(current_state) - 2):
            pat = current_state[i - 2:i + 3]
            next_state[i] = patterns[pat]
            print_state(screen, current_state, next_state, i, generation)

        next_state = ''.join(next_state)
        total = compute_total(next_state, indices)

        if trim(current_state) == trim(next_state):
            print(total + (total - prev_total) * (num_generations - generation - 1))
            return

        prev_total = total

        current_state = next_state
        assert trim(current_state) == trim(Expected[generation + 1])

def print_state(screen, cur, nxt, i, gen):
    screen.move(0, 0)

    pat = cur[i - 2:i + 3]

    screen.addstr(cur[:i - 2], curses.color_pair(1))
    screen.addstr(pat, curses.color_pair(2) | curses.A_BOLD | curses.A_STANDOUT)
    screen.addstr(cur[i + 3:], curses.color_pair(1))
    screen.addstr(' (')
    screen.addstr('{:2d}'.format(gen), curses.color_pair(3))
    screen.addstr(')\n')

    screen.move(1, 0)
    screen.clrtoeol()
    screen.addstr(1, i, patterns[pat], curses.color_pair(4))
    screen.addstr('\n')

    screen.addstr(''.join(nxt), curses.color_pair(5) | curses.A_BOLD)
    screen.addstr(' (')
    screen.addstr('{:2d}'.format(gen + 1), curses.color_pair(3))
    screen.addstr(')\n')

    screen.refresh()
    time.sleep(.01)

initial_state, patterns = read_input()

def main(screen):
    curses.init_color(curses.COLOR_BLACK  , 300 , 86  , 0)
    curses.init_color(curses.COLOR_WHITE  , 1000, 1000, 1000)
    curses.init_color(curses.COLOR_RED    , 1000, 300 , 0)
    curses.init_color(curses.COLOR_GREEN  , 0   , 1000, 0)
    curses.init_color(curses.COLOR_MAGENTA, 1000, 0   , 1000)

    curses.init_pair(1, curses.COLOR_WHITE  , curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW , curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN  , curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED    , curses.COLOR_BLACK)

    screen.clear()
    evolve(initial_state, patterns, len(Expected) - 1, screen)

curses.wrapper(main)
