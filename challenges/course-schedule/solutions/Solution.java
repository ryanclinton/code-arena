import java.util.*;

class Solution {
    public boolean canFinish(int numCourses, int[][] prerequisites) {
        // Kahn's algorithm: repeatedly take a course with no remaining prerequisites.
        List<List<Integer>> after = new ArrayList<>();
        for (int i = 0; i < numCourses; i++) after.add(new ArrayList<>());
        int[] indegree = new int[numCourses];
        for (int[] p : prerequisites) {
            after.get(p[1]).add(p[0]);
            indegree[p[0]]++;
        }
        ArrayDeque<Integer> ready = new ArrayDeque<>();
        for (int c = 0; c < numCourses; c++) if (indegree[c] == 0) ready.add(c);
        int taken = 0;
        while (!ready.isEmpty()) {
            int c = ready.poll();
            taken++;
            for (int next : after.get(c)) {
                if (--indegree[next] == 0) ready.add(next);
            }
        }
        return taken == numCourses;
    }
}
