"""Phase 3a - Weighted undirected graph and Dijkstra's shortest path.

Adjacency-list graph; Dijkstra uses a binary heap => O((V+E) log V).
"""
import heapq


class Graph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v, w):
        if w < 0:
            raise ValueError("Dijkstra requires non-negative weights")
        self.adj.setdefault(u, []).append((v, w))
        self.adj.setdefault(v, []).append((u, w))

    @property
    def nodes(self):
        return list(self.adj)

    def dijkstra(self, source):
        """Return (dist, prev) dicts from source to every reachable node."""
        dist = {n: float("inf") for n in self.adj}
        prev = {n: None for n in self.adj}
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue  # stale heap entry
            for v, w in self.adj[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        return dist, prev

    @staticmethod
    def path_to(prev, target):
        path = []
        while target is not None:
            path.append(target)
            target = prev[target]
        return path[::-1]
