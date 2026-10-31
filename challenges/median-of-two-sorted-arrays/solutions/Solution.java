import java.util.*;

class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        if (nums1.length > nums2.length) return findMedianSortedArrays(nums2, nums1);
        int m = nums1.length, n = nums2.length;
        int half = (m + n + 1) / 2;
        int lo = 0, hi = m;
        while (lo <= hi) {
            int i = (lo + hi) / 2;   // elements taken from nums1
            int j = half - i;        // elements taken from nums2
            int aLeft = i > 0 ? nums1[i - 1] : Integer.MIN_VALUE;
            int aRight = i < m ? nums1[i] : Integer.MAX_VALUE;
            int bLeft = j > 0 ? nums2[j - 1] : Integer.MIN_VALUE;
            int bRight = j < n ? nums2[j] : Integer.MAX_VALUE;
            if (aLeft <= bRight && bLeft <= aRight) {
                if ((m + n) % 2 == 1) return Math.max(aLeft, bLeft);
                return (Math.max(aLeft, bLeft) + (double) Math.min(aRight, bRight)) / 2.0;
            }
            if (aLeft > bRight) hi = i - 1;
            else lo = i + 1;
        }
        throw new IllegalArgumentException("inputs are not sorted");
    }
}
