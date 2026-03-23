---
name: data-structures-algorithms
description: Common data structures, algorithms, and complexity analysis for problem solving
---

# Data Structures & Algorithms

## Complexity Quick Reference
| Structure/Op | Access | Search | Insert | Delete |
|-------------|--------|--------|--------|--------|
| Array       | O(1)   | O(n)   | O(n)   | O(n)   |
| Hash Map    | O(1)   | O(1)   | O(1)   | O(1)   |
| Linked List | O(n)   | O(n)   | O(1)   | O(1)   |
| Binary Tree | O(log n) | O(log n) | O(log n) | O(log n) |
| Heap        | O(1)*  | O(n)   | O(log n) | O(log n) |

*Heap: O(1) for min/max only

## When to Use What
- **Need fast lookup by key** → Hash Map / Dictionary
- **Need sorted order** → Balanced BST / TreeMap / sorted array
- **Need min/max quickly** → Heap / Priority Queue
- **Need FIFO** → Queue (deque in Python)
- **Need LIFO** → Stack (list in Python)
- **Need fast prefix search** → Trie
- **Need to track components / unions** → Union-Find / Disjoint Set

## Common Patterns
### Two Pointers (sorted arrays, linked lists)
```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target: return [left, right]
        elif s < target: left += 1
        else: right -= 1
```

### Sliding Window (subarrays, substrings)
```python
def max_sum_subarray(nums, k):
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best
```

### BFS / DFS (graphs, trees)
```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

## Sorting Algorithms
- **Built-in sort** — Always prefer language built-in (Timsort: O(n log n))
- **Counting sort** — When values are in small, known range (O(n + k))
- **Bucket sort** — When data is uniformly distributed

## Optimization Tips
- Profile before optimizing — don't guess the bottleneck
- Prefer hash maps over nested loops (O(n) vs O(n^2))
- Cache repeated computations (memoization)
- Use generators/iterators for large datasets (avoid loading all in memory)
