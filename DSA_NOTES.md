# DSA Learning Journey — Test Notes

---

## DSA 1: HASH MAP — StockHashMap `backend/structures/stock_map.py`

### What is a Hash Map?
A hash map is like a **giant filing cabinet with labeled drawers**. You give it a label (like `"AAPL"`), it instantly knows which drawer to open — no searching through all the files.

**Real-world analogy:** A coat check counter. You hand over ticket `"AAPL"`, the attendant goes straight to rack `"AAPL"` and hands you your coat. They don't check every rack.

### How the code works
```python
self._map: dict[str, StockRecord] = {}   # The filing cabinet
```
```python
def get(self, symbol):                    # O(1) — instant
    return self._map.get(symbol.upper())  # Hash "AAPL" -> bucket -> record
```
Python's `dict` hashes the string `"AAPL"` into a number, uses that number to find the exact bucket. Every bucket access takes the same time — whether there are 10 items or 10 million.

### Command
```powershell
curl.exe -s http://localhost:5000/api/stocks/XOM -H "Authorization: Bearer <token>"
```

### Result
```json
{
  "symbol": "XOM",
  "price": 112.6,
  "volume": 7000000,
  "sector": "ENERGY",
  "gain_7d_pct": -1.61,
  "price_history_count": 90
}
```

### What the output means
| Field | Meaning |
|-------|---------|
| `symbol: "XOM"` | Ticker for Exxon Mobil |
| `price: 112.6` | Latest trade price ($112.60) |
| `volume: 7,000,000` | Shares traded recently |
| `sector: "ENERGY"` | Industry sector |
| `gain_7d_pct: -1.61` | Lost 1.61% in the last 7 days |
| `price_history_count: 90` | 90 days of price history stored |

### Why O(1) matters
The hash map finds `"XOM"` in **one step** — hash → bucket → done. If we used a list, we'd have to scan all 10,000 stocks to find XOM (O(n)).

**Test file:** `test_hashmap.py`

---

## DSA 2: QUEUE — IngestionQueue `backend/structures/ingestion_queue.py`

### What is a Queue?
A queue is a **line of people waiting**. The first person in line is the first person served. New people join at the back.

**Real-world analogy:** A ticketing line at a counter. Person A arrives first (front of line), then B, then C. A gets served first, then B, then C. **FIFO = First In, First Out.**

### How the code works
```python
from collections import deque
self._queue: deque[Tick] = deque()       # The waiting line
```
```python
def enqueue(self, tick):    # O(1) — person joins the back
    self._queue.append(tick)

def dequeue(self):          # O(1) — person at front gets served
    return self._queue.popleft()
```
The simulator adds price ticks (price updates) to the queue every 2 seconds. The server removes them from the front and updates the hash map. The `deque` (doubly-linked list) makes adding/removing from either end instant.

### Command
```powershell
curl.exe -s http://localhost:5000/api/health -H "Authorization: Bearer <token>"
```

### Result
```json
{
  "status": "ok",
  "stocks": 10000,
  "queue_size": 0,
  "ticks_processed": 735,
  "alerts": 2,
  "timestamp": "2026-07-11T20:56:38"
}
```

### What the output means
| Field | Meaning |
|-------|---------|
| `stocks: 10,000` | Hash map holds 10,000 stocks |
| `queue_size: 0` | No ticks waiting (server just drained them) |
| `ticks_processed: 735` | 735 price updates have flowed through the queue so far |
| `alerts: 2` | 2 price alerts still sitting on the stack |

### Why deque over list
`list.pop(0)` removes the first element but then **shifts every remaining element left** — O(n), slow. `deque.popleft()` just moves a **pointer** — O(1), instant. With 10,000+ ticks, this matters.

### What to watch
Run the health endpoint twice, a few seconds apart. `ticks_processed` increases because the simulator keeps adding ticks to the queue and the server keeps draining them — **all in FIFO order.**

**Test file:** `test_queue.py`

---

## DSA 3: STACK — AlertStack `backend/structures/alert_stack.py`

### What is a Stack?
A stack is like a **stack of plates**. You put a new plate on top. When you need a plate, you take the top one. The last plate you put on is the first one you take off.

**Real-world analogy:** Your browser's back button. You visit Page A → Page B → Page C. Clicking "Back" takes you to C first (the most recent), then B, then A. **LIFO = Last In, First Out.**

### How the code works
```python
self._stack: list[Alert] = []      # The plate stack
self._undo_buf: list[Alert] = []   # The "put back" tray
```
```python
def push(self, alert):        # O(1) — put new plate on top
    self._stack.append(alert)

def pop(self):                # O(1) — take top plate off
    removed = self._stack.pop()
    self._undo_buf.append(removed)  # Save it in case of undo
    return removed
```

