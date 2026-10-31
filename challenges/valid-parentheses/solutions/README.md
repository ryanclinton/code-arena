## Approach: Stack

Brackets close in last-opened-first-closed order, which is exactly what a stack models.

- On an opening bracket, push it (or, as in the Java version, push the closer we now *expect*).
- On a closing bracket, the stack must be non-empty and its top must match; pop it.
- At the end the stack must be empty — otherwise some bracket was never closed.

**Complexity**
- Time: `O(n)`
- Space: `O(n)` in the worst case (all opening brackets).

Tip: an odd-length string can be rejected immediately.
