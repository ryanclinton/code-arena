import java.util.*;

class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public int numIslands(char[][] grid) {
        int m = grid.length, n = grid[0].length, islands = 0;
        ArrayDeque<int[]> queue = new ArrayDeque<>();
        for (int r = 0; r < m; r++) {
            for (int c = 0; c < n; c++) {
                if (grid[r][c] != '1') continue;
                islands++;
                grid[r][c] = '0'; // sink it so it isn't counted again
                queue.add(new int[] {r, c});
                while (!queue.isEmpty()) {
                    int[] cell = queue.poll();
                    for (int[] d : DIRS) {
                        int x = cell[0] + d[0], y = cell[1] + d[1];
                        if (x >= 0 && x < m && y >= 0 && y < n && grid[x][y] == '1') {
                            grid[x][y] = '0';
                            queue.add(new int[] {x, y});
                        }
                    }
                }
            }
        }
        return islands;
    }
}
