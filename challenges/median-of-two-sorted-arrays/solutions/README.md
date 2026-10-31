## Approach: Binary Search on the Partition

Split the combined array into a left half and right half of (almost) equal size. If we take
`i` elements from the shorter array `a`, we must take `j = half - i` from `b`. The split is
correct when every element on the left is `<=` every element on the right:

```
a[i-1] <= b[j]   and   b[j-1] <= a[i]
```

Binary-search `i` over `[0, m]`: if `a[i-1] > b[j]` we took too many from `a` (move left),
otherwise too few (move right). Missing neighbours at the edges count as `-∞` / `+∞`.

Once found, the median is `max(leftSide)` for an odd total, or the average of
`max(leftSide)` and `min(rightSide)` for an even total.

**Complexity**
- Time: `O(log(min(m, n)))`
- Space: `O(1)`

Merging the arrays (`O(m + n)`) is simpler and passes here, but misses the follow-up.
