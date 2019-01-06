#! /usr/bin/env python3

TargetScores    = list(map(int, input().strip()))
NumberOfRecipes = int(''.join(map(str, TargetScores)))

def print_scoreboard(scoreboard, current_recipes):
    print(''.join(
        [
                 '({})'.format(score) if i == current_recipes[0]\
            else '[{}]'.format(score) if i == current_recipes[1]\
            else ' {} '.format(score)

            for i, score in enumerate(scoreboard)
        ]
    ))

def cook(stop_criteria):
    scoreboard      = [ 3, 7 ]
    current_recipes = 0, 1

    while True:
        #print_scoreboard(scoreboard, current_recipes)

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
                return scoreboard

            scoreboard.append(score_sum %  10)

        if stop_criteria(scoreboard):
            return scoreboard

        current_recipes = (
            (1 + score[0] + current_recipes[0]) % len(scoreboard),
            (1 + score[1] + current_recipes[1]) % len(scoreboard)
        )

def part1_criteria(scoreboard):
    return len(scoreboard) == NumberOfRecipes + 10

def part2_criteria(scoreboard):
    return scoreboard[-len(TargetScores):] == TargetScores

scoreboard = cook(part1_criteria)
print(''.join(map(str, scoreboard[NumberOfRecipes:NumberOfRecipes + 10])))

scoreboard = cook(part2_criteria)
print(len(scoreboard) - len(TargetScores))
