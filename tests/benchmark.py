import json
import platform
import random
import statistics
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "Python"))

from algorithms import kruskal, prim

SIZES = (
    (2000, 8000, 20261021),
    (20000, 80000, 20261022),
    (100000, 250000, 20261023),
)

def make_edges(n, m, seed):
    rng = random.Random(seed)
    edges = []
    for _ in range(m):
        u = rng.randrange(n)
        v = rng.randrange(n - 1)
        if v >= u:
            v += 1
        edges.append([u, v, rng.randint(-1000, 1000)])
    return edges

def time_call(function, request, runs=3):
    function(request)  # warm-up
    samples = []
    for _ in range(runs):
        start = time.perf_counter()
        result = function(request)
        samples.append(time.perf_counter() - start)
    return result, samples


def main():
    rows = []
    for n, m, seed in SIZES:
        edges = make_edges(n, m, seed)
        request_k = {"n": n, "edges": edges}
        request_p = {"n": n, "edges": edges}
        kruskal_result, kruskal_times = time_call(kruskal, request_k)
        prim_result, prim_times = time_call(prim, request_p)
        if kruskal_result["cost"] != prim_result["cost"] or kruskal_result["components"] != prim_result["components"]:
            raise SystemExit(f"cost mismatch at n={n}")
        if len(kruskal_result["edge_ids"]) != n - kruskal_result["components"]:
            raise SystemExit(f"forest size mismatch at n={n}")
        rows.append({
            "n": n,
            "m": m,
            "seed": seed,
            "weight_range": [-1000, 1000],
            "cost": kruskal_result["cost"],
            "components": kruskal_result["components"],
            "kruskal_seconds": kruskal_times,
            "kruskal_median": statistics.median(kruskal_times),
            "prim_seconds": prim_times,
            "prim_median": statistics.median(prim_times),
        })
        print(
            f"n={n} m={m} cost={kruskal_result['cost']} components={kruskal_result['components']} "
            f"kruskal_median={statistics.median(kruskal_times):.6f} "
            f"prim_median={statistics.median(prim_times):.6f}"
        )
    cpu = "unknown"
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": cpu,
        "timer": "time.perf_counter",
        "runs": 3,
        "warmup": 1,
        "timed": "algorithm body only, including adjacency-list and heap construction",
        "not_timed": "JSON parsing, printing, and generation of the edge list",
        "rows": rows,
    }
    out = ROOT / "tests" / "benchmark_results.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
