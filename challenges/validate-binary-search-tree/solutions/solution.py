class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        # Every node must lie strictly inside the (low, high) bounds set by its ancestors.
        stack = [(root, -inf, inf)]
        while stack:
            node, low, high = stack.pop()
            if not node:
                continue
            if not low < node.val < high:
                return False
            stack.append((node.left, low, node.val))
            stack.append((node.right, node.val, high))
        return True
