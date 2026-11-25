"""Phase 3b - Nearest-Neighbour TSP approximation for the overall route.

Uses Dijkstra distances between the depot and delivery points (a metric
closure), so the visiting order is chosen greedily: always go to the closest
unvisited stop, then return to the depot. Time O(k^2) after k Dijkstra runs.
It is a heuristic (no constant-factor guarantee in general; worst case
O(log k) times optimal on metric graphs), so a brute-force optimum is provided
for small k to measure the gap.
"""
from itertools import permutations


def build_distance_matrix(graph, stops):
    """Run Dijkstra from each stop; return (dist_matrix, prev_per_stop)."""
    dist, prevs = {}, {}
    for s in stops:
        d, p = graph.dijkstra(s)
        dist[s] = d
        prevs[s] = p
    return dist, prevs


def nearest_neighbor_route(dist, depot, stops):
    """Return (ordered route starting and ending at depot, total length)."""
    unvisited = set(stops) - {depot}
    route, cur, total = [depot], depot, 0
    while unvisited:
        nxt = min(unvisited, key=lambda s: dist[cur][s])
        total += dist[cur][nxt]
        route.append(nxt)
        unvisited.remove(nxt)
        cur = nxt
    total += dist[cur][depot]
    route.append(depot)
    return route, total


def optimal_route_bruteforce(dist, depot, stops):
    """Exact TSP by trying all permutations - only for k <= ~9, used to compare."""
    others = [s for s in stops if s != depot]
    best, best_len = None, float("inf")
    for perm in permutations(others):
        r = [depot, *perm, depot]
        L = sum(dist[r[i]][r[i + 1]] for i in range(len(r) - 1))
        if L < best_len:
            best, best_len = r, L
    return best, best_len


def expand_route(prevs, route, graph_path_fn):
    """Expand stop-to-stop legs into the full node-by-node road path."""
    full = [route[0]]
    for a, b in zip(route, route[1:]):
        leg = graph_path_fn(prevs[a], b)
        full.extend(leg[1:])
    return full
