SAMPLE = [
    {"args": [[1, 3], [2]]},
    {"args": [[1, 2], [3, 4]]},
]


def _sorted(rng, n, lo=-10**6, hi=10**6):
    return sorted(rng.randint(lo, hi) for _ in range(n))


def hidden(rng):
    cases = [
        {"name": "first empty", "args": [[], [1]]},
        {"name": "second empty", "args": [[2], []]},
        {"name": "first empty, even", "args": [[], [2, 3]]},
        {"name": "both single", "args": [[1], [2]]},
        {"name": "all equal", "args": [[1, 1, 1], [1, 1, 1]]},
        {"name": "disjoint, first smaller", "args": [[1, 2, 3], [4, 5, 6]]},
        {"name": "disjoint, second smaller", "args": [[4, 5, 6], [1, 2, 3]]},
        {"name": "interleaved", "args": [[1, 3, 5, 7], [2, 4, 6, 8]]},
        {"name": "negative numbers", "args": [[-5, -3, -1], [-4, -2]]},
        {"name": "very unequal sizes", "args": [[100], list(range(1, 20))]},
        {"name": "extreme values", "args": [[-10**6, 10**6], [-10**6, 10**6]]},
        {"name": "half value median", "args": [[1, 2], [-1, 3]]},
        {"name": "zeros", "args": [[0, 0], [0, 0]]},
        {"name": "duplicates across", "args": [[1, 2, 2], [2, 2, 3]]},
    ]
    for _ in range(25):
        m, n = rng.randint(0, 10), rng.randint(0, 10)
        if m + n == 0:
            m = 1
        cases.append({"args": [_sorted(rng, m, -20, 20), _sorted(rng, n, -20, 20)]})
    for _ in range(10):
        cases.append({"args": [_sorted(rng, rng.randint(0, 2000)), _sorted(rng, rng.randint(1, 2000))]})
    for m, n in ((100_000, 100_000), (100_000, 1), (0, 100_000), (99_999, 100_000)):
        cases.append({"name": f"large m={m}, n={n}", "args": [_sorted(rng, m), _sorted(rng, n)]})
    return cases
