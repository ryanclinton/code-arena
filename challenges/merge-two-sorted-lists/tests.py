SAMPLE = [
    {"args": [[1, 2, 4], [1, 3, 4]]},
    {"args": [[], []]},
    {"args": [[], [0]]},
]


def _sorted_list(rng, n, lo=-10_000, hi=10_000):
    return sorted(rng.randint(lo, hi) for _ in range(n))


def hidden(rng):
    cases = [
        {"name": "first empty", "args": [[], [1, 2, 3]]},
        {"name": "second empty", "args": [[1, 2, 3], []]},
        {"name": "single nodes", "args": [[2], [1]]},
        {"name": "all of list1 smaller", "args": [[1, 2, 3], [4, 5, 6]]},
        {"name": "all of list2 smaller", "args": [[4, 5, 6], [1, 2, 3]]},
        {"name": "interleaved", "args": [[1, 3, 5, 7], [2, 4, 6, 8]]},
        {"name": "identical lists", "args": [[1, 2, 3], [1, 2, 3]]},
        {"name": "all equal values", "args": [[5, 5, 5], [5, 5]]},
        {"name": "negatives", "args": [[-10_000, -5, 0], [-7, -6, 10_000]]},
        {"name": "very different lengths", "args": [[0], list(range(-50, 50))]},
        {"name": "one long tail", "args": [[1, 2], list(range(3, 40))]},
    ]
    for _ in range(20):
        cases.append({"args": [_sorted_list(rng, rng.randint(0, 10), -20, 20),
                               _sorted_list(rng, rng.randint(0, 10), -20, 20)]})
    for _ in range(8):
        cases.append({"args": [_sorted_list(rng, rng.randint(100, 1000)), _sorted_list(rng, rng.randint(100, 1000))]})
    cases.append({"name": "maximum length", "args": [_sorted_list(rng, 5000), _sorted_list(rng, 5000)]})
    cases.append({"name": "maximum length, few distinct values",
                  "args": [_sorted_list(rng, 5000, 0, 3), _sorted_list(rng, 5000, 0, 3)]})
    cases.append({"name": "maximum length, disjoint ranges",
                  "args": [_sorted_list(rng, 5000, 0, 100), _sorted_list(rng, 5000, -100, -1)]})
    return cases
