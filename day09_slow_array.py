#! /usr/bin/env python3

def highest_score(number_of_players, last_marble):
    score       = [ 0 for _ in range(number_of_players) ]
    circle      = [ 0 ]
    next_number = 0
    current     = 0
    turn        = 0

    #print_turn(turn - 1, circle, current)
    while next_number != last_marble:
        next_number += 1

        if next_number % 23 != 0:
            current = (current + 1) % len(circle) + 1

            circle.insert(current, next_number)
        else:
            score[turn] += next_number

            current = (current - 7) % len(circle)

            removed = circle.pop(current)
            score[turn] += removed

            current = current % len(circle)

        #print_turn(turn, circle, current)
        turn = (turn + 1) % number_of_players

    return max(score)

def print_turn(turn, circle, current):
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
