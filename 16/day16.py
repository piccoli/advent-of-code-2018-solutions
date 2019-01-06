#! /usr/bin/env python3
import sys, re, time

inp = sys.stdin.read().strip()

record_set, program = inp.split('\n\n\n')

class VM:
    def __init__(self, values = [ 0, 0, 0, 0 ]):
        self.register = values[:]

    def addr(self, a, b, c): self.register[c] = self.register[a] + self.register[b]
    def addi(self, a, b, c): self.register[c] = self.register[a] + b

    def mulr(self, a, b, c): self.register[c] = self.register[a] * self.register[b]
    def muli(self, a, b, c): self.register[c] = self.register[a] * b

    def banr(self, a, b, c): self.register[c] = self.register[a] & self.register[b]
    def bani(self, a, b, c): self.register[c] = self.register[a] & b

    def borr(self, a, b, c): self.register[c] = self.register[a] | self.register[b]
    def bori(self, a, b, c): self.register[c] = self.register[a] | b

    def setr(self, a, b, c): self.register[c] = self.register[a]
    def seti(self, a, b, c): self.register[c] = a

    def gtir(self, a, b, c): self.register[c] = int(a > self.register[b])
    def gtri(self, a, b, c): self.register[c] = int(self.register[a] > b)
    def gtrr(self, a, b, c): self.register[c] = int(self.register[a] > self.register[b])

    def eqir(self, a, b, c): self.register[c] = int(a == self.register[b])
    def eqri(self, a, b, c): self.register[c] = int(self.register[a] == b)
    def eqrr(self, a, b, c): self.register[c] = int(self.register[a] == self.register[b])

    instruction_set = {
        addi, addr,
        mulr, muli,
        banr, bani,
        borr, bori,
        setr, seti,
        gtir, gtri, gtrr,
        eqir, eqri, eqrr
    }

def get_state(s, when):
    m = re.match(r'{}:\s*\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]'.format(when), s)
    return list(map(int, m.groups()))

def records():
    for record in record_set.split('\n\n'):
        before, instruction, after = record.split('\n')
        before = get_state(before, 'Before')
        after  = get_state(after , 'After')
        opcode, a, b, c = map(int, instruction.split())

        yield before, after, opcode, a, b, c

def instructions():
    for instruction in program.strip().split('\n'):
        opcode, a, b, c = map(int, instruction.strip().split())

        yield opcode, a, b, c

op_set = { instruction: set(range(16)) for instruction in VM.instruction_set }
op_map = {}

total_ambiguous = 0

for before, after, opcode, a, b, c in records():
    possible_opcodes = 0

    for instruction in VM.instruction_set:
        vm = VM(before)
        instruction(vm, a, b, c)
        if vm.register == after:
            possible_opcodes += 1
        elif opcode in op_set[instruction]:
            op_set[instruction].remove(opcode)

    if possible_opcodes >= 3:
        total_ambiguous += 1

print(total_ambiguous)

for opcode in range(16):
    min_instruction = min(op_set.keys(), key = lambda instruction: len(op_set[instruction]))

    min_opcodes = op_set[min_instruction]

    assert len(min_opcodes) == 1

    op_map[list(min_opcodes)[0]] = min_instruction
    del op_set[min_instruction]

    for instruction in op_set.keys():
        op_set[instruction] -= min_opcodes

machine = VM()
for opcode, a, b, c in instructions():
    op_map[opcode](machine, a, b, c)

print(machine.register[0])
