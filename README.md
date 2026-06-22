# DSA-CH23-GROUP-01 — Stock Query Server

A real-time stock query server built for the **Chapter 23 5-Step System Design** (Hemant Jain).  
Implements **10,000 stocks** with **9 DSA structures**, **JWT authentication**, **22 REST API endpoints**, and a live market simulator.

---

## Team Contributions

### 👤 Person 1 — Team Lead / Integrator

**Files:** `.gitignore`, `README.md`, `vercel.json`, `start.bat`, `start.sh`, `requirements.txt`, `docs/`

**What they did:**
- Created the GitHub repository and project structure
- Wrote the `.gitignore` (Python, Node, IDE, OS patterns)
- Wrote the professional README with API table, complexity matrix, and run instructions
- Set up Vercel deployment config (`vercel.json`)
- Created launch scripts for Windows (`start.bat`) and Linux/Mac (`start.sh`)
- Managed Python dependencies (`requirements.txt`)
- Wrote the **Chapter 23 5-Step System Design** (`docs/system_design.md`):
  - **Step 1 — Use Cases:** Login, view stocks, set alerts, sector exploration, sorted history, benchmarks
  - **Step 2 — Constraints:** 10,000 stocks, 90-day history, O(1)/O(log n) requirements, in-memory
  - **Step 3 — Basic Design:** Flask app, background simulator, JWT auth, DSA engine layer
  - **Step 4 — Bottlenecks:** Linear scans → hash maps, list.pop(0) → deque, recursion depth → iterative DFS
  - **Step 5 — Scalability:** Phase 1 (in-memory) → Phase 2 (PostgreSQL + Redis) → Phase 3 (Kafka + Kubernetes)
- Wrote the **12-page Final Report** (`docs/final_report.md`)
- Generated the **Architecture Diagram** (`docs/architecture.py` + `docs/architecture.svg`)
- Authored the Team Workflow Guide (`docs/TEAM_WORKFLOW.md`)

---

### 👤 Person 2 — Data Structures Lead

**Files:** `backend/structures/stock_map.py`, `ingestion_queue.py`, `alert_stack.py`, `top_k_heap.py`, `sector_graph.py`, `lru_cache.py`

**What they did — 6 DSA structures:**

**① StockHashMap (Hash Table) — O(1) lookup**
- Wraps Python dict with domain-specific API
- Case-insensitive symbol resolution — "aapl", "AAPL", "Aapl" all match
- Methods: `put`, `get`, `update`, `remove`, `contains`, `all_records`
- 7 unit tests covering: put/get, missing key, update, remove, case-insensitivity

**② IngestionQueue (Queue — FIFO) — O(1) enqueue/dequeue**
- Backed by `collections.deque` — O(1) `popleft()` instead of O(n) `pop(0)`
- `Tick` class with `__slots__` for memory efficiency
- `drain()` method for batch consumption (O(n) intentional)
- 5 unit tests covering: enqueue/dequeue, FIFO order, empty raise, drain, peek

**③ AlertStack (Stack — LIFO with undo) — O(1) push/pop**
- Python list with `append()`/`pop()` — both O(1)
- Single-level undo buffer — restores last popped alert
- MAX_SIZE = 1,000 enforced in `push()`
- 6 unit tests covering: push/pop, LIFO order, empty raise, undo, max size

**④ TopKHeap (Min-Heap) — O(log K) push, O(K log K) top-K**
- Size-bounded min-heap using Python's `heapq`
- Only keeps top-K largest values — discards smaller ones
- Unique symbol tracking via `_symbols` dict prevents duplicates
- 4 unit tests covering: descending order, size bound, small value discard, peek min

**⑤ SectorGraph (Graph — Adjacency List) — O(V + E) BFS/DFS**
- Directed graph stored as `{sector: [neighbours]}`
- **BFS:** Uses `deque` as frontier — returns sectors by proximity
- **DFS (recursive):** Full reachability via Python call stack
- **DFS (iterative):** Explicit stack for large graphs (n > 1000)
- 7 unit tests covering: add node/edge, BFS order, DFS order, iterative DFS, empty start

**⑥ LRUCache (HashMap + Doubly Linked List) — O(1) get/put**
- `_Node` class with `prev`/`next` pointers for O(1) list surgery
- `_move_to_head()` on every access — most recently used stays at front
- `_evict_tail()` when over capacity — removes least recently used
- Hit/miss counters and `stats()` for monitoring
- 8 unit tests covering: get/put, miss, eviction, LRU refresh, update, remove, clear, stats

