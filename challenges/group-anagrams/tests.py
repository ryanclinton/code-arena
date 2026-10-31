import string

SAMPLE = [
    {"args": [["eat", "tea", "tan", "ate", "nat", "bat"]]},
    {"args": [[""]]},
    {"args": [["a"]]},
]


def _words(rng, n, max_len, alphabet):
    return ["".join(rng.choice(alphabet) for _ in range(rng.randint(0, max_len))) for _ in range(n)]


def _anagram_heavy(rng, groups, per_group, length):
    out = []
    for _ in range(groups):
        base = [rng.choice(string.ascii_lowercase) for _ in range(length)]
        for _ in range(per_group):
            rng.shuffle(base)
            out.append("".join(base))
    rng.shuffle(out)
    return out


def hidden(rng):
    cases = [
        {"name": "two empty strings", "args": [["", ""]]},
        {"name": "empty and non-empty", "args": [["", "b", ""]]},
        {"name": "no anagrams", "args": [["abc", "def", "ghi"]]},
        {"name": "all anagrams", "args": [["abc", "bca", "cab", "acb", "bac", "cba"]]},
        {"name": "duplicates", "args": [["aa", "aa", "aa"]]},
        {"name": "same letters, different counts", "args": [["aab", "abb", "bab", "aba"]]},
        {"name": "different lengths", "args": [["a", "aa", "aaa"]]},
        {"name": "single letters", "args": [["a", "b", "a", "c", "b"]]},
        {"name": "sorted-key collision trap", "args": [["ab", "c", "abc", "bc", "a"]]},
        {"name": "long words", "args": [["z" * 100, "y" * 100, "z" * 100]]},
    ]
    for _ in range(15):
        cases.append({"args": [_words(rng, rng.randint(1, 15), 4, "abc")]})
    for _ in range(10):
        cases.append({"args": [_anagram_heavy(rng, rng.randint(1, 20), rng.randint(1, 8), rng.randint(1, 8))]})
    cases.append({"name": "large, many groups", "args": [_words(rng, 10_000, 6, "abcde")]})
    cases.append({"name": "large, long words", "args": [_anagram_heavy(rng, 500, 20, 100)]})
    cases.append({"name": "large, all unique", "args": [list({w: None for w in _words(rng, 12_000, 12, string.ascii_lowercase)})[:10_000]]})
    return cases
