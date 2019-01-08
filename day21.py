#! /usr/bin/env python3
'''
Day 21's solution: still an assumption of how it works in general
based solely on my input.
'''
from elfcode_emulator import *

def min_and_max_instructions(r5_initial_value):
    sequence = []
    cache = set()

    f = 0
    while True:
        c = f | 65536
        f = r5_initial_value

        while True:
            f += c & 255; f &= (1 << 24) - 1
            f *= 65899  ; f &= (1 << 24) - 1

            if c < 256:
                break

            c //= 256

        if f in cache:
            return sequence[0], sequence[-1]

        cache.add(f)
        sequence.append(f)

def find_r5_initial_value(program_text):
    m = Machine(program_text)

    for _ in range(9):
        regs = next(m)

    return regs[5]

program_text = sys.stdin.read()

r5_initial_value = find_r5_initial_value(program_text)

print('\n'.join(map(str,
    min_and_max_instructions(r5_initial_value)
)))
