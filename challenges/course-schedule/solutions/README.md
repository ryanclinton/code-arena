## Approach: Topological sort (Kahn's algorithm)

Model courses as nodes and each prerequisite `[a, b]` as a directed edge `b → a`. All courses can be
finished exactly when this graph has **no cycle**.

Kahn's algorithm finds an order directly:

1. Count each course's unmet prerequisites (its *in-degree*).
2. Put every course with in-degree `0` in a queue: they can be taken now.
3. Take courses from the queue. Each one taken lowers its dependents' in-degrees; any that drop to `0`
   join the queue.

If every course gets taken, there's no cycle. Courses on (or behind) a cycle never reach in-degree `0`,
so the count comes up short.

**Alternative:** DFS with three colours (unvisited / in progress / done). Meeting an "in progress" node
means a cycle. On the 10,000-course chain, recursion goes 10,000 deep.

**Complexity**
- Time: `O(V + E)`
- Space: `O(V + E)` for the adjacency lists
