## Approach: Breadth-first search, one level at a time

A queue visits nodes in level order. The trick for grouping by level is to note the queue's size
at the start of each round: exactly that many nodes belong to the current level. Pop that many,
record their values, and push their children, which form the next level.

The Python reference builds each level as a list directly from the previous one, which is the same idea.

**Complexity**
- Time: `O(n)`
- Space: `O(w)` for the queue, where `w` is the tree's maximum width (up to `n/2`)
