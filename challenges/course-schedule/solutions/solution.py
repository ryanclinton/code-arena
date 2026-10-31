class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        # Kahn's algorithm: repeatedly take a course with no remaining prerequisites.
        after = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        for course, pre in prerequisites:
            after[pre].append(course)
            indegree[course] += 1
        ready = deque(c for c in range(numCourses) if indegree[c] == 0)
        taken = 0
        while ready:
            c = ready.popleft()
            taken += 1
            for nxt in after[c]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    ready.append(nxt)
        return taken == numCourses