**Pipeline connection:**
```
Simulator → IngestionQueue → StockHashMap → TopKHeap
                                              └→ AlertStack
Client → LRUCache → StockHashMap
SectorGraph (independent exploration)
```

---

### 👤 Person 3 — Algorithms Lead + Benchmarks

**Files:** `backend/structures/merge_sort.py`, `binary_search.py`, `benchmarks.py`

**What they did — 2 algorithms + empirical verification:**

**① MergeSort (Divide & Conquer) — O(n log n) stable sort**
- Top-down recursive implementation
- Optional `key` function for custom sorting (date, price, etc.)
- Merge phase compares left vs right, picks smaller element
- 5 unit tests covering: numbers, already sorted, reverse sorted, empty/single, custom key
- **Used by:** `/api/stocks/<sym>/history` (sort by date), `/api/stocks/sorted` (sort by price), `/api/stocks/search` (sort before binary search)

```
Divide: [38, 27, 43, 3, 9, 82, 10]
              ↓
        [38, 27, 43, 3]    [9, 82, 10]
              ↓                  ↓
     [38, 27]    [43, 3]    [9, 82]  [10]
        ↓          ↓          ↓
     [27, 38]   [3, 43]    [9, 82]
        ↓          ↓          ↓
     [3, 27, 38, 43]      [9, 10, 82]
              ↓                  ↓
        [3, 9, 10, 27, 38, 43, 82]  ← Conquer (Merge)
```

**② BinarySearch (Divide & Conquer) — O(log n) search**
- Classic binary search — returns index or -1
- `lower_bound` — first index where value >= target
- `upper_bound` — first index where value > target
- `range_search` — uses lower_bound + upper_bound for O(log n + k) range queries
- 4 unit tests covering: find existing, find missing, lower bound, upper bound
- **Used by:** `/api/stocks/search` (price range query)

**③ Benchmarks — Empirical Complexity Verification**
- Runs every DSA operation at N = 1K, 10K, 100K
- 5 repetitions per operation, median timing with `time.perf_counter()`
- Expected pattern:
  - O(1): HashMap.get, Queue.dequeue, Stack.push — flat across N
  - O(n): Graph.BFS, Graph.DFS — 10x time at 10x data
  - O(n log n): MergeSort.sort — slightly more than 10x at 10x
  - O(log n): BinarySearch.search — nearly flat across N
- **Endpoint:** `GET /api/benchmarks` (admin only)

---

### 👤 Person 4 — API Developer

**Files:** `backend/api/server.py`, `backend/api/__init__.py`, `backend/requirements.txt`

**What they did — 22 REST API endpoints:**

