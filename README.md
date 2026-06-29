# Stock Query Server — DSA Learning Journey

**Theme C, Variant C3:** Alerts + Event Queue  
**Team:** 6 Members | **Course:** BIT3208 — DSA (Chapter 23, Hemant Jain)  
**Stack:** Python 3.14 · Flask 3.0 · JWT · In-Memory · 10,000 Stocks  
**Repo:** [DSA-CH23-GROUP-01](https://github.com/jacksonvincent012-web/DSA-CH23-GROUP-01)

---

## Problem

Build a real-time stock server that handles lookups, top-K by volume, sector exploration, price alerts with undo, sorted history, price-range search, and live tick simulation — all in-memory, no database, with JWT role-based access.

---

## 8 DSA Structures — Problem → Solution

| Structure | Problem It Solves | Complexity |
|-----------|-------------------|------------|
| **HashMap** (`stock_map.py`) | O(1) stock lookup by ticker | O(1) avg |
| **Queue** (`ingestion_queue.py`) | FIFO buffer for tick ingestion (avoids `list.pop(0)` O(n) trap) | O(1) |
| **Stack** (`alert_stack.py`) | LIFO alerts with undo capability | O(1) |
| **Min-Heap** (`top_k_heap.py`) | Top-K by volume without sorting all 10K records | O(n log k) |
| **Graph** (`sector_graph.py`) | Sector relationships via BFS/DFS traversal | O(V+E) |
| **MergeSort** (`merge_sort.py`) | Stable O(n log n) stock sorting by price/volume | O(n log n) |
| **BinarySearch** (`binary_search.py`) | Fast price-range queries on sorted data | O(log n) |
| **LRU Cache** (`lru_cache.py`) | Hot-stock caching (HashMap + Doubly Linked List) | O(1) |

---

## Bottlenecks Found & Fixed

| Bottleneck | Root Cause | Fix |
|------------|-----------|-----|
| Top-K linear scan | Sorting all 10K per request O(n log n) | TopKHeap incremental O(log k) |
| Queue O(n) dequeue | `list.pop(0)` shifts all elements | `deque.popleft()` O(1) |
| Repeated stock lookups | Hitting HashMap every request | LRU Cache (50 entries) |
| Graph recursion depth | DFS hit Python recursion limit | Iterative DFS with explicit stack |
| Cold start data loss | Restart wiped stocks | Simulator re-seeds 24 anchors |

---

## Architecture

```
Client → JWT Middleware → 22 REST Endpoints → DSA Engine ← Simulator Thread
                              ↕
                          LRU Cache (50)
                              ↕
                    StockHashMap (10,000 stocks)
```

---

## JWT Roles

| Role | Permissions |
|------|-----------|
| **Viewer** | Lookup, top-K, sectors, sort, search, health |
| **Analyst** | Viewer + create/undo alerts |
| **Admin** | Analyst + benchmarks, upsert stocks, clear cache |

**Pre-seeded accounts:** `admin@stockquery.io`, `analyst@stockquery.io`, `viewer@stockquery.io` (password: `user123`, admin: `admin123`)

---

## 22 REST Endpoints

| Method | Endpoint | DSA Used |
|--------|----------|----------|
| GET | `/api/health` | Queue (queue_size) |
| POST | `/api/auth/login` | JWT |
| GET | `/api/stocks/<symbol>` | HashMap |
| PUT | `/api/stocks/<symbol>` | HashMap (admin) |
| DELETE | `/api/stocks/<symbol>` | HashMap (admin) |
| GET | `/api/stocks/top?metric=&k=` | Min-Heap |
| GET | `/api/stocks/sector/<s>/friends` | Graph BFS |
| GET | `/api/stocks/sector/<s>/friends/DFS` | Graph DFS |
| GET | `/api/stocks/sorted?metric=&order=` | MergeSort |
| POST | `/api/stocks/search` | BinarySearch |
| POST | `/api/alerts` | Stack (push) |
| DELETE | `/api/alerts` | Stack (pop/undo) |
| GET | `/api/alerts` | Stack (list) |
| GET | `/api/cache/stats` | LRU Cache |
| POST | `/api/cache/clear` | LRU Cache (admin) |
| GET | `/api/benchmarks` | All DSA timing |

---

## Testing

```bash
python -m pytest backend/tests/test_engine.py -v    # 46/46 passing
```

---

## Quick Start

```bash
pip install -r backend/requirements.txt
python index.py           # seeds 10K stocks, starts on :5000
```

---

## Deliverables

- **`LOGBOOK.docx`** — Full learning journey with screenshots
- **`README.md`** — This summary
- **`backend/`** — Complete source code (8 DSA, server, auth, simulator, 46 tests)
- **`docs/architecture.svg`** — System architecture diagram

*See `LOGBOOK.docx` for detailed DSA decision process, benchmarks, team reflections, and 25 screenshots.*
