#! /usr/bin/env python3
from collections import deque

def highest_score(number_of_players, last_marble):
    score = [ 0 for _ in range(number_of_players) ]
    circle = deque([ 0 ])

    next_number = 0
    turn        = 0
    rotation    = 0

    print_turn(turn - 1, circle, rotation)
    while next_number != last_marble:
        next_number += 1

        if next_number % 23 != 0:
            circle.rotate(-1)
            circle.append(next_number)
            rotation = (rotation + 2) % len(circle)
        else:
            score[turn] += next_number

            circle.rotate(7)

            score[turn] += circle.pop()

            circle.rotate(-1)
            rotation = (rotation - 5) % len(circle)

        print_turn(turn, circle, rotation)
        turn = (turn + 1) % number_of_players

    return max(score)

def print_turn(turn, circle, rotation = 0):
    circle = deque(circle)
    circle.rotate(rotation)

    current = (len(circle) - 1 + rotation) % len(circle)

    print('\033[1;37m[{}]\033[0m {}'.format(
        '-' if turn == -1 else turn + 1,
        ' '.join(
                 '\033[1;37m(\033[0m\033[1;33m{}\033[1;37m)\033[0m'.format(num) if i == current\
            else '{}'.format(num)

            for i, num in enumerate(circle)
        )
    ))

record = input().strip().split()

number_of_players = int(record[0])
last_marble       = int(record[6])

print(highest_score(number_of_players, last_marble      ))
print(highest_score(number_of_players, last_marble * 100))
