# Own tests

Run from the repository root:

```sh
python tests/check_cases.py
python tests/benchmark.py
python tools/run.py --input tests/cases.jsonl
```

Files:

- `cases.jsonl`: requests, including a chain of 3000 vertices
- `expected.jsonl`: justified answers
- `actual.jsonl`: answers from `src/Python/algorithms.py`
- `explanations.md`: why each expected answer is right
- `check_cases.py`: compares answers by meaning, calls the route helper, tests chains of 100000 vertices
- `benchmark.py`: Kruskal and Prim timings on three graphs
- `benchmark_results.json`: recorded timings

`tools/run.py --input` only prints answers. The comparison is done in `check_cases.py`
