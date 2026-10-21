import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "Python"))
sys.path.insert(0, str(ROOT / "tools"))

import algorithms
from public_validate import check


def line(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


CASES = [
    {
        "name": "ping",
        "input": {"task": "ping"},
        "expected": {"status": "ready"},
        "why": "The supplied adapter must answer the setup check.",
    },
    {
        "name": "dsu empty",
        "input": {"task": "dsu", "n": 0, "operations": []},
        "expected": {"states": []},
        "why": "n = 0 has no operations. largest would be 0, but no state is emitted.",
    },
    {
        "name": "dsu self and repeat",
        "input": {"task": "dsu", "n": 3, "operations": [[1, 1], [0, 2], [2, 0], [0, 2]]},
        "expected": {"states": [[3, 1], [2, 2], [2, 2], [2, 2]]},
        "why": "Self-union keeps 3 components. 0-2 merges them into size 2. Repeating that union does nothing. Vertex 1 stays alone.",
    },
    {
        "name": "dsu growing largest",
        "input": {"task": "dsu", "n": 5, "operations": [[0, 1], [2, 3], [1, 2], [4, 4]]},
        "expected": {"states": [[4, 2], [3, 2], [2, 4], [2, 4]]},
        "why": "Two pairs, then those pairs merge into size 4. The last operation is a self-union of the remaining vertex.",
    },
    {
        "name": "kruskal empty",
        "input": {"task": "kruskal", "n": 0, "edges": []},
        "expected": {"cost": 0, "edge_ids": [], "components": 0},
        "why": "An empty vertex set has an empty forest and zero components.",
    },
    {
        "name": "prim empty",
        "input": {"task": "prim", "n": 0, "edges": []},
        "expected": {"cost": 0, "edge_ids": [], "components": 0},
        "why": "Prim has no vertex at which to start a tree.",
    },
    {
        "name": "kruskal isolates loops parallel negative",
        "input": {
            "task": "kruskal",
            "n": 4,
            "edges": [[0, 0, -100], [0, 1, 5], [1, 0, -3], [0, 1, 4], [2, 2, -50]],
        },
        "expected": {"cost": -3, "edge_ids": [2], "components": 3},
        "why": "Self-loops on 0 and 2 are rejected. The parallel edges between 0 and 1 contribute only the cheapest, weight -3. Vertex 3 is isolated, so there are 3 components.",
    },
    {
        "name": "prim same negative graph",
        "input": {
            "task": "prim",
            "n": 4,
            "edges": [[0, 0, -100], [0, 1, 5], [1, 0, -3], [0, 1, 4], [2, 2, -50]],
        },
        "expected": {"cost": -3, "edge_ids": [2], "components": 3},
        "why": "The same undirected graph as the Kruskal case. Cost and component count must match; this graph has only one safe edge.",
    },
    {
        "name": "kruskal tie",
        "input": {"task": "kruskal", "n": 3, "edges": [[0, 1, 1], [1, 2, 1], [0, 2, 1]]},
        "expected": {"cost": 2, "edge_ids": [0, 1], "components": 1},
        "why": "Every edge has weight 1. Any two edges form an optimal tree of cost 2. The third edge would close the triangle.",
    },
    {
        "name": "prim tie",
        "input": {"task": "prim", "n": 3, "edges": [[0, 1, 1], [1, 2, 1], [0, 2, 1]]},
        "expected": {"cost": 2, "edge_ids": [0, 1], "components": 1},
        "why": "Prim starts at 0. The two edges of weight 1 are tied, and the heap orders them by edge id, so it takes 0-1 (id 0) and then 1-2 (id 1). Cost 2, one component. Kruskal happens to choose the same ids on this graph; a different optimal pair would also be accepted.",
    },
    {
        "name": "kruskal 64-bit",
        "input": {
            "task": "kruskal",
            "n": 4,
            "edges": [[0, 1, 1000000000], [1, 2, 1000000000], [2, 3, 1000000000]],
        },
        "expected": {"cost": 3000000000, "edge_ids": [0, 1, 2], "components": 1},
        "why": "3 * 10^9 = 3000000000, which is larger than 2^31 - 1. The total must stay a full integer.",
    },
    {
        "name": "prim 64-bit",
        "input": {
            "task": "prim",
            "n": 4,
            "edges": [[0, 1, 1000000000], [1, 2, 1000000000], [2, 3, 1000000000]],
        },
        "expected": {"cost": 3000000000, "edge_ids": [0, 1, 2], "components": 1},
        "why": "Same path as the Kruskal 64-bit case. Both methods must report the same sum.",
    },
    {
        "name": "scc empty",
        "input": {"task": "scc", "n": 0, "edges": []},
        "expected": {"component": [], "condensation": []},
        "why": "No vertices, so both arrays are empty.",
    },
    {
        "name": "scc isolates loops duplicates",
        "input": {"task": "scc", "n": 4, "edges": [[0, 0], [0, 1], [0, 1], [1, 0], [3, 3]]},
        "expected": {"component": [2, 2, 1, 0], "condensation": []},
        "why": "0 and 1 reach each other, so they share a label. Vertex 2 is isolated and vertex 3 has only a self-loop, so each is its own SCC. The numbers are the order of the second DFS, not a special canonical numbering. No edge leaves its SCC, so the condensation is empty.",
    },
    {
        "name": "scc condensation",
        "input": {"task": "scc", "n": 4, "edges": [[0, 1], [1, 0], [1, 2], [0, 2], [2, 3], [1, 2]]},
        "expected": {"component": [0, 0, 1, 2], "condensation": [[0, 1], [1, 2]]},
        "why": "{0,1} is an SCC. 1->2 and the duplicate 1->2 become one condensation arc. 2->3 becomes the second. 0->2 is the same pair of labels as 1->2.",
    },
    {
        "name": "topo empty",
        "input": {"task": "topo", "n": 0, "edges": []},
        "expected": {"acyclic": True, "order": []},
        "why": "The empty digraph has no cycle.",
    },
    {
        "name": "topo diamond",
        "input": {"task": "topo", "n": 4, "edges": [[0, 2], [1, 2], [2, 3], [0, 2]]},
        "expected": {"acyclic": True, "order": [1, 0, 2, 3]},
        "why": "Edges into the finished vertex 2 are not cycles. The duplicate 0->2 does not change the order. 0 and 1 are both before 2, and 3 is last.",
    },
    {
        "name": "topo self loop",
        "input": {"task": "topo", "n": 1, "edges": [[0, 0]]},
        "expected": {"acyclic": False, "order": []},
        "why": "A self-loop is a directed cycle. The order must be empty.",
    },
    {
        "name": "topo cycle elsewhere",
        "input": {"task": "topo", "n": 4, "edges": [[0, 1], [2, 3], [3, 2]]},
        "expected": {"acyclic": False, "order": []},
        "why": "The component {0,1} is acyclic, but {2,3} is a cycle. The whole request is cyclic.",
    },
    {
        "name": "dag published shape",
        "input": {"task": "dag", "n": 5, "source": 0, "edges": [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4]]},
        "expected": {"acyclic": True, "distance": [0, 3, -4, 0, None], "parent_edge": [-1, 0, 2, 3, -1]},
        "why": "0->1->2 costs 3 + -7 = -4, better than the direct edge of 8. 2->3 costs 4, so vertex 3 is at distance 0. Vertex 4 has no incoming path.",
    },
    {
        "name": "dag distance is minus one",
        "input": {"task": "dag", "n": 3, "source": 0, "edges": [[0, 1, -1]]},
        "expected": {"acyclic": True, "distance": [0, -1, None], "parent_edge": [-1, 0, -1]},
        "why": "Distance -1 is a real finite cost. Only vertex 2 is unreachable, so only its distance is null.",
    },
    {
        "name": "dag cycle not from source",
        "input": {"task": "dag", "n": 3, "source": 0, "edges": [[1, 2, 1], [2, 1, 1]]},
        "expected": {"acyclic": False, "distance": [], "parent_edge": []},
        "why": "Source 0 cannot reach the cycle, but the cycle is still in the graph. Both arrays must be empty.",
    },
    {
        "name": "dag self loop",
        "input": {"task": "dag", "n": 1, "source": 0, "edges": [[0, 0, -5]]},
        "expected": {"acyclic": False, "distance": [], "parent_edge": []},
        "why": "A self-loop makes the graph cyclic even when its weight is negative.",
    },
    {
        "name": "dag parallel tie",
        "input": {
            "task": "dag",
            "n": 3,
            "source": 0,
            "edges": [[0, 1, 5], [0, 1, 5], [0, 2, 9], [1, 2, 4], [0, 2, 9]],
        },
        "expected": {
            "acyclic": True,
            "distance": [0, 5, 9],
            "parent_edge": [-1, 0, 2],
        },
        "why": "Two edges of weight 5 tie for vertex 1. Vertex 2 can be reached by 0->2 weight 9 or by 0->1->2 weight 9. Both parents are optimal.",
    },
    {
        "name": "dag 64-bit",
        "input": {
            "task": "dag",
            "n": 4,
            "source": 0,
            "edges": [[0, 1, 1000000000], [1, 2, 1000000000], [2, 3, 1000000000]],
        },
        "expected": {
            "acyclic": True,
            "distance": [0, 1000000000, 2000000000, 3000000000],
            "parent_edge": [-1, 0, 1, 2],
        },
        "why": "The distances 2*10^9 and 3*10^9 do not fit in a signed 32-bit integer.",
    },
    {
        "name": "deep chain topo",
        "input": {
            "task": "topo",
            "n": 3000,
            "edges": [[i, i + 1] for i in range(2999)],
        },
        "expected": {"acyclic": True, "order": list(range(3000))},
        "why": "A directed chain has one topological order. Recursive DFS would use 3000 frames; the explicit stack does not.",
    },
]


