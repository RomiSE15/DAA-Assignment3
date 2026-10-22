# Assignment 3 analysis

Student: Ramazan Zhunussov, group SE-2515

Language: Python 3. The algorithms are in `src/Python/algorithms.py`. The supplied `main.py` is unchanged and `submission.json` contains `{"language":"Python"}`. No graph library is used; only `heapq` is imported, for Prim's priority queue

## Build, run and test

Python needs no compilation. From the repository root:

```sh
python tools/run.py --setup
python tools/run.py --check
python tests/check_cases.py
python tests/benchmark.py
python tools/run.py --input tests/cases.jsonl
```

Development and benchmark machine: Windows 11 Pro, Python 3.12. The last command only prints answers; the comparison is done in `tests/check_cases.py`

## State reset

No function keeps global state. `dsu`, `kruskal`, `prim`, `scc`, `topo` and `dag` create their own lists on every call and return a new dictionary, so a later request cannot see an earlier graph. This is checked by the public runner (it sends every case more than once in one process) and by my own test, which solves a 100000-vertex DAG and then a one-vertex DSU and gets `[[1,1]]`

## Deep DFS

Python's call stack is about 1000 frames, so a recursive DFS would fail on a chain of 2000 or 100000 vertices. All searches here are iterative. The stack holds pairs `(vertex, next neighbour index)`, so a suspended vertex continues where it stopped and its neighbour list is not rescanned. Colours are 0 (unseen), 1 (on the current path) and 2 (finished). One routine is shared by Kosaraju's first pass, the topological order and the DAG cycle check. Kosaraju's second pass uses an explicit stack on the transposed lists

## 1. Disjoint-set union

Steps: every vertex starts alone with size 1. `find` walks to the root and points every visited vertex at it (path compression). `union` links the smaller root under the larger one and adds the sizes. After each operation the program outputs `[components, largest]`. Union by size is used, so the size array already gives the largest component

Invariant: `parent` forms trees, the size of a root is the number of vertices in its tree, `components` is the number of roots, and `largest` is the maximum root size

Correctness: merging two different roots replaces two blocks by one block of their combined size. A repeated union or a self-union finds the same root and returns before any change. Path compression does not change roots

Boundary cases: for `n = 0` the result is `states = []`. Self-unions and repeated unions leave the state unchanged

Complexity: `O(n + q α(n))` amortised time, `O(n + q)` memory including the states

## 2. Kruskal

Steps: attach the original index to every edge and sort by weight. Scan the edges and accept one only when `union` joins two different components. Return the cost, the accepted ids and the DSU component count

Invariant: the accepted edges form a forest and never connect two vertices that are already connected

Correctness: this is the usual cut argument. The cheapest edge between two different components belongs to some minimum spanning forest. Self-loops are rejected because both ends have the same root. Among parallel edges the cheaper one is seen first. A forest with `c` components has exactly `n - c` edges

Boundary cases: `n = 0` gives cost 0, no ids and 0 components. Isolated vertices count as components. Negative weights work because sorting puts them first. Ties are broken by edge id. Sums use Python integers, so values above 32 bits are fine

Complexity: `O(n + m log(m + 1))` time, `O(n + m)` memory

## 3. Prim

Steps: build adjacency lists with `(weight, edge id, other end)`, skipping self-loops; both directions share one edge id. For every unvisited vertex start a new tree and add one to the component count. Keep a min-heap of edges leaving the tree. Pop the cheapest; if its other end is already visited, discard it, otherwise accept the edge and push the new vertex's edges

Invariant: every accepted edge has one end in the current tree and one end outside it at the moment it is accepted.

Correctness: the cheapest edge leaving a set of vertices is safe for a minimum spanning forest (same cut argument as Kruskal). Restarting at an unvisited vertex handles the next component. An edge id is added only when a vertex is first visited, so ids are never repeated

Boundary cases: the same as Kruskal. On a triangle with three edges of weight 1 both methods return ids `[0, 1]` and cost 2.

