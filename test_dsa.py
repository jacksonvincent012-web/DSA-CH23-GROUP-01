"""Live API test for all 7 data structures."""
import requests, json

BASE = "http://localhost:5000"

# Login
r = requests.post(f"{BASE}/api/auth/login", json={"email":"admin@stockquery.io","password":"admin123"})
token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}
jh = {**h, "Content-Type": "application/json"}

def sec(n, s):
    print(f"\n{'='*60}")
    print(f"  {n}. {s}")
    print('='*60)

# 1. HASHMAP
sec(1, "HASHMAP - GET /api/stocks (list 2)")
r = requests.get(f"{BASE}/api/stocks?limit=2", headers=h)
data = r.json()
print(f"  Total stocks: {len(data)}" if isinstance(data, list) else f"  {json.dumps(data, indent=2)[:300]}")

sec(2, "HASHMAP - GET /api/stocks/AAPL")
r = requests.get(f"{BASE}/api/stocks/AAPL", headers=h)
print(f"  {json.dumps(r.json(), indent=2)[:400]}")

# 3. QUEUE (via health)
sec(3, "QUEUE - GET /api/health (queue_size)")
r = requests.get(f"{BASE}/api/health")
print(f"  {json.dumps(r.json(), indent=2)}")

# 4. STACK - push alert
sec(4, "STACK - POST /api/alerts (push)")
r = requests.post(f"{BASE}/api/alerts", json={"symbol":"MSFT","message":"test","type":"volume_spike"}, headers=jh)
print(f"  {json.dumps(r.json(), indent=2)}")

# 5. STACK - get alerts
sec(5, "STACK - GET /api/alerts (list)")
r = requests.get(f"{BASE}/api/alerts", headers=h)
print(f"  {json.dumps(r.json(), indent=2)[:400]}")

# 6. HEAP
sec(6, "HEAP - GET /api/stocks/top?metric=volume&k=5")
r = requests.get(f"{BASE}/api/stocks/top", params={"metric":"volume","k":5}, headers=h)
print(f"  {json.dumps(r.json(), indent=2)[:600]}")

# 7. GRAPH BFS
sec(7, "GRAPH BFS - GET /api/stocks/sector/TECH/friends")
r = requests.get(f"{BASE}/api/stocks/sector/TECH/friends", headers=h)
print(f"  {json.dumps(r.json(), indent=2)[:500]}")

# 8. GRAPH DFS
sec(8, "GRAPH DFS - GET /api/stocks/sector/HEALTHCARE/friends/DFS")
r = requests.get(f"{BASE}/api/stocks/sector/HEALTHCARE/friends/DFS", headers=h)
print(f"  {json.dumps(r.json(), indent=2)[:500]}")

# 9. MERGE SORT + BINARY SEARCH
sec(9, "MERGE SORT + BINARY SEARCH - POST /api/stocks/search")
r = requests.post(f"{BASE}/api/stocks/search", json={"metric":"price","range_start":100,"range_end":500}, headers=jh)
print(f"  Stocks in $100-500 range: {len(r.json().get('stocks', r.json()))}")
print(f"  {json.dumps(r.json(), indent=2)[:400]}")

# 10. MERGE SORT - sorted list
sec(10, "MERGE SORT - GET /api/stocks/sorted?metric=price&order=asc")
r = requests.get(f"{BASE}/api/stocks/sorted", params={"metric":"price","order":"asc"}, headers=h)
data = r.json()
stocks = data.get("stocks", data)
print(f"  Count: {data.get('count', len(stocks))}, cheapest: {stocks[0] if stocks else 'none'}")

# 11. LRU CACHE
sec(11, "LRU CACHE - GET /api/cache/stats")
r = requests.get(f"{BASE}/api/cache/stats", headers=h)
print(f"  {json.dumps(r.json(), indent=2)}")

# 12. BENCHMARKS
sec(12, "BENCHMARKS - GET /api/benchmarks")
r = requests.get(f"{BASE}/api/benchmarks", headers=h)
bm = r.json()
for name, result in bm.items():
    print(f"  {name}: {result}")
