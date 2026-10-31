## Approach: Sliding Window with Last-Seen Index

Keep a window `[start, i]` that never contains a duplicate. For each character, remember the
last index where it appeared.

When `s[i]` was last seen *inside* the window, move `start` to just past that occurrence —
skipping straight there instead of shrinking one step at a time. The `>= start` check (or
`max` in the Java version) prevents `start` from moving backwards, which is the trap in
inputs like `"abba"`.

**Complexity**
- Time: `O(n)` — each character is visited once.
- Space: `O(min(n, alphabet))`.
