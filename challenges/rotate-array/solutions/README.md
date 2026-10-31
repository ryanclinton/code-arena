## Approach: Triple Reverse

First reduce `k` with `k %= n` — rotating by `n` is a no-op, and `k` can be huge.

Rotating right by `k` moves the last `k` elements to the front. Reversing the whole array
puts them at the front but backwards; reversing each of the two parts fixes the order:

```
[1,2,3,4,5,6,7], k = 3
reverse all      -> [7,6,5,4,3,2,1]
reverse [0, k)   -> [5,6,7,4,3,2,1]
reverse [k, n)   -> [5,6,7,1,2,3,4]
```

**Complexity**
- Time: `O(n)`
- Space: `O(1)`

In Python, `nums[:] = nums[-k:] + nums[:-k]` is a concise `O(n)`-space alternative — note the
slice assignment `nums[:] =`; plain `nums = ...` only rebinds the local name.