def handle(request):
    task = request["task"]
    if task == "ping":
        return {"status": "ready"}
    return getattr(algorithms, task)(request)


def reaches(n, edges, source):
    adj = [[] for _ in range(n)]
    for row in edges:
        adj[row[0]].append(row[1])
    seen = [False] * n
    stack = [source]
    seen[source] = True
    while stack:
        vertex = stack.pop()
        for nxt in adj[vertex]:
            if not seen[nxt]:
                seen[nxt] = True
                stack.append(nxt)
    return seen


def brute_scc_labels(n, edges):
    reach = [reaches(n, edges, v) for v in range(n)]
    label = [-1] * n
    next_label = 0
    for v in range(n):
        if label[v] != -1:
            continue
        for u in range(n):
            if reach[v][u] and reach[u][v]:
                label[u] = next_label
        next_label += 1
    return label


def same_partition(left, right):
    forward = {}
    reverse = {}
    for a, b in zip(left, right):
        if forward.setdefault(a, b) != b or reverse.setdefault(b, a) != a:
            return False
    return True


def check_invariants(case, answer):
    request = case["input"]
    expected = case["expected"]
    task = request["task"]
    if task == "ping":
        return answer == expected, "ping mismatch"
    if task == "scc" and request["n"] <= 20:
        labels = brute_scc_labels(request["n"], request["edges"])
        if not same_partition(answer["component"], labels):
            return False, f"SCC partition {answer['component']} != brute {labels}"
    if task == "dag" and answer["acyclic"]:
        dist = answer["distance"]
        parents = answer["parent_edge"]
        source = request["source"]
        if dist[source] != 0 or parents[source] != -1:
            return False, "source distance/parent is wrong"
        seen = reaches(request["n"], request["edges"], source)
        for vertex, reachable in enumerate(seen):
            if reachable and dist[vertex] is None:
                return False, f"vertex {vertex} is reachable but distance is null"
            if not reachable and dist[vertex] is not None:
                return False, f"vertex {vertex} is unreachable but has a distance"
        for u, v, weight in request["edges"]:
            if dist[u] is not None and dist[v] is not None and dist[u] + weight < dist[v]:
                return False, f"edge {u}->{v} improves a supposed shortest path"
        route = algorithms.reconstruct_route(request["edges"], parents, source, source)
        if route != [source]:
            return False, "route to the source is not [source]"
    if not check(request, answer, expected):
        return False, f"contract failed\n expected={expected}\n actual={answer}"
    return True, "ok"


