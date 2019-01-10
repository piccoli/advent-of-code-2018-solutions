#! /usr/bin/env python3

class Node:
    def __init__(self, tree):
        self.children = []
        self.metadata = []

        number_of_children         = tree[0]
        number_of_metadata_entries = tree[1]

        tree[:] = tree[2:]

        self.children = [ Node(tree) for _ in range(number_of_children) ]
        self.metadata = list(tree[:number_of_metadata_entries])

        tree[:] = tree[number_of_metadata_entries:]

    def collect_metadata(self):
        return sum(c.collect_metadata() for c in self.children)\
             + sum(self.metadata)

    def value(self):
        if not self.children:
            return sum(self.metadata)

        total = 0

        for m in self.metadata:
            m -= 1

            if m < 0 or m >= len(self.children):
                continue

            total += self.children[m].value()

        return total

tree = list(map(int, input().strip().split()))

root = Node(tree)

print(root.collect_metadata())
print(root.value())
