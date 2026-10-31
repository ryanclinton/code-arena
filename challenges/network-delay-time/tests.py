def _random(rng, n, m, max_w=100, connected_from=None):
    edges = {}
    if connected_from is not None:
        # A random spanning tree out of the source, so every node is reachable.
        order = [connected_from] + rng.sample([v for v in range(1, n + 1) if v != connected_from], n - 1)
        for i in range(1, n):
            edges[(order[rng.randrange(i)], order[i])] = rng.randint(0, max_w)
    m = min(m, n * (n - 1))
    while len(edges) < m:
        u, v = rng.sample(range(1, n + 1), 2)
        edges.setdefault((u, v), rng.randint(0, max_w))
    out = [[u, v, w] for (u, v), w in edges.items()]
    rng.shuffle(out)
    return out


SAMPLE = [
    {"args": [[[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2]},
    {"args": [[[1, 2, 1]], 2, 1]},
    {"args": [[[1, 2, 1]], 2, 2]},
]


def hidden(rng):
    cases = [
        {"name": "single node, no edges", "args": [[], 1, 1]},
        {"name": "two nodes, no edges", "args": [[], 2, 1]},
        {"name": "zero-weight edges", "args": [[[1, 2, 0], [2, 3, 0]], 3, 1]},
        {"name": "indirect path is shorter", "args": [[[1, 2, 10], [1, 3, 1], [3, 2, 1]], 3, 1]},
        {"name": "edge points the wrong way", "args": [[[2, 1, 5]], 2, 1]},
        {"name": "cycle back to the source", "args": [[[1, 2, 1], [2, 3, 1], [3, 1, 1]], 3, 2]},
        {"name": "one node unreachable", "args": [[[1, 2, 1], [2, 3, 1]], 4, 1]},
        {"name": "answer is the farthest, not the sum", "args": [[[1, 2, 5], [1, 3, 7], [1, 4, 3]], 4, 1]},
        {"name": "many paths to the same node", "args": [[[1, 2, 1], [1, 3, 4], [2, 3, 2], [3, 4, 1], [2, 4, 5]], 4, 1]},
        {"name": "greedy first edge is wrong", "args": [[[1, 2, 1], [2, 4, 100], [1, 3, 2], [3, 4, 2]], 4, 1]},
        {"name": "source is the last node", "args": [[[3, 1, 2], [3, 2, 4], [1, 2, 1]], 3, 3]},
    ]
    for _ in range(12):
        n = rng.randint(2, 10)
        k = rng.randint(1, n)
        cases.append({"args": [_random(rng, n, rng.randint(n - 1, 3 * n), connected_from=k), n, k]})
        cases.append({"args": [_random(rng, n, rng.randint(0, 2 * n)), n, k]})
    for _ in range(4):
        n = rng.randint(100, 2000)
        k = rng.randint(1, n)
        cases.append({"args": [_random(rng, n, rng.randint(n, 5 * n), connected_from=k), n, k]})
    n = 10_000
    cases.append({"name": "large, all reachable", "args": [_random(rng, n, 50_000, connected_from=1), n, 1]})
    cases.append({"name": "large, small weights", "args": [_random(rng, n, 50_000, max_w=3, connected_from=5000), n, 5000]})
    cases.append({"name": "large, sparse random", "args": [_random(rng, n, 20_000), n, 1]})
    chain = [[i, i + 1, 100] for i in range(1, n)]
    cases.append({"name": "long chain", "args": [chain, n, 1]})
    cases.append({"name": "long chain plus shortcuts", "args": [chain + [[1, i, 50 * i] for i in range(3, n + 1, 7)], n, 1]})
    return cases
