from judge.testgen import random_tree, skewed_tree, zigzag_tree

SAMPLE = [
    {"args": [[3, 9, 20, None, None, 15, 7]]},
    {"args": [[1]]},
    {"args": [[]]},
]


def hidden(rng):
    cases = [
        {"name": "only a left child", "args": [[1, 2]]},
        {"name": "only a right child", "args": [[1, None, 2]]},
        {"name": "gaps in a level", "args": [[1, 2, 3, 4, None, None, 5]]},
        {"name": "left chain", "args": [skewed_tree([1, 2, 3, 4], "left")]},
        {"name": "zigzag", "args": [zigzag_tree([1, 2, 3, 4, 5, 6])]},
        {"name": "perfect tree, depth 4", "args": [list(range(1, 16))]},
        {"name": "negative and duplicate values", "args": [[-1, -1, 0, 0, None, 1000, -1000]]},
        {"name": "deep level with one node", "args": [[1, 2, 3, None, 4, None, None, 5]]},
    ]
    for _ in range(20):
        cases.append({"args": [random_tree(rng, rng.randint(0, 15), -1000, 1000)]})
    for _ in range(8):
        cases.append({"args": [random_tree(rng, rng.randint(100, 2000), -1000, 1000)]})
    cases.append({"name": "large random tree", "args": [random_tree(rng, 10_000, -1000, 1000)]})
    cases.append({"name": "large complete tree", "args": [[rng.randint(-1000, 1000) for _ in range(10_000)]]})
    cases.append({"name": "deep chain", "args": [skewed_tree([rng.randint(-1000, 1000) for _ in range(5000)], "right")]})
    return cases