**Auth (5 endpoints):**
| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/api/auth/register` | POST | ❌ | Register new user |
| `/api/auth/login` | POST | ❌ | Login → JWT tokens |
| `/api/auth/me` | GET | ✅ | Current user profile |
| `/api/auth/refresh` | POST | ❌ | Refresh expired token |
| `/api/auth/logout` | POST | ❌ | Revoke refresh token |

**Stock (8 endpoints):**
| Route | Method | Auth | DSA Used |
|-------|--------|------|----------|
| `/api/health` | GET | ❌ | StockHashMap.size() |
| `/api/stocks` | GET | ✅ | StockHashMap.all_records() |
| `/api/stocks` | PUT | admin | StockHashMap.put/update + TopKHeap.push |
| `/api/stocks/<sym>` | GET | ✅ | LRUCache.get → StockHashMap.get |
| `/api/stocks/<sym>/history` | GET | ✅ | MergeSort.sort() |
| `/api/stocks/sorted` | GET | ✅ | MergeSort.sort(all records) |
| `/api/stocks/search` | POST | ✅ | MergeSort + BinarySearch.range_search |
| `/api/stocks/top` | GET | ✅ | TopKHeap.top_k() |

**Sector (2 endpoints):**
| Route | Method | Auth | DSA Used |
|-------|--------|------|----------|
| `/api/stocks/sector/<s>/friends` | GET | ✅ | SectorGraph.bfs() |
| `/api/stocks/sector/<s>/friends/DFS` | GET | ✅ | SectorGraph.dfs() |

**Alert (3 endpoints):**
| Route | Method | Auth | DSA Used |
|-------|--------|------|----------|
| `/api/alerts` | GET | ✅ | AlertStack.all_alerts() |
| `/api/alerts` | POST | analyst/admin | AlertStack.push() |
| `/api/alerts/undo` | DELETE | analyst/admin | AlertStack.pop() + undo() |

**Admin (3 endpoints):**
| Route | Method | Auth | DSA Used |
|-------|--------|------|----------|
| `/api/benchmarks` | GET | admin | run_all_benchmarks() |
| `/api/cache/stats` | GET | ✅ | LRUCache.stats() |
| `/api/cache/clear` | POST | admin | LRUCache.clear() |

**Server architecture:**
- Flask app with CORS enabled
- DSA singletons attached to `app` context
- Simulator starts on boot (unless `SERVERLESS=1`)
- LRU cache sits in front of StockHashMap for hot stocks
- Error handling returns JSON consistently

---

### 👤 Person 5 — Auth & Simulator Developer

**Files:** `backend/api/auth.py`, `backend/api/simulator.py`, `api/index.py`

**What they did — security + live data generation:**

**① JWT Authentication with RBAC (`auth.py`)**
- **Access tokens:** 1-hour expiry (short-lived, secure)
- **Refresh tokens:** 7-day expiry (convenience, revocable)
- **Password security:** SHA-256 hashing (not plaintext)
- **3 Demo Accounts:**
  | Email | Password | Role | Permissions |
  |-------|----------|------|-------------|
  | admin@stockquery.io | admin123 | **admin** | Everything |
  | analyst@stockquery.io | analyst123 | **analyst** | Create/undo alerts |
  | viewer@stockquery.io | viewer123 | **viewer** | Read-only |
- **Decorators:** `@require_auth` (any valid JWT), `@require_role("admin")` (role check)
- **Token endpoints:** Login returns `{access_token, refresh_token, role, email}`

**② Market Simulator (`simulator.py`)**
- **10,000 stocks:** 24 anchor stocks (AAPL, MSFT, NVDA, JPM, etc.) + 9,976 synthetic (A0000–Z0374)
- **10 sectors:** TECH, FINANCE, ENERGY, HEALTHCARE, CONSUMER, MEDIA, RETAIL, TRANSPORT, UTILITIES, REAL_ESTATE
- **90-day price history:** Random walk with ±2% daily noise
- **Live ticks:** Every 2 seconds, picks random stock, generates ±2% price change
- **Pipeline:** Enqueue → drain → StockHashMap.update → TopKHeap.push → AlertStack check
- **Daemon thread:** Starts automatically with Flask (skipped when `SERVERLESS=1`)
- **Health check:** `/api/health` shows stock count, alert count, queue size, ticks processed

**③ Vercel Serverless (`api/index.py`)**
- Sets `SERVERLESS=1` to skip simulator thread
- Exposes Flask app as Vercel serverless function
- Read-only mode for deployment (no background tick generation)

```
SYMBOL GENERATION SCHEME:
  Stock #1     → A0000
  Stock #2     → A0001
  ...
  Stock #26    → A0025
  Stock #27    → B0000
  ...
  Stock #10000 → Z0374
```

---

### 👤 Person 6 — Testing & QA Lead

**Files:** `backend/tests/test_engine.py`, `backend/tests/__init__.py`

**What they did — 46 pytest unit tests:**

| Test Class | Tests | Coverage |
|-----------|-------|----------|
| `TestStockHashMap` | 7 | put/get, missing, update, remove, case-insensitive |
| `TestIngestionQueue` | 5 | enqueue/dequeue, FIFO, empty raise, drain, peek |
| `TestAlertStack` | 6 | push/pop, LIFO, empty raise, undo, max size |
| `TestTopKHeap` | 4 | descending order, size bound, small discard, peek min |
| `TestSectorGraph` | 7 | add node/edge, BFS, DFS, iterative DFS, empty start |
| `TestMergeSort` | 5 | numbers, sorted, reverse, empty/single, key |
| `TestBinarySearch` | 4 | find existing, missing, lower bound, upper bound |
| `TestLRUCache` | 8 | get/put, miss, eviction, LRU refresh, update, remove, clear, stats |

**Running tests:**
```bash
cd backend
pytest tests/test_engine.py -v
# 46 passed in ~0.45s
```

**Edge cases tested:**
- Empty structures → returns None or raises IndexError gracefully
- Full capacity → raises ValueError with message
- Case sensitivity → "aapl" == "AAPL"
- Undo with nothing to undo → returns False
- LRU eviction evicts correct entry
- MergeSort with custom key function
- BinarySearch on empty array
- Graph BFS/DFS with unknown start node

---

## System Architecture

```
┌─────────────┐     ┌──────────────────────────────────────┐
│   Client    │     │            Flask Server               │
│  curl/HTTP  │────▶│  ┌────────┐  ┌──────────────────┐    │
└─────────────┘     │  │ JWT    │  │  22 REST Routes  │    │
                    │  │ Auth   │  │                  │    │
                    │  └────────┘  └──────┬───────────┘    │
                    │                     ▼                │
                    │  ┌────────────────────────────────┐  │
                    │  │     DSA Engine Layer           │  │
                    │  │  ┌──────────┐  ┌────────────┐  │  │
                    │  │  │ LRU     │──│ StockHashMap│  │  │
                    │  │  │ Cache   │  └──────┬─────┘  │  │
                    │  │  └────────┘         │         │  │
                    │  │           ┌─────────┼────────┐ │  │
                    │  │           ▼         ▼        ▼ │  │
                    │  │  ┌──────────┐ ┌────────┐ ┌────┐ │  │
                    │  │  │ TopKHeap │ │AlertStk│ │Sect│ │  │
                    │  │  └──────────┘ └────────┘ │Grap│ │  │
                    │  │                          └────┘ │  │
                    │  └────────────────────────────────┘  │
                    │                    ▲                 │
                    │  ┌─────────────────┴──────────────┐  │
                    │  │   Background Simulator Thread   │  │
                    │  │  Seeds 10K stocks, ticks / 2s  │  │
                    │  └────────────────────────────────┘  │
                    └──────────────────────────────────────┘
