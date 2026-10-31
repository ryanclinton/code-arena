class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        """Reverse the whole array, then reverse each part."""
        n = len(nums)
        k %= n

        def reverse(lo, hi):
            while lo < hi:
                nums[lo], nums[hi] = nums[hi], nums[lo]
                lo, hi = lo + 1, hi - 1

        reverse(0, n - 1)
        reverse(0, k - 1)
        reverse(k, n - 1)
