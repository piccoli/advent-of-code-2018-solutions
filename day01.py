#! /usr/bin/env python3
import sys

def first_duplicate_sum(numbers):
    i = 0
    seen = { 0 }
    freq = numbers[0]
    n = len(numbers)

    while not freq in seen:
        seen.add(freq)

        i = (i + 1) % n

        freq += numbers[i]

    return freq

numbers = list(map(int, sys.stdin.read().split()))

print(sum(numbers))
print(first_duplicate_sum(numbers))
