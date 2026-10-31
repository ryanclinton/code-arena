## Approach: Dummy head and two pointers

Start from a **dummy** node so there's no special case for choosing the first node, and keep a
`tail` pointer to the end of the merged list.

While both lists have nodes, attach the smaller head to `tail` and advance that list. When one list
runs out, the other one is already sorted, so attach the whole remainder in one step.
The answer is `dummy.next`.

Using `<=` when the values are equal takes from `list1` first, which keeps the merge stable.

**Complexity**
- Time: `O(n + m)`
- Space: `O(1)`, since the existing nodes are relinked rather than copied
