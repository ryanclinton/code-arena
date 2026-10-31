"""Helpers for writing challenge tests.py files that need trees or graphs.

    from judge.testgen import random_tree, random_bst, skewed_tree

Trees are returned in the judge's JSON form: LeetCode-style level order with
None for missing children, e.g. [1, None, 2].
"""

from __future__ import annotations


class _Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val, self.left, self.right = val, None, None


def level_order(root: _Node | None) -> list:
    out, level = [], [root]
    while level:
        nxt = []
        for node in level:
            if node is None:
                out.append(None)
            else:
                out.append(node.val)
                nxt += [node.left, node.right]
        level = nxt
    while out and out[-1] is None:
        out.pop()
    return out


def random_shape(rng, values: list) -> _Node | None:
    """A random tree shape holding `values` in BFS order of attachment."""
    if not values:
        return None
    root = _Node(values[0])
    open_slots = [(root, "left"), (root, "right")]
    for v in values[1:]:
        parent, side = open_slots.pop(rng.randrange(len(open_slots)))
        child = _Node(v)
        setattr(parent, side, child)
        open_slots += [(child, "left"), (child, "right")]
    return root


def random_tree(rng, n: int, lo: int = -100, hi: int = 100) -> list:
    return level_order(random_shape(rng, [rng.randint(lo, hi) for _ in range(n)]))


def complete_tree(values: list) -> list:
    return list(values)


def skewed_tree(values: list, side: str = "right") -> list:
    """A chain going always left or always right (maximum depth)."""
    if not values:
        return []
    root = cur = _Node(values[0])
    for v in values[1:]:
        child = _Node(v)
        setattr(cur, side, child)
        cur = child
    return level_order(root)


def zigzag_tree(values: list) -> list:
    """A chain that alternates left and right children."""
    if not values:
        return []
    root = cur = _Node(values[0])
    for i, v in enumerate(values[1:]):
        child = _Node(v)
        setattr(cur, "left" if i % 2 == 0 else "right", child)
        cur = child
    return level_order(root)


def bst_root(rng, sorted_values: list) -> _Node | None:
    """A random-shaped binary search tree over sorted, distinct values (iterative)."""
    if not sorted_values:
        return None
    root_holder = _Node(None)
    stack = [(0, len(sorted_values) - 1, root_holder, "left")]
    while stack:
        lo, hi, parent, side = stack.pop()
        if lo > hi:
            continue
        mid = rng.randint(lo, hi) if hi - lo < 4 else rng.randint(lo + (hi - lo) // 4, hi - (hi - lo) // 4)
        node = _Node(sorted_values[mid])
        setattr(parent, side, node)
        stack += [(lo, mid - 1, node, "left"), (mid + 1, hi, node, "right")]
    return root_holder.left


def random_bst(rng, n: int, lo: int = -10_000, hi: int = 10_000) -> list:
    return level_order(bst_root(rng, sorted(rng.sample(range(lo, hi + 1), n))))
