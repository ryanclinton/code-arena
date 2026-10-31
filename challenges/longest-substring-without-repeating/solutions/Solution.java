import java.util.*;

class Solution {
    public int lengthOfLongestSubstring(String s) {
        int[] last = new int[128]; // last index + 1 for each ASCII char, 0 = unseen
        int best = 0, start = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            start = Math.max(start, last[c]);
            last[c] = i + 1;
            best = Math.max(best, i - start + 1);
        }
        return best;
    }
}
