#! /usr/bin/env python3
import sys

import time, curses, random

Left, Right, Straight = range(3)

next_direction = Straight, Left, Right

wwidth  = 80
wheight = 25
wx      = 0
wy      = 0

def main(screen):
    global wwidth, wheight

    curses.init_color(curses.COLOR_CYAN  , 0   , 1000, 1000)
    curses.init_color(curses.COLOR_YELLOW, 1000, 1000, 0)
    curses.init_color(curses.COLOR_RED   , 1000, 0   , 0)

    curses.init_pair(1, curses.COLOR_CYAN  , curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED   , curses.COLOR_BLACK)

    curses.curs_set(False)

    diagram, cars = read_diagram()

    dwidth  = len(diagram[0])
    dheight = len(diagram)
    wwidth  = min(wwidth, dwidth)
    wheight = min(wheight, dheight)

    screen.resize(wheight + 2, wwidth + 2)
    screen.nodelay(True)
    screen.timeout(10)
    screen.clear()

    random.seed(12345)
    simulate(diagram, cars, screen)

def simulate(diagram, cars, screen, focus_on_new_car_after = 10):
    i = 0

    fy, fx = None if not cars else list(cars.keys())[0]

    while len(cars) > 1:
        for y, x in sorted(cars):
            pan_to_car(diagram, cars, screen, (fy, fx))

            if (y, x) not in cars:
                continue

            draw(diagram, cars, screen, (fy, fx))

            dy, dx, dr = cars[y, x]

            del cars[y, x]

            if (fy, fx) == (y, x):
                fy += dy
                fx += dx

            y += dy
            x += dx

            if (y, x) in cars:
                del cars[y, x]
                pan_to_car(diagram, cars, screen, (y, x))
                time.sleep(.5)
                draw(diagram, cars, screen, None, pause = True, X = (y, x))
                continue

            d = diagram[y][x]

            if d == '\\':
                dy, dx = dx, dy
            elif d == '/':
                dy, dx = -1 * dx, -1 * dy
            elif d == '+':
                dr = next_direction[dr]
                dy, dx = turn(dr, dy, dx)

            cars[y, x] = (dy, dx, dr)

        i += 1
        if i % focus_on_new_car_after == 0: 
            fy, fx = random.sample(cars.keys(), 1)[0]
            pan_to_car(diagram, cars, screen, (fy, fx))
            time.sleep(.5)

        draw(diagram, cars, screen, (fy, fx))

def read_diagram():
    global cars

    diagram = [ list(line[:-1]) for line in sys.stdin.readlines() ]

    cars = {}
    direction = {
        '^': (-1,  0),
        'v': ( 1,  0),
        '<': ( 0, -1),
        '>': ( 0,  1)
    }

    for y, row in enumerate(diagram):
        for x, obj in enumerate(row):
            if obj in direction.keys():
                row[x] = '-' if obj in '><' else '|'
                cars[y, x] = (*direction[obj], Right)

    return diagram, cars

def turn(dr, dy, dx):
    if dr == Left:
        if dy == 0: dy, dx = -dx, dy
        else:       dy, dx =  dx, dy
    elif dr == Right:
        if dx == 0: dy, dx = dx, -dy
        else:       dy, dx = dx,  dy

    return dy, dx

def pan_to_car(diagram, cars, screen, current_car):
    global wx, wy

    if not current_car:
        return

    y, x = current_car

    dwidth  = len(diagram[0])
    dheight = len(diagram)

    assert 0 <= y < dheight and 0 <= x < dwidth

    while    wx > x or wx + wwidth  <= x\
          or wy > y or wy + wheight <= y:

        if wx > x:            wx -= 1
        if wx + wwidth  <= x: wx += 1
        if wy > y:            wy -= 1
        if wy + wheight <= y: wy += 1

        draw(diagram, cars, screen, current_car)

def draw(diagram, cars, screen, current_car, pause = False, X = None):
    #pan_if_key_pressed(diagram, screen)

    screen.move(1, 1)
    screen.border()

    for y, row in enumerate(diagram[wy:wy + wheight]):
        screen.addstr(
            y + 1,
            1, ''.join(row[wx:wx + wwidth]),
            curses.color_pair(1)
        )

    for (y, x), (dy, dx, dr) in cars.items():
        x -= wx
        y -= wy
        if 0 <= x < wwidth and 0 <= y < wheight:
            color = curses.color_pair(2)
            if (y + wy, x + wx) == current_car:
                color |= curses.A_STANDOUT

            screen.addstr(
                y + 1,
                x + 1,
                '^< >v'[2 * dy + dx + 2],
                color
            )

    if X is not None:
        x = X[1] - wx
        y = X[0] - wy
        if 0 <= x < wwidth and 0 <= y < wheight:
            curses.flash()
            screen.addstr(
                y + 1,
                x + 1,
                'X',
                curses.color_pair(3) | curses.A_BLINK | curses.A_BOLD
            )

    screen.refresh()

    time.sleep(.01 if not pause else .5)

def pan_if_key_pressed(diagram, screen):
    global wx, wy

    dwidth  = len(diagram[0])
    dheight = len(diagram)

    key = screen.getch()

    if key == ord('q'):
        sys.exit(0)
    if key == curses.KEY_UP or key == ord('w'):
        wy = max(0, wy - 1)
    elif key == curses.KEY_DOWN or key == ord('s'):
        wy = min(dheight - wheight, wy + 1)
    elif key == curses.KEY_LEFT or key == ord('a'):
        wx = max(0, wx - 1)
    elif key == curses.KEY_RIGHT or key == ord('d'):
        wx = min(dwidth - wwidth, wx + 1)

curses.wrapper(main)

print('Remaining:')
for y, x in cars:
    print(x, y, sep = ',')
