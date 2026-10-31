## Approach 1: Bounds passed down from ancestors

Checking only each node against its own children isn't enough: in `[5,4,6,null,null,3,7]` every
parent and child pair looks fine, but `3` sits in the root's right subtree and must be greater
than `5`.

Instead, carry an open interval `(low, high)` down the tree. The root may be anything. Going left,
the upper bound becomes the parent's value; going right, the lower bound does. A node outside its
interval means the tree is invalid. The Python reference does this with an explicit stack.

## Approach 2: In-order traversal

An in-order traversal (left, node, right) of a BST visits values in **strictly increasing**
order, so walk it and compare each value with the previous one. The Java reference does this
iteratively.

**Watch the edge values:** node values span the whole 32-bit range, so sentinels like
`Integer.MIN_VALUE` collide with real values. Use `long` (Java), `-inf`/`inf` (Python), or `null` bounds.

**Complexity**
- Time: `O(n)`
- Space: `O(h)`, where `h` is the tree's height
