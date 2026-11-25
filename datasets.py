"""Dataset loading / generation (Phase 1 data design + Phase 4 larger inputs)."""
import json
import random
from graph import Graph
from models import Parcel


def load_dataset(path):
    with open(path) as f:
        d = json.load(f)
    g = Graph()
    for u, v, w in d["edges"]:
        g.add_edge(u, v, w)
    parcels = [Parcel(**p) for p in d["parcels"]]
    return g, d["depot"], parcels, d["van_capacity"]


def generate_dataset(n_parcels, n_nodes, capacity, seed=42):
    """Random connected graph (a spanning chain + extra edges) and random parcels."""
    rng = random.Random(seed)
    nodes = ["Depot"] + [f"N{i}" for i in range(1, n_nodes)]
    edges = []
    for i in range(1, n_nodes):                      # guarantees connectivity
        edges.append([nodes[rng.randrange(i)], nodes[i], rng.randint(1, 20)])
    for _ in range(n_nodes * 2):                     # extra shortcuts
        u, v = rng.sample(nodes, 2)
        edges.append([u, v, rng.randint(1, 30)])
    parcels = [dict(pid=i, dest=rng.choice(nodes[1:]), weight=rng.randint(1, 10),
                    priority=rng.randint(1, 5), deadline=rng.randint(1, 24))
               for i in range(1, n_parcels + 1)]
    return dict(depot="Depot", van_capacity=capacity, edges=edges, parcels=parcels)


def save_dataset(d, path):
    with open(path, "w") as f:
        json.dump(d, f, indent=1)
