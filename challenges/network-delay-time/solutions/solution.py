class Solution:
    def networkDelayTime(self, times: List[List[int]], n: int, k: int) -> int:
        graph = defaultdict(list)
        for u, v, w in times:
            graph[u].append((v, w))
        dist = {}
        heap = [(0, k)]
        while heap:
            d, node = heappop(heap)
            if node in dist:
                continue
            dist[node] = d
            for nxt, w in graph[node]:
                if nxt not in dist:
                    heappush(heap, (d + w, nxt))
        return max(dist.values()) if len(dist) == n else -1
