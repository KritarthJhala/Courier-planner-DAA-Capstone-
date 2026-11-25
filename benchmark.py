"""Phase 4 - runtime experiments. Run: python benchmark.py
Produces charts/*.png and data/medium.json, data/large.json."""
import time
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datasets import generate_dataset, save_dataset
from graph import Graph
from models import Parcel
from sorting import merge_sort, insertion_sort
from knapsack import knapsack
from tsp import build_distance_matrix, nearest_neighbor_route, optimal_route_bruteforce
from main import plan
from datasets import load_dataset


def timeit(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter(); fn(); best = min(best, time.perf_counter() - s)
    return best * 1000  # ms


def parcels_of(d):
    return [Parcel(**p) for p in d["parcels"]]


def graph_of(d):
    g = Graph()
    for u, v, w in d["edges"]: g.add_edge(u, v, w)
    return g


# 1. Sorting: merge sort vs insertion sort
sizes = [100, 200, 400, 800, 1600]
ms, ins = [], []
for n in sizes:
    ps = parcels_of(generate_dataset(n, 10, 50, seed=n))
    ms.append(timeit(lambda: merge_sort(ps))); ins.append(timeit(lambda: insertion_sort(ps)))
plt.figure(figsize=(6, 4))
plt.plot(sizes, ms, "o-", label="Merge sort O(n log n)")
plt.plot(sizes, ins, "s-", label="Insertion sort O(n^2)")
plt.xlabel("Number of parcels (n)"); plt.ylabel("Time (ms)"); plt.title("Sorting runtime")
plt.legend(); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig("charts/sorting.png", dpi=150); plt.close()

# 2. Knapsack: time vs n (W fixed) and vs W (n fixed)
ns = [50, 100, 200, 400, 800]
kn_n = [timeit(lambda ps=parcels_of(generate_dataset(n, 10, 100, 1)): knapsack(ps, 100), 2) for n in ns]
Ws = [50, 100, 200, 400, 800]
ps200 = parcels_of(generate_dataset(200, 10, 100, 1))
kn_w = [timeit(lambda W=W: knapsack(ps200, W), 2) for W in Ws]
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(ns, kn_n, "o-"); ax[0].set_xlabel("Parcels n (W=100)"); ax[0].set_ylabel("Time (ms)")
ax[0].set_title("Knapsack DP vs n"); ax[0].grid(alpha=.3)
ax[1].plot(Ws, kn_w, "o-", color="tab:green"); ax[1].set_xlabel("Capacity W (n=200)")
ax[1].set_title("Knapsack DP vs W"); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig("charts/knapsack.png", dpi=150); plt.close()

# 3. Dijkstra vs graph size
vs = [100, 200, 400, 800, 1600]
dj = [timeit(lambda g=graph_of(generate_dataset(10, v, 50, 3)): g.dijkstra("Depot")) for v in vs]
plt.figure(figsize=(6, 4)); plt.plot(vs, dj, "o-", color="tab:red")
plt.xlabel("Nodes V (E ~ 3V)"); plt.ylabel("Time (ms)"); plt.title("Dijkstra (single source)")
plt.grid(alpha=.3); plt.tight_layout(); plt.savefig("charts/dijkstra.png", dpi=150); plt.close()

# 4. Whole pipeline: stage breakdown across dataset sizes
labels, stage = [], {k: [] for k in ("sort", "knapsack", "dijkstra", "tsp")}
configs = [("small", 8, 8, 20), ("medium", 100, 40, 60), ("large", 500, 120, 100)]
for name, n, v, cap in configs:
    if name == "small":
        g, depot, ps, cap = load_dataset("data/small.json")
    else:
        d = generate_dataset(n, v, cap, seed=11); save_dataset(d, f"data/{name}.json")
        g, depot, ps = graph_of(d), "Depot", parcels_of(d)
    _, t = plan(g, depot, ps, cap, verbose=False)
    labels.append(f"{name}\n({n} parcels)")
    for k in stage: stage[k].append(t[k] * 1000)
    print(name, {k: round(v_ * 1000, 3) for k, v_ in t.items()})
fig, ax = plt.subplots(figsize=(7, 4)); bottom = [0] * len(labels)
for k, vals in stage.items():
    ax.bar(labels, vals, bottom=bottom, label=k); bottom = [b + v for b, v in zip(bottom, vals)]
ax.set_ylabel("Time (ms)"); ax.set_yscale("linear"); ax.set_title("Pipeline stage runtime by dataset size")
ax.legend(); plt.tight_layout(); plt.savefig("charts/pipeline_stages.png", dpi=150); plt.close()

# 5. TSP quality: nearest neighbour vs optimal (small k)
rng = random.Random(7)
d = generate_dataset(10, 30, 50, seed=9); g = graph_of(d)
nodes = [n for n in g.nodes if n != "Depot"]
ratios = []
for _ in range(20):
    stops = ["Depot"] + rng.sample(nodes, 7)
    dist, _ = build_distance_matrix(g, stops)
    _, L = nearest_neighbor_route(dist, "Depot", stops)
    _, opt = optimal_route_bruteforce(dist, "Depot", stops)
    ratios.append(L / opt)
print(f"NN/optimal over 20 random 7-stop trips: avg={sum(ratios)/20:.3f} worst={max(ratios):.3f}")
plt.figure(figsize=(6, 4)); plt.bar(range(1, 21), ratios, color="tab:purple"); plt.axhline(1, color="k", lw=.8)
plt.xlabel("Random trip #"); plt.ylabel("NN length / optimal"); plt.title("TSP approximation quality (7 stops)")
plt.tight_layout(); plt.savefig("charts/tsp_quality.png", dpi=150); plt.close()
print("sorting ms:", [round(x, 2) for x in ms], [round(x, 2) for x in ins])
print("knap vs n:", [round(x, 1) for x in kn_n], " vs W:", [round(x, 1) for x in kn_w])
print("dijkstra:", [round(x, 2) for x in dj])