### Command
```powershell
python test_stack.py
```

### Result
```
Push: Alert created  (AAPL)     ← stack: [AAPL]
Push: Alert created  (MSFT)     ← stack: [AAPL, MSFT]
Push: Alert created  (NVDA)     ← stack: [AAPL, MSFT, NVDA]

Stack (5 alerts, top is last):
  [0] AAPL — above $500.0     ← bottom (oldest)
  [1] MSFT — above $500.0
  [2] AAPL — above $500.0     ← from earlier test run
  [3] MSFT — above $500.0     ← from earlier test run
  [4] NVDA — above $500.0     ← TOP (newest, pushed last)

Pop: Undo successful — removed NVDA
Stack now: ['AAPL', 'MSFT', 'AAPL', 'MSFT']
```

### What the output means
- Each `Push` adds an alert to the **top** of the stack
- The stack prints bottom (oldest) → top (newest)
- `NVDA` was pushed last, so it sits on **top**
- `Pop` removes the **top** plate = NVDA (LIFO)
- The undo buffer saved NVDA, so we could restore it if needed

### Why LIFO matters for alerts
Analysts review alerts newest-first. The most urgent alert (just created) should be seen first. If you accidentally delete it, undo restores just that one.

**Test file:** `test_stack.py`

---

## DSA 4: HEAP — TopKHeap `backend/structures/top_k_heap.py`

### What is a Heap?
A heap is a **priority queue** — it keeps track of the "biggest" or "smallest" items without sorting everything.

**Real-world analogy:** A talent show judge keeping a clipboard of the **top 10** contestants. When a new contestant performs, the judge checks: "Are you better than #10?" If yes, #10 is kicked off the list and the new contestant is inserted in the right spot. The judge never needs to rank all 1000 contestants — just maintain the top 10.

### How the code works
```python
# Min-heap of size K=10
# Root = smallest volume among the top-10 candidates
self._heap: list[tuple] = []
```
```python
def push(self, symbol, metric_value):        # O(log K)
    if len(self._heap) < self.k:
        heapq.heappush(self._heap, item)     # Heap not full -> accept
    elif metric_value > self._heap[0][0]:    # Bigger than #10?
        heapq.heapreplace(self._heap, item)  # Kick #10 out, insert new
    # If metric <= root -> discard (not good enough)
```
The heap always holds exactly the **K largest values** seen. The smallest of those K (the root) is the "gatekeeper" — any new item must beat it to enter the top-K.

### Command
```powershell
python test_heap.py
```

### Result
```
=== HEAP: Top 10 Stocks by Volume ===

   1. A0300    volume= 59,988,129  price=$1016.61
   2. J0044    volume= 59,987,996  price=$949.45
   3. X0130    volume= 59,981,667  price=$55.85
   4. U0143    volume= 59,979,041  price=$530.72
   5. B0330    volume= 59,973,379  price=$417.05
   6. M0240    volume= 59,972,412  price=$928.64
   7. N0113    volume= 59,971,304  price=$466.93
   8. J0160    volume= 59,970,690  price=$102.28
   9. T0057    volume= 59,958,461  price=$608.53
  10. Z0133    volume= 59,955,548  price=$438.34
```

### What the output means
- These are the **10 stocks with the highest trading volume** out of 10,000
- Stock `A0300` has the highest volume (59.9 million shares)
- Stock `Z0133` is #10 (gatekeeper) — any new stock needs volume > 59.9M to enter
- The price column shows these are random simulated stock tickers

### Why a heap instead of sorting
**Sorting all 10,000 stocks** every time someone asks for top-10: **O(N log N)** = ~130,000 comparisons.

**Heap approach:** Each new tick just does **O(log K)** = ~3 comparisons (K=10). That's **43,000x faster** for a single update.

### The min-heap trick explained
```
Heap stores (volume, symbol) tuples. K=10.
Root = smallest volume in top-10 = 59,955,548 (Z0133).
New stock with volume 60,000,000 > 59,955,548? → Yes, replace root, re-heapify.
New stock with volume 50,000,000 < 59,955,548? → Discard, not top-10 material.
```

**Test file:** `test_heap.py`

---

## DSA 5: GRAPH — BFS (Breadth-First Search) `backend/structures/sector_graph.py`

### What is BFS?
BFS explores a graph **level by level** — like ripples in a pond. Start at one node, visit all its neighbors first, then the neighbors' neighbors, etc.

