def _grid(rows):
    return [list(r) for r in rows]


def _random(rng, m, n, land):
    return [["1" if rng.random() < land else "0" for _ in range(n)] for _ in range(m)]


def _spiral(n):
    """One long, winding island: a square spiral of land."""
    g = [["0"] * n for _ in range(n)]
    top, left, bottom, right = 0, 0, n - 1, n - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            g[top][j] = "1"
        for i in range(top, bottom + 1):
            g[i][right] = "1"
        if top + 2 <= bottom:
            for j in range(left, right + 1):
                g[bottom][j] = "1"
        if left + 2 <= right and top + 2 <= bottom:
            for i in range(top + 2, bottom + 1):
                g[i][left] = "1"
        top, left, bottom, right = top + 2, left + 2, bottom - 2, right - 2
    return g


SAMPLE = [
    {"args": [_grid(["11110", "11010", "11000", "00000"])]},
    {"args": [_grid(["11000", "11000", "00100", "00011"])]},
]


def hidden(rng):
    cases = [
        {"name": "single land cell", "args": [[["1"]]]},
        {"name": "single water cell", "args": [[["0"]]]},
        {"name": "all water", "args": [[["0"] * 5 for _ in range(4)]]},
        {"name": "all land", "args": [[["1"] * 5 for _ in range(4)]]},
        {"name": "diagonal cells are separate", "args": [_grid(["101", "010", "101"])]},
        {"name": "checkerboard", "args": [_grid(["1010", "0101", "1010", "0101"])]},
        {"name": "one row", "args": [_grid(["1101011"])]},
        {"name": "one column", "args": [_grid(["1", "1", "0", "1", "0", "1"])]},
        {"name": "ring with a lake", "args": [_grid(["11111", "10001", "10101", "10001", "11111"])]},
        {"name": "U shape joins at the bottom", "args": [_grid(["101", "101", "111"])]},
        {"name": "comb connected along the top", "args": [_grid(["11111", "10101", "10101"])]},
        {"name": "land on every edge only", "args": [_grid(["01110", "10001", "10001", "01110"])]},
    ]
    for _ in range(20):
        cases.append({"args": [_random(rng, rng.randint(1, 8), rng.randint(1, 8), rng.choice([0.3, 0.5, 0.7]))]})
    for _ in range(6):
        cases.append({"args": [_random(rng, rng.randint(30, 100), rng.randint(30, 100), rng.choice([0.3, 0.5, 0.7]))]})
    cases.append({"name": "300x300 all land", "args": [[["1"] * 300 for _ in range(300)]]})
    cases.append({"name": "300x300 checkerboard", "args": [[["1" if (i + j) % 2 == 0 else "0" for j in range(300)] for i in range(300)]]})
    cases.append({"name": "300x300 random, sparse", "args": [_random(rng, 300, 300, 0.3)]})
    cases.append({"name": "300x300 random, dense", "args": [_random(rng, 300, 300, 0.6)]})
    cases.append({"name": "300x300 spiral (very long island)", "args": [_spiral(300)]})
    return cases
