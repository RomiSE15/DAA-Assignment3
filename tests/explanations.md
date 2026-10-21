# Test explanations

Run `python tests/check_cases.py` from the repository root. It writes `cases.jsonl`, `expected.jsonl` and `actual.jsonl` and checks them. Answers that are not unique (another optimal forest, another SCC numbering, another topological order, another parent edge) are accepted when they are valid. The chain of 100000 vertices is generated in the script, not stored

1. **ping.** The adapter returns `{"status":"ready"}`
2. **dsu, empty.** `n = 0`, no operations, so `states = []`
3. **dsu, self and repeated unions.** `n = 3`, operations `[1,1]`, `[0,2]`, `[2,0]`, `[0,2]`. Result `[3,1]`, `[2,2]`, `[2,2]`, `[2,2]`: only the first real merge changes the state
4. **dsu, growing largest.** `n = 5`, operations `[0,1]`, `[2,3]`, `[1,2]`, `[4,4]`. Result `[4,2]`, `[3,2]`, `[2,4]`, `[2,4]`
5. **kruskal and prim, empty.** Cost 0, no ids, 0 components
6. **kruskal and prim, loops, parallel edges, negative weight.** `n = 4`, edges `[0,0,-100]`, `[0,1,5]`, `[1,0,-3]`, `[0,1,4]`, `[2,2,-50]`. Loops are never used and only the edge of weight `-3` (id 2) is needed. Cost `-3`, ids `[2]`, 3 components
7. **tie.** Triangle with three edges of weight 1. Any two edges give cost 2. Ids `[0,1]` and `[1,2]` are accepted; `[0,1,2]` (a cycle), a wrong cost and a self-loop as a tree edge are rejected
8. **sum above 32 bits.** A path of three edges of weight `10^9`. Cost `3000000000`, ids `[0,1,2]`
9. **scc, empty.** Both arrays are empty
10. **scc, isolate, self-loop, duplicate.** Edges `[0,0]`, `[0,1]`, `[0,1]`, `[1,0]`, `[3,3]`. Vertices 0 and 1 are one SCC, 2 is alone, 3 is alone. The condensation is empty
11. **scc, condensation.** Edges `[0,1]`, `[1,0]`, `[1,2]`, `[0,2]`, `[2,3]`, `[1,2]`. The SCCs are `{0,1}`, `{2}`, `{3}`. The condensation has two pairs; duplicates are stored once
12. **topo, empty.** Acyclic, empty order
13. **topo, diamond.** Edges `[0,2]`, `[1,2]`, `[2,3]` and a duplicate `[0,2]`. One valid order is `[1,0,2,3]`. An edge into a finished vertex is not a cycle
14. **topo, self-loop.** `n = 1`, edge `[0,0]`. Cyclic, order `[]`
15. **topo, cycle in another component.** Edges `[0,1]`, `[2,3]`, `[3,2]`. The whole graph is cyclic
16. **dag, published example.** Edges `[0,1,3]`, `[0,2,8]`, `[1,2,-7]`, `[2,3,4]`, source 0. Distances `[0,3,-4,0,null]`. Route helper: target 3 gives `[0,1,2,3]` with weight 0, target 0 gives `[0]`, target 4 gives `[]`
17. **dag, distance -1.** Edge `[0,1,-1]`. Distances `[0,-1,null]`: `-1` stays a number, only vertex 2 is null
18. **dag, cycle not reachable from the source.** Edges `[1,2,1]`, `[2,1,1]`, source 0. Cyclic, both arrays empty
19. **dag, self-loop.** Edge `[0,0,-5]`. Cyclic
20. **dag, parallel tie.** Edges `[0,1,5]`, `[0,1,5]`, `[0,2,9]`, `[1,2,4]`, `[0,2,9]`. Distances `[0,5,9]`, parents `[-1,0,2]`. The routes `[0,2]` and `[0,1,2]` both have weight 9
21. **dag, sum above 32 bits.** Three edges of weight `10^9`. Distances up to `3000000000`
22. **deep chain, 3000.** Edges `i -> i+1`. The only topological order is `0..2999`
23. **deep chain, 100000 (generated).** Topological order, SCC labels and DAG distance (last distance `-99999000000000`). Afterwards a one-vertex DSU request returns `[[1,1]]`, which shows that no state was left behind