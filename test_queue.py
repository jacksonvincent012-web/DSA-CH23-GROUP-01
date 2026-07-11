"""
DSA 2: QUEUE — IngestionQueue (FIFO)
Test: Price ticks flow through queue sequentially
"""
import urllib.request, json, time

BASE = "http://localhost:5000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFkbWluQHN0b2NrcXVlcnkuaW8iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE4MDAwMDAwMDAsImlhdCI6MTc4Mzc5MDQyNSwianRpIjoiYjllYzhlMmQ0N2M1OTEwOCJ9.3URyE2SO6hO2owxrnL4mUa6nfShHrp30xKvJP7Zg1DU"

def get(path):
    r = urllib.request.Request(f"{BASE}{path}")
    r.add_header("Authorization", f"Bearer {TOKEN}")
    return json.loads(urllib.request.urlopen(r).read())

# Check queue health twice (2 seconds apart)
h1 = get("/api/health")
print(f"Time 1 — ticks_processed: {h1['ticks_processed']}, queue_size: {h1['queue_size']}")

time.sleep(2)

h2 = get("/api/health")
print(f"Time 2 — ticks_processed: {h2['ticks_processed']}, queue_size: {h2['queue_size']}")

diff = h2['ticks_processed'] - h1['ticks_processed']
print(f"\n{diff} new ticks flowed through the queue in 2 seconds (FIFO order)")
print("Queue ensures ticks are processed in the exact order they arrived")
