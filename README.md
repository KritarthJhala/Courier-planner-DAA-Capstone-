# Mini-Courier Planner (DAA Capstone, ETCCDA302)

Python prototype that takes parcels + a road graph and produces (1) a priority-sorted
parcel list, (2) an optimal van load per trip, (3) shortest paths and (4) an ordered
delivery route per trip, with runtime measurements of every stage.

## How to run
```
python3 main.py                  # small sample (data/small.json)
python3 main.py data/large.json  # 500 parcels, 120 nodes
python3 tests.py                 # 7 correctness tests
python3 benchmark.py             # regenerates charts/ and medium/large datasets (needs matplotlib)
```
Only `benchmark.py` needs a third-party library (matplotlib); everything else is standard library.

## Phase 1 - Design
**Data.** `Parcel(pid, dest, weight kg, priority 1-5, deadline hrs)`; graph = weighted undirected
adjacency list; dataset JSON = `{depot, van_capacity, edges[[u,v,w]], parcels[...]}`.

**Pipeline**
```
parcels --Merge Sort--> ordered list
   repeat until empty:
     0/1 Knapsack DP  -> best parcel set for one trip (capacity = van limit)
     Dijkstra x k     -> shortest distance between depot & each stop
     Nearest-Neighbour TSP -> visiting order, return to depot
```
| Need | Algorithm | Why | Complexity |
|---|---|---|---|
| Prioritise | Merge sort (key = deadline, then -priority) | stable, guaranteed O(n log n) | O(n log n) time, O(n) space |
| Box filling | 0/1 Knapsack DP | each parcel is taken whole or not; greedy can miss the optimum | O(nW) time & space |
| Shortest paths | Dijkstra + binary heap | non-negative road lengths | O((V+E) log V) per source |
| Route order | Nearest-neighbour TSP | exact TSP is NP-hard; greedy is fast | O(k^2) after k Dijkstras |

Knapsack value of a parcel = `priority*10 + max(0, 24 - deadline)`, so urgent, high-tier parcels win scarce space.
Parcels left over after a trip go to the next trip, so every parcel is eventually delivered
(parcels heavier than the van are reported and skipped).

## Phase 2 - Prioritisation & box filling (`sorting.py`, `knapsack.py`)
Small sample sorted order: `[2, 6, 4, 8, 1, 7, 3, 5]`. Trip 1 loads parcels `[2, 6, 4, 8]`
at 20/20 kg with value 261. The DP table is returned by `knapsack()` and the chosen set is
traced back from it. Verified against brute force on 40 random cases.

## Phase 3 - Graph & route (`graph.py`, `tsp.py`)
Trip 1 stop order `Depot -> B -> A -> C -> E -> Depot`, length 26, with the expanded road
path shown in `sample_output.txt`.

## Phase 4 - Results (`benchmark.py`, `charts/`)
| Experiment | Finding |
|---|---|
| Sorting (100 to 1600 parcels) | Merge sort 2.96 ms vs insertion sort 77.8 ms at n=1600; quadratic growth visible |
| Knapsack | Time doubles when n doubles and when W doubles: matches O(nW) |
| Dijkstra (100 to 1600 nodes) | 0.07 ms to 1.58 ms, near-linear growth |
| Whole pipeline, 500 parcels | Knapsack (~64 ms) and Dijkstra (~45 ms) dominate; sorting and TSP under 1 ms |
| TSP quality (20 random 7-stop trips) | NN route averages 1.066x optimal, worst 1.206x |

Charts: `charts/sorting.png`, `knapsack.png`, `dijkstra.png`, `pipeline_stages.png`, `tsp_quality.png`.
Timings are from one machine and vary run to run; the shapes of the curves are what matter.

**Improvement ideas.** Rerunning knapsack on the full pending list each trip is the main cost: restrict it to
the next ~k most urgent parcels, or use a 1-D DP array when the chosen set is not needed.
Run Dijkstra once per stop only (already done) and cache distances across trips; improve the TSP with 2-opt;
add time windows and multiple vans.

## Phase 5 - Evidence
`sample_output.txt` is the captured run of `python3 main.py`. Take your own screenshots of the
terminal run, `python3 tests.py` and the charts for submission.

## Limitations
Nearest-neighbour has no tight guarantee, weights must be integers for the DP table,
and deadlines are only used for ordering and knapsack value, not as hard constraints.
