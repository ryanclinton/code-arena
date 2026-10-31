import java.util.*;

class Solution {
    public boolean isValidBST(TreeNode root) {
        // In-order traversal of a valid BST visits values in strictly increasing order.
        Deque<TreeNode> stack = new ArrayDeque<>();
        TreeNode node = root;
        long prev = Long.MIN_VALUE;
        while (node != null || !stack.isEmpty()) {
            while (node != null) {
                stack.push(node);
                node = node.left;
            }
            node = stack.pop();
            if (node.val <= prev) return false;
            prev = node.val;
            node = node.right;
        }
        return true;
    }
}
