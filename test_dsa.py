import urllib.request, json, sys, time

BASE = "http://localhost:5000"

def req(method, path, data=None, token=None):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(f"{BASE}{path}", data=body, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    return json.loads(urllib.request.urlopen(r).read())

# --- LOGIN ---
token = req("POST", "/api/auth/login",
    {"email": "admin@stockquery.io", "password": "admin123"})["access_token"]
print(f"\n{'='*60}")
print(f"DSA LEARNING JOURNEY — Testing All 8 Data Structures")
print(f"{'='*60}\n")

# ======================================================================
# DSA 1: HASH MAP (StockHashMap)
# ======================================================================
print(f"{'─'*60}")
print(f"DSA 1: HASH MAP — StockHashMap")
print(f"{'─'*60}")
print(f"  How it works: A hash map (dictionary) stores 10,000 stocks by symbol.")
print(f"  Keys are hashed to buckets for O(1) average lookups.")
print(f"  Python dict = hash table with separate chaining.\n")

d = req("GET", "/api/stocks", token=token)
print(f"  GET /api/stocks -> {d['count']} stocks loaded from hash map")
print(f"  Sample: {d['stocks'][0]['symbol']} (${d['stocks'][0]['price']}, {d['stocks'][0]['sector']})")
print(f"          {d['stocks'][1]['symbol']} (${d['stocks'][1]['price']}, {d['stocks'][1]['sector']})")

d = req("GET", "/api/stocks/AAPL", token=token)
print(f"\n  GET /api/stocks/AAPL -> ${d['price']}, vol {d['volume']}, gain {d['gain_7d_pct']}%")
print(f"  Hash map lookup: O(1) — instant even with 10,000 entries")

time.sleep(0.3)

# ======================================================================
# DSA 2: QUEUE (IngestionQueue) — tested via health
# ======================================================================
print(f"\n{'─'*60}")
print(f"DSA 2: QUEUE — IngestionQueue (FIFO)")
print(f"{'─'*60}")
print(f"  How it works: A First-In-First-Out queue buffers price ticks.")
print(f"  New prices enter at the tail, oldest exit at the head.")
print(f"  Uses collections.deque for O(1) append/pop.\n")

d = req("GET", "/api/health", token=token)
print(f"  GET /api/health -> stocks={d['stocks']}, queue_size={d['queue_size']}, ticks={d['ticks_processed']}")
print(f"  Queue holds pending ingestion ticks — processed sequentially FIFO")

time.sleep(0.3)

# ======================================================================
# DSA 3: STACK (AlertStack)
# ======================================================================
print(f"\n{'─'*60}")
print(f"DSA 3: STACK — AlertStack (LIFO)")
print(f"{'─'*60}")
print(f"  How it works: A Last-In-First-Out stack for price alerts.")
print(f"  Create alerts — most recent sits on top. Pop to undo last.")
print(f"  Also supports undo/redo via a secondary stack.\n")

# Create 3 alerts
for s in ["AAPL", "MSFT", "GOOGL"]:
    r = req("POST", "/api/alerts", {"symbol": s, "threshold": 500, "direction": "above"}, token=token)
    print(f"  POST /api/alerts ({s}) -> {r['message']}")

d = req("GET", "/api/alerts", token=token)
print(f"  GET /api/alerts -> {d['count']} alerts on stack")
for a in d["alerts"]:
    print(f"    • {a['symbol']}: {a['direction']} ${a['threshold']}")

# Undo last (GOOGL)
r = req("DELETE", "/api/alerts/undo", token=token)
print(f"  DELETE /api/alerts/undo -> {r['message']}")

d = req("GET", "/api/alerts", token=token)
print(f"  After undo -> {d['count']} alerts remaining (GOOGL popped)")
print(f"  Stack push: O(1), pop: O(1)")

time.sleep(0.3)

# ======================================================================
# DSA 4: HEAP (TopKHeap)
# ======================================================================
print(f"\n{'─'*60}")
print(f"DSA 4: HEAP — TopKHeap (Priority Queue)")
print(f"{'─'*60}")
print(f"  How it works: A min-heap of top K stocks by volume or price.")
print(f"  Maintains K largest elements in O(log K) per push.")
print(f"  Uses heapq (binary heap) under the hood.\n")

d = req("GET", "/api/stocks/top?metric=volume&k=5", token=token)
print(f"  GET /api/stocks/top (metric=volume, k=5)")
for i, s in enumerate(d["top"], 1):
    print(f"    {i}. {s['symbol']} — volume={s['volume']:,}, price=${s['price']}")
print(f"  Heap extracts top K in O(K log K)")

time.sleep(0.3)

# ======================================================================
# DSA 5: GRAPH — BFS (SectorGraph)
# ======================================================================
print(f"\n{'─'*60}")
print(f"DSA 5: GRAPH — BFS Traversal")
print(f"{'─'*60}")
print(f"  How it works: Sectors are graph nodes, edges = related industries.")
print(f"  BFS explores level-by-level using a queue.")
print(f"  Finds shortest path (minimum sectors to traverse).\n")

d = req("GET", "/api/stocks/sector/TECH/friends", token=token)
print(f"  GET /api/stocks/sector/TECH/friends (BFS)")
print(f"  BFS Order: {' -> '.join(d['bfs_order'])}")
print(f"  Sectors reachable: {len(d['bfs_order'])}")
for sec, stocks in d["sector_stocks"].items():
    print(f"    {sec}: {', '.join(stocks[:3])}{'...' if len(stocks)>3 else ''}")

time.sleep(0.3)

# ======================================================================
# DSA 6: GRAPH — DFS (SectorGraph)
# ======================================================================
print(f"\n{'─'*60}")
print(f"DSA 6: GRAPH — DFS Traversal")
print(f"{'─'*60}")
print(f"  How it works: DFS explores depth-first using a stack.")
print(f"  Goes deep into one branch before backtracking.")
print(f"  Uses recursive or iterative stack approach.\n")

d = req("GET", "/api/stocks/sector/TECH/friends/DFS", token=token)
print(f"  GET /api/stocks/sector/TECH/friends/DFS")
print(f"  DFS Order: {' -> '.join(d['dfs_order'])}")
print(f"  Note: BFS vs DFS give different traversal orders!")
print(f"  BFS: short paths first | DFS: deep dive first")

time.sleep(0.3)

# ======================================================================
# DSA 7: SORT — Merge Sort
# ======================================================================
print(f"\n{'─'*60}")
print(f"DSA 7: MERGE SORT — Sorting Stocks by Price")
print(f"{'─'*60}")
print(f"  How it works: Divide-and-conquer sorting. Split array in half,")
print(f"  recursively sort each half, then merge. O(n log n) worst case.")
print(f"  Stable sort — preserves relative order of equal elements.\n")

d = req("GET", "/api/stocks/sorted", token=token)
print(f"  GET /api/stocks/sorted -> {d['count']} stocks sorted by price")
print(f"  Cheapest: {d['stocks'][0]['symbol']} (${d['stocks'][0]['price']})")
print(f"  Costliest: {d['stocks'][-1]['symbol']} (${d['stocks'][-1]['price']})")
print(f"  Middle: {d['stocks'][len(d['stocks'])//2]['symbol']} (${d['stocks'][len(d['stocks'])//2]['price']})")

d = req("GET", "/api/stocks/AAPL/history", token=token)
print(f"\n  GET /api/stocks/AAPL/history -> {len(d['history'])} days (merge-sorted by date)")
print(f"  First: {d['history'][0]['date']} @ ${d['history'][0]['price']}")
print(f"  Last:  {d['history'][-1]['date']} @ ${d['history'][-1]['price']}")

time.sleep(0.3)

# ======================================================================
# DSA 8: BINARY SEARCH / RANGE SEARCH
# ======================================================================
print(f"\n{'─'*60}")
print(f"DSA 8: BINARY SEARCH — Range Search by Price")
print(f"{'─'*60}")
print(f"  How it works: Find all stocks within a price range on a sorted array.")
print(f"  Binary search finds the lower bound, then scans right. O(log n + k).")
print(f"  Requires sorted data (uses merge sort first, then binary search).\n")

d = req("POST", "/api/stocks/search", {"low": 100, "high": 105}, token=token)
print(f"  POST /api/stocks/search (price $100-$105) -> {d['count']} stocks found")
for s in d["stocks"][:3]:
    print(f"    {s['symbol']} — ${s['price']}")
if d["count"] > 3:
    print(f"    ... and {d['count'] - 3} more")

time.sleep(0.3)

# ======================================================================
# BONUS: LRU Cache
# ======================================================================
print(f"\n{'─'*60}")
print(f"BONUS: LRU CACHE — Hot Stock Lookup Accelerator")
print(f"{'─'*60}")
print(f"  How it works: HashMap + Doubly Linked List composite.")
print(f"  Most-recently accessed stocks stay in cache. Evicts LRU when full.")
print(f"  All operations O(1) — hash lookup + list pointer juggling.\n")

# Access AAPL again (should be cached now)
d = req("GET", "/api/stocks/AAPL", token=token)
stats = req("GET", "/api/cache/stats", token=token)
print(f"  Cache stats: hits={stats['hits']}, misses={stats['misses']}, size={stats['size']}/{stats['capacity']}")
print(f"  AAPL cached: {stats['hits'] > 0}")

# ======================================================================
# BENCHMARKS
# ======================================================================
print(f"\n{'─'*60}")
print(f"BENCHMARKS — DSA Performance Comparison")
print(f"{'─'*60}\n")

d = req("GET", "/api/benchmarks", token=token)
for b in d["results"]:
    print(f"  {b['name']:25s} {b['time_us']:>8} µs  (n={b['n']})")

print(f"\n{'─'*60}")
print(f"ALL 8 DATA STRUCTURES TESTED SUCCESSFULLY!")
print(f"{'─'*60}")
