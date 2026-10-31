## Approach: Iterative pointer reversal

Walk the list once, turning each `next` pointer around. Keep three references:

- `prev`: the head of the part already reversed (starts as `null`)
- `head`: the node being processed
- `next`: saved before overwriting `head.next`, so the rest of the list isn't lost

For each node: save `next`, point `head.next` at `prev`, then move `prev` and `head` one step forward.
When `head` becomes `null`, `prev` is the new head.

**Recursive version:** reverse the rest of the list first, then make the next node point back at
the current one (`head.next.next = head; head.next = null`). It uses `O(n)` stack space.

**Complexity**
- Time: `O(n)`
- Space: `O(1)` iterative, `O(n)` recursive
