# Stock Query Server — Chapter 23 Five-Step System Design
**DSA-CH23-GROUP | Theme C — Stock Query Server (Variant C3: Alerts + Event Queue)**
**Method: Hemant Jain, Chapter 23 — System Design**

---

## Step 1: Use Cases Generation

We begin by identifying every actor and every operation the system must support.

### Actors
| Actor | Description |
|-------|-------------|
| **Viewer** | Read-only access — can browse stocks, view prices, watch benchmarks |
| **Analyst** | Viewer + can create and undo price alerts |
| **Admin** | Analyst + can run benchmarks, trigger tests, upsert stock records |
| **Simulator** | Internal background thread that generates live price ticks |

### Use Cases

| ID | Actor | Use Case | DSA Structure | Justification |
|----|-------|----------|---------------|---------------|
| UC1 | All | Store and retrieve a stock record by ticker symbol in O(1) | **Hash Map** | Symbol → StockRecord lookup must be constant-time regardless of how many stocks are tracked |
| UC2 | Simulator | Buffer incoming price ticks in arrival order (FIFO) before committing to the map | **Queue** | Ticks must be processed in the order received; deque gives O(1) enqueue and dequeue |
| UC3 | Analyst/Admin | Create a price threshold alert; undo the last-created alert | **Stack** | Alerts are managed LIFO — the most recently pushed alert is the first to be undone; undo is O(1) |
| UC4 | Viewer/All | Retrieve the top-K stocks ranked by volume or 7-day gain | **Min-Heap** | Maintaining top-K with a size-bounded min-heap costs O(log K) per push, far cheaper than sorting all N stocks per request |
| UC5 | Viewer/All | Explore which sectors are correlated (BFS) or trace dependency chains (DFS) | **Graph** | Sector co-movement is naturally modelled as a directed adjacency list; BFS gives breadth-first sector proximity, DFS gives full dependency chains |
| UC6 | Viewer/All | Sort a stock's 90-day price history for display and range queries | **Merge Sort** | O(n log n) stable sort; required by the rubric; used before binary search |
| UC7 | Viewer/All | Search for the closest price or a price range in sorted history | **Binary Search** | O(log n) search on the sorted price array; used in StockDetail and the `/search` endpoint |
| UC8 | All | Register, log in, refresh tokens, log out | **JWT + RBAC** | Stateless auth scales horizontally; role claims embedded in token payload |
| UC9 | Admin | Measure empirical Big-O timings for all DSA operations at N=1K/10K/100K | **Benchmarks** | Required by rubric; results feed the complexity analysis section |
| UC10 | Simulator | Seed 24 stocks with 90-day random-walk history on startup | Internal init | Ensures the system has data without external dependencies |

---

## Step 2: Constraints and Analysis

We derive hard numbers for every constraint before writing code.

### Scale Targets

| Constraint | Value | Derivation |
|------------|-------|------------|
| Stocks tracked | N = 10,000 max | Covers all major global exchanges; HashMap load factor stays below 0.75 |
| Price ticks buffered | M = 100,000 max | Queue drains every 2 s; at 24 stocks × 30 ticks/s worst-case we see 720 ticks/s → 1,440 queued per cycle |
| Alerts in stack | A = 1,000 max | Analyst/Admin bounded; enforced by server-side guard |
| Top-K heap size | K ≤ 100 | O(log K) ≈ 7 comparisons at K=100; negligible cost |
| Graph nodes (sectors) | V = 50 | Realistic sector count; adjacency list stays small |
| Graph edges | E = 200 | ~4 edges per sector on average |
| Sort input size | n = 100,000 | 90-day history × up to 1,111 intra-day ticks |
| JWT expiry | 3,600 s (1 h) | Standard web app TTL; refresh token 7 days |
| Server memory | < 512 MB | All structures in-memory; no external DB in Phase 1 |
| Target latency | p99 < 200 ms | REST API over LAN; all operations are sub-millisecond in isolation |

### Complexity Targets

