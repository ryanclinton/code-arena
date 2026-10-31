SAMPLE = [
    {"args": [[1, 2, 3, 4, 5], 2]},
    {"args": [[1], 1]},
    {"args": [[1, 2], 1]},
]


def _case(rng, size, name=None, n=None):
    vals = [rng.randint(0, 100) for _ in range(size)]
    case = {"args": [vals, n if n is not None else rng.randint(1, size)]}
    if name:
        case["name"] = name
    return case


def hidden(rng):
    cases = [
        {"name": "remove the head of two", "args": [[1, 2], 2]},
        {"name": "remove the head", "args": [[1, 2, 3, 4, 5], 5]},
        {"name": "remove the tail", "args": [[1, 2, 3, 4, 5], 1]},
        {"name": "remove the middle", "args": [[1, 2, 3, 4, 5], 3]},
        {"name": "duplicate values", "args": [[7, 7, 7, 7], 2]},
        {"name": "zeros", "args": [[0, 0, 0], 3]},
        {"name": "three nodes, second", "args": [[10, 20, 30], 2]},
    ]
    for _ in range(20):
        cases.append(_case(rng, rng.randint(1, 12)))
    for _ in range(10):
        cases.append(_case(rng, rng.randint(100, 2000)))
    cases.append(_case(rng, 10_000, "maximum length, remove head", n=10_000))
    cases.append(_case(rng, 10_000, "maximum length, remove tail", n=1))
    cases.append(_case(rng, 10_000, "maximum length, remove middle", n=5_000))
    return cases
