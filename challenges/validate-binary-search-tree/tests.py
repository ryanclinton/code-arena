from judge.testgen import bst_root, level_order, random_bst, skewed_tree

INT_MIN, INT_MAX = -2**31, 2**31 - 1

SAMPLE = [
    {"args": [[2, 1, 3]]},
    {"args": [[5, 1, 4, None, None, 3, 6]]},
]


def _broken_bst(rng, n):
    """A valid BST with two values swapped, so it is no longer valid."""
    root = bst_root(rng, sorted(rng.sample(range(-10**6, 10**6), n)))
    nodes, stack = [], [root]
    while stack:
        node = stack.pop()
        if node:
            nodes.append(node)
            stack += [node.left, node.right]
    a, b = rng.sample(nodes, 2)
    a.val, b.val = b.val, a.val
    return level_order(root)


def hidden(rng):
    cases = [
        {"name": "single node", "args": [[1]]},
        {"name": "single node, INT_MIN", "args": [[INT_MIN]]},
        {"name": "single node, INT_MAX", "args": [[INT_MAX]]},
        {"name": "INT_MIN root, INT_MAX right child", "args": [[INT_MIN, None, INT_MAX]]},
        {"name": "INT_MAX root, INT_MIN left child", "args": [[INT_MAX, INT_MIN]]},
        {"name": "duplicate on the left", "args": [[2, 2]]},
        {"name": "duplicate on the right", "args": [[2, None, 2]]},
        {"name": "all equal", "args": [[2, 2, 2]]},
        {"name": "grandchild breaks the root's bound", "args": [[5, 4, 6, None, None, 3, 7]]},
        {"name": "left grandchild too large", "args": [[10, 5, 15, None, 11]]},
        {"name": "equal to an ancestor", "args": [[3, 1, 5, None, 3]]},
        {"name": "valid left chain", "args": [skewed_tree([5, 4, 3, 2, 1], "left")]},
        {"name": "valid right chain", "args": [skewed_tree([1, 2, 3, 4, 5], "right")]},
        {"name": "invalid chain", "args": [skewed_tree([1, 2, 3, 2], "right")]},
        {"name": "valid, every child correct", "args": [[8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15]]},
        {"name": "children fine, deep node wrong", "args": [[8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 9, 9, 11, 13, 15]]},
    ]
    for _ in range(12):
        cases.append({"args": [random_bst(rng, rng.randint(1, 15), -50, 50)]})
    for _ in range(12):
        cases.append({"args": [_broken_bst(rng, rng.randint(2, 15))]})
    for _ in range(5):
        cases.append({"args": [random_bst(rng, rng.randint(100, 2000), INT_MIN, INT_MAX)]})
        cases.append({"args": [_broken_bst(rng, rng.randint(100, 2000))]})
    cases.append({"name": "large valid BST", "args": [random_bst(rng, 10_000, INT_MIN, INT_MAX)]})
    cases.append({"name": "large BST with two values swapped", "args": [_broken_bst(rng, 10_000)]})
    cases.append({"name": "deep valid chain", "args": [skewed_tree(list(range(5000)), "right")]})
    cases.append({"name": "deep chain, last node wrong", "args": [skewed_tree(list(range(4999)) + [0], "right")]})
    return cases