| Operation | Structure | Expected O-class | Worst-case at N=100K |
|-----------|-----------|-----------------|---------------------|
| Symbol lookup | StockHashMap | O(1) avg | ~0.003 ms |
| Tick enqueue | IngestionQueue | O(1) | ~0.002 ms |
| Alert push/pop | AlertStack | O(1) | ~0.002 ms |
| Top-K push | TopKHeap | O(log K) | ~0.005 ms |
| BFS traversal | SectorGraph | O(V+E) | ~1.2 ms at V=100K |
| Merge sort | MergeSort | O(n log n) | ~170 ms at n=100K |
| Binary search | BinarySearch | O(log n) | ~0.003 ms |

---

## Step 3: Basic Design

### Component Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  React/TypeScript (Vite)   │  Vanilla HTML/JS  │  Postman Suite │
└──────────────┬──────────────────────────────────┬───────────────┘
               │  HTTP/HTTPS + JWT Bearer          │
┌──────────────▼──────────────────────────────────▼───────────────┐
│                     API & AUTH LAYER                            │
│  Flask REST (server.py)   JWT + RBAC (auth.py)                  │
│  Background Simulator (simulator.py)                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │  Python imports
┌──────────────────────────────▼──────────────────────────────────┐
│                     CORE DSA ENGINE                             │
│  StockHashMap  IngestionQueue  AlertStack  TopKHeap             │
│  SectorGraph   MergeSort       BinarySearch   Benchmarks        │
└─────────────────────────────────────────────────────────────────┘
```

### API Surface (all 15 endpoints)

| # | Method | Endpoint | Auth | DSA Used | Purpose |
|---|--------|----------|------|----------|---------|
| 1 | GET | `/api/health` | None | — | System health check |
| 2 | GET | `/api/stocks` | JWT | HashMapallrecords | List all stocks |
| 3 | PUT | `/api/stocks` | JWT+admin | HashMap.put/update | Upsert stock record |
| 4 | GET | `/api/stocks/<sym>` | JWT | HashMap.get | Get stock + 7-day metrics |
| 5 | GET | `/api/stocks/<sym>/history` | JWT | MergeSort | Price history (sorted) |
| 6 | GET | `/api/stocks/sorted` | JWT | MergeSort | All stocks sorted by price |
| 7 | POST | `/api/stocks/search` | JWT | BinarySearch | Search by price range |
| 8 | GET | `/api/stocks/top` | JWT | TopKHeap | Top-K by volume or gain |
| 9 | GET | `/api/stocks/sector/<s>/friends` | JWT | SectorGraph BFS | Sector BFS traversal |
| 10 | GET | `/api/stocks/sector/<s>/friends/DFS` | JWT | SectorGraph DFS | Sector DFS traversal |
| 11 | GET | `/api/alerts` | JWT | AlertStack | List all alerts |
| 12 | POST | `/api/alerts` | JWT+analyst | AlertStack.push | Create alert |
| 13 | DELETE | `/api/alerts/undo` | JWT+analyst | AlertStack.pop+undo | Undo last alert |
| 14 | GET | `/api/benchmarks` | JWT+admin | All structures | Run timing benchmarks |
| 15 | GET | `/api/cache/stats` | JWT | Counter | Cache hit/miss stats |

### Auth endpoints (blueprint)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login → JWT pair |
| GET | `/api/auth/me` | Current user profile |
| POST | `/api/auth/refresh` | Rotate access token |
| POST | `/api/auth/logout` | Invalidate refresh token |

### Data Flow — Write Path
```
Client PUT /api/stocks
  → JWT check
  → HashMap.put(symbol, StockRecord)   O(1)
  → heap.push(symbol, volume)          O(log K)
  → return 201
```

### Data Flow — Tick Path (Simulator)
```
Simulator thread (every 2 s)
  → pick random symbol
  → compute ±2% price change
  → Queue.enqueue(Tick)                O(1)
  → Queue.drain()                      O(n)
  → for each tick:
      HashMap.update(symbol, price)    O(1)
      record.price_history.append()   O(1)
      Heap.push(symbol, volume)        O(log K)
      check AlertStack thresholds      O(A)
