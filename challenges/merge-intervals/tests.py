SAMPLE = [
    {"args": [[[1, 3], [2, 6], [8, 10], [15, 18]]]},
    {"args": [[[1, 4], [4, 5]]]},
    {"args": [[[4, 7], [1, 4]]]},
]


def _random(rng, n, span, max_len):
    out = []
    for _ in range(n):
        a = rng.randint(0, span)
        out.append([a, a + rng.randint(0, max_len)])
    return out


def hidden(rng):
    cases = [
        {"name": "single interval", "args": [[[1, 4]]]},
        {"name": "zero-length", "args": [[[0, 0]]]},
        {"name": "zero-length touching", "args": [[[1, 1], [1, 1], [1, 2]]]},
        {"name": "fully contained", "args": [[[1, 10], [2, 3], [4, 5]]]},
        {"name": "contained but sorted after", "args": [[[2, 3], [1, 10]]]},
        {"name": "no overlap", "args": [[[1, 2], [3, 4], [5, 6]]]},
        {"name": "unsorted input", "args": [[[8, 10], [1, 3], [15, 18], [2, 6]]]},
        {"name": "all identical", "args": [[[5, 7]] * 6]},
        {"name": "chain merge", "args": [[[1, 2], [2, 3], [3, 4], [4, 5]]]},
        {"name": "gap of one", "args": [[[1, 2], [3, 4]]]},
        {"name": "reverse sorted", "args": [[[9, 10], [7, 8], [5, 6], [3, 4], [1, 2]]]},
        {"name": "big values", "args": [[[0, 1_000_000_000], [999_999_999, 1_000_000_000]]]},
        {"name": "later interval extends end", "args": [[[1, 4], [2, 3], [3, 8]]]},
        {"name": "same start different end", "args": [[[1, 4], [1, 5], [1, 2]]]},
    ]
    for _ in range(20):
        cases.append({"args": [_random(rng, rng.randint(1, 12), 30, 6)]})
    for _ in range(10):
        cases.append({"args": [_random(rng, rng.randint(100, 1000), 10_000, 50)]})
    cases.append({"name": "large, mostly disjoint", "args": [_random(rng, 100_000, 10**9, 100)]})
    cases.append({"name": "large, heavy overlap", "args": [_random(rng, 100_000, 10**6, 1000)]})
    cases.append({"name": "large, one big merge", "args": [_random(rng, 100_000, 1000, 10**6)]})
    return cases
