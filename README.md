# Stock Query Server — DSA-CH23-GROUP (Theme C)

**Course:** CS — Data Structures & Algorithms
**Theme:** C — Stock Query Server (Variant C3: Alerts + Event Queue)
**Language:** Python 3.11+ · Flask 3.0 · React 18 · TypeScript · Vite 5
**Design Method:** Chapter 23 — System Design (Hemant Jain)

---

## Team Roles

| Role | Responsibility |
|------|---------------|
| Team Lead / Integrator | Repository management, integration, final review |
| System Design Lead | Chapter 23 five-step process, architecture diagrams |
| Data Structures Lead | 9 DSA structures in `backend/structures/` |
| Algorithms Lead | MergeSort, BinarySearch, BFS/DFS, complexity analysis |
| Backend / API Developer | Flask server, 15 REST endpoints, simulator |
| Auth Developer | JWT auth, RBAC, token refresh |
| UI Developer | React/TypeScript frontend, 6 tabs, Recharts |
| Testing & QA Lead | 37 pytest cases, 15-test Postman suite |
| Performance / Benchmark Lead | Empirical Big-O benchmarks, timing matrix |
| Demo / Video Presenter | YouTube walkthrough, script, narration |

---

## Repository Structure

```
stock-query-server/
│
├── docs/
│   ├── system_design.md          ← Chapter 23 five-step design (primary design doc)
│   ├── final_report.md           ← 8–12 page technical report (Chapter 23 compliant)
│   ├── architecture.svg          ← System architecture diagram
│   └── architecture.py           ← SVG diagram generator script
│
├── backend/
│   ├── structures/               ← PHASE 2: Core DSA Engine (9 structures)
│   │   ├── stock_map.py          ← Hash Map  — O(1) symbol lookup
│   │   ├── ingestion_queue.py    ← Queue     — O(1) FIFO tick buffer
│   │   ├── alert_stack.py        ← Stack     — O(1) LIFO + undo
│   │   ├── top_k_heap.py         ← Min-Heap  — O(log K) top-K
│   │   ├── sector_graph.py       ← Graph     — O(V+E) BFS/DFS
│   │   ├── merge_sort.py         ← Sort      — O(n log n)
│   │   ├── binary_search.py      ← Search    — O(log n)
│   │   ├── lru_cache.py          ← Composite — HashMap + Doubly Linked List
│   │   └── benchmarks.py         ← Empirical timing at N=1K/10K/100K
│   │
│   ├── api/                      ← PHASE 3: Flask API + Auth + Simulator
│   │   ├── server.py             ← 15 REST endpoints
│   │   ├── auth.py               ← JWT + RBAC (admin/analyst/viewer)
│   │   └── simulator.py          ← Background market data thread
│   │
│   ├── tests/                    ← PHASE 4: Tests
│   │   ├── test_engine.py        ← 37 pytest unit tests
│   │   └── test_suite.postman_collection.json  ← 15-test Postman suite
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/                      ← PHASE 5: React/TypeScript UI
│   │   ├── components/           ← 6 tab components
│   │   ├── context/              ← AuthContext + apiFetch
│   │   └── styles/               ← Dark finance theme
│   │
│   ├── vanilla/                  ← PHASE 6: Static HTML/JS fallback
│   └── package.json
│
├── api/
│   └── index.py                  ← Vercel serverless entry point
│
├── requirements.txt              ← Root-level deps (for Vercel)
├── vercel.json                   ← Deployment config
├── start.bat                     ← Windows quick-start
├── start.sh                      ← Linux/Mac quick-start
└── README.md                     ← This file
```

---

## Chapter 23 — Five-Step System Design Process

> Full detail in `docs/system_design.md`. Summaries below.

### Step 1: Use Cases