def route_demo():
    edges = [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4]]
    result = algorithms.dag({"task": "dag", "n": 5, "source": 0, "edges": edges})
    parents = result["parent_edge"]
    demos = {
        "reachable_3": algorithms.reconstruct_route(edges, parents, 0, 3),
        "reachable_3_weight": algorithms.route_weight(edges, parents, algorithms.reconstruct_route(edges, parents, 0, 3)),
        "reachable_3_edges": [parents[v] for v in algorithms.reconstruct_route(edges, parents, 0, 3)[1:]],
        "source": algorithms.reconstruct_route(edges, parents, 0, 0),
        "unreachable_4": algorithms.reconstruct_route(edges, parents, 0, 4),
    }
    tie_edges = [[0, 1, 5], [0, 1, 5], [0, 2, 9], [1, 2, 4], [0, 2, 9]]
    tie = algorithms.dag({"task": "dag", "n": 3, "source": 0, "edges": tie_edges})
    route = algorithms.reconstruct_route(tie_edges, tie["parent_edge"], 0, 2)
    demos["tie_route"] = route
    demos["tie_parent_edge"] = tie["parent_edge"]
    demos["tie_weight"] = algorithms.route_weight(tie_edges, tie["parent_edge"], route)
    demos["tie_distance"] = tie["distance"]
    return demos