```

### Data Flow — Search Path
```
Client POST /api/stocks/search { low, high }
  → collect all prices from HashMap    O(N)
  → MergeSort(prices)                  O(N log N)
  → BinarySearch(sorted, low)          O(log N)
  → BinarySearch(sorted, high)         O(log N)
  → return stocks whose current price ∈ [low, high]
```

---

## Step 4: Bottlenecks

We identify the top bottlenecks found during design and describe mitigations.

| # | Bottleneck | Root Cause | Mitigation Applied |
|---|-----------|------------|-------------------|
| B1 | Tick fan-out at scale | Draining the queue and updating the hash map for every tick is O(N ticks); at 24 stocks × high frequency this becomes CPU-heavy | Drain is batched per 2-second cycle, not per tick; deque drain is O(n) one-shot |
| B2 | BFS on large graphs | Naïve `list.pop(0)` for BFS queue is O(n) per dequeue, making BFS O(V²+E) | Use `collections.deque` with `popleft()` for true O(1) dequeue → O(V+E) BFS |
| B3 | Top-K rebuild | Rebuilding the heap from all N stocks on every `/top` request is O(N log K) | Heap is maintained incrementally; each tick pushes O(log K); no full rebuild at read time |
| B4 | Sort on every history request | MergeSort is O(n log n); running it on every `/history` request wastes CPU | Sort is lazy — only triggered when client requests `/history`; raw history stored unsorted |
| B5 | Cold-start data loss | All state is in-memory; server restart wipes stocks, users, alerts | Simulator re-seeds 24 stocks with 90-day history on every startup; pre-seeded demo users always present |
| B6 | Concurrent refresh token storm | Multiple 401s can trigger parallel refresh requests | `apiFetch` client-side queue serialises concurrent refresh calls |
| B7 | Serverless cold start | Vercel Python function must import 7 DSA modules per cold start | Modules are lightweight pure Python; import time < 200 ms; acceptable for demo |

---

## Step 5: Scalability

We iterate on bottlenecks until the design is acceptable, then define the phased growth path.

### Iteration — Bottleneck Resolution

After applying the mitigations in Step 4:
- BFS is now O(V+E) ✅
- Top-K reads are O(K log K) (extract only, no rebuild) ✅
- Tick ingestion is bounded O(batch size) per cycle ✅
- Sort is deferred and lazy ✅

The remaining fundamental constraint is **in-memory only** — acceptable for Phase 1 (demo/educational) but not for production.

### Phase Growth Path

| Phase | Description | What Changes |
|-------|-------------|--------------|
| **Phase 1 (Now)** | In-memory DSA engine, simulated data, JWT auth, React + vanilla frontend, 15-test Postman suite, 37 pytest cases | This implementation |
| **Phase 2** | Persistence layer | Replace in-memory `_users` dict with SQLite/PostgreSQL; stock records survive restart; alert history persisted |
| **Phase 3** | Real market data | Swap simulator for Yahoo Finance / Alpha Vantage API calls; background thread pulls live OHLCV every minute |
| **Phase 4** | Production hardening | Redis caching for hot stock lookups; rate limiting per IP/user; Docker + CI/CD pipeline; horizontal scaling with sticky sessions or shared Redis |

### Throughput Estimate at Phase 1

```
N = 10,000 stocks
K = 10 top-K
1 analyst creating 100 alerts/day

Read  /api/stocks/<sym>  : O(1)   → limited by network, not code
Read  /api/stocks/top    : O(K log K) ≈ 33 comparisons at K=10  → negligible
Write /api/alerts        : O(1)   → bounded by alert stack size A=1000
BFS   /api/.../friends   : O(V+E) → ~50 nodes, ~200 edges → <1 ms

Bottleneck: MergeSort on /api/stocks/sorted at N=10K
  → 10,000 × 13 ≈ 130,000 comparisons ≈ 1–5 ms per request
  → Acceptable for educational demo; cache result for production
```

**Verdict:** Phase 1 design is scalable to the educational demo target of 1,000 concurrent users given the in-memory constraint. Phase 2 persistence removes the restart data-loss issue. Phase 4 adds the caching layer needed for production traffic.
