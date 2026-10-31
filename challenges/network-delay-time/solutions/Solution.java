import java.util.*;

class Solution {
    public int networkDelayTime(int[][] times, int n, int k) {
        List<List<int[]>> graph = new ArrayList<>();
        for (int i = 0; i <= n; i++) graph.add(new ArrayList<>());
        for (int[] t : times) graph.get(t[0]).add(new int[] {t[1], t[2]});

        int[] dist = new int[n + 1];
        Arrays.fill(dist, Integer.MAX_VALUE);
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        heap.add(new int[] {0, k});
        while (!heap.isEmpty()) {
            int[] top = heap.poll();
            int d = top[0], node = top[1];
            if (dist[node] != Integer.MAX_VALUE) continue;
            dist[node] = d;
            for (int[] e : graph.get(node)) {
                if (dist[e[0]] == Integer.MAX_VALUE) heap.add(new int[] {d + e[1], e[0]});
            }
        }
        int answer = 0;
        for (int i = 1; i <= n; i++) {
            if (dist[i] == Integer.MAX_VALUE) return -1;
            answer = Math.max(answer, dist[i]);
        }
        return answer;
    }
}