def alternative_witness_demo():
    request = {"task": "kruskal", "n": 3, "edges": [[0, 1, 1], [1, 2, 1], [0, 2, 1]]}
    expected = {"cost": 2, "edge_ids": [0, 1], "components": 1}
    valid_a = {"cost": 2, "edge_ids": [0, 1], "components": 1}
    valid_b = {"cost": 2, "edge_ids": [1, 2], "components": 1}
    uses_cycle = {"cost": 3, "edge_ids": [0, 1, 2], "components": 1}
    wrong_cost = {"cost": 3, "edge_ids": [0, 2], "components": 1}
    self_loop_graph = {"task": "kruskal", "n": 2, "edges": [[0, 0, -5], [0, 1, 4]]}
    bad_loop = {"cost": -5, "edge_ids": [0], "components": 1}
    return {
        "accepts_first_tree": check(request, valid_a, expected),
        "accepts_other_tree": check(request, valid_b, expected),
        "rejects_cycle": not check(request, uses_cycle, expected),
        "rejects_wrong_cost": not check(request, wrong_cost, expected),
        "rejects_self_loop": not check(self_loop_graph, bad_loop, {"cost": 4, "edge_ids": [1], "components": 1}),
    }


def large_cases():
    results = []
    n = 100000
    edges = [[i, i + 1] for i in range(n - 1)]
    topo = algorithms.topo({"n": n, "edges": edges})
    results.append(("topo chain 100000", topo["acyclic"] is True and topo["order"] == list(range(n))))
    scc = algorithms.scc({"n": n, "edges": edges})
    results.append(("scc chain 100000", scc["component"] == list(range(n)) and len(scc["condensation"]) == n - 1))
    weighted = [[i, i + 1, -1000000000] for i in range(n - 1)]
    dag = algorithms.dag({"n": n, "source": 0, "edges": weighted})
    expected_last = -1000000000 * (n - 1)
    results.append((
        "dag chain 100000 negative",
        dag["acyclic"] is True and dag["distance"][0] == 0 and dag["distance"][-1] == expected_last
        and dag["parent_edge"][0] == -1 and dag["parent_edge"][-1] == n - 2,
    ))
    after = algorithms.dsu({"n": 1, "operations": [[0, 0]]})
    results.append(("state reset after large dag", after == {"states": [[1, 1]]}))
    return results

def main():
    failures = 0
    inputs = []
    expected_lines = []
    actual_lines = []
    for case in CASES:
        answer = handle(case["input"])
        ok, detail = check_invariants(case, answer)
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
            print(f"{status} {case['name']}: {detail}")
        else:
            print(f"{status} {case['name']}")
        inputs.append(line(case["input"]))
        expected_lines.append(line({"name": case["name"], "output": case["expected"], "why": case["why"]}))
        actual_lines.append(line({"name": case["name"], "output": answer}))

    tests = ROOT / "tests"
    (tests / "cases.jsonl").write_text("\n".join(inputs) + "\n", encoding="utf-8")
    (tests / "expected.jsonl").write_text("\n".join(expected_lines) + "\n", encoding="utf-8")
    (tests / "actual.jsonl").write_text("\n".join(actual_lines) + "\n", encoding="utf-8")

    demos = route_demo()
    print("ROUTE", json.dumps(demos))
    witnesses = alternative_witness_demo()
    print("WITNESS", json.dumps(witnesses))
    if not all(witnesses.values()):
        failures += 1
        print("FAIL witness demo")
    if demos["reachable_3"] != [0, 1, 2, 3] or demos["reachable_3_weight"] != 0:
        failures += 1
        print("FAIL route demo")
    if demos["source"] != [0] or demos["unreachable_4"] != []:
        failures += 1
        print("FAIL route endpoints")
    if demos["tie_weight"] != 9 or demos["tie_route"][0] != 0 or demos["tie_route"][-1] != 2:
        failures += 1
        print("FAIL tie route")

    print("Running large chains...")
    for name, ok in large_cases():
        print(("PASS " if ok else "FAIL ") + name)
        failures += not ok
    print(f"failures={failures}")
    return failures

if __name__ == "__main__":
    sys.exit(main())