```

---

## Complexity Matrix

| Operation | Complexity | N=1K | N=10K | N=100K |
|-----------|-----------|------|-------|--------|
| HashMap.get | **O(1)** | ~0.0001s | ~0.0001s | ~0.0001s |
| HashMap.put | **O(1)** | ~0.0002s | ~0.0002s | ~0.0002s |
| Queue.enqueue | **O(1)** | ~0.0001s | ~0.0001s | ~0.0001s |
| Queue.dequeue | **O(1)** | ~0.0002s | ~0.0002s | ~0.0002s |
| Stack.push | **O(1)** | ~0.0002s | ~0.0002s | ~0.0002s |
| Heap.push | **O(log K)** | ~0.003s | ~0.03s | ~0.3s |
| MergeSort.sort | **O(n log n)** | ~0.003s | ~0.04s | ~0.5s |
| BinarySearch | **O(log n)** | ~1μs | ~1μs | ~2μs |
| Graph.BFS | **O(V+E)** | ~0.0003s | ~0.003s | ~0.03s |
| LRUCache.get | **O(1)** | ~0.0002s | ~0.0002s | ~0.0002s |

---

## How to Run

```bash
# Clone
git clone https://github.com/jacksonvincent012-web/DSA-CH23-GROUP-01.git
cd DSA-CH23-GROUP-01

# Install backend deps
cd backend
pip install -r requirements.txt

# Start server
python api/server.py
# Server starts on http://localhost:5000
# Seeding 10,000 stocks takes ~18-20s on first boot
# Check health: curl http://localhost:5000/api/health

# In another terminal — test it:
# Login
curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@stockquery.io","password":"admin123"}'

TOKEN="<paste_access_token_here>"

# Get a stock
curl -s http://localhost:5000/api/stocks/AAPL \
  -H "Authorization: Bearer $TOKEN"

# Top 10 by volume
curl -s "http://localhost:5000/api/stocks/top?metric=volume&k=10" \
  -H "Authorization: Bearer $TOKEN"

# Sector BFS
curl -s http://localhost:5000/api/stocks/sector/TECH/friends \
  -H "Authorization: Bearer $TOKEN"

# Run tests
cd backend
pytest tests/test_engine.py -v
```

---

## VS Code Launch Configuration

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Stock Query Server",
            "type": "python",
            "request": "launch",
            "module": "api.server",
            "cwd": "${workspaceFolder}/backend",
            "console": "integratedTerminal",
            "env": { "FLASK_DEBUG": "1" }
        }
    ]
}
```

---

## Submission Checklist

- [x] 10,000 stocks seeded
- [x] 9 DSA structures (HashMap, Queue, Stack, Heap, Graph, MergeSort, BinarySearch, LRUCache, Benchmarks)
- [x] 22 REST API endpoints
- [x] JWT authentication with RBAC (3 roles)
- [x] 46 passing pytest tests
- [x] Chapter 23 5-Step System Design document
- [x] 12-page final report
- [x] Architecture diagram
- [x] Complexity analysis with empirical benchmarks
- [x] Commit history showing 6 contributors
- [x] Professional README

---

**Group 01 — Stock Query Server**  
*Chapter 23 5-Step System Design — Hemant Jain*  
*DSA Assignment — Theme C, Variant C3: Alerts + Event Queue*
