import string

SAMPLE = [
    {"args": ["abcabcbb"]},
    {"args": ["bbbbb"]},
    {"args": ["pwwkew"]},
]

PRINTABLE = string.ascii_letters + string.digits + string.punctuation + " "


def hidden(rng):
    cases = [
        {"name": "empty string", "args": [""]},
        {"name": "single space", "args": [" "]},
        {"name": "single char", "args": ["a"]},
        {"name": "two same", "args": ["aa"]},
        {"name": "two different", "args": ["au"]},
        {"name": "window must jump back", "args": ["abba"]},
        {"name": "restart in middle", "args": ["dvdf"]},
        {"name": "all unique", "args": ["abcdefghijklmnopqrstuvwxyz"]},
        {"name": "answer at end", "args": ["aab"]},
        {"name": "spaces and symbols", "args": ["a b!c a"]},
        {"name": "digits", "args": ["0123401234567"]},
        {"name": "case sensitive", "args": ["aAbBcCaA"]},
        {"name": "palindrome", "args": ["tmmzuxt"]},
        {"name": "all printable", "args": [PRINTABLE]},
    ]
    for _ in range(15):
        alpha = rng.choice(["ab", "abc", "abcdef", string.ascii_lowercase])
        cases.append({"args": ["".join(rng.choice(alpha) for _ in range(rng.randint(1, 30)))]})
    for _ in range(10):
        cases.append({"args": ["".join(rng.choice(PRINTABLE) for _ in range(rng.randint(50, 500)))]})
    cases.append({"name": "large repeated char", "args": ["z" * 50_000]})
    cases.append({"name": "large cycling alphabet", "args": [PRINTABLE * (50_000 // len(PRINTABLE))]})
    for alpha in (string.ascii_lowercase, PRINTABLE, "ab"):
        cases.append({"name": "large random", "args": ["".join(rng.choice(alpha) for _ in range(50_000))]})
    return cases
