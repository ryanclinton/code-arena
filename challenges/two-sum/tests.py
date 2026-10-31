SAMPLE = [
    {"args": [[2, 7, 11, 15], 9]},
    {"args": [[3, 2, 4], 6]},
    {"args": [[3, 3], 6]},
]


def _random_case(rng, n, lo, hi):
    nums = [rng.randint(lo, hi) for _ in range(n)]
    i, j = rng.sample(range(n), 2)
    return [nums, nums[i] + nums[j]]


def hidden(rng):
    cases = [
        {"name": "minimum length", "args": [[1, 2], 3]},
        {"name": "negative numbers", "args": [[-1, -2, -3, -4, -5], -8]},
        {"name": "zeros", "args": [[0, 4, 3, 0], 0]},
        {"name": "mixed signs", "args": [[-3, 4, 3, 90], 0]},
        {"name": "answer at the ends", "args": [[5, 1, 2, 3, 4, 10], 15]},
        {"name": "duplicate values", "args": [[1, 1, 1, 1, 2, 2], 4]},
        {"name": "same value cannot be reused", "args": [[3, 2, 4], 6]},
        {"name": "large values", "args": [[1_000_000_000, -1_000_000_000, 999_999_999, 1], 2_000_000_000 - 1]},
        {"name": "large negative target", "args": [[-1_000_000_000, 5, -1_000_000_000], -2_000_000_000]},
        {"name": "target is double an element", "args": [[4, 1, 8, 7], 8]},
    ]
    for _ in range(25):
        cases.append({"args": _random_case(rng, rng.randint(2, 20), -50, 50)})
    for _ in range(10):
        cases.append({"args": _random_case(rng, rng.randint(100, 2000), -10**9, 10**9)})
    # Large inputs where the only valid pair is the last two elements, punishing O(n^2).
    # Every other element is a multiple of 4 and the last two are 1 (mod 4), so no other
    # pair can reach a target that is 2 (mod 4).
    for n in (50_000, 100_000, 100_000):
        nums = [4 * v for v in rng.sample(range(-2 * 10**8, 2 * 10**8), n - 2)]
        nums += [4 * rng.randint(-10**8, 10**8) + 1, 4 * rng.randint(-10**8, 10**8) + 1]
        cases.append({"name": f"large n={n}, pair at end", "args": [nums, nums[-1] + nums[-2]]})
    return cases
