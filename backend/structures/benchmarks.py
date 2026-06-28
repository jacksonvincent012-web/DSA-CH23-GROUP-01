"""
PHASE 2 — DSA Structure 8: Benchmarks
Rubric requirement: Complexity analysis + benchmark for major operations

WHY BENCHMARKS?
  The project requires empirical verification of Big-O claims.
  This module times every DSA operation at N = 1K, 10K, and 100K
  and returns a timing matrix displayed in the admin UI.

  Timing is done with time.perf_counter() for nanosecond precision
  and repeated (REPETITIONS = 5) to smooth out noise.
"""

import os
import sys
import time
import random
import statistics

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from structures.stock_map import StockRecord, StockHashMap
from structures.ingestion_queue import IngestionQueue, Tick
from structures.alert_stack import AlertStack, Alert
from structures.top_k_heap import TopKHeap
from structures.sector_graph import SectorGraph
from structures.merge_sort import merge_sort
from structures.binary_search import binary_search, range_search
from structures.lru_cache import LRUCache

from datetime import datetime, timedelta

REPETITIONS = 5
SIZES = [1_000, 10_000, 100_000]


def _timed(name: str, fn, *args, **kwargs) -> float:
    """Run fn() REPETITIONS times, return median time in seconds."""
    times = []
    for _ in range(REPETITIONS):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return statistics.median(times)


# ------------------------------------------------------------------ #
# Per-structure benchmark suites                                      #
# ------------------------------------------------------------------ #

def _bench_hashmap(n: int) -> dict:
    """Benchmark StockHashMap.put and .get at size n."""
    hm = StockHashMap()
    # PUT — insert n records
    t_put = _timed("put", hm.put, "SYM0", StockRecord("SYM0", 100.0, 1000, "TECH"))
    for i in range(n):
        sym = f"SYM{i}"
        hm.put(sym, StockRecord(sym, random.uniform(10, 500), random.randint(100, 1_000_000), "TECH"))

    # GET — retrieve a random existing key
    target = f"SYM{random.randint(0, n-1)}"
    t_get = _timed("get", hm.get, target)

    return {"HashMap.put": t_put, "HashMap.get": t_get}


def _bench_queue(n: int) -> dict:
    """Benchmark IngestionQueue.enqueue and .dequeue at size n."""
    q = IngestionQueue()
    ticks = [Tick(f"SYM{i}", 100.0, 1000, datetime.now()) for i in range(n)]

    t_enq = _timed("enqueue batch", lambda: [q.enqueue(t) for t in ticks])

    t_deq = _timed("dequeue all", lambda: [q.dequeue() for _ in range(n)])

    return {"Queue.enqueue": t_enq, "Queue.dequeue": t_deq}


def _bench_stack(n: int) -> dict:
    """Benchmark AlertStack.push and .pop at size n (capped at 500 per run)."""
    count = min(n, 500)

    def _do_push():
        s = AlertStack()
        for _ in range(count):
            s.push(Alert("AAPL", 200, "above"))

    def _do_pop():
        s = AlertStack()
        for _ in range(count):
            s.push(Alert("AAPL", 200, "above"))
        for _ in range(count):
            s.pop()

    t_push = _timed("push", _do_push)
    t_pop = _timed("pop", _do_pop)
    return {"Stack.push": t_push, "Stack.pop": t_pop}


def _bench_heap(n: int) -> dict:
    """Benchmark TopKHeap.push at size n with K=10."""
    h = TopKHeap(k=10)
    t_push = _timed("push batch", lambda: [h.push(f"SYM{i}", random.random() * 1000) for i in range(n)])
    t_top = _timed("top_k", h.top_k)
    return {"Heap.push": t_push, "Heap.top_k": t_top}


def _bench_graph(n: int) -> dict:
    """Benchmark SectorGraph BFS/DFS with n nodes ~2n edges."""
    import sys
    sys.setrecursionlimit(max(sys.getrecursionlimit(), min(n, 2000) + 100))
    g = SectorGraph()
    for i in range(n):
        g.add_node(f"S{i}")
    for i in range(n - 1):
        g.add_edge(f"S{i}", f"S{i+1}")
        if i + 2 < n:
            g.add_edge(f"S{i}", f"S{i+2}")

    t_bfs = _timed("BFS", g.bfs, "S0")
    # DFS with iterative stack for large n to avoid recursion limit
    if n <= 2000:
        t_dfs = _timed("DFS", g.dfs, "S0")
    else:
        t_dfs = _timed("DFS", g.dfs_iterative, "S0")
    return {"Graph.BFS": t_bfs, "Graph.DFS": t_dfs}


def _bench_sort(n: int) -> dict:
    """Benchmark MergeSort at size n."""
    data = [random.random() * 1000 for _ in range(n)]
    t_sort = _timed("merge_sort", merge_sort, data)
    return {"MergeSort.sort": t_sort}


def _bench_search(n: int) -> dict:
    """Benchmark BinarySearch at size n."""
    data = sorted([random.random() * 1000 for _ in range(n)])
    target = data[n // 2]
    t_search = _timed("binary_search", binary_search, data, target)
    t_range = _timed("range_search", range_search, data, target - 1, target + 1)
    return {"BinarySearch.search": t_search, "BinarySearch.range": t_range}


def _bench_lru_cache(n: int) -> dict:
    """Benchmark LRUCache.get and .put at size n (capacity = n)."""
    c = LRUCache(capacity=n)
    # PUT n entries
    t_put = _timed("put batch", lambda: [c.put(f"K{i}", f"V{i}") for i in range(n)])

    # GET n entries (all hits after first)
    for i in range(n):
        c.put(f"K{i}", f"V{i}")
    t_get_hit = _timed("get (hit)", lambda: [c.get(f"K{i}") for i in range(n)])

    # GET n entries (all misses)
    t_get_miss = _timed("get (miss)", lambda: [c.get(f"NOT{i}") for i in range(n)])

    return {"LRUCache.put": t_put, "LRUCache.get_hit": t_get_hit, "LRUCache.get_miss": t_get_miss}


# ------------------------------------------------------------------ #
# Public entry point                                                  #
# ------------------------------------------------------------------ #

def run_all_benchmarks() -> dict:
    """
    Run all benchmarks at all sizes.
    Returns a dict:
        {
            "HashMap.put":  {"1K": ..., "10K": ..., "100K": ...},
            "HashMap.get":  {"1K": ..., "10K": ..., "100K": ...},
            ...
        }
    """
    results: dict[str, dict[str, float]] = {}

    for size in SIZES:
        size_label = f"{size//1000}K" if size >= 1000 else str(size)

        suites = [
            _bench_hashmap,
            _bench_queue,
            _bench_stack,
            _bench_heap,
            _bench_graph,
            _bench_sort,
            _bench_search,
            _bench_lru_cache,
        ]

        for suite_fn in suites:
            suite_results = suite_fn(size)
            for op_name, elapsed in suite_results.items():
                if op_name not in results:
                    results[op_name] = {}
                results[op_name][size_label] = round(elapsed, 6)

    return results


def format_benchmark_table(results: dict) -> str:
    """Pretty-print the benchmark matrix."""
    header = f"{'Operation':<30} {'1K':>12} {'10K':>12} {'100K':>12}"
    sep = "-" * len(header)
    lines = [header, sep]
    for op_name, timings in results.items():
        row = f"{op_name:<30}"
        for label in ["1K", "10K", "100K"]:
            val = timings.get(label, "-")
            row += f"{val:>12}"
        lines.append(row)
    return "\n".join(lines)
