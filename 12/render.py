#! /usr/bin/env python3
import re, sys

import cv2
import numpy as np

def to_set(pattern):
    return set(i for i, pot in enumerate(pattern) if pot == '#')

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

def to_pattern(state, i = None, j = None):
    if len(state) == 0:
        if i is None or j is None:
            return ''
        return '.' * (j - i + 1)

    if i is None: i = min(state)
    if j is None: j = max(state)

    return ''.join('.#'[k in state] for k in range(i, j + 1))

def trim(state):
    return re.sub(r'^\.+(.*?)\.+$', r'\1', to_pattern(state))

def evolve(initial_state, patterns):
    min_x = -10
    max_x = 150

    size = max_x - min_x + 1
    video_size = size * 8

    num_generations = size - 1

    def render_frame(generation, pattern):
        im[generation, :, :] = np.array([
            [ 0, 255 - int(i / (len(pattern) - 1) * 63), 0 ]
                if pot == '#' else [ 0, 0, 0 ]
                    for i, pot in enumerate(pattern)
        ])
        video.write(cv2.resize(im, (video_size, video_size)))

    four_cc = cv2.VideoWriter_fourcc(*'MP42')
    video = cv2.VideoWriter('output.avi', four_cc, 60.0, (video_size, video_size))

    current_state = initial_state

    im = np.zeros((size, size, 3), np.uint8)
    for generation in range(num_generations):
        pat = to_pattern(current_state, min_x, max_x)

        render_frame(generation, pat)

        mins = min(current_state)
        maxs = max(current_state)

        next_state = set()

        pattern = to_pattern(current_state, mins - 5, maxs + 5)
        for i in range(mins - 2, maxs + 3):
            if pattern[i - (mins - 5) - 2:i - (mins - 5) + 3] in patterns:
                next_state.add(i)

        current_state = next_state

    pat = to_pattern(current_state, min_x, max_x)

    render_frame(num_generations, pat)
    video.release()

initial_state, patterns = read_input()

evolve(initial_state, patterns)
