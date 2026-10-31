# Names available to every Python solution without importing (mirrors LeetCode).
from typing import *
import collections, heapq, bisect, math, itertools, functools, string, re, random, operator
from collections import *
from heapq import *
from bisect import *
from functools import *
from itertools import *
from math import inf


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val})"


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TreeNode({self.val})"
