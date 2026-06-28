"""
PHASE 3 — Flask REST API Server
15 DSA-backed endpoints + 5 auth endpoints
"""

import os
import sys
import json
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, g
from flask_cors import CORS

# Ensure backend/ is on the path for direct execution:  python api/server.py
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from structures.stock_map import StockHashMap, StockRecord
from structures.ingestion_queue import IngestionQueue
from structures.alert_stack import AlertStack, Alert
from structures.top_k_heap import TopKHeap
from structures.sector_graph import SectorGraph
from structures.merge_sort import merge_sort
from structures.binary_search import binary_search, range_search
from structures.benchmarks import run_all_benchmarks, format_benchmark_table
from structures.lru_cache import LRUCache

from api.auth import (
    require_auth, require_role, optional_auth,
    handle_register, handle_login, handle_refresh,
    handle_me, handle_logout,
)
from api.simulator import Simulator, SECTORS, SECTOR_EDGES

# ------------------------------------------------------------------ #
# App Initialisation                                                  #
# ------------------------------------------------------------------ #

app = Flask(__name__)
CORS(app, supports_credentials=True)

# DSA Engine instances (singletons attached to app)
app.stock_map = StockHashMap()
app.queue = IngestionQueue()
app.alerts = AlertStack()
app.heap = TopKHeap(k=10)
app.graph = SectorGraph()

# Build sector graph (mirrors simulator sectors)
for s in SECTORS:
    app.graph.add_node(s)
for f, t in SECTOR_EDGES:
    app.graph.add_edge(f, t)

# LRU Cache — hot stock lookups (HashMap + Doubly Linked List composite)
app.cache = LRUCache(capacity=50)

# Simulator
app.simulator = Simulator(app.stock_map, app.queue, app.alerts, app.heap)

# Start simulator (skip in serverless)
if os.environ.get("SERVERLESS", "") != "1":
    app.simulator.start()

# ------------------------------------------------------------------ #
# Helper: serialise a StockRecord to dict                              #
# ------------------------------------------------------------------ #

def _serialise(r: StockRecord) -> dict:
    return {
        "symbol": r.symbol,
        "price": r.price,
        "volume": r.volume,
        "sector": r.sector,
        "price_history_count": len(r.price_history),
    }

# ------------------------------------------------------------------ #
# Auth Routes                                                         #
# ------------------------------------------------------------------ #

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    result, status = handle_register(data)
    return jsonify(result), status

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    result, status = handle_login(data)
    return jsonify(result), status

@app.route("/api/auth/me", methods=["GET"])
@require_auth
def me():
    result, status = handle_me()
    return jsonify(result), status

@app.route("/api/auth/refresh", methods=["POST"])
def refresh():
    data = request.get_json(force=True) or {}
    result, status = handle_refresh(data)
    return jsonify(result), status

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    data = request.get_json(force=True) or {}
    result, status = handle_logout(data)
    return jsonify(result), status

# ------------------------------------------------------------------ #
# Health                                                              #
# ------------------------------------------------------------------ #

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "stocks": app.stock_map.size(),
        "alerts": app.alerts.size(),
        "queue_size": app.queue.size(),
        "ticks_processed": app.simulator.tick_count,
        "timestamp": datetime.now().isoformat(),
    })

# ------------------------------------------------------------------ #
# Stock CRUD                                                          #
# ------------------------------------------------------------------ #

@app.route("/api/stocks", methods=["GET"])
@require_auth
def list_stocks():
    records = app.stock_map.all_records()
    return jsonify({
        "count": len(records),
        "stocks": [_serialise(r) for r in records],
    })

