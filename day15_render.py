#! /usr/bin/env python3
import sys

from copy import deepcopy
from collections import deque

import time, curses

Wait  = .05
Sleep = True

UNKNOWN, RANGE, REACHABLE, NEAREST, CHOSEN, EMPTY, WALL, ELF, GOBLIN, HIT = '*?@!+.#EGX'

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

        chosen = { (uy, ux): self.symbol.lower() }
        parent = { (uy, ux): None }
        cost   = { (uy, ux): 0    }

        q = deque([ (cost[uy, ux], uy, ux) ])

        while q:
            c, y, x = q.popleft()

            draw_board(self.board, targets, cost, chosen, wait = 0)

            if (y, x) in targets:
                chosen[y, x] = CHOSEN

                draw_board(self.board, targets, cost, chosen, wait = .05)

                while parent[y, x] is not None and parent[y, x] != (uy, ux):
                    y, x = parent[y, x]
                    chosen[y, x] = NEAREST

                    draw_board(self.board, targets, cost, chosen, wait = .0005)

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

            draw_board(self.board, { (y, x): HIT })

            selected = self.board[y, x]

            selected.hit_points -= self.attack_power

            if selected.hit_points <= 0:
                selected.is_dead = True
                self.board[y, x] = Empty(self.board, x, y)

            return True

        return False

    def move(self, units):
        my_enemies = units[self.enemy_type()]

        targets = {}

        for enemy in my_enemies:
            if not enemy.is_dead:
                targets.update({
                    (y, x): '?' for y, x in enemy.range()
                })

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

screen = None

def main(scr):
    # FIXME Lazy hack
    global screen
    screen = scr

    curses.init_pair(1, curses.COLOR_RED    , curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN  , curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW , curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE   , curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN   , curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE  , curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK  , curses.COLOR_BLACK)

    curses.curs_set(False)

    initial_board = read_board()

    fight(screen, initial_board, min_elf_attack_power = 3 , max_elf_attack_power = 3)
    fight(screen, initial_board, min_elf_attack_power = 12, max_elf_attack_power = 12)

def read_board():
    board = {}
    for y, row in enumerate(sys.stdin.read().strip().split()):
        for x, col in enumerate(row):
            board[y, x] = Type[col](board, x, y)

    return board

def fight(screen, initial_board, min_elf_attack_power = 3, max_elf_attack_power = 200):
    l = min_elf_attack_power
    u = max_elf_attack_power

    board_height = max(y + 1 for y, x in initial_board)
    board_width  = max(x + 1 for y, x in initial_board)

    original_height, original_width = screen.getmaxyx()

    screen.move(0, 0)
    screen.clear()
    screen.resize(board_height + 2, board_width + 2)
    screen.clear()

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

    screen.resize(
        max(board_height, original_height) + 2,
        max(board_width , original_width ) + 2
    )

    print_battle_summary(
        screen,
        initial_board,
        board,
        all_units,
        total_rounds,
        total_hit_points,
        elf_attack_power
    )

    return total_rounds * total_hit_points

def next_round(board, all_units, units):
    for unit in sorted(all_units, key = lambda unit: (unit.y, unit.x)):
        if not unit.is_dead:
            draw_board(board, { (unit.y, unit.x): unit.symbol.lower() })

            if not units[Elf] or not units[Goblin]:
                return False

            action = unit.attack() or (unit.move(units) and unit.attack())

            draw_board(board, { (unit.y, unit.x): unit.symbol.lower() })

            units[Elf]    = [ elf    for elf    in units[Elf]    if not elf.is_dead    ]
            units[Goblin] = [ goblin for goblin in units[Goblin] if not goblin.is_dead ]

            all_units[:] = units[Elf] + units[Goblin]

    return True

def draw_board(board, *overlays, wait = Wait, move_to_top = True):
    global screen

    overlaid_board = {
        k: str(v) for k, v in board.items()
    }

    for overlay in overlays:
        overlaid_board.update(overlay)

    if move_to_top:
        screen.border()
        screen.move(1, 1)

    oy, ox = screen.getyx()

    for y, x in sorted(overlaid_board):
        tile = overlaid_board[y, x]
        if tile == HIT:
            curses.flash()
        elif isinstance(tile, int):
            tile = str(board[y, x])

        screen.addstr(
            y + oy,
            x + ox,
            tile,
            color(overlaid_board[y, x])
        )

    screen.refresh()

    if wait > 0 and Sleep:
        time.sleep(wait)

color_map = {
    UNKNOWN  : (8, 0),
    RANGE    : (2, 0),
    REACHABLE: (3, 0),
    NEAREST  : (5, curses.A_STANDOUT),
    CHOSEN   : (1, curses.A_UNDERLINE),
    EMPTY    : (7, 0),
    WALL     : (3, 0),
    ELF      : (4, curses.A_BOLD),
    GOBLIN   : (1, curses.A_BOLD),
    'e'      : (2, curses.A_BOLD),
    'g'      : (2, curses.A_BOLD),
    HIT      : (5, curses.A_BOLD | curses.A_BLINK)
}

def color(k):
    if isinstance(k, int):
        return curses.color_pair(7) | curses.A_BOLD

    if k not in color_map:
        return curses.color_pair(8)

    pair, attr = color_map[k]

    return curses.color_pair(pair) | attr

def print_battle_summary(screen, initial_board, final_board,
        all_units, total_rounds, total_hit_points, elf_attack_power):

    print_info(screen, 'Battle Summary:', wait = 1)

    print_info(screen, 'Initial Board:')
    draw_board(initial_board, wait = 3, move_to_top = False)

    print_info(screen, 'Final Board:')
    draw_board(final_board, wait = 3, move_to_top = False)

    info = []
    info.append('Elf attack power: {}'.format(elf_attack_power))
    info.append('Remaining units:')

    for unit in sorted(all_units, key = lambda unit: (unit.y, unit.x)):
        if not unit.is_dead:
            info.append('{}({} hit points)'.format(unit, unit.hit_points))

    info.append('Total hit points: {}'.format(total_hit_points))
    info.append('Number of rounds completed: {}'.format(total_rounds))
    info.append('Answer: {}'.format(total_rounds * total_hit_points))

    print_info(screen, *info, wait = 5)

def print_info(screen, *info, wait = 0):
    screen.clear()
    screen.move(0, 0)

    for text in info:
        screen.addstr('\n{}\n'.format(text))

    screen.refresh()
    time.sleep(wait)

curses.wrapper(main)
