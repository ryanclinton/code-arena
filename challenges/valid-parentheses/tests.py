PAIRS = {"(": ")", "[": "]", "{": "}"}

SAMPLE = [
    {"args": ["()"]},
    {"args": ["()[]{}"]},
    {"args": ["(]"]},
    {"args": ["([)]"]},
]


def _valid(rng, pairs):
    """Random balanced string with the given number of bracket pairs."""
    out, stack = [], []
    opens_left = pairs
    while opens_left or stack:
        if opens_left and (not stack or rng.random() < 0.55):
            o = rng.choice("([{")
            out.append(o)
            stack.append(PAIRS[o])
            opens_left -= 1
        else:
            out.append(stack.pop())
    return "".join(out)


def _corrupt(rng, s):
    i = rng.randrange(len(s))
    return s[:i] + rng.choice([c for c in "()[]{}" if c != s[i]]) + s[i + 1:]


def hidden(rng):
    cases = [
        {"name": "empty string", "args": [""]},
        {"name": "single open", "args": ["("]},
        {"name": "single close", "args": [")"]},
        {"name": "closed before opened", "args": [")("]},
        {"name": "nested", "args": ["{[]}"]},
        {"name": "deep nesting", "args": ["([{}])"]},
        {"name": "only opens", "args": ["(((((("]},
        {"name": "only closes", "args": ["]]]]"]},
        {"name": "extra close at end", "args": ["()())"]},
        {"name": "extra open at end", "args": ["()()("]},
        {"name": "mismatched type", "args": ["{)"]},
        {"name": "interleaved", "args": ["[(])"]},
        {"name": "valid after invalid prefix", "args": ["]()"]},
        {"name": "long sequence", "args": ["()" * 10 + "[]" * 10 + "{}" * 10]},
        {"name": "odd length", "args": ["(()"]},
    ]
    for _ in range(15):
        cases.append({"args": [_valid(rng, rng.randint(1, 15))]})
    for _ in range(15):
        cases.append({"args": [_corrupt(rng, _valid(rng, rng.randint(1, 15)))]})
    cases.append({"name": "deep nesting 50k", "args": ["(" * 25_000 + "[" * 25_000 + "]" * 25_000 + ")" * 25_000]})
    cases.append({"name": "deep nesting, wrong last", "args": ["{" * 50_000 + "}" * 49_999 + ")"]})
    for _ in range(3):
        cases.append({"name": "large valid", "args": [_valid(rng, 50_000)]})
    for _ in range(3):
        cases.append({"name": "large invalid", "args": [_corrupt(rng, _valid(rng, 50_000))]})
    return cases
