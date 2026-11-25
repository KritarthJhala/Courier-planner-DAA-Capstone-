"""Correctness tests: python tests.py"""
import random
import unittest
from models import Parcel
from sorting import merge_sort, insertion_sort
from knapsack import knapsack, knapsack_bruteforce
from graph import Graph
from tsp import build_distance_matrix, nearest_neighbor_route, optimal_route_bruteforce
from datasets import generate_dataset, load_dataset
from main import plan


def rand_parcels(rng, n):
    return [Parcel(i, "X", rng.randint(1, 8), rng.randint(1, 5), rng.randint(1, 24)) for i in range(n)]


class Tests(unittest.TestCase):
    def test_sort_matches_python(self):
        rng = random.Random(1)
        ps = rand_parcels(rng, 200)
        key = lambda p: (p.deadline, -p.priority)
        self.assertEqual(merge_sort(ps), sorted(ps, key=key))
        self.assertEqual(insertion_sort(ps), sorted(ps, key=key))

    def test_sort_edge_cases(self):
        self.assertEqual(merge_sort([]), [])
        p = Parcel(1, "A", 1, 1, 1)
        self.assertEqual(merge_sort([p]), [p])

    def test_knapsack_vs_bruteforce(self):
        rng = random.Random(2)
        for _ in range(40):
            ps = rand_parcels(rng, rng.randint(1, 10))
            cap = rng.randint(1, 30)
            val, chosen, _ = knapsack(ps, cap)
            self.assertEqual(val, knapsack_bruteforce(ps, cap))
            self.assertLessEqual(sum(p.weight for p in chosen), cap)
            self.assertEqual(sum(p.value for p in chosen), val)

    def test_dijkstra_known(self):
        g, depot, _, _ = load_dataset("data/small.json")
        dist, prev = g.dijkstra("Depot")
        self.assertEqual(dist["A"], 3)      # Depot-B-A = 2+1
        self.assertEqual(dist["F"], 13)     # Depot-G-F = 9+4
        self.assertEqual(Graph.path_to(prev, "A"), ["Depot", "B", "A"])

    def test_dijkstra_unreachable_and_negative(self):
        g = Graph(); g.add_edge("a", "b", 1); g.adj["c"] = []
        self.assertEqual(g.dijkstra("a")[0]["c"], float("inf"))
        with self.assertRaises(ValueError):
            g.add_edge("a", "c", -1)

    def test_tsp_valid_and_near_optimal(self):
        d = generate_dataset(30, 12, 50, seed=5)
        g = Graph()
        for u, v, w in d["edges"]: g.add_edge(u, v, w)
        stops = ["Depot", "N1", "N3", "N5", "N7", "N9"]
        dist, _ = build_distance_matrix(g, stops)
        route, L = nearest_neighbor_route(dist, "Depot", stops)
        self.assertEqual(route[0], "Depot"); self.assertEqual(route[-1], "Depot")
        self.assertEqual(sorted(route[1:-1]), sorted(stops[1:]))
        _, opt = optimal_route_bruteforce(dist, "Depot", stops)
        self.assertGreaterEqual(L, opt)

    def test_full_pipeline_assigns_all_parcels(self):
        g, depot, ps, cap = load_dataset("data/small.json")
        trips, _ = plan(g, depot, ps, cap, verbose=False)
        ids = sorted(p.pid for t in trips for p in t["parcels"])
        self.assertEqual(ids, sorted(p.pid for p in ps))
        for t in trips:
            self.assertLessEqual(sum(p.weight for p in t["parcels"]), cap)


if __name__ == "__main__":
    unittest.main(verbosity=2)