Complexity: `O(n + m log(m + 1))` time with a lazy heap, `O(n + m)` memory

## 4. Kosaraju SCC

Steps: build forward and transposed lists. Run the iterative DFS on the forward graph to get the finish order. Go through that order backwards; each vertex without a label starts a DFS on the transposed graph and every vertex reached gets the next label. Finally, for every input edge between different labels, add the pair to the condensation once (a set removes duplicates)

Invariant: in the second pass a label is given only to vertices reached from the current start that no earlier start has claimed.

Correctness: the component with the latest finish time is a source of the original graph, so it is a sink of the transpose and the second DFS cannot leave it. Removing it and repeating assigns every vertex to exactly one component.

Boundary cases: for `n = 0` both outputs are empty. An isolated vertex and a vertex with only a self-loop are separate components. Duplicate edges give one condensation pair. For edges `0->1, 1->0, 1->2, 0->2, 2->3, 1->2` the result is `component = [0, 0, 1, 2]` and `condensation = [[0, 1], [1, 2]]`. Label values depend on the second pass; only the grouping matters

Complexity: `O(n + m)` expected time with hashing, `O(n + m)` memory

## 5. DFS topological order

Steps: run the three-colour iterative DFS from every unvisited vertex. An edge into a colour-1 vertex is a back edge, so the graph has a cycle and the answer is `acyclic = false`, `order = []`. Otherwise the reversed finish order is the answer.

Invariant: colour-1 vertices are exactly the current DFS stack. Without a back edge, every edge `u -> v` finishes `v` before `u`.

Correctness: reversing the finish order puts `u` before `v` for every edge. An edge into a finished vertex is not a cycle. A self-loop points at a colour-1 vertex, so it is a cycle. A cycle in any component makes the whole answer cyclic.

Boundary cases: `n = 0` gives `acyclic = true` and an empty order. For the diamond `0->2, 1->2, 2->3` one valid order is `[1, 0, 2, 3]`.

Complexity: `O(n + m)` time and memory

## 6. DAG shortest paths

Steps: check the whole graph for cycles. If there is one, even unreachable from the source, return `acyclic = false` with empty arrays. Otherwise set `distance[source] = 0`, all others `None`, and relax outgoing edges in topological order, skipping vertices whose distance is still `None`. An edge replaces the distance only if it gives a strictly smaller value, and `parent_edge` stores the edge id

Invariant: when a vertex is processed, all its predecessors have been processed, so its distance is final.

Correctness: one pass in topological order is enough even with negative weights. Unreachable vertices never relax anything, so no false path appears. The parent edge ends at its vertex and its tail is earlier in the topological order, so following parents reaches the source. Unreachable distances are `None` (JSON `null`), not `-1`, because `-1` can be a real distance

Boundary cases: one vertex and no edges gives `[0]` and `[-1]`. Edge `0->1` of weight `-1` with an extra vertex 2 gives `[0, -1, null]`. A cycle not reachable from the source and a self-loop are both reported as cyclic. Three edges of weight `10^9` give distances up to `3000000000`.

Complexity: `O(n + m)` time and memory

## Route helper

`reconstruct_route(edges, parent_edge, source, target)` follows parent edge ids from the target back to the source and reverses the result. The route to the source is `[source]`. For an unreachable target it returns `[]` (this is my chosen no-route value; JSON distances still use `null`). `route_weight` sums the weights of the parent edges along a route

Calls made in `tests/check_cases.py`, with `n = 5`, `source = 0` and edges `[0,1,3]`, `[0,2,8]`, `[1,2,-7]`, `[2,3,4]`:

- Target 3 (reachable): route `[0, 1, 2, 3]`, parent edge ids 0, 2, 3, weight `3 - 7 + 4 = 0`, equal to `distance[3]`. The direct edge `0->2` (id 1, weight 8) is not used
- Target 0 (the source): route `[0]`, weight 0.
- Target 4 (unreachable): route `[]`, because `parent_edge[4] = -1`

