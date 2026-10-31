## Approach: Flood fill

Treat the grid as a graph: each land cell is a node, connected to the land cells above, below,
left and right of it. The answer is the number of **connected components**.

Scan every cell. When you find unvisited land, that's a new island: count it, then flood fill
(BFS or DFS) from it and mark every reachable land cell as visited. The reference "sinks" visited
cells by overwriting them with `'0'`, so no separate visited array is needed.

Mark a cell as visited **when it's added to the queue**, not when it's removed. Otherwise the same cell
can be queued many times.

**Recursive DFS works too**, but a winding island in a 300×300 grid can be 45,000 cells deep. The
judge gives you a large stack, but BFS or an explicit stack avoids the question.

**Union-Find** is another option: union each land cell with its land neighbours and count the roots.

**Complexity**
- Time: `O(m·n)`
- Space: `O(min(m, n))` for the BFS queue, `O(m·n)` worst case for DFS
