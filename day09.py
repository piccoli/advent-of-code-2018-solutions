#! /usr/bin/env python3
from collections import deque

def highest_score(number_of_players, last_marble):
    score = [ 0 for _ in range(number_of_players) ]
    circle = deque([ 0 ])

    next_number = 0
    turn        = 0

    while next_number != last_marble:
        next_number += 1

        if next_number % 23 != 0:
            circle.rotate(-1)
            circle.append(next_number)
        else:
            score[turn] += next_number

            circle.rotate(7)

            score[turn] += circle.pop()

            circle.rotate(-1)

        turn = (turn + 1) % number_of_players

    return max(score)

record = input().strip().split()

number_of_players = int(record[0])
last_marble       = int(record[6])

print(highest_score(number_of_players, last_marble      ))
print(highest_score(number_of_players, last_marble * 100))