| ID | Actor | Use Case | DSA Structure |
|----|-------|----------|---------------|
| UC1 | All | O(1) stock lookup by ticker symbol | Hash Map |
| UC2 | Simulator | Buffer price ticks in arrival order | Queue (FIFO) |
| UC3 | Analyst | Create alert; undo last alert | Stack (LIFO) |
| UC4 | All | Retrieve top-K stocks by volume/gain | Min-Heap |
| UC5 | All | Explore sector correlations (BFS/DFS) | Graph |
| UC6 | All | Sort 90-day price history | Merge Sort O(n log n) |
| UC7 | All | Search prices by range | Binary Search O(log n) |
| UC8 | All | Register, login, refresh token, logout | JWT + RBAC |
| UC9 | Admin | Measure empirical Big-O at N=1K/10K/100K | Benchmarks |
| UC10 | Simulator | Seed 24 stocks with 90-day history on startup | Internal init |

### Step 2: Constraints and Analysis

| Constraint | Value | Justification |
|------------|-------|---------------|
| Stocks tracked | N ≤ 10,000 | HashMap load factor < 0.75 |
| Ticks buffered | M ≤ 100,000 | Drained every 2 s by simulator |
| Alerts in stack | A ≤ 1,000 | Hard cap enforced in `alert_stack.py` |
| Top-K heap size | K ≤ 100 | O(log K) ≈ 7 comparisons at K=100 |
| Sectors (graph nodes) | V ≤ 50 | Realistic global sector count |
| JWT expiry | 3,600 s | Standard; refresh token valid 7 days |
| Memory budget | < 512 MB | All in-memory, no external DB (Phase 1) |
| Target latency | p99 < 200 ms | All core ops sub-millisecond |

### Step 3: Basic Design

Three-layer architecture:

```
[ Client Layer ]   React/TS UI  |  Vanilla HTML  |  Postman
                        ↓  HTTP/HTTPS + JWT Bearer
[ API Layer    ]   Flask REST (server.py)  +  auth.py  +  simulator.py
                        ↓  Python imports
[ DSA Engine   ]   StockHashMap · IngestionQueue · AlertStack
                   TopKHeap · SectorGraph · MergeSort · BinarySearch
```

15 REST endpoints covering all 7 DSA structures — see `docs/system_design.md` Step 3 for full endpoint table.

### Step 4: Bottlenecks

| Bottleneck | Root Cause | Fix Applied |
|------------|-----------|-------------|
| BFS O(V²+E) | `list.pop(0)` is O(n) | Use `deque.popleft()` → O(V+E) |
| Top-K rebuild per request | Sorting all N stocks | Heap maintained incrementally per tick |
| Tick fan-out at scale | O(N) per tick cycle | Batched drain every 2 s |
| Sort on every history call | MergeSort O(n log n) per request | Lazy sort — only on `/history` request |
| Cold-start data loss | In-memory only | Simulator re-seeds on every startup |
| Refresh token storm | Parallel 401 retries | Client-side refresh queue |

### Step 5: Scalability

Growth path across 4 phases:

| Phase | What Changes |
|-------|-------------|
| **Phase 1 (this build)** | In-memory DSA, simulated data, JWT, React + vanilla UI, full test suite |
| **Phase 2** | PostgreSQL persistence — users, stocks, alerts survive restart |
| **Phase 3** | Live market data via Yahoo Finance / Alpha Vantage API |
| **Phase 4** | Redis caching, rate limiting, Docker, CI/CD, horizontal scaling |

---

## Data Structures & Complexity

| Structure | Use Case | Insert | Lookup | Space |
|-----------|----------|--------|--------|-------|
| **StockHashMap** | Symbol → Record | O(1) avg | O(1) avg | O(n) |
| **IngestionQueue** | FIFO tick buffer | O(1) | O(1) peek | O(n) |
| **AlertStack** | LIFO alerts + undo | O(1) | O(1) peek | O(n) |
| **TopKHeap** | Top-K ranking | O(log K) | O(1) peek-min | O(K) |
| **SectorGraph** | BFS/DFS traversal | O(1) edge | O(V+E) BFS/DFS | O(V+E) |
| **MergeSort** | Sort price history | — | — | O(n log n) time, O(n) space |
| **BinarySearch** | Price range query | — | O(log n) | O(1) extra |
| **LRUCache** | Hot stock caching | O(1) | O(1) | O(capacity) |

