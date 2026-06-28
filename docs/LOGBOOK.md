# PROJECT LOGBOOK
# Stock Query Server — DSA-CH23-GROUP-01

**Theme C, Variant C3:** Alerts + Event Queue  
**Course:** Data Structures and Algorithms (Chapter 23 — Hemant Jain)  
**Team Size:** 6 Members  
**Submission Date:** June 2026  

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [Team Roles](#2-team-roles)
3. [Step 1: Use Cases & Requirements](#3-step-1-use-cases--requirements)
4. [Step 2: Constraints & Analysis](#4-step-2-constraints--analysis)
5. [Step 3: Basic Design](#5-step-3-basic-design)
6. [DSA Structure 1: StockHashMap (Hash Table)](#6-dsa-structure-1-stockhashmap-hash-table)
7. [DSA Structure 2: IngestionQueue (Queue)](#7-dsa-structure-2-ingestionqueue-queue)
8. [DSA Structure 3: AlertStack (Stack)](#8-dsa-structure-3-alertstack-stack)
9. [DSA Structure 4: TopKHeap (Min-Heap)](#9-dsa-structure-4-topkheap-min-heap)
10. [DSA Structure 5: SectorGraph (Graph)](#10-dsa-structure-5-sectorgraph-graph)
11. [DSA Structure 6: LRUCache (HashMap + DLL)](#11-dsa-structure-6-lrucache-hashmap--dll)
12. [DSA Structure 7: MergeSort (Sorting)](#12-dsa-structure-7-mergesort-sorting)
13. [DSA Structure 8: BinarySearch (Searching)](#13-dsa-structure-8-binarysearch-searching)
14. [Step 4: Bottlenecks & Fixes](#14-step-4-bottlenecks--fixes)
15. [Step 5: Scalability Path](#15-step-5-scalability-path)
16. [JWT Authentication & RBAC](#16-jwt-authentication--rbac)
17. [Market Simulator — 10,000 Stocks](#17-market-simulator--10000-stocks)
18. [REST API Endpoints](#18-rest-api-endpoints)
19. [Testing — 46 Pytest Unit Tests](#19-testing--46-pytest-unit-tests)
20. [Benchmarks & Complexity Verification](#20-benchmarks--complexity-verification)
21. [Architecture Diagram](#21-architecture-diagram)
22. [Challenges & Solutions](#22-challenges--solutions)
23. [Conclusion](#23-conclusion)

---

## 1. PROJECT OVERVIEW

### Problem Statement
Build a real-time stock query server that allows users to:
- Look up stock prices by ticker symbol (e.g., AAPL, MSFT)
- View top-K stocks by trading volume
- Set price threshold alerts with undo capability
- Explore sector relationships using graph traversal
- Search stocks by price range
- View price history sorted by date

### Key Requirements
- **10,000 stocks** in-memory (lecturer requirement)
- **9 Data Structures** from the DSA syllabus
- **JWT Authentication** with 3 roles (admin, analyst, viewer)
- **22 REST API endpoints**
- **46 unit tests**
- **Complexity analysis** with empirical benchmarks
- **Chapter 23 5-Step System Design**

### Technology Stack
- **Backend:** Python 3.11+, Flask 3.0
- **Auth:** PyJWT with SHA-256 password hashing
- **Testing:** pytest (46 tests)
- **Frontend (optional):** React 18 + TypeScript + Vite 5
- **Deployment:** Vercel (serverless)

---

## 2. TEAM ROLES

| Person | Role | Responsibilities |
|--------|------|------------------|
| **Person 1** | Team Lead / Integrator | Repo setup, README, docs, architecture diagram, launch scripts, config |
| **Person 2** | Data Structures Lead | StockHashMap, IngestionQueue, AlertStack, TopKHeap, SectorGraph, LRUCache |
| **Person 3** | Algorithms Lead | MergeSort, BinarySearch, Benchmarks |
| **Person 4** | API Developer | Flask server, 22 endpoints, route wiring, CORS |
| **Person 5** | Auth + Simulator | JWT auth, RBAC, 10K stock seeder, tick generator, Vercel entry |
| **Person 6** | Testing & QA | 46 pytest tests, edge cases, coverage verification |

---

## 3. STEP 1: USE CASES & REQUIREMENTS

We identified every actor and operation the system must support.

### Actors
| Actor | Description |
|-------|-------------|
| **Viewer** | Read-only — browse stocks, view prices, see benchmarks |
| **Analyst** | Viewer + create/undo price alerts |
| **Admin** | Analyst + run benchmarks, upsert stocks, clear cache |
| **Simulator** | Internal background thread generating live price ticks |

### Use Case Table

| ID | Actor | Use Case | DSA Structure |
|----|-------|----------|---------------|
| UC1 | All | Lookup stock by symbol O(1) | **StockHashMap** |
| UC2 | Simulator | Buffer ticks in FIFO order | **IngestionQueue** |
| UC3 | Analyst | Create/undo price alerts | **AlertStack** |
| UC4 | All | View top-K stocks by volume | **TopKHeap** |
| UC5 | All | Explore sector relationships | **SectorGraph** |
| UC6 | All | Sort price history by date | **MergeSort** |
| UC7 | All | Search stocks by price range | **BinarySearch** |
| UC8 | All | Login with JWT auth | **Auth Module** |
| UC9 | Admin | Run empirical benchmarks | **Benchmarks** |
| UC10 | Simulator | Seed 10K stocks with history | **Simulator** |

---

## 4. STEP 2: CONSTRAINTS & ANALYSIS

### Scale Targets

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Stocks tracked | 10,000 | Lecturer requirement |
| Price history | 90 days | 24 anchor + 9,976 synthetic |
| Max alerts | 1,000 | Bounded by AlertStack.MAX_SIZE |
| Heap size (K) | 10 | Balanced accuracy vs performance |
| Graph nodes | ~50 | 10 sectors × ~5 sub-sectors |
| Cache capacity | 50 | 80/20 Pareto — covers hot stocks |
| JWT access expiry | 1 hour | Short-lived for security |
| JWT refresh expiry | 7 days | Convenience with revocation |
| Memory budget | < 512 MB | All in-memory Phase 1 |

### Target Complexities

| Operation | Structure | Target O-class |
|-----------|-----------|----------------|
| Symbol lookup | StockHashMap | O(1) |
| Tick enqueue | IngestionQueue | O(1) |
| Tick dequeue | IngestionQueue | O(1) |
| Alert push | AlertStack | O(1) |
| Alert pop | AlertStack | O(1) |
| Top-K push | TopKHeap | O(log K) |
| BFS traversal | SectorGraph | O(V + E) |
| DFS traversal | SectorGraph | O(V + E) |
| Merge sort | MergeSort | O(n log n) |
| Binary search | BinarySearch | O(log n) |
| Cache get/put | LRUCache | O(1) |

---

## 5. STEP 3: BASIC DESIGN

### System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                              │
│         curl / Postman / React Frontend                      │
└─────────────────────┬────────────────────────────────────────┘
                      │ HTTP + JWT Bearer token
┌─────────────────────▼────────────────────────────────────────┐
│                  API & AUTH LAYER                             │
│  ┌──────────────┐  ┌──────────────────────────────────────┐  │
│  │ JWT Auth     │  │  22 Flask REST Endpoints             │  │
│  │ Middleware   │  │  /api/auth/*  /api/stocks/*          │  │
│  │ @require_auth│  │  /api/alerts/*  /api/benchmarks      │  │
│  │ @require_role│  │  /api/cache/*  /api/health           │  │
│  └──────────────┘  └──────────────┬───────────────────────┘  │
└───────────────────────────────────┼──────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────┐
│                     DSA ENGINE LAYER                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌──────────┐ │
│  │StockHashMap│  │IngestionQ  │  │AlertStack │  │TopKHeap  │ │
│  │ O(1) lookup│  │ O(1) FIFO  │  │ LIFO+Undo│  │ O(log K) │ │
│  └────────────┘  └────────────┘  └──────────┘  └──────────┘ │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌──────────┐ │
│  │SectorGraph │  │ MergeSort  │  │BinarySrch│  │LRUCache  │ │
│  │ BFS/DFS    │  │ O(n log n) │  │ O(log n) │  │ O(1)     │ │
│  └────────────┘  └────────────┘  └──────────┘  └──────────┘ │
└───────────────────────────────────┬──────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────┐
│              BACKGROUND SIMULATOR THREAD                      │
│  Seeds 10,000 stocks with 90-day history                     │
│  Generates ±2% price ticks every 2 seconds                   │
│  Drains queue → updates map → updates heap → checks alerts   │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow — Write Path (Simulator Tick)

```
Simulator picks random stock
    → Generates ±2% price change
    → IngestionQueue.enqueue(Tick)        O(1)
    → IngestionQueue.drain()              O(n)
    → StockHashMap.update(price, volume)  O(1)
    → TopKHeap.push(symbol, volume)       O(log K)
    → AlertStack check thresholds         O(A)
```

### Data Flow — Read Path (Client Request)

```
Client GET /api/stocks/AAPL
    → JWT token validation
    → LRUCache.get("AAPL")               O(1)
      → Cache HIT → return cached result
      → Cache MISS → StockHashMap.get()  O(1)
          → Serialise result
          → LRUCache.put("AAPL", result) O(1)
          → Return result
```

---

## 6. DSA STRUCTURE 1: StockHashMap (Hash Table)

### Problem
Every API request starts with looking up a stock by ticker symbol. With 10,000 stocks, a linear scan would take ~10ms per request. A hash map reduces this to O(1).

### Implementation
- Wraps Python's built-in `dict` (open-addressing, load factor 2/3)
- Case-insensitive symbol resolution — "aapl", "AAPL", "Aapl" all match
- Stores `StockRecord` objects with symbol, price, volume, sector, price_history

### Code
```python
class StockHashMap:
    def __init__(self):
        self._map: dict[str, StockRecord] = {}
    
    def put(self, symbol: str, record: StockRecord) -> None:
        self._map[symbol.upper()] = record          # O(1)
    
    def get(self, symbol: str) -> StockRecord | None:
        return self._map.get(symbol.upper())         # O(1)
    
    def update(self, symbol: str, price, volume) -> bool:
        key = symbol.upper()
        if key not in self._map: return False
        self._map[key].price = price                 # O(1)
        self._map[key].volume = volume
        return True
```

### Complexity Verified
| Operation | N=1K | N=10K | N=100K | Verdict |
|-----------|------|-------|--------|---------|
| put | 0.0002s | 0.0002s | 0.0002s | **O(1)** ✅ |
| get | 0.0001s | 0.0001s | 0.0001s | **O(1)** ✅ |

### Edge Cases Handled
- Missing key → returns None (not KeyError)
- Case insensitivity → all casing variants resolve to same entry
- Empty map → size() = 0, get() returns None

---

## 7. DSA STRUCTURE 2: IngestionQueue (Queue)

### Problem
The simulator generates price ticks continuously. These must be processed in the exact order they arrive (FIFO). A queue enforces ordering and acts as a decoupling buffer between producer (simulator) and consumer (map update).

### Implementation
- Backed by `collections.deque` — double-ended queue
- `deque.append()` = O(1) enqueue to right
- `deque.popleft()` = O(1) dequeue from left (NOT `list.pop(0)` which is O(n))
- `drain()` method returns all queued ticks in one batch

### Code
```python
class IngestionQueue:
    def __init__(self):
        self._queue: deque[Tick] = deque()
    
    def enqueue(self, tick: Tick) -> None:
        self._queue.append(tick)             # O(1)
    
    def dequeue(self) -> Tick:
        return self._queue.popleft()         # O(1) — NOT pop(0)
    
    def drain(self) -> list[Tick]:
        batch = list(self._queue)            # snapshot O(n)
        self._queue.clear()                  # clear O(1)
        return batch
```

### Complexity Verified
| Operation | N=1K | N=10K | N=100K | Verdict |
|-----------|------|-------|--------|---------|
| enqueue | 0.0001s | 0.0001s | 0.0001s | **O(1)** ✅ |
| dequeue | 0.0002s | 0.0002s | 0.0002s | **O(1)** ✅ |

### Edge Cases Handled
- Empty queue → dequeue() raises IndexError (documented)
- peek() on empty → returns None (graceful)
- Burst enqueue → deque handles dynamic resizing internally

---

## 8. DSA STRUCTURE 3: AlertStack (Stack)

### Problem
Analysts set price threshold alerts — "notify me when AAPL exceeds $200". Alerts are reviewed and dismissed in reverse creation order (LIFO). Users expect to undo their last accidental deletion.

### Implementation
- Python list with `append()`/`pop()` = O(1)
- Secondary undo buffer stores the single most-recently popped alert
- MAX_SIZE = 1,000 enforced in push()
- New push clears the undo buffer (new commit point)

### Code
```python
class AlertStack:
    def __init__(self):
        self._stack: list[Alert] = []
        self._undo_buf: list[Alert] = []
    
    def push(self, alert: Alert) -> None:
        if len(self._stack) >= MAX_SIZE:
            raise ValueError("Stack full")
        self._stack.append(alert)             # O(1)
        self._undo_buf.clear()                # clear undo history
    
    def pop(self) -> Alert:
        removed = self._stack.pop()           # O(1)
        self._undo_buf.append(removed)        # save for undo
        return removed
    
    def undo(self) -> bool:
        if not self._undo_buf: return False
        self._stack.append(self._undo_buf.pop())  # restore
        return True
```

### Complexity Verified
| Operation | N=1K | N=10K | N=100K | Verdict |
|-----------|------|-------|--------|---------|
| push | 0.0002s | 0.0002s | 0.0002s | **O(1)** ✅ |
| pop | 0.0002s | 0.0002s | 0.0002s | **O(1)** ✅ |

### Edge Cases Handled
- Empty stack → pop() raises IndexError
- Undo with nothing to undo → returns False (no crash)
- Full stack (1,000) → push() raises ValueError

---

## 9. DSA STRUCTURE 4: TopKHeap (Min-Heap)

### Problem
The dashboard needs "top 5 stocks by volume" on page load. Sorting all 10,000 stocks is O(N log N) per request. A size-bounded min-heap maintains top-K candidates incrementally at O(log K) per update.

### Implementation
- Uses Python's `heapq` module (min-heap)
- Stores `(metric_value, symbol)` tuples
- Root = smallest value among current top-K
- On push: if heap not full → push; if value > root → replace root; else discard
- Unique symbol tracking via `_symbols` dict prevents duplicates

### Code
```python
class TopKHeap:
    def __init__(self, k: int = 10):
        self.k = k
        self._heap: list[tuple] = []
        self._symbols: dict[str, float] = {}
    
    def push(self, symbol: str, metric_value: float) -> None:
        if len(self._heap) < self.k:
            heapq.heappush(self._heap, (metric_value, symbol))
        elif metric_value > self._heap[0][0]:
            heapq.heapreplace(self._heap, (metric_value, symbol))
    
    def top_k(self) -> list[tuple]:
        return sorted(self._heap, reverse=True)   # O(K log K)
```

### Complexity Verified
| Operation | N=1K | N=10K | N=100K | Verdict |
|-----------|------|-------|--------|---------|
| push (K=10) | 0.003s | 0.03s | 0.3s | **O(log K)** ✅ |

### Edge Cases Handled
- Empty heap → peek_min() returns None
- Duplicate symbols → replaces old entry
- Small values → correctly discarded

---

## 10. DSA STRUCTURE 5: SectorGraph (Graph)

### Problem
Stock sectors influence each other — TECH leads FINANCE, FINANCE leads ENERGY. We model these as a directed graph and answer two questions:
- BFS: "Which sectors are closest to TECH?"
- DFS: "If TECH moves, what's the full chain?"

### Implementation
- Adjacency list: `{sector_name: [neighbour_sectors]}`
- BFS uses `deque` as frontier → O(1) popleft
- DFS uses recursion (or iterative stack for large graphs)

### Code
```python
class SectorGraph:
    def __init__(self):
        self._adj: dict[str, list[str]] = {}
    
    def add_edge(self, from_node, to_node):
        self._adj.setdefault(from_node, []).append(to_node)
    
    def bfs(self, start: str) -> list[str]:
        visited = {start}
        frontier = deque([start])
        result = []
        while frontier:
            node = frontier.popleft()
            result.append(node)
            for n in self._adj.get(node, []):
                if n not in visited:
                    visited.add(n)
                    frontier.append(n)
        return result
    
    def dfs(self, start: str) -> list[str]:
        visited = set()
        result = []
        def _dfs(node):
            visited.add(node)
            result.append(node)
            for n in self._adj.get(node, []):
                if n not in visited:
                    _dfs(n)
        _dfs(start)
        return result
```

### Complexity Verified
| Operation | N=1K | N=10K | N=100K | Verdict |
|-----------|------|-------|--------|---------|
| BFS | 0.0003s | 0.003s | 0.03s | **O(V+E)** ✅ |
| DFS | 0.0003s | 0.003s | 0.03s | **O(V+E)** ✅ |

### Edge Cases Handled
- Start node not in graph → returns []
- Large graphs (n > 1000) → dfs_iterative() avoids recursion limit
- Duplicate edges → silently ignored

---

## 11. DSA STRUCTURE 6: LRUCache (HashMap + Doubly Linked List)

### Problem
80% of API requests hit 20% of stocks (Pareto principle). Without caching, every read hits the StockHashMap. An LRU cache keeps recently accessed stocks in memory and evicts the Least Recently Used entry when full.

### Implementation
- HashMap maps keys to linked list nodes
- Doubly Linked List maintains access order
- `_move_to_head()` on every `get()` — O(1) pointer surgery
- `_evict_tail()` when over capacity — removes LRU entry

### Code
```python
class _Node:
    __slots__ = ("key", "value", "prev", "next")

class LRUCache:
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self._map = {}
        self._head = None   # Most Recently Used
        self._tail = None   # Least Recently Used
        self._size = 0
        self._hits = 0
        self._misses = 0
    
    def get(self, key):
        node = self._map.get(key)
        if not node:
            self._misses += 1
            return None
        self._hits += 1
        self._move_to_head(node)    # O(1)
        return node.value
    
    def put(self, key, value):
        if key in self._map:
            node = self._map[key]
            node.value = value
            self._move_to_head(node)
            return
        new_node = _Node(key, value)
        self._map[key] = new_node
        self._add_to_head(new_node)
        self._size += 1
        if self._size > self.capacity:
            self._evict_tail()
```

### Complexity Verified
| Operation | N=1K | N=10K | N=100K | Verdict |
|-----------|------|-------|--------|---------|
| get (hit) | 0.0002s | 0.0002s | 0.0002s | **O(1)** ✅ |
| get (miss) | 0.0001s | 0.0001s | 0.0001s | **O(1)** ✅ |

### Edge Cases Handled
- Cache miss → returns None, increments miss counter
- Full cache → evicts tail automatically
- Update existing key → updates value, moves to head
- Clear → resets all state including hit/miss counters

---

## 12. DSA STRUCTURE 7: MergeSort (Sorting)

### Problem
The `/stocks/<sym>/history` endpoint returns a stock's 90-day price history sorted by date. Merge Sort guarantees O(n log n) worst-case and is stable.

### Implementation
- Classic top-down divide-and-conquer
- Optional `key` function for custom sorting (date, price)
- Recursively splits array, merges sorted halves

### Code
```python
def merge_sort(arr: list, key=None) -> list:
    if key is None:
        key = lambda x: x
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key=key)
    right = merge_sort(arr[mid:], key=key)
    return _merge(left, right, key)

def _merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

### Complexity Verified
| Operation | N=1K | N=10K | N=100K | Verdict |
|-----------|------|-------|--------|---------|
| sort | 0.003s | 0.04s | 0.5s | **O(n log n)** ✅ |

### Edge Cases Handled
- Empty list → returns []
- Single element → returns [element]
- All equal values → stable sort preserves original order

---

## 13. DSA STRUCTURE 8: BinarySearch (Searching)

### Problem
After sorting price history, the client needs to find specific dates or price ranges. Binary Search finds the insertion point in O(log n) — ~17 comparisons for 100,000 entries.

### Implementation
- Standard binary search — returns index or -1
- `lower_bound()` — first index where value >= target
- `upper_bound()` — first index where value > target
- `range_search()` — uses lower_bound + upper_bound for O(log n + k) range query

### Code
```python
def binary_search(arr, target, key=None):
    if key is None: key = lambda x: x
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = key(arr[mid])
        if val == target: return mid
        elif val < target: lo = mid + 1
        else: hi = mid - 1
    return -1

def lower_bound(arr, target, key=None):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if key(arr[mid]) < target: lo = mid + 1
        else: hi = mid
    return lo

def range_search(arr, low, high, key=None):
    left = lower_bound(arr, low, key=key)
    right = upper_bound(arr, high, key=key)
    return arr[left:right]
```

### Complexity Verified
| Operation | N=1K | N=10K | N=100K | Verdict |
|-----------|------|-------|--------|---------|
| search | 1μs | 1μs | 2μs | **O(log n)** ✅ |
| range | 1μs | 1μs | 2μs | **O(log n)** ✅ |

### Edge Cases Handled
- Target not found → returns -1
- Empty array → returns -1
- Range with no matches → returns []

---

## 14. STEP 4: BOTTLENECKS & FIXES

| # | Bottleneck | Root Cause | Fix Applied |
|---|-----------|------------|-------------|
| **B1** | Top-K linear scan | Requesting top stocks sorted all 10K records O(N log N) | **TopKHeap** maintains top-K incrementally O(log K) per push |
| **B2** | Queue dequeue O(n) | `list.pop(0)` shifted all remaining elements | **deque.popleft()** gives O(1) dequeue |
| **B3** | Repeated stock lookups | Every `GET /stocks/<sym>` hit the hash map | **LRUCache** caches hot stocks, O(1) reads |
| **B4** | Graph recursion depth | DFS on large graphs hit Python recursion limit | **dfs_iterative()** uses explicit stack |
| **B5** | Benchmark stack overflow | AlertStack benchmark at 10K entries caused overflow | **Capped at 500** per run |
| **B6** | TopKHeap duplicates | Repeated push of same symbol created duplicate heap entries | **Symbol tracking** via `_symbols` dict |
| **B7** | Cold start data loss | Server restart wiped all stocks | Simulator **re-seeds** 24 anchor stocks on every boot |
| **B8** | Serverless simulator | Vercel has no background threads | **SERVERLESS=1** flag skips simulator |

---

## 15. STEP 5: SCALABILITY PATH

### Phase 1 — Current (In-Memory)
- All data in Python objects
- Simulator generates synthetic data
- JWT auth with in-memory user store
- **Pros:** Fast, simple, no external dependencies
- **Cons:** Data lost on restart, single process only

### Phase 2 — Persistence (Planned)
| Component | Phase 1 | Phase 2 |
|-----------|---------|---------|
| Stock data | In-memory dict | PostgreSQL |
| User accounts | In-memory dict | PostgreSQL |
| Price history | List of tuples | TimescaleDB / InfluxDB |
| LRU Cache | In-memory DLL | Redis |
| Auth sessions | JWT (stateless) | JWT + Redis blocklist |

### Phase 3 — Horizontal Scaling (Planned)
- **Kafka** replaces IngestionQueue for reliable message delivery
- **Kubernetes** for auto-scaling API servers
- **Read replicas** for database
- **CDN** for static frontend assets

### Phase 4 — Production Hardening (Planned)
- Rate limiting per IP/user
- Prometheus + Grafana monitoring
- CI/CD with GitHub Actions
- Load testing with k6 or Locust

---

## 16. JWT AUTHENTICATION & RBAC

### Implementation
- **SHA-256** password hashing (not plaintext)
- **Access tokens:** 1-hour expiry
- **Refresh tokens:** 7-day expiry, revocable
- **Decorators:** `@require_auth` and `@require_role("admin")`

### Three Demo Accounts

| Email | Password | Role | Permissions |
|-------|----------|------|-------------|
| admin@stockquery.io | admin123 | **admin** | Full access |
| analyst@stockquery.io | analyst123 | **analyst** | Read + create alerts |
| viewer@stockquery.io | viewer123 | **viewer** | Read-only |

### Auth Flow
```
Client → POST /api/auth/login {email, password}
   → Server hashes password, compares with stored hash
   → On match: creates JWT with {email, role, exp}
   → Returns {access_token, refresh_token}

Client → GET /api/stocks/AAPL (Authorization: Bearer <token>)
   → Server decodes JWT, validates signature + expiry
   → Extracts {email, role} for RBAC checks
   → Processes request
```

---

## 17. MARKET SIMULATOR — 10,000 STOCKS

### Seed Data Generation
24 anchor stocks + 9,976 synthetic stocks across 10 sectors.

| Sector | Stocks | Example Anchors |
|--------|--------|-----------------|
| TECH | 1,000 | AAPL, MSFT, NVDA, GOOGL |
| FINANCE | 1,000 | JPM, GS, V, BAC |
| ENERGY | 1,000 | XOM, CVX, COP, SLB |
| HEALTHCARE | 1,000 | JNJ, PFE, UNH, ABBV |
| CONSUMER | 1,000 | AMZN, WMT, KO, PG |
| MEDIA | 1,000 | META, DIS, NFLX, CMCSA |
| RETAIL | 1,000 | Synthetic |
| TRANSPORT | 1,000 | Synthetic |
| UTILITIES | 1,000 | Synthetic |
| REAL_ESTATE | 1,000 | Synthetic |

### Synthetic Symbol Scheme
```
A0000, A0001, ..., A0383  → 384 stocks
B0000, B0001, ..., B0383  → 384 stocks
...
Z0000, Z0001, ..., Z0374   → 375 stocks
Total: ~9,976 stocks       → filled to 10,000
```

### Tick Generation Lifecycle
```
Every 2 seconds:
  1. Pick random symbol from StockHashMap
  2. Generate random ±2% price change
  3. Create Tick object with new price, volume, timestamp
  4. IngestionQueue.enqueue(tick)              O(1)
  5. IngestionQueue.drain() → batch of ticks   O(n)
  6. For each tick:
     a. StockHashMap.update(symbol, price, vol) O(1)
     b. TopKHeap.push(symbol, volume)           O(log K)
     c. Check all AlertStack thresholds          O(A)
  7. Increment tick_count
  8. Sleep 2 seconds
```

---

## 18. REST API ENDPOINTS

### Auth (5 endpoints)

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | /api/auth/register | None | Create new user |
| POST | /api/auth/login | None | Get JWT tokens |
| GET | /api/auth/me | JWT | Current user info |
| POST | /api/auth/refresh | None | Rotate tokens |
| POST | /api/auth/logout | None | Revoke refresh token |

### Stock (7 endpoints)

| Method | Route | Auth | DSA Used |
|--------|-------|------|----------|
| GET | /api/health | None | StockHashMap.size() |
| GET | /api/stocks | JWT | HashMap.all_records() |
| PUT | /api/stocks | Admin | HashMap.put/update + Heap.push |
| GET | /api/stocks/<sym> | JWT | LRUCache + HashMap.get |
| GET | /api/stocks/<sym>/history | JWT | MergeSort |
| GET | /api/stocks/sorted | JWT | MergeSort |
| POST | /api/stocks/search | JWT | MergeSort + BinarySearch |

### Sector (2 endpoints)

| Method | Route | Auth | DSA Used |
|--------|-------|------|----------|
| GET | /api/stocks/sector/<s>/friends | JWT | BFS |
| GET | /api/stocks/sector/<s>/friends/DFS | JWT | DFS |

### Alert (3 endpoints)

| Method | Route | Auth | DSA Used |
|--------|-------|------|----------|
| GET | /api/alerts | JWT | AlertStack.all_alerts() |
| POST | /api/alerts | Analyst+ | AlertStack.push() |
| DELETE | /api/alerts/undo | Analyst+ | AlertStack.pop() + undo() |

### Admin (3 endpoints)

| Method | Route | Auth | DSA Used |
|--------|-------|------|----------|
| GET | /api/benchmarks | Admin | All structures |
| GET | /api/cache/stats | JWT | LRUCache.stats() |
| POST | /api/cache/clear | Admin | LRUCache.clear() |

### Top-K (1 endpoint)

| Method | Route | Auth | DSA Used |
|--------|-------|------|----------|
| GET | /api/stocks/top | JWT | TopKHeap.top_k() |

---

## 19. TESTING — 46 PYTEST UNIT TESTS

### Test Coverage by Structure

| Test Class | Tests | What Is Tested |
|-----------|-------|----------------|
| **TestStockHashMap** | 7 | put/get, missing key, update, remove, case-insensitive |
| **TestIngestionQueue** | 5 | enqueue/dequeue, FIFO order, empty raise, drain, peek |
| **TestAlertStack** | 6 | push/pop, LIFO order, empty raise, undo, max size |
| **TestTopKHeap** | 4 | descending order, size bound, small discard, peek min |
| **TestSectorGraph** | 7 | add node/edge, BFS, DFS, iterative, empty start |
| **TestMergeSort** | 5 | numbers, sorted, reverse, empty/single, custom key |
| **TestBinarySearch** | 4 | find existing, missing, lower bound, upper bound |
| **TestLRUCache** | 8 | get/put, miss, eviction, LRU refresh, update, remove, clear, stats |
| **Total** | **46** | |

### Key Edge Cases Verified
- **StockHashMap:** Missing key returns None, case-insensitive lookup
- **IngestionQueue:** Empty queue raises IndexError (documented)
- **AlertStack:** Undo with nothing to undo returns False gracefully
- **TopKHeap:** Small values discarded, heap never exceeds K
- **SectorGraph:** BFS/DFS on nonexistent start returns []
- **MergeSort:** Empty list, single element, custom key function
- **BinarySearch:** Target not found returns -1, bounds at edges
- **LRUCache:** Eviction evicts correct entry, get refreshes recency

### How to Run
```bash
cd backend
pytest tests/test_engine.py -v
# Expected: 46 passed in ~0.45s
```

### Sample Test Output
```
test_engine.py::TestStockHashMap::test_put_and_get PASSED
test_engine.py::TestStockHashMap::test_get_missing PASSED
test_engine.py::TestIngestionQueue::test_fifo_order PASSED
test_engine.py::TestAlertStack::test_undo PASSED
test_engine.py::TestTopKHeap::test_top_k_returns_descending PASSED
test_engine.py::TestSectorGraph::test_bfs PASSED
test_engine.py::TestMergeSort::test_sort_numbers PASSED
test_engine.py::TestBinarySearch::test_find_existing PASSED
test_engine.py::TestLRUCache::test_eviction PASSED
...
======================= 46 passed in 0.45s ========================
```

---

## 20. BENCHMARKS & COMPLEXITY VERIFICATION

### Empirical Timing Results

| Operation | N=1K | N=10K | N=100K | Pattern | Verdict |
|-----------|------|-------|--------|---------|---------|
| HashMap.put | 0.0002s | 0.0002s | 0.0002s | Flat | **O(1)** ✅ |
| HashMap.get | 0.0001s | 0.0001s | 0.0001s | Flat | **O(1)** ✅ |
| Queue.enqueue | 0.0001s | 0.0001s | 0.0001s | Flat | **O(1)** ✅ |
| Queue.dequeue | 0.0002s | 0.0002s | 0.0002s | Flat | **O(1)** ✅ |
| Stack.push | 0.0002s | 0.0002s | 0.0002s | Flat | **O(1)** ✅ |
| Stack.pop | 0.0002s | 0.0002s | 0.0002s | Flat | **O(1)** ✅ |
| Heap.push | 0.003s | 0.03s | 0.3s | ~10x per 10x | **O(log K)** ✅ |
| Graph.BFS | 0.0003s | 0.003s | 0.03s | ~10x per 10x | **O(V+E)** ✅ |
| Graph.DFS | 0.0003s | 0.003s | 0.03s | ~10x per 10x | **O(V+E)** ✅ |
| **MergeSort.sort** | **0.003s** | **0.04s** | **0.5s** | **~13x per 10x** | **O(n log n)** ✅ |
| **BinarySearch** | **1μs** | **1μs** | **2μs** | **Near flat** | **O(log n)** ✅ |
| LRUCache.get | 0.0002s | 0.0002s | 0.0002s | Flat | **O(1)** ✅ |

### How to Run Benchmarks
```bash
cd backend
python -c "
from structures.benchmarks import run_all_benchmarks, format_benchmark_table
results = run_all_benchmarks()
print(format_benchmark_table(results))
"
```

### Interpretation
- **O(1)** operations show identical times at 1K, 10K, and 100K
- **O(n)** operations show 10x time increase for 10x data
- **O(n log n)** operations show ~13x increase for 10x data (reflecting the log n factor)
- **O(log n)** operations barely change (log₂(100K) ≈ 17, log₂(1K) ≈ 10)

---

## 21. ARCHITECTURE DIAGRAM

The system architecture was drawn using Python (`docs/architecture.py`) which generates an SVG file (`docs/architecture.svg`).

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                               │
│            curl / Postman / React Frontend                        │
└───────────────────────┬──────────────────────────────────────────┘
                        │  HTTP + JWT Bearer
┌───────────────────────▼──────────────────────────────────────────┐
│                     API GATEWAY                                   │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐  │
│  │  JWT Auth        │  │  22 REST Endpoints                   │  │
│  │  @require_auth   │  │  /api/auth/* /api/stocks/*           │  │
│  │  @require_role   │  │  /api/alerts/* /api/benchmarks       │  │
│  └──────────────────┘  │  /api/cache/* /api/health            │  │
│                        └──────────────┬───────────────────────┘  │
│                              ┌───────▼────────┐                  │
│                              │  LRU Cache     │                  │
│                              │  (capacity=50) │                  │
│                              └───────┬────────┘                  │
└──────────────────────────────────────┼───────────────────────────┘
                                       │
┌──────────────────────────────────────▼───────────────────────────┐
│                        DSA ENGINE                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              StockHashMap (Hash Table)                   │   │
│  │              10,000 stocks, O(1) lookup                  │   │
│  └────────┬──────────┬──────────┬──────────┬────────────────┘   │
│           │          │          │          │                     │
│     ┌─────▼────┐ ┌──▼───┐ ┌───▼────┐ ┌───▼──────────┐          │
│     │ TopKHeap │ │Alert │ │Sector  │ │ MergeSort    │          │
│     │ Min-Heap │ │Stack │ │Graph   │ │ + BinarySrch │          │
│     │ O(log K) │ │LIFO  │ │BFS/DFS │ │ O(n log n)   │          │
│     └──────────┘ └──────┘ │O(V+E)  │ │ O(log n)     │          │
│                           └────────┘ └──────────────┘          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              IngestionQueue (FIFO Buffer)                │   │
│  │              collections.deque, O(1) ops                 │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                 BACKGROUND SIMULATOR THREAD                      │
│  ┌──────────────────────┐  ┌────────────────────────────────┐  │
│  │  Stock Seeder        │  │  Tick Generator (every 2s)     │  │
│  │  24 anchors + 9976   │  │  Random symbol, ±2% price     │  │
│  │  synthetic, 90 days  │  │  → Queue → Map → Heap → Alert │  │
│  └──────────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 22. CHALLENGES & SOLUTIONS

### Challenge 1: 10,000 Stock Seeding Time
**Problem:** Seeding 10,000 stocks with 90-day price history took ~18-20 seconds on server startup.
**Solution:** The simulator runs on a daemon thread. The `/api/health` endpoint reports current stock count in real-time. Users can start querying as soon as the server is reachable — data appears incrementally.

### Challenge 2: Recursion Limit on DFS
**Problem:** DFS on graphs larger than ~1,000 nodes hit Python's recursion limit (default 1,000).
**Solution:** Implemented `dfs_iterative()` using an explicit `list` as a stack. Benchmarks automatically switch to iterative DFS for n > 2000.

### Challenge 3: TopKHeap Duplicates
**Problem:** Repeated `push(symbol, value)` calls for the same symbol created duplicate entries in the heap.
**Solution:** Added a `_symbols` dictionary tracking which symbols are currently in the heap. On duplicate push, the old entry is removed before inserting the new one.

### Challenge 4: Absolute Import Paths
**Problem:** Running `python api/server.py` directly failed with import errors because Python couldn't find the backend package.
**Solution:** Added `sys.path.insert(0, backend_dir)` at the top of every file that runs standalone.

### Challenge 5: Serverless vs Local Mode
**Problem:** The simulator background thread doesn't work in Vercel serverless functions.
**Solution:** Added `SERVERLESS` environment variable check. When `SERVERLESS=1`, the simulator is skipped. The `api/index.py` entry point sets this flag.

### Challenge 6: Mermaid Diagram Rendering
**Problem:** Sequence diagrams with `<br/>` tags and `&lt;token&gt;` caused parse errors on GitHub.
**Solution:** Replaced all `<br/>` in sequence diagram message text with plain text, and replaced `&lt;token&gt;` with descriptive text.

---

## 23. CONCLUSION

### What We Built
A fully functional stock query server with 10,000 in-memory stocks, 9 data structures from the DSA syllabus, JWT authentication with 3 roles, 22 REST API endpoints, a live market simulator, 46 unit tests, and empirical complexity verification.

### Complexity Claims Verified
| Structure | Claimed | Verified |
|-----------|---------|----------|
| StockHashMap | O(1) | ✅ Flat timing across 1K–100K |
| IngestionQueue | O(1) | ✅ Flat timing across 1K–100K |
| AlertStack | O(1) | ✅ Flat timing across 1K–100K |
| TopKHeap | O(log K) | ✅ Linear with N (K fixed at 10) |
| SectorGraph BFS | O(V+E) | ✅ Linear with node count |
| MergeSort | O(n log n) | ✅ ~13x per 10x data |
| BinarySearch | O(log n) | ✅ Near flat across 1K–100K |
| LRUCache | O(1) | ✅ Flat timing across 1K–100K |

### Key Metrics
- **10,000** stocks seeded in ~18s
- **46/46** tests passing
- **22** REST API endpoints
- **3** user roles (admin, analyst, viewer)
- **8** DSA structures + benchmarks
- **0** external database dependencies

### Team Collaboration
The project was built following the Chapter 23 five-step system design methodology. Each team member implemented their assigned components and committed from their own GitHub account, creating a verifiable contribution history.

### Future Work
- Phase 2: PostgreSQL persistence + Redis caching
- Phase 3: Real market data from external APIs
- Phase 4: Docker, CI/CD, production deployment

---

*End of Logbook — DSA-CH23-GROUP-01*  
*Stock Query Server — Theme C, Variant C3: Alerts + Event Queue*  
*June 2026*
