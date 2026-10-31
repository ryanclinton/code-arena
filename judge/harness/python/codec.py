"""Converts test values between JSON and Python objects for a judge type.

Linked lists travel as JSON arrays ([1,2,3]) and binary trees as LeetCode-style
level-order arrays ([1,null,2]); everything else is passed through unchanged.
Used by the harness and by the judge when it runs the reference solution.
"""

MAX_NODES = 1_000_000


def _inner(t):
    if t.endswith("[]"):
        return t[:-2]
    if t.startswith("list<"):
        return t[5:-1]
    return None


def decode(value, t, ns):
    """JSON value -> Python value. ns supplies the ListNode / TreeNode classes."""
    if "Node" not in t:
        return value
    inner = _inner(t)
    if inner is not None:
        return None if value is None else [decode(v, inner, ns) for v in value]
    if t == "ListNode":
        head = None
        for v in reversed(value or []):
            head = ns["ListNode"](v, head)
        return head
    if t == "TreeNode":
        return _build_tree(value or [], ns["TreeNode"])
    return value


def _build_tree(values, cls):
    if not values or values[0] is None:
        return None
    root = cls(values[0])
    level, i = [root], 1
    while level and i < len(values):
        nxt = []
        for node in level:
            for side in ("left", "right"):
                if i < len(values) and values[i] is not None:
                    child = cls(values[i])
                    setattr(node, side, child)
                    nxt.append(child)
                i += 1
        level = nxt
    return root


def encode(value, t):
    """Python value -> JSON value."""
    inner = _inner(t)
    if inner is not None and isinstance(value, (list, tuple, set, frozenset)):
        return [encode(v, inner) for v in value]
    if t == "ListNode":
        return _list_values(value)
    if t == "TreeNode":
        return _tree_values(value)
    if isinstance(value, (tuple, set, frozenset, list)):
        return [encode(v, "") for v in value]
    return value


def _list_values(node):
    out = []
    while node is not None:
        if len(out) >= MAX_NODES:
            raise ValueError("Returned linked list has a cycle (or more than 1,000,000 nodes)")
        out.append(node.val)
        node = node.next
    return out


def _tree_values(root):
    out, level, count = [], [root], 0
    while level:
        nxt = []
        for node in level:
            if node is None:
                out.append(None)
                continue
            count += 1
            if count > MAX_NODES:
                raise ValueError("Returned tree has a cycle (or more than 1,000,000 nodes)")
            out.append(node.val)
            nxt += [node.left, node.right]
        level = nxt
    while out and out[-1] is None:
        out.pop()
    return out
