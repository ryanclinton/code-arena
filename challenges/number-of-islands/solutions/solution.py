class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        m, n = len(grid), len(grid[0])
        islands = 0
        for r in range(m):
            for c in range(n):
                if grid[r][c] != "1":
                    continue
                islands += 1
                grid[r][c] = "0"  # sink it so it isn't counted again
                queue = deque([(r, c)])
                while queue:
                    i, j = queue.popleft()
                    for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                        if 0 <= x < m and 0 <= y < n and grid[x][y] == "1":
                            grid[x][y] = "0"
                            queue.append((x, y))
        return islands