Tied and parallel edges `[0,1,5]`, `[0,1,5]`, `[0,2,9]`, `[1,2,4]`, `[0,2,9]`: the result is `distance = [0, 5, 9]` and `parent_edge = [-1, 0, 2]`. The route to vertex 2 is `[0, 2]` using edge id 2 with weight 9. The other route `[0, 1, 2]` (ids 0 and 3, weight `5 + 4 = 9`) has the same total, so both are valid.

## Own tests

The files are in `tests/`: `cases.jsonl` (inputs, including a chain of 3000 vertices), `expected.jsonl`, `actual.jsonl`, `explanations.md` (why each expected answer is right) and `check_cases.py`

Answers that are not unique are checked by meaning, not as text: forest validity and optimal cost, SCC grouping and exact condensation, topological precedence, and shortest distances with valid parent paths. The check accepts another optimal forest on the weight-1 triangle (ids `[0, 1]` and `[1, 2]`) and rejects a cycle, a wrong cost and a self-loop used as a tree edge. Chains of 100000 vertices are generated inside the test script; for the DAG with weights `-10^9` the last distance is `-99999000000000`

## Benchmark

Kruskal and Prim were timed on the same three random graphs, generated by `tests/benchmark.py` with `random.Random(seed)`: `m` edges with different endpoints and weights from -1000 to 1000. The sizes are `(n, m, seed)` = (2000, 8000, 20261021), (20000, 80000, 20261022) and (100000, 250000, 20261023). Before timing, both methods must give the same cost and component count, and the forest must have `n - components` edges

Conditions: command `python tests/benchmark.py`; Python 3.12.0 (64-bit); Windows 11; AMD Ryzen 5 7430U with Radeon Graphics, 2.30 GHz; 16 GB RAM; timer `time.perf_counter`; one unrecorded warm-up call and then three recorded calls per method and size. Timed: sorting, DSU, adjacency lists and heap work inside `kruskal` and `prim`. Not timed: generating the edges, JSON parsing and printing. Both methods use the same boundary. Python has no compilation step

Results (seconds, three runs and the median):

- n = 2000, m = 8000: cost -1395898, components 1. Kruskal 0.012169, 0.012434, 0.012150, median 0.012169. Prim 0.015099, 0.015950, 0.018735, median 0.015950.
- n = 20000, m = 80000: cost -13968940, components 12. Kruskal 0.243732, 0.226608, 0.209621, median 0.226608. Prim 0.352957, 0.370730, 0.361445, median 0.361445.
- n = 100000, m = 250000: cost -52909328, components 710. Kruskal 0.745850, 0.748362, 0.754194, median 0.748362. Prim 1.476807, 1.506563, 1.576243, median 1.506563.

Observations: Kruskal was faster than Prim at every size, by a factor of about 1.3, 1.6 and 2.0. From 8000 to 80000 edges the input grows 10 times and the medians grow about 19 times for Kruskal and about 23 times for Prim. From 80000 to 250000 edges the input grows 3.1 times and the medians grow about 3.3 and 4.2 times. This is somewhat above linear, as expected for a sort or a heap with a large Python constant. Prim stores every edge in two adjacency lists and keeps stale entries in the heap until they are popped, while Kruskal sorts once and then does nearly linear DSU work. The asymptotic bounds come from the sort and the heap, not from these three measurements

Limitations: these are three random graphs, not worst cases, and three runs per size are few. The runs were made on a laptop, so some noise is expected (for example the three Kruskal runs at n = 20000 fall from 0.24 s to 0.21 s). Another machine or Python version can change the numbers

## Sources and AI use

The algorithms are standard: union by size with path compression, Kruskal, Prim with a lazy heap, Kosaraju, DFS topological order and DAG relaxation. AI tools were used to understand the assignment text and the structure of the required files (code, `tests/`, `ANALYSIS.md`) and in this document, to review and shorten the text. I ran the tests and the benchmark on my own machine and the numbers above come from those runs