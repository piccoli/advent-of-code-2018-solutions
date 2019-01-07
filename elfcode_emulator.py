#! /usr/bin/env python3
import sys

import operator
from functools import wraps

def log(*args, **kwargs):
    print(*args, **kwargs, flush = True, file = sys.stderr)

log = lambda *args, **kwargs: None

class Machine:
    def __init__(self, program_text, values = [ 0, 0, 0, 0, 0, 0 ]):
        self.register     = values[:]
        self.ip           = 0
        self.ip_bound     = None
        self.program_text = program_text
        self.program      = [ instruction for instruction in self.__instructions() ]

    def run(self):
        for regs in self:
            pass

    def __instructions(self):
        for instruction in self.program_text.strip().split('\n'):
            if instruction[:3] == '#ip':
                _, register = instruction.split()
                self.ip_bound = int(register)
                continue

            opcode, *operands = instruction.split()
            a, b, c = map(int, operands)

            yield opcode, a, b, c

    # Turns integer-based bitwise instructions into string-based
    # ones. This was not really necessary in the end, but looked
    # like a clue at first in the problem statement.
    def hacked(operation = None, immediate_addressing = False):
        def wrapper(op):
            @wraps(op)
            def wrapped_op(self, a, b, c):
                if not operation:
                    return op(self, a, b, c)

                if not immediate_addressing:
                    b = self.register[b]

                self.register[c] = int(''.join(
                    str(operation(*map(ord, (ca, cb))))
                    for ca, cb in zip(
                        *map(str, (self.register[a], b))
                    )
                ))
            return wrapped_op
        return wrapper

    def microcoded(op):
        @wraps(op)
        def wrapped_op(self, a, b, c):
            if self.ip_bound is not None:
                self.register[self.ip_bound] = self.ip

            log('ip={:3d} {:4s} {:10d} {:10d} {:10d}'.format(
                self.ip,
                op.__name__, a, b, c
            ), end = '')

            op(self, a, b, c)

            log(' -> [ {} ]'.format(
                ' '.join('{:11d}'.format(r) for r in self.register)
            ))

            if self.ip_bound is not None:
                self.ip = self.register[self.ip_bound]

            self.ip += 1

        return wrapped_op

    @microcoded
    def addr(self, a, b, c):
        self.register[c] = self.register[a] + self.register[b]

    @microcoded
    def addi(self, a, b, c):
        self.register[c] = self.register[a] + b

    @microcoded
    def mulr(self, a, b, c):
        self.register[c] = self.register[a] * self.register[b]

    @microcoded
    def muli(self, a, b, c):
        self.register[c] = self.register[a] * b

    @microcoded
    #@hacked(operator.and_, False)
    def banr(self, a, b, c):
        self.register[c] = self.register[a] & self.register[b]

    @microcoded
    def bani(self, a, b, c):
        self.register[c] = self.register[a] & b

    @microcoded
    #@hacked(operator.and_, False)
    def borr(self, a, b, c):
        self.register[c] = self.register[a] | self.register[b]

    @microcoded
    #@hacked(operator.or_, True)
    def bori(self, a, b, c):
        self.register[c] = self.register[a] | b

    @microcoded
    def setr(self, a, b, c):
        self.register[c] = self.register[a]

    @microcoded
    def seti(self, a, b, c):
        self.register[c] = a

    @microcoded
    def gtir(self, a, b, c):
        self.register[c] = int(a > self.register[b])

    @microcoded
    def gtri(self, a, b, c):
        self.register[c] = int(self.register[a] > b)

    @microcoded
    def gtrr(self, a, b, c):
        self.register[c] = int(self.register[a] > self.register[b])

    @microcoded
    def eqir(self, a, b, c):
        self.register[c] = int(a == self.register[b])

    @microcoded
    def eqri(self, a, b, c):
        self.register[c] = int(self.register[a] == b)

    @microcoded
    def eqrr(self, a, b, c):
        self.register[c] = int(self.register[a] == self.register[b])

    instruction_set = {
        addi, addr,
        mulr, muli,
        banr, bani,
        borr, bori,
        setr, seti,
        gtir, gtri, gtrr,
        eqir, eqri, eqrr
    }

    def __iter__(self):
        return self

    def __next__(self):
        if self.ip < 0 or self.ip >= len(self.program):
            raise StopIteration

        opcode, a, b, c = self.program[self.ip]

        getattr(Machine, opcode)(self, a, b, c)

        return self.register

if __name__ == '__main__':
    program_text = sys.stdin.read()

    try:
        r0 = int(sys.argv[1])
    except:
        r0 = 0

    machine = Machine(program_text, values = [ r0, 0, 0, 0, 0, 0 ])
    machine.run()
    print(machine.register[0])
