#! /usr/bin/env python3
import sys
from functools import partial

verbose = len(sys.argv) > 1 and sys.argv[1] == '--verbose'
log = partial(print, flush = True, file = sys.stderr) if verbose\
    else (lambda *a, **k: None)

def cook(stop_criteria):
    scoreboard = [ 3, 7 ]
    current_recipes = 0, 1

    while True:
        print_scoreboard(scoreboard, current_recipes)

        score = (
            scoreboard[current_recipes[0]],
            scoreboard[current_recipes[1]]
        )

        score_sum = sum(score)

        if score_sum < 10:
            scoreboard.append(score_sum)
        else:
            scoreboard.append(score_sum // 10)

            if stop_criteria(scoreboard):
                print_scoreboard(scoreboard, current_recipes)
                return scoreboard

            scoreboard.append(score_sum %  10)

        if stop_criteria(scoreboard):
            print_scoreboard(scoreboard, current_recipes)
            return scoreboard

        current_recipes = (
            (1 + score[0] + current_recipes[0]) % len(scoreboard),
            (1 + score[1] + current_recipes[1]) % len(scoreboard)
        )

def part1_criteria(scoreboard):
    return len(scoreboard) == number_of_recipes + 10

def part2_criteria(scoreboard):
    return scoreboard[-len(target_scores):] == target_scores

def print_scoreboard(scoreboard, current_recipes):
    if not verbose:
        return

    log(''.join(
        [
                 '({})'.format(score) if i == current_recipes[0]\
            else '[{}]'.format(score) if i == current_recipes[1]\
            else ' {} '.format(score)

            for i, score in enumerate(scoreboard)
        ]
    ))

target_scores     = list(map(int, input().strip()))
number_of_recipes = int(''.join(map(str, target_scores)))

scoreboard = cook(part1_criteria)
print(''.join(map(str, scoreboard[number_of_recipes:number_of_recipes + 10])))

scoreboard = cook(part2_criteria)
print(len(scoreboard) - len(target_scores))