@app.route("/api/stocks", methods=["PUT"])
@require_auth
@require_role("admin")
def upsert_stock():
    data = request.get_json(force=True) or {}
    symbol = data.get("symbol", "").upper()
    if not symbol:
        return jsonify({"error": "symbol required"}), 400
    price = float(data.get("price", 100))
    volume = int(data.get("volume", 0))
    sector = data.get("sector", "GENERAL")

    existing = app.stock_map.get(symbol)
    if existing:
        app.stock_map.update(symbol, price, volume)
        app.heap.push(symbol, volume)
        return jsonify({"message": f"{symbol} updated"}), 200
    else:
        record = StockRecord(symbol, price, volume, sector)
        app.stock_map.put(symbol, record)
        app.heap.push(symbol, volume)
        return jsonify({"message": f"{symbol} created"}), 201

@app.route("/api/stocks/<sym>", methods=["GET"])
@require_auth
def get_stock(sym):
    key = sym.upper()

    # Check LRU cache first
    cached = app.cache.get(key)
    if cached is not None:
        return jsonify(cached)

    record = app.stock_map.get(key)
    if not record:
        return jsonify({"error": "Stock not found"}), 404

    # Compute 7-day gain if we have enough history
    gain_7d = 0.0
    if len(record.price_history) >= 7:
        try:
            recent = record.price_history[-7:]
            first_close = float(recent[0][1])
            last_close = float(recent[-1][1])
            gain_7d = round((last_close - first_close) / first_close * 100, 2)
        except (ValueError, IndexError):
            pass

    result = _serialise(record)
    result["gain_7d_pct"] = gain_7d

    # Cache the result for subsequent reads
    app.cache.put(key, result)
    return jsonify(result)

# ------------------------------------------------------------------ #
# History — Merge Sort                                                #
# ------------------------------------------------------------------ #

@app.route("/api/stocks/<sym>/history", methods=["GET"])
@require_auth
def get_history(sym):
    record = app.stock_map.get(sym.upper())
    if not record:
        return jsonify({"error": "Stock not found"}), 404

    sorted_hist = merge_sort(record.price_history, key=lambda x: x[0])
    return jsonify({
        "symbol": sym.upper(),
        "history": [{"date": d, "price": p} for d, p in sorted_hist],
    })

# ------------------------------------------------------------------ #
# Sorted stocks — Merge Sort                                          #
# ------------------------------------------------------------------ #

@app.route("/api/stocks/sorted", methods=["GET"])
@require_auth
def get_sorted():
    records = app.stock_map.all_records()
    sorted_records = merge_sort(records, key=lambda r: r.price)
    return jsonify({
        "count": len(sorted_records),
        "stocks": [_serialise(r) for r in sorted_records],
    })

# ------------------------------------------------------------------ #
# Search — Binary Search                                              #
# ------------------------------------------------------------------ #

@app.route("/api/stocks/search", methods=["POST"])
@require_auth
def search_stocks():
    data = request.get_json(force=True) or {}
    low = float(data.get("low", 0))
    high = float(data.get("high", 1_000_000))

    records = app.stock_map.all_records()
    sorted_by_price = merge_sort(records, key=lambda r: r.price)
    matching = range_search(sorted_by_price, low, high, key=lambda r: r.price)
    return jsonify({
        "low": low,
        "high": high,
        "count": len(matching),
        "stocks": [_serialise(r) for r in matching],
    })

# ------------------------------------------------------------------ #
# Top-K — Heap                                                       #
# ------------------------------------------------------------------ #

@app.route("/api/stocks/top", methods=["GET"])
@require_auth
def top_stocks():
    metric = request.args.get("metric", "volume")
    k = int(request.args.get("k", 10))

    records = app.stock_map.all_records()
    # If heap is stale, rebuild from current data
    for r in records:
        app.heap.push(r.symbol, r.volume if metric == "volume" else r.price)

    top = app.heap.top_k()
    results = []
    for val, sym in top:
        rec = app.stock_map.get(sym)
        if rec:
            results.append({"symbol": sym, metric: val, "price": rec.price, "volume": rec.volume})
    return jsonify({"metric": metric, "top": results})

