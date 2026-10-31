SAMPLE = [
    {"args": [[1, 2, 3, 4, 5]]},
    {"args": [[1, 2]]},
    {"args": [[]]},
]


def hidden(rng):
    cases = [
        {"name": "single node", "args": [[7]]},
        {"name": "two equal values", "args": [[3, 3]]},
        {"name": "negative values", "args": [[-5000, -1, 0, 1, 5000]]},
        {"name": "all duplicates", "args": [[4] * 10]},
        {"name": "palindrome", "args": [[1, 2, 3, 2, 1]]},
        {"name": "already descending", "args": [[5, 4, 3, 2, 1]]},
        {"name": "three nodes", "args": [[1, 2, 3]]},
    ]
    for _ in range(20):
        cases.append({"args": [[rng.randint(-5000, 5000) for _ in range(rng.randint(0, 12))]]})
    for _ in range(10):
        cases.append({"args": [[rng.randint(-5000, 5000) for _ in range(rng.randint(100, 1000))]]})
    for _ in range(3):
        cases.append({"name": "maximum length", "args": [[rng.randint(-5000, 5000) for _ in range(5000)]]})
    return cases
