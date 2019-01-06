#! /usr/bin/env python3
import sys, re, time

from functools import wraps

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

    def microcoded(op):
        @wraps(op)
        def wrapped_op(self, a, b, c):
            if self.ip_bound is not None:
                self.register[self.ip_bound] = self.ip

            print('ip={:2d} [{}] {:4s} {:d} {:d} {:d}'.format(
                self.ip,
                ', '.join('{:6d}'.format(r) for r in self.register),
                op.__name__, a, b, c
            ), end = '', flush = True, file = sys.stderr)

            op(self, a, b, c)

            print(' [{}]'.format(
                ', '.join('{:6d}'.format(r) for r in self.register)
            ), flush = True, file = sys.stderr)

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
    def banr(self, a, b, c):
        self.register[c] = self.register[a] & self.register[b]

    @microcoded
    def bani(self, a, b, c):
        self.register[c] = self.register[a] & b

    @microcoded
    def borr(self, a, b, c):
        self.register[c] = self.register[a] | self.register[b]

    @microcoded
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

program_text = sys.stdin.read()

for registers in [ 0, 0, 0, 0, 0, 0 ], [ 1, 0, 0, 0, 0, 0 ]:
    machine = Machine(program_text, values = registers)
    machine.run()
    print(machine.register[0])
