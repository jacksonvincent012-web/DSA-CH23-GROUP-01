# Team Workflow Guide

**Repo:** `https://github.com/jacksonvincent012-web/-stockqueryserver.git`  
**Current commit:** `db6829f` — all code in one batch  

## Goal
Each team member must commit their assigned files from **their own GitHub account** so the commit history shows 6 contributors.

---

## Step 1 — Everyone: Fork & Clone

```bash
# 1. Go to the repo URL and click "Fork" (top-right)
#    Fork to YOUR OWN GitHub account

# 2. Clone YOUR fork
git clone https://github.com/YOUR_USERNAME/-stockqueryserver.git
cd -stockqueryserver

# 3. Add the original repo as upstream
git remote add upstream https://github.com/jacksonvincent012-web/-stockqueryserver.git

# 4. Pull the latest code
git pull upstream master
```

---

## Step 2 — Each Person: Commit Your Assigned Files

### Person 1 — Team Lead: `.gitignore`, `README.md`, `vercel.json`, `start.bat`, `start.sh`, `requirements.txt`, `docs/`

```bash
git add .gitignore README.md vercel.json start.bat start.sh requirements.txt docs/
git commit -m "docs: add project setup, README, start scripts, and Chapter 23 design docs"
git push origin master
```

---

### Person 2 — DSA Lead: `backend/structures/` (stock_map, ingestion_queue, alert_stack, top_k_heap, sector_graph, lru_cache)

```bash
git add backend/structures/__init__.py backend/structures/stock_map.py
git commit -m "feat: add StockHashMap — hash table O(1) symbol lookup"

git add backend/structures/ingestion_queue.py
git commit -m "feat: add IngestionQueue — deque FIFO tick buffer"

git add backend/structures/alert_stack.py
git commit -m "feat: add AlertStack — LIFO stack with undo"

git add backend/structures/top_k_heap.py
git commit -m "feat: add TopKHeap — min-heap top-K ranking"

git add backend/structures/sector_graph.py
git commit -m "feat: add SectorGraph — adjacency-list BFS/DFS"

git add backend/structures/lru_cache.py backend/__init__.py
git commit -m "feat: add LRUCache — HashMap + doubly linked list composite"

git push origin master
```

---

### Person 3 — Algorithms Lead: `merge_sort.py`, `binary_search.py`, `benchmarks.py`

```bash
git add backend/structures/merge_sort.py
git commit -m "feat: add MergeSort — O(n log n) stable divide-and-conquer sort"

git add backend/structures/binary_search.py
git commit -m "feat: add BinarySearch — O(log n) with lower/upper bound and range search"

git add backend/structures/benchmarks.py
git commit -m "feat: add Benchmarks — empirical Big-O timing at N=1K/10K/100K"

git push origin master
```

---

### Person 4 — API Developer: `backend/api/server.py` + `backend/requirements.txt`

```bash
git add backend/api/__init__.py backend/api/server.py
git commit -m "feat: add Flask server with 22 REST endpoints covering all DSA structures"

git add backend/requirements.txt
git commit -m "chore: add project dependencies (Flask, Flask-CORS, PyJWT, pytest)"

git push origin master
```

---

### Person 5 — Auth + Simulator: `backend/api/auth.py`, `backend/api/simulator.py`, `api/index.py`

```bash
git add backend/api/auth.py
git commit -m "feat: add JWT auth with RBAC — admin/analyst/viewer roles"

git add backend/api/simulator.py
git commit -m "feat: add market simulator — seeds 10K stocks, generates live ticks every 2s"

git add api/index.py
git commit -m "feat: add Vercel serverless entry point"

git push origin master
```

---

### Person 6 — Testing Lead: `backend/tests/test_engine.py`

```bash
git add backend/tests/__init__.py backend/tests/test_engine.py
git commit -m "test: add 46 pytest cases covering all 9 DSA structures with edge cases"

git push origin master
```

---

## Step 3 — After Everyone Commits

Create a Pull Request from your fork to the original repo:

```bash
# On GitHub:
# 1. Go to YOUR forked repo
# 2. Click "Contribute" → "Open Pull Request"
# 3. Base repo: jacksonvincent012-web/-stockqueryserver
# 4. Create PR
```

The team lead merges all PRs. Final commit history will show 6 different authors.

---

## Verify

```bash
git log --oneline --all --graph
git shortlog -sn --all
```
