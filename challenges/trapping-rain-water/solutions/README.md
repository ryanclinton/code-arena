## Approach: Two Pointers

The water above bar `i` is `min(maxLeft(i), maxRight(i)) - height[i]`. Computing both maxima
with prefix/suffix arrays is a fine `O(n)`-space solution; two pointers remove the arrays.

Move inward from both ends. If `height[left] < height[right]`, the right side already has a
wall at least as tall as anything on the left, so the water at `left` is limited only by
`leftMax` — settle it and advance. Otherwise do the mirror image on the right.

**Complexity**
- Time: `O(n)`
- Space: `O(1)`

A monotonic stack (fill water layer by layer as you find right walls) is another `O(n)` approach.