**Real-world analogy:** Finding the shortest route on a subway map. You check all stations 1 stop away, then 2 stops away, then 3 stops away. The first time you reach your destination, that's the shortest path.

### Command
```powershell
curl.exe -s http://localhost:5000/api/stocks/sector/TECH/friends -H "Authorization: Bearer <token>"
```

### Result
```json
{
  "start": "TECH",
  "bfs_order": ["TECH", "MEDIA", "FINANCE", "CONSUMER", "RETAIL", "ENERGY", "HEALTHCARE", "TRANSPORT"],
  "sector_stocks": {
    "CONSUMER": ["AMZN", "WMT", "KO", ...],
    "ENERGY": ["XOM", "CVX", "COP", ...],
    "FINANCE": ["JPM", "GS", "V", ...],
    "HEALTHCARE": ["JNJ", "PFE", "UNH", ...],
    "MEDIA": ["META", "DIS", "NFLX", ...],
    "RETAIL": ["A0006", "A0016", ...],
    "TECH": ["AAPL", "MSFT", "GOOGL", ...],
    "TRANSPORT": ["A0007", "A0017", ...]
  }
}
```

### What the output means
- Starting at **TECH**, BFS visits:
  - **Level 1 (1 step away):** MEDIA (TECH's direct neighbor)
  - **Level 2 (2 steps away):** FINANCE, CONSUMER
  - **Level 3 (3 steps away):** RETAIL, ENERGY
  - **Level 4+ :** HEALTHCARE, TRANSPORT
- BFS finds the **shortest path** — the minimum number of edges to reach any sector
- Each sector shows its stocks underneath

### Why BFS is used here
BFS guarantees the shortest path in an unweighted graph. If you ask "how is TECH connected to HEALTHCARE?", BFS gives the fewest jumps. This matters for finding related sectors quickly.

---

## DSA 6: GRAPH — DFS (Depth-First Search) `backend/structures/sector_graph.py`

### What is DFS?
DFS explores a graph by going **deep first** — like exploring a maze by following one wall until you hit a dead end, then backtracking.

**Real-world analogy:** Solving a maze. You pick a direction and walk until you hit a wall, then backtrack and try another path. You go deep before going wide.

### Command
```powershell
curl.exe -s http://localhost:5000/api/stocks/sector/TECH/friends/DFS -H "Authorization: Bearer <token>"
```

### Result
```json
{
  "start": "TECH",
  "dfs_order": ["TECH", "MEDIA", "CONSUMER", "ENERGY", "TRANSPORT", "RETAIL", "FINANCE", "HEALTHCARE"]
}
```

### BFS vs DFS — the difference
```
BFS: TECH → MEDIA → FINANCE → CONSUMER → RETAIL → ENERGY → HEALTHCARE → TRANSPORT
     (level by level — wide first)

DFS: TECH → MEDIA → CONSUMER → ENERGY → TRANSPORT → RETAIL → FINANCE → HEALTHCARE
     (deep dive — go as far as possible before backtracking)
```

### Why both matter
| | BFS | DFS |
|---|---|---|
| Strategy | Explore neighbors first | Go deep first |
| Data structure | Queue (FIFO) | Stack (LIFO) |
| Best for | Shortest path, social networks | Maze solving, puzzle games |
| Order | Level-order | Pre-order / depth-order |

---

## DSA 7: MERGE SORT — Sorting `backend/structures/merge_sort.py`

### What is Merge Sort?
A **divide-and-conquer** sorting algorithm. Split the array in half, sort each half recursively, then merge them back together in order.

**Real-world analogy:** Organizing a deck of cards. Split the deck in half, have two friends each sort their half, then merge the two sorted piles by comparing the top card of each.

### How the code works
```python
def merge_sort(items, key=lambda x: x):
    if len(items) <= 1:
        return items                     # Base case: single item = already sorted

    mid = len(items) // 2
    left = merge_sort(items[:mid], key)  # Sort left half
    right = merge_sort(items[mid:], key) # Sort right half
    return merge(left, right, key)       # Merge sorted halves
```
```
Steps for 10,000 stocks:
1. Split into 5,000 + 5,000
2. Split each into 2,500 + 2,500
3. Keep splitting until single elements
4. Merge pairs back up, comparing prices each time
```

### Command
```powershell
curl.exe -s http://localhost:5000/api/stocks/sorted -H "Authorization: Bearer <token>"
```

### Result
```json
{
  "count": 10000,
  "stocks": [
    {"symbol": "Q0380", "price": 5.02, ...},    ← cheapest
    {"symbol": "..." , "price": ...  , ...},
    {"symbol": "T0085", "price": 594.8, ...},    ← middle
    {"symbol": "..." , "price": ...  , ...},
    {"symbol": "C0073", "price": 1217.95, ...}   ← most expensive
  ]
}
```

### What the output means
- All 10,000 stocks sorted from **lowest price to highest price**
- Cheapest: `Q0380` at $5.02
- Most expensive: `C0073` at $1,217.95
- Middle (5,000th stock): `T0085` at $594.80

### Why Merge Sort O(n log n)
```
Level 1: 10,000 items → split into 2 × 5,000
Level 2: 5,000 → 2 × 2,500
Level 3: 2,500 → 2 × 1,250
...
Level 14: single elements (log₂ 10,000 ≈ 14 levels)

At each level, we touch all 10,000 items to merge.
Total: 10,000 × 14 = 140,000 operations = O(n log n)
```

### Why Merge Sort over Quick Sort
Merge Sort is **stable** (equal-price stocks keep original order) and guarantees O(n log n) even on already-sorted data. Quick Sort can degrade to O(n²) on sorted data.

---

## DSA 8: BINARY SEARCH — Range Search `backend/structures/binary_search.py`

### What is Binary Search?
**"Guess the number" strategy.** To find a price in a sorted list of 10,000 stocks, check the middle first. If it's too high, ignore the right half. If too low, ignore the left half. Repeat until found.

**Real-world analogy:** Looking up a word in a dictionary. You open to the middle. If your word comes later alphabetically, you ignore the first half and open the middle of the second half — you never scan page by page.

### How the code works
```python
def binary_search(sorted_list, value, key=lambda x: x):
    low, high = 0, len(sorted_list) - 1
    while low <= high:
        mid = (low + high) // 2
        if key(sorted_list[mid]) < value:
            low = mid + 1       # Too low → search right half
        elif key(sorted_list[mid]) > value:
            high = mid - 1      # Too high → search left half
        else:
            return mid          # Found it!
```
```
10,000 stocks → check middle (5,000)
Half the list → check middle (2,500 or 7,500)
Half again → check middle (1,250 or ...)
...after ~14 checks → found! (log₂ 10,000 ≈ 14)
```

### Command
```powershell
curl.exe -s -X POST http://localhost:5000/api/stocks/search -H "Content-Type: application/json" -d '{"low":100,"high":105}' -H "Authorization: Bearer <token>"
```

### Result
```json
{
  "low": 100,
  "high": 105,
  "count": 95,
  "stocks": [
    {"symbol": "A0428", "price": 100.09, ...},
    {"symbol": "A0366", "price": 100.15, ...},
    {"symbol": "A0482", "price": 100.39, ...},
    ...
  ]
}
```

### What the output means
- **95 stocks** found with prices between $100 and $105
- Each stock's symbol, exact price, and other details shown
- Binary search found the first stock ≥ $100, then scanned right until > $105

### Why binary search over linear scan
- **Linear scan** through 10,000 stocks: check every single one → **10,000 comparisons**
- **Binary search** on sorted data: split in half 14 times → **14 comparisons**
- For 100 million items: linear = 100M checks, binary = 27 checks

### The two-step process
1. **Merge Sort** sorts all 10,000 stocks by price (O(n log n))
2. **Binary Search** finds the lower bound ($100) in O(log n)
3. Scan right until price exceeds $105 (O(k) where k = 95 results)

**Test file:** `test_binary_search.py`

---

## BONUS: LRU CACHE — Hot Stock Lookup Accelerator `backend/structures/lru_cache.py`

### What is LRU Cache?
**Least Recently Used** cache. Keeps the most recently accessed stocks in a fast buffer. When full, evicts the one that hasn't been used in the longest time.

**Real-world analogy:** A desk drawer for frequently used files. If the drawer is full and you need a new file, you remove the one you haven't looked at in the longest time.

### Command
```powershell
curl.exe -s http://localhost:5000/api/cache/stats -H "Authorization: Bearer <token>"
```

### Result
```json
{
  "hits": 2,
  "misses": 10001,
  "size": 1,
  "capacity": 50
}
```

### What the output means
- `hits: 2` — 2 times a stock was found in cache (instant)
- `misses: 10,001` — 10,001 times stock was NOT in cache (had to hit hash map)
- `size: 1/50` — cache has 1 item stored (AAPL from our earlier lookup)
- When `size` hits 50, the least recently used stock gets evicted

### What makes it O(1)
The LRU Cache uses a **HashMap** (for instant O(1) lookups by key) + **Doubly Linked List** (for O(1) reordering when an item is accessed). This combination lets us find, move, and evict items in constant time.

---
