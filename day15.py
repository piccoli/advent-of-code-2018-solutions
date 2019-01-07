#! /usr/bin/env python3
import sys

from copy import deepcopy
from collections import deque

UNKNOWN, EMPTY, WALL, ELF, GOBLIN = '*.#EG'

Symbol = dict(
    Thing  = UNKNOWN,
    Unit   = UNKNOWN,
    Empty  = EMPTY,
    Wall   = WALL,
    Elf    = ELF,
    Goblin = GOBLIN
)

class ThingType(type):
    def __init__(cls, name, bases, dct):
        def default_init(self, *args, **kwargs):
            super(cls, self).__init__(*args, **kwargs)
            cls.__my_init_(self, *args, **kwargs)

        cls.__my_init_ = cls.__init__
        cls.__init__   = default_init

class AbstractThing:
    def __init__(self, *args, **kwargs):
        pass

class Thing(AbstractThing, metaclass = ThingType):
    def __init__(self, board, x, y, sym = None, *args, **kwargs):
        self.board = board
        self.x     = x
        self.y     = y

        self.symbol = sym if sym is not None\
                else Symbol[self.__class__.__name__]

    def __str__(self):
        return self.symbol

    def nearby(self, thing_type):
        return tuple(
            (y, x) for x, y in (
                (self.x    , self.y - 1),
                (self.x - 1, self.y    ),
                (self.x + 1, self.y    ),
                (self.x    , self.y + 1)
            )
            if (y, x) in self.board\
               and isinstance(self.board[y, x], thing_type)
        )

    def range(self):
        return self.nearby(Empty)

class Unit(Thing):
    def __init__(self, *args, hit_points = 200, attack_power = 3, **kwargs):
        self.hit_points   = hit_points
        self.attack_power = attack_power
        self.is_dead      = False

    def nearby_enemies(self):
        return self.nearby(self.enemy_type())

    def enemy_type(self):
        return Unit

    def next_move(self, targets):
        ux, uy = self.x, self.y

        parent = { (uy, ux): None }
        cost   = { (uy, ux): 0    }

        q = deque([ (cost[uy, ux], uy, ux) ])

        while q:
            c, y, x = q.popleft()

            if (y, x) in targets:
                while parent[y, x] is not None and parent[y, x] != (uy, ux):
                    y, x = parent[y, x]

                return x, y

            for ry, rx in self.board[y, x].range():
                if (ry, rx) not in cost or c + 1 < cost[ry, rx]:
                    cost[ry, rx] = c + 1
                    parent[ry, rx] = y, x

                    q.append((cost[ry, rx], ry, rx))

        return None, None

    def attack(self):
        nearby = self.nearby_enemies()

        if nearby:
            y, x = min(nearby, key = lambda pos: (self.board[pos].hit_points, *pos))

            selected = self.board[y, x]

            selected.hit_points -= self.attack_power

            if selected.hit_points <= 0:
                selected.is_dead = True
                self.board[y, x] = Empty(self.board, x, y)

            return True

        return False

    def move(self, units):
        my_enemies = units[self.enemy_type()]

        targets = set()

        for enemy in my_enemies:
            if not enemy.is_dead:
                targets.update(enemy.range())

        if not targets:
            return False

        nx, ny = self.next_move(targets)

        if nx is not None and ny is not None:
            self.board[ny, nx] = self.board[self.y, self.x]
            self.board[self.y, self.x] = Empty(self.board, self.x, self.y)

            self.x = nx
            self.y = ny

            return True

        return False

class Empty(Thing): pass
class Wall(Thing):  pass

class Goblin(Unit):
    def enemy_type(self):
        return Elf

class Elf(Unit):
    def enemy_type(self):
        return Goblin

Type = {
    EMPTY:  Empty,
    WALL:   Wall,
    ELF:    Elf,
    GOBLIN: Goblin
}

def read_board():
    board = {}
    for y, row in enumerate(sys.stdin.read().strip().split()):
        for x, col in enumerate(row):
            board[y, x] = Type[col](board, x, y)

    return board

def fight(initial_board, max_elf_attack_power = 200):
    l = 3
    u = max_elf_attack_power

    while l <= u:
        board = deepcopy(initial_board)
        elf_attack_power = (l + u) // 2

        all_units = [
            thing for thing in board.values() if isinstance(thing, Unit)
        ]

        units = {
            Elf:    [ unit for unit in all_units if isinstance(unit, Elf) ],
            Goblin: [ unit for unit in all_units if isinstance(unit, Goblin) ]
        }

        total_elves = len(units[Elf])

        for elf in units[Elf]:
            elf.attack_power = elf_attack_power

        total_rounds = 0

        while next_round(board, all_units, units):
            total_rounds += 1

        total_hit_points = sum([ unit.hit_points for unit in all_units if not unit.is_dead ])

        if len(units[Elf]) == total_elves:
            u = elf_attack_power - 1
        else:
            l = elf_attack_power + 1

    return total_rounds * total_hit_points

def next_round(board, all_units, units):
    for unit in sorted(all_units, key = lambda unit: (unit.y, unit.x)):
        if not unit.is_dead:
            if not units[Elf] or not units[Goblin]:
                return False

            action = unit.attack() or (unit.move(units) and unit.attack())

            units[Elf]    = [ elf    for elf    in units[Elf]    if not elf.is_dead    ]
            units[Goblin] = [ goblin for goblin in units[Goblin] if not goblin.is_dead ]

            all_units[:] = units[Elf] + units[Goblin]

    return True

initial_board = read_board()

print(fight(initial_board, max_elf_attack_power = 3))
print(fight(initial_board))
