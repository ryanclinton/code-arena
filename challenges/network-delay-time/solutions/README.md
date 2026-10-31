## Approach: Dijkstra's algorithm

The time for the signal to reach a node is its **shortest-path distance** from `k`. Everyone has
the signal once the farthest node has it, so the answer is the largest shortest-path distance,
or `-1` if some node can't be reached.

All weights are non-negative, so Dijkstra applies:

1. Push `(0, k)` onto a min-heap.
2. Pop the closest unsettled node. Its distance is now final.
3. Push each neighbour with `distance + weight`.

A node can be pushed several times. Skipping it when it's popped a second time (`if node in dist`)
is simpler than a decrease-key operation and just as fast in practice.

**Why not BFS?** BFS finds the fewest *edges*, not the least total *time*. The "indirect path is
shorter" test catches this.

**Complexity**
- Time: `O(E log E)`
- Space: `O(V + E)`
