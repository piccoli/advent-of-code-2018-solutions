#! /usr/bin/env python3
import re, sys

def evolve(initial_state, patterns, num_generations):
    current_state = initial_state

    prev_total = 0
    for generation in range(num_generations):
        mins = min(current_state)
        maxs = max(current_state)

        next_state = set()

        pattern = to_pattern(current_state, mins - 5, maxs + 5)
        for i in range(mins - 2, maxs + 3):
            if pattern[i - (mins - 5) - 2:i - (mins - 5) + 3] in patterns:
                next_state.add(i)

        total = sum(next_state)

        if trim(current_state) == trim(next_state):
            return total + (total - prev_total) * (num_generations - generation - 1)

        prev_total = total

        current_state = next_state

    return sum(current_state)

def to_pattern(state, i = None, j = None):
    if len(state) == 0:
        if i is None or j is None:
            return ''
        return '.' * (j - i + 1)

    if i is None: i = min(state)
    if j is None: j = max(state)

    return ''.join(
        '.#'[k in state] for k in range(i, j + 1)
    )

def trim(state):
    return re.sub(r'^\.+(.*?)\.+$', r'\1', to_pattern(state))

def read_input():
    initial_state = set()
    patterns      = set()

    match = None
    def in_event(pattern, line):
        nonlocal match
        match = re.match(pattern, line)
        return match

    for line in sys.stdin.readlines():
        if in_event(r'initial state: (.*)', line):
            initial_state = to_set(match.group(1))

        elif in_event(r'([.#]+) => #', line):
            patterns.add(match.group(1))

    return initial_state, patterns

def to_set(pattern):
    return set(i for i, pot in enumerate(pattern) if pot == '#')

initial_state, patterns = read_input()

number_of_pots = evolve(initial_state, patterns, 20)
print(number_of_pots)

number_of_pots = evolve(initial_state, patterns, 50000000000)
print(number_of_pots)
