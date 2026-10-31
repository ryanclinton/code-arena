## Approach: Two pointers, one pass

Move a `fast` pointer `n` nodes ahead, then move `fast` and `slow` together until `fast` reaches
the last node. The gap between them stays `n`, so `slow` stops just **before** the node to remove,
and `slow.next = slow.next.next` unlinks it.

Both pointers start at a **dummy** node placed before `head`. That handles removing the head itself
(`n == size`) with no special case: `slow` stays on the dummy and the answer is `dummy.next`.

**Complexity**
- Time: `O(sz)`, one pass
- Space: `O(1)`
