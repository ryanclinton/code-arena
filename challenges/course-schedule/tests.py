def _dag(rng, n, m):
    """Random acyclic prerequisites: edges only go 'forward' in a hidden random order."""
    order = list(range(n))
    rng.shuffle(order)
    pairs = set()
    m = min(m, n * (n - 1) // 2)
    while len(pairs) < m:
        i, j = sorted(rng.sample(range(n), 2))
        pairs.add((order[j], order[i]))  # take order[j] after order[i]
    return [list(p) for p in pairs], order


def _with_cycle(rng, n, m):
    """A DAG plus one edge that closes a cycle."""
    pairs, order = _dag(rng, n, m)
    existing = {tuple(p) for p in pairs}
    i, j = sorted(rng.sample(range(n), 2))
    back = (order[i], order[j])  # order[i] after order[j]: points backwards
    if back not in existing:
        pairs.append(list(back))
    # Make sure the backward edge actually closes a cycle by adding the forward edge too.
    if (order[j], order[i]) not in existing:
        pairs.append([order[j], order[i]])
    rng.shuffle(pairs)
    return pairs


SAMPLE = [
    {"args": [2, [[1, 0]]]},
    {"args": [2, [[1, 0], [0, 1]]]},
]


def hidden(rng):
    chain = [[i + 1, i] for i in range(9999)]
    cases = [
        {"name": "one course, no prerequisites", "args": [1, []]},
        {"name": "many courses, no prerequisites", "args": [5, []]},
        {"name": "self-loop", "args": [1, [[0, 0]]]},
        {"name": "self-loop among valid courses", "args": [3, [[1, 0], [2, 2]]]},
        {"name": "three-course cycle", "args": [3, [[0, 1], [1, 2], [2, 0]]]},
        {"name": "diamond (shared prerequisite)", "args": [4, [[1, 0], [2, 0], [3, 1], [3, 2]]]},
        {"name": "cycle in a separate component", "args": [6, [[1, 0], [2, 1], [4, 3], [5, 4], [3, 5]]]},
        {"name": "course with many prerequisites", "args": [5, [[4, 0], [4, 1], [4, 2], [4, 3]]]},
        {"name": "cycle reachable only from the end", "args": [5, [[1, 0], [2, 1], [3, 2], [4, 3], [3, 4]]]},
        {"name": "unused courses", "args": [10, [[1, 0]]]},
    ]
    for _ in range(12):
        n = rng.randint(2, 10)
        cases.append({"args": [n, _dag(rng, n, rng.randint(0, 15))[0]]})
        cases.append({"args": [n, _with_cycle(rng, n, rng.randint(0, 15))]})
    for _ in range(4):
        n = rng.randint(100, 2000)
        cases.append({"args": [n, _dag(rng, n, rng.randint(n, 5 * n))[0]]})
        cases.append({"args": [n, _with_cycle(rng, n, rng.randint(n, 5 * n))]})
    cases.append({"name": "long chain", "args": [10_000, chain]})
    cases.append({"name": "long chain closed into a cycle", "args": [10_000, chain + [[0, 9999]]]})
    cases.append({"name": "large DAG", "args": [10_000, _dag(rng, 10_000, 50_000)[0]]})
    cases.append({"name": "large graph with one cycle", "args": [10_000, _with_cycle(rng, 10_000, 49_998)]})
    return cases
