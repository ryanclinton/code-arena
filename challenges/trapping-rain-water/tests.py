SAMPLE = [
    {"args": [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]]},
    {"args": [[4, 2, 0, 3, 2, 5]]},
]


def hidden(rng):
    cases = [
        {"name": "empty", "args": [[]]},
        {"name": "single bar", "args": [[5]]},
        {"name": "two bars", "args": [[5, 5]]},
        {"name": "all zeros", "args": [[0, 0, 0, 0]]},
        {"name": "increasing", "args": [[1, 2, 3, 4, 5]]},
        {"name": "decreasing", "args": [[5, 4, 3, 2, 1]]},
        {"name": "simple valley", "args": [[3, 0, 3]]},
        {"name": "uneven walls", "args": [[2, 0, 5]]},
        {"name": "peak in middle", "args": [[0, 2, 4, 2, 0]]},
        {"name": "plateau", "args": [[3, 3, 3, 3]]},
        {"name": "nested valleys", "args": [[5, 1, 3, 1, 5]]},
        {"name": "flat bottom", "args": [[4, 0, 0, 0, 4]]},
        {"name": "w shape", "args": [[5, 0, 5, 0, 5]]},
        {"name": "tall edges", "args": [[10000, 0, 0, 0, 0, 10000]]},
        {"name": "staircase into wall", "args": [[1, 0, 2, 0, 3, 0, 4]]},
    ]
    for _ in range(25):
        cases.append({"args": [[rng.randint(0, 10) for _ in range(rng.randint(0, 25))]]})
    for _ in range(8):
        cases.append({"args": [[rng.randint(0, 10_000) for _ in range(rng.randint(100, 5000))]]})
    n = 100_000
    cases.append({"name": "large random", "args": [[rng.randint(0, 10_000) for _ in range(n)]]})
    cases.append({"name": "large bowl", "args": [[10_000] + [0] * (n - 2) + [10_000]]})
    cases.append({"name": "large mountain", "args": [[min(i, n - i) // 10 for i in range(n)]]})
    cases.append({"name": "large zig-zag", "args": [[10_000 if i % 2 == 0 else 0 for i in range(n)]]})
    return cases
