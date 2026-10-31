Given an array of strings `strs`, group **the anagrams** together. You can return the answer in **any order** — both the order of the groups and the order of words within a group are ignored.

An **anagram** is a word formed by rearranging the letters of another word, using all the original letters exactly once.

### Example 1

```
Input: strs = ["eat","tea","tan","ate","nat","bat"]
Output: [["bat"],["nat","tan"],["ate","eat","tea"]]
```

### Example 2

```
Input: strs = [""]
Output: [[""]]
```

### Example 3

```
Input: strs = ["a"]
Output: [["a"]]
```

### Constraints

- `1 <= strs.length <= 10^4`
- `0 <= strs[i].length <= 100`
- `strs[i]` consists of lowercase English letters.
- Duplicate words belong to the same group (and each copy is kept).
