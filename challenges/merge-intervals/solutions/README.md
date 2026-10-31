## Approach: Sort, then Sweep

After sorting by start, any interval that overlaps the current merged block must come
right after it. Sweep left to right:

- If the next interval starts at or before the end of the last merged interval, extend that
  end to `max(lastEnd, end)` — the `max` matters for contained intervals like `[1,10],[2,3]`.
- Otherwise it starts a new block.

**Complexity**
- Time: `O(n log n)` for the sort; the sweep is `O(n)`.
- Space: `O(n)` for the output (plus sort overhead).
