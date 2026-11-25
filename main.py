"""Mini-Courier Planner - integrated pipeline.

Usage:  python main.py [dataset.json]      (default: data/small.json)

Pipeline per run:
  1. Merge-sort all parcels by deadline/priority            (Phase 2)
  2. Repeat until all parcels are assigned:
       a. 0/1 Knapsack DP picks the best set for one van trip (Phase 2)
       b. Dijkstra gives shortest paths between the stops    (Phase 3)
       c. Nearest-neighbour TSP orders the stops             (Phase 3)
  3. Print the trip plans, route lengths and stage runtimes  (Phase 4)
"""
import sys
import time
from sorting import merge_sort
from knapsack import knapsack
from tsp import build_distance_matrix, nearest_neighbor_route, expand_route
from graph import Graph
from datasets import load_dataset


def plan(graph, depot, parcels, capacity, verbose=True):
    """Return (trips, timings). timings = seconds spent in each major stage."""
    t = dict(sort=0.0, knapsack=0.0, dijkstra=0.0, tsp=0.0)

    s = time.perf_counter()
    pending = merge_sort(parcels)
    t["sort"] += time.perf_counter() - s

    trips, trip_no = [], 0
    while pending:
        # parcels heavier than the van can never be loaded - report and drop them
        too_heavy = [p for p in pending if p.weight > capacity]
        if too_heavy:
            if verbose:
                print(f"  ! Skipping parcels heavier than van capacity: {[p.pid for p in too_heavy]}")
            pending = [p for p in pending if p.weight <= capacity]
            if not pending:
                break

        s = time.perf_counter()
        value, chosen, _ = knapsack(pending, capacity)
        t["knapsack"] += time.perf_counter() - s

        chosen_ids = {p.pid for p in chosen}
        pending = [p for p in pending if p.pid not in chosen_ids]

        stops = [depot] + sorted({p.dest for p in chosen})
        s = time.perf_counter()
        dist, prevs = build_distance_matrix(graph, stops)
        t["dijkstra"] += time.perf_counter() - s

        s = time.perf_counter()
        route, length = nearest_neighbor_route(dist, depot, stops)
        t["tsp"] += time.perf_counter() - s

        trip_no += 1
        trips.append(dict(trip=trip_no, parcels=chosen, value=value, route=route,
                          length=length, road_path=expand_route(prevs, route, Graph.path_to)))
    return trips, t


def report(trips, timings, capacity):
    for tr in trips:
        load = sum(p.weight for p in tr["parcels"])
        print(f"\n=== Trip {tr['trip']} ===")
        print(f"Parcels   : {[p.pid for p in tr['parcels']]}  "
              f"(load {load}/{capacity} kg, value {tr['value']})")
        print(f"Stop order: {' -> '.join(tr['route'])}")
        print(f"Road path : {' -> '.join(tr['road_path'])}")
        print(f"Route len : {tr['length']}")
    print("\n--- Stage runtimes (ms) ---")
    for k, v in timings.items():
        print(f"{k:9s}: {v * 1000:.3f}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/small.json"
    g, depot, parcels, cap = load_dataset(path)
    print(f"Dataset: {path} | parcels={len(parcels)} nodes={len(g.nodes)} capacity={cap}")
    print("Sorted order (deadline, -priority):",
          [p.pid for p in merge_sort(parcels)])
    trips, timings = plan(g, depot, parcels, cap)
    report(trips, timings, cap)
