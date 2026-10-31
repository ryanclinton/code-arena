## Approach: Swap children at every node

The mirror image of a tree is the same tree with the left and right children of **every** node
swapped. Visit each node once, in any order, and swap its two children.

Recursively, that's three lines:

```python
if root:
    root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)
return root
```

The reference uses an explicit stack, so a 5000-deep chain doesn't rely on the call stack.

**Complexity**
- Time: `O(n)`
- Space: `O(h)` for the stack, where `h` is the tree's height (`O(n)` for a chain)