---

## API Reference

### Auth Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | None | Register new user |
| POST | `/api/auth/login` | None | Login → JWT pair |
| GET | `/api/auth/me` | JWT | Current user profile |
| POST | `/api/auth/refresh` | None | Rotate access token |
| POST | `/api/auth/logout` | JWT | Invalidate refresh token |

### Data Endpoints
| Method | Endpoint | Auth | DSA Used |
|--------|----------|------|----------|
| GET | `/api/health` | None | — |
| GET | `/api/stocks` | JWT | HashMap.all_records |
| PUT | `/api/stocks` | JWT+admin | HashMap.put/update |
| GET | `/api/stocks/<sym>` | JWT | HashMap.get |
| GET | `/api/stocks/<sym>/history` | JWT | MergeSort |
| GET | `/api/stocks/sorted` | JWT | MergeSort |
| POST | `/api/stocks/search` | JWT | BinarySearch |
| GET | `/api/stocks/top` | JWT | TopKHeap |
| GET | `/api/stocks/sector/<s>/friends` | JWT | SectorGraph BFS |
| GET | `/api/stocks/sector/<s>/friends/DFS` | JWT | SectorGraph DFS |
| GET | `/api/alerts` | JWT | AlertStack |
| POST | `/api/alerts` | JWT+analyst | AlertStack.push |
| DELETE | `/api/alerts/undo` | JWT+analyst | AlertStack.pop+undo |
| GET | `/api/benchmarks` | JWT+admin | All structures |
| GET | `/api/cache/stats` | JWT | Counter |

### Role Permissions
| Role | Read Stocks | Create Alerts | Upsert Stocks | Run Benchmarks |
|------|------------|--------------|---------------|---------------|
| viewer | ✅ | ❌ | ❌ | ❌ |
| analyst | ✅ | ✅ | ❌ | ❌ |
| admin | ✅ | ✅ | ✅ | ✅ |

---

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python api/server.py
# → http://localhost:5000
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Frontend (Vanilla — no install needed)
```
open frontend/vanilla/index.html  (double-click in Explorer)
```

### Run All Tests
```bash
cd backend
python -m pytest tests/test_engine.py -v
```

### Windows One-Click Start
```
double-click start.bat
```

---

## Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| `admin@stockquery.io` | `admin123` | Admin — full access |
| `analyst@stockquery.io` | `analyst123` | Analyst — create alerts |
| `viewer@stockquery.io` | `viewer123` | Viewer — read only |

---

## Empirical Complexity Matrix

*(populated after Phase 6 benchmarks run)*

| Structure | Operation | O-Class | N=1K | N=10K | N=100K |
|-----------|-----------|---------|------|-------|--------|
| StockHashMap | put | O(1) | — | — | — |
| StockHashMap | get | O(1) | — | — | — |
| IngestionQueue | enqueue | O(1) | — | — | — |
| IngestionQueue | drain | O(n) | — | — | — |
| AlertStack | push | O(1) | — | — | — |
| AlertStack | pop | O(1) | — | — | — |
| TopKHeap | push | O(log K) | — | — | — |
| TopKHeap | top_k | O(K log K) | — | — | — |
| SectorGraph | BFS | O(V+E) | — | — | — |
| SectorGraph | DFS | O(V+E) | — | — | — |
| MergeSort | sort | O(n log n) | — | — | — |
| BinarySearch | search | O(log n) | — | — | — |

---

## Demo Video

🎥 [YouTube — 7-minute walkthrough](_link_to_be_added_)

Contents:
1. System architecture and Chapter 23 five-step design
2. DSA engine demo — all 7 structures live
3. Postman 15-test suite execution
4. Frontend — Dashboard, Alerts, Graph, Benchmarks tabs
5. Auth flow — JWT login, role guards
6. Scalability and bottleneck discussion

---

## License

MIT — Educational project, CS Data Structures & Algorithms.
