## Approach: One-pass Hash Map

For each number `x`, the partner we need is `target - x`. Walk the array once while
remembering every value we've seen and its index. If the partner is already in the map,
we've found the pair.

Checking before inserting guarantees we never pair an element with itself.

**Complexity**
- Time: `O(n)` — one pass, `O(1)` average hash lookups.
- Space: `O(n)` for the map.

The brute-force `O(n²)` double loop works on small inputs but times out on the large hidden tests.
