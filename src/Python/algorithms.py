import heapq

class DSU:

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n
        self.largest = 1 if n > 0 else 0

    def find(self, x):
        parent = self.parent
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def union(self, a, b):
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        if self.size[a] > self.largest:
            self.largest = self.size[a]
        self.components -= 1
        return True


def dsu(request):
    forest = DSU(request["n"])
    states = []
    for u, v in request["operations"]:
        forest.union(u, v)
        states.append([forest.components, forest.largest])
    return {"states": states}


def kruskal(request):
    n = request["n"]
    edges = request["edges"]
    forest = DSU(n)
    ordered = [(weight, edge_id, u, v) for edge_id, (u, v, weight) in enumerate(edges)]
    ordered.sort()
    chosen = []
    cost = 0
    for weight, edge_id, u, v in ordered:
        if forest.union(u, v):
            chosen.append(edge_id)
            cost += weight
    return {"cost": cost, "edge_ids": chosen, "components": forest.components}


def prim(request):
    n = request["n"]
    edges = request["edges"]
    adj = [[] for _ in range(n)]
    for edge_id, (u, v, weight) in enumerate(edges):
        if u == v:
            continue
        adj[u].append((weight, edge_id, v))
        adj[v].append((weight, edge_id, u))

    visited = [False] * n
    chosen = []
    cost = 0
    components = 0
    for start in range(n):
        if visited[start]:
            continue
        components += 1
        visited[start] = True
        heap = list(adj[start])
        heapq.heapify(heap)
        while heap:
            weight, edge_id, vertex = heapq.heappop(heap)
            if visited[vertex]:
                continue
            visited[vertex] = True
            chosen.append(edge_id)
            cost += weight
            for item in adj[vertex]:
                if not visited[item[2]]:
                    heapq.heappush(heap, item)
    return {"cost": cost, "edge_ids": chosen, "components": components}


def _adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    return adj


def _dfs_finish(n, adj, detect_cycles):
    color = [0] * n
    finish = []
    for start in range(n):
        if color[start] != 0:
            continue
        color[start] = 1
        stack = [(start, 0)]
        while stack:
            vertex, index = stack[-1]
            if index < len(adj[vertex]):
                nxt = adj[vertex][index]
                stack[-1] = (vertex, index + 1)
                state = color[nxt]
                if state == 0:
                    color[nxt] = 1
                    stack.append((nxt, 0))
                elif state == 1 and detect_cycles:
                    return finish, True
            else:
                color[vertex] = 2
                finish.append(vertex)
                stack.pop()
    return finish, False


def scc(request):
    n = request["n"]
    edges = request["edges"]
    forward = _adjacency(n, edges)
    backward = [[] for _ in range(n)]
    for u, v in edges:
        backward[v].append(u)

    finish, _cycle = _dfs_finish(n, forward, detect_cycles=False)
    component = [-1] * n
    label = 0
    for start in reversed(finish):
        if component[start] != -1:
            continue
        component[start] = label
        stack = [start]
        while stack:
            vertex = stack.pop()
            for nxt in backward[vertex]:
                if component[nxt] == -1:
                    component[nxt] = label
                    stack.append(nxt)
        label += 1

    seen = set()
    condensation = []
    for u, v in edges:
        a = component[u]
        b = component[v]
        if a != b and (a, b) not in seen:
            seen.add((a, b))
            condensation.append([a, b])
    return {"component": component, "condensation": condensation}


def topo(request):
    n = request["n"]
    finish, cyclic = _dfs_finish(n, _adjacency(n, request["edges"]), detect_cycles=True)
    if cyclic:
        return {"acyclic": False, "order": []}
    finish.reverse()
    return {"acyclic": True, "order": finish}


def dag(request):
    n = request["n"]
    source = request["source"]
    edges = request["edges"]
    adj = [[] for _ in range(n)]
    weighted = [[] for _ in range(n)]
    for edge_id, (u, v, weight) in enumerate(edges):
        adj[u].append(v)
        weighted[u].append((v, weight, edge_id))

    finish, cyclic = _dfs_finish(n, adj, detect_cycles=True)
    if cyclic:
        return {"acyclic": False, "distance": [], "parent_edge": []}

    finish.reverse()
    distance = [None] * n
    parent_edge = [-1] * n
    distance[source] = 0
    for vertex in finish:
        base = distance[vertex]
        if base is None:
            continue
        for nxt, weight, edge_id in weighted[vertex]:
            candidate = base + weight
            if distance[nxt] is None or candidate < distance[nxt]:
                distance[nxt] = candidate
                parent_edge[nxt] = edge_id
    return {"acyclic": True, "distance": distance, "parent_edge": parent_edge}


def reconstruct_route(edges, parent_edge, source, target):
    if target == source:
        return [source]
    if target < 0 or target >= len(parent_edge) or parent_edge[target] < 0:
        return []

    path = []
    vertex = target
    seen = set()
    while vertex != source:
        if vertex in seen:
            return []
        seen.add(vertex)
        edge_id = parent_edge[vertex]
        if edge_id < 0 or edge_id >= len(edges):
            return []
        predecessor, head, _weight = edges[edge_id]
        if head != vertex:
            return []
        path.append(vertex)
        vertex = predecessor
    path.append(source)
    path.reverse()
    return path


def route_weight(edges, parent_edge, path):
    if len(path) <= 1:
        return 0
    total = 0
    for vertex in path[1:]:
        total += edges[parent_edge[vertex]][2]
    return total
