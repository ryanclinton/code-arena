"""Answer comparison strategies, selected by ``compare`` in problem.json."""

from __future__ import annotations

import json

FLOAT_TOL = 1e-5


def _equal(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if isinstance(a, int) and isinstance(b, int):
            return a == b
        return abs(a - b) <= FLOAT_TOL * max(1.0, abs(b))
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_equal(x, y) for x, y in zip(a, b))
    return a == b


def _sort_key(v):
    return json.dumps(v, sort_keys=True)


def _sorted(v):
    return sorted(v, key=_sort_key) if isinstance(v, list) else v


def check(mode: str, args, expected, actual, validator=None) -> tuple[bool, str]:
    """Returns (passed, message)."""
    if mode == "validator":
        if validator is None:
            raise RuntimeError("compare is 'validator' but the challenge has no validator.py")
        res = validator(args, expected, actual)
        if isinstance(res, tuple):
            return bool(res[0]), res[1] if len(res) > 1 else ""
        return bool(res), ""
    if mode == "unordered":
        return _equal(_sorted(actual), _sorted(expected)), ""
    if mode == "unordered_nested":
        def norm(v):
            if not isinstance(v, list):
                return v
            return _sorted([_sorted(x) for x in v])
        return _equal(norm(actual), norm(expected)), ""
    return _equal(actual, expected), ""
