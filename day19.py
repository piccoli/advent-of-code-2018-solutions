#! /usr/bin/env python3
from elfcode_emulator import *

def loop_limit(register_values, iterations):
    m = Machine(program_text, register_values)

    for i in range(iterations):
        regs = next(m)

    return regs[3]

def result(n):
    # Translated machine code (from my input at least)
    # boils down to:
    #acc = 0
    #for i in range(n + 1):
    #    for j in range(1, n + 1):
    #        if i * j == n:
    #            acc += i

    # Here is a slight improvement though:
    return sum(0 if n % i else n // i for i in range(1, n + 1))

program_text = sys.stdin.read()

# This was discovered empirically by actually running the 
# input Elfcode.
print(result(loop_limit([ 0, 0, 0, 0, 0, 0 ],     3 * 3)))
print(result(loop_limit([ 1, 0, 0, 0, 0, 0 ], 1 + 4 * 4)))
