"""
DSA 4: HEAP — TopKHeap (Priority Queue)
Test: Top 10 stocks by volume using a size-bounded min-heap
"""
import urllib.request, json

BASE = "http://localhost:5000"

def req(method, path, data=None, token=None):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(f"{BASE}{path}", data=body, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    return json.loads(urllib.request.urlopen(r).read())

token = req("POST", "/api/auth/login",
    {"email": "admin@stockquery.io", "password": "admin123"})["access_token"]

d = req("GET", "/api/stocks/top?metric=volume&k=10", token=token)
print(f"=== HEAP: Top {len(d['top'])} Stocks by Volume ===")
print(f"Heap maintains only top-K (K=10), discards the rest\n")
for i, s in enumerate(d["top"], 1):
    print(f"  {i:2}. {s['symbol']:6s}  volume={s['volume']:>10,}  price=${s['price']:<8.2f}")

print(f"\nHow it works:")
print(f"  Min-heap of size K=10 stores (volume, symbol) tuples")
print(f"  Root = smallest volume among top-10 candidates")
print(f"  New item > root? -> replace root, sift down O(log K)")
print(f"  New item <= root? -> discard (not in top-10)")
print(f"  Final extraction: sorted(reverse=True) -> O(K log K)")
