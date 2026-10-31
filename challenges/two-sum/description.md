Given an array of integers `nums` and an integer `target`, return *the indices of the two numbers such that they add up to `target`*.

You may assume that each input has **at least one solution**, and you may not use the *same* element twice. If several pairs work, return any of them. You can return the answer in any order.

### Example 1

```
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

### Example 2

```
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

### Example 3

```
Input: nums = [3,3], target = 6
Output: [0,1]
```

### Constraints

- `2 <= nums.length <= 10^5`
- `-10^9 <= nums[i] <= 10^9`
- `-2 * 10^9 <= target <= 2 * 10^9`
- At least one valid answer exists.

**Follow-up:** Can you come up with an algorithm that is faster than `O(n²)`?
