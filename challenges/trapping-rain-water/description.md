Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.

### Example 1

```
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
Explanation: The elevation map traps 6 units of rain water.

        #
    #~~~##~#
  #~##~######
```

### Example 2

```
Input: height = [4,2,0,3,2,5]
Output: 9
```

### Constraints

- `0 <= n <= 10^5`
- `0 <= height[i] <= 10^4`
- The answer fits in a 32-bit signed integer.
