"""
DSA 1: HASH MAP — StockHashMap
Test: O(1) stock lookup by symbol
"""
import urllib.request, json

BASE = "http://localhost:5000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFkbWluQHN0b2NrcXVlcnkuaW8iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3ODM3OTQwMjUsImlhdCI6MTc4Mzc5MDQyNSwianRpIjoiYjllYzhlMmQ0N2M1OTEwOCJ9.3URyE2SO6hO2owxrnL4mUa6nfShHrp30xKvJP7Zg1DU"

def get(path):
    r = urllib.request.Request(f"{BASE}{path}")
    r.add_header("Authorization", f"Bearer {TOKEN}")
    return json.loads(urllib.request.urlopen(r).read())

# 1. Lookup AAPL (O(1) hash → bucket → record)
aapl = get("/api/stocks/AAPL")
print("GET /api/stocks/AAPL")
print(json.dumps(aapl, indent=2))

# 2. Lookup XOM (O(1) — same speed, different bucket)
xom = get("/api/stocks/XOM")
print("\nGET /api/stocks/XOM")
print(json.dumps(xom, indent=2))

# 3. List all 10,000 stocks (iterates hash map values)
all_stocks = get("/api/stocks")
print(f"\nGET /api/stocks -> {all_stocks['count']} stocks (HashMap iteration O(n))")
print(f"First 3: {[s['symbol'] for s in all_stocks['stocks'][:3]]}")
