from judge.testgen import random_tree, skewed_tree, zigzag_tree

SAMPLE = [
    {"args": [[4, 2, 7, 1, 3, 6, 9]]},
    {"args": [[2, 1, 3]]},
    {"args": [[]]},
]


def hidden(rng):
    cases = [
        {"name": "single node", "args": [[1]]},
        {"name": "only a left child", "args": [[1, 2]]},
        {"name": "only a right child", "args": [[1, None, 2]]},
        {"name": "left chain", "args": [skewed_tree([1, 2, 3, 4, 5], "left")]},
        {"name": "right chain", "args": [skewed_tree([1, 2, 3, 4, 5], "right")]},
        {"name": "zigzag", "args": [zigzag_tree(list(range(1, 8)))]},
        {"name": "duplicate values", "args": [[1, 1, 1, 1, None, None, 1]]},
        {"name": "negative values", "args": [[-1, -2, -3, None, -4]]},
        {"name": "perfect tree, depth 4", "args": [list(range(1, 16))]},
        {"name": "symmetric tree", "args": [[1, 2, 2, 3, 4, 4, 3]]},
    ]
    for _ in range(20):
        cases.append({"args": [random_tree(rng, rng.randint(0, 15))]})
    for _ in range(8):
        cases.append({"args": [random_tree(rng, rng.randint(100, 2000))]})
    cases.append({"name": "large random tree", "args": [random_tree(rng, 10_000)]})
    cases.append({"name": "large complete tree", "args": [[rng.randint(-100, 100) for _ in range(10_000)]]})
    cases.append({"name": "deep left chain", "args": [skewed_tree([rng.randint(-100, 100) for _ in range(5000)], "left")]})
    cases.append({"name": "deep right chain", "args": [skewed_tree([rng.randint(-100, 100) for _ in range(5000)], "right")]})
    return cases
