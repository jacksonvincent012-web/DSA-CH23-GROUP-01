"""
DSA 3: STACK — AlertStack (LIFO)
Test: Push alerts, pop last one (undo)
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

# Get fresh token
token = req("POST", "/api/auth/login",
    {"email": "admin@stockquery.io", "password": "admin123"})["access_token"]

# Push 3 alerts onto the stack (LIFO)
for s in ["AAPL", "MSFT", "NVDA"]:
    r = req("POST", "/api/alerts", {"symbol": s, "threshold": 500, "direction": "above"}, token)
    print(f"Push: {r['message']}")

# View stack (bottom → top)
alerts = req("GET", "/api/alerts", token=token)
print(f"\nStack ({alerts['count']} alerts, top is last):")
for i, a in enumerate(alerts["alerts"]):
    print(f"  [{i}] {a['symbol']} — {a['direction']} ${a['threshold']}")

# Pop the top (NVDA — LIFO)
r = req("DELETE", "/api/alerts/undo", token=token)
print(f"\nPop: {r['message']} — removed {r['removed']['symbol']}")

alerts = req("GET", "/api/alerts", token=token)
print(f"Stack now: {[a['symbol'] for a in alerts['alerts']]}")
print("LIFO: Last In (NVDA) was First Out")
print("Stack push: O(1), pop: O(1)")