# ------------------------------------------------------------------ #
# Sector Graph — BFS/DFS                                              #
# ------------------------------------------------------------------ #

@app.route("/api/stocks/sector/<s>/friends", methods=["GET"])
@require_auth
def sector_bfs(s):
    path = app.graph.bfs(s.upper())
    if not path:
        return jsonify({"error": f"Sector {s} not found"}), 404
    stocks_in_sectors = {}
    for sector in path:
        stocks = [r.symbol for r in app.stock_map.all_records() if r.sector == sector]
        stocks_in_sectors[sector] = stocks
    return jsonify({"start": s.upper(), "bfs_order": path, "sector_stocks": stocks_in_sectors})

@app.route("/api/stocks/sector/<s>/friends/DFS", methods=["GET"])
@require_auth
def sector_dfs(s):
    path = app.graph.dfs(s.upper())
    if not path:
        return jsonify({"error": f"Sector {s} not found"}), 404
    stocks_in_sectors = {}
    for sector in path:
        stocks = [r.symbol for r in app.stock_map.all_records() if r.sector == sector]
        stocks_in_sectors[sector] = stocks
    return jsonify({"start": s.upper(), "dfs_order": path, "sector_stocks": stocks_in_sectors})

# ------------------------------------------------------------------ #
# Alerts — Stack                                                      #
# ------------------------------------------------------------------ #

@app.route("/api/alerts", methods=["GET"])
@require_auth
def list_alerts():
    alerts = app.alerts.all_alerts()
    return jsonify({
        "count": len(alerts),
        "alerts": [
            {
                "symbol": a.symbol,
                "threshold": a.threshold,
                "direction": a.direction,
                "triggered": a.triggered,
                "note": a.note,
            }
            for a in alerts
        ],
    })

@app.route("/api/alerts", methods=["POST"])
@require_auth
@require_role("analyst", "admin")
def create_alert():
    data = request.get_json(force=True) or {}
    symbol = data.get("symbol", "").upper()
    threshold = float(data.get("threshold", 0))
    direction = data.get("direction", "above")
    note = data.get("note", "")

    if not symbol:
        return jsonify({"error": "symbol required"}), 400
    if not app.stock_map.contains(symbol):
        return jsonify({"error": f"Unknown symbol {symbol}"}), 404

    try:
        alert = Alert(symbol, threshold, direction, note)
        app.alerts.push(alert)
        return jsonify({"message": "Alert created", "symbol": symbol, "threshold": threshold}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/alerts/undo", methods=["DELETE"])
@require_auth
@require_role("analyst", "admin")
def undo_alert():
    try:
        popped = app.alerts.pop()
        return jsonify({
            "message": "Undo successful",
            "removed": {
                "symbol": popped.symbol,
                "threshold": popped.threshold,
                "direction": popped.direction,
            },
        }), 200
    except IndexError:
        # Try restore via undo
        if app.alerts.undo():
            return jsonify({"message": "Restored last alert"}), 200
        return jsonify({"error": "No alerts to undo"}), 404

# ------------------------------------------------------------------ #
# Benchmarks                                                          #
# ------------------------------------------------------------------ #

@app.route("/api/benchmarks", methods=["GET"])
@require_auth
@require_role("admin")
def benchmarks():
    results = run_all_benchmarks()
    table = format_benchmark_table(results)
    return jsonify({
        "results": results,
        "table": table,
    })

# ------------------------------------------------------------------ #
# Cache Stats                                                         #
# ------------------------------------------------------------------ #

@app.route("/api/cache/stats", methods=["GET"])
@require_auth
def cache_stats():
    return jsonify(app.cache.stats())

@app.route("/api/cache/clear", methods=["POST"])
@require_auth
@require_role("admin")
def cache_clear():
    app.cache.clear()
    return jsonify({"message": "Cache cleared"})

# ------------------------------------------------------------------ #
# Entry point                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
