#! /usr/bin/env python3

from collections import deque

def longest_paths(floorplan, root):
    distance = { root: 0 }

    q = deque([ (0, root) ])

    while len(distance) < len(floorplan):
        dist, node = q.popleft()
        dist += 1

        for adjacent in floorplan[node]:
            if adjacent not in distance or dist < distance[adjacent]:
                distance[adjacent] = dist
                q.append((dist, adjacent))

    return max(distance.values()),\
           sum(d >= 1000 for d in distance.values())

stack     = []
floorplan = {}

for token in input().strip():
    if token == '^':
        root = 0, 0
        floorplan[root] = set()
        stack.append(root)

    if token in 'NEWS':
        y, x = root

        child =  (y - 1, x    ) if token == 'N'\
            else (y    , x - 1) if token == 'W'\
            else (y    , x + 1) if token == 'E'\
            else (y + 1, x    )

        if child not in floorplan:
            floorplan[child] = set()

        floorplan[root].add(child)
        #floorplan[child].add(root)
        root = child

    elif token == '(': stack.append(root)
    elif token == '|': root = stack[-1]
    elif token == ')': stack.pop()
    elif token == '$': root = stack.pop()

longest, large_count = longest_paths(floorplan, root)

print(longest)
print(large_count)
