import java.util.*;

class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String word : strs) {
            char[] key = word.toCharArray();
            Arrays.sort(key);
            groups.computeIfAbsent(new String(key), k -> new ArrayList<>()).add(word);
        }
        return new ArrayList<>(groups.values());
    }
}
