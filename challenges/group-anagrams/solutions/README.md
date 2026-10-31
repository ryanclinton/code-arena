## Approach: Canonical Key in a Hash Map

Two words are anagrams exactly when their sorted letters are equal, so the sorted word is a
perfect grouping key. Bucket every word under its key and return the buckets.

**Complexity** (n words, max length k)
- Time: `O(n · k log k)` for sorting each word.
- Space: `O(n · k)` for the map.

**Alternative:** use a 26-length letter-count tuple as the key for `O(n · k)` time.
Just make sure the key is unambiguous — joining counts without a separator can collide.
