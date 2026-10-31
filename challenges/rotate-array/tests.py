SAMPLE = [
    {"args": [[1, 2, 3, 4, 5, 6, 7], 3]},
    {"args": [[-1, -100, 3, 99], 2]},
]

INT_MIN, INT_MAX = -2**31, 2**31 - 1


def hidden(rng):
    cases = [
        {"name": "single element", "args": [[1], 0]},
        {"name": "single element, big k", "args": [[42], 1_000_000_000]},
        {"name": "k = 0", "args": [[1, 2, 3], 0]},
        {"name": "k = n", "args": [[1, 2, 3], 3]},
        {"name": "k > n", "args": [[1, 2, 3], 4]},
        {"name": "k multiple of n", "args": [[1, 2, 3, 4], 12]},
        {"name": "k = n - 1", "args": [[1, 2, 3, 4, 5], 4]},
        {"name": "two elements", "args": [[1, 2], 1]},
        {"name": "duplicates", "args": [[7, 7, 1, 7], 2]},
        {"name": "int extremes", "args": [[INT_MIN, 0, INT_MAX], 1]},
        {"name": "even length, half rotation", "args": [[1, 2, 3, 4, 5, 6], 3]},
        {"name": "gcd(n, k) > 1", "args": [[1, 2, 3, 4, 5, 6], 4]},
    ]
    for _ in range(25):
        n = rng.randint(1, 30)
        cases.append({"args": [[rng.randint(-100, 100) for _ in range(n)], rng.randint(0, 3 * n)]})
    for _ in range(8):
        n = rng.randint(100, 5000)
        cases.append({"args": [[rng.randint(INT_MIN, INT_MAX) for _ in range(n)], rng.randint(0, 10**9)]})
    for n, k in ((100_000, 1), (100_000, 99_999), (100_000, 54_321), (99_991, 1_000_000_000)):
        cases.append({"name": f"large n={n}, k={k}", "args": [[rng.randint(INT_MIN, INT_MAX) for _ in range(n)], k]})
    return cases
