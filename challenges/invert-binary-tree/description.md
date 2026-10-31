Given the `root` of a binary tree, invert the tree (mirror it left to right), and return *its root*.

Trees are shown in level order, with `null` where a child is missing: `[1,null,2]` is a root `1` whose
right child is `2`. `[]` is an empty tree.

### Example 1

```
Input: root = [4,2,7,1,3,6,9]
Output: [4,7,2,9,6,3,1]
```

### Example 2

```
Input: root = [2,1,3]
Output: [2,3,1]
```

### Example 3

```
Input: root = []
Output: []
```

### Constraints

- The number of nodes in the tree is in the range `[0, 10^4]`.
- `-100 <= Node.val <= 100`
