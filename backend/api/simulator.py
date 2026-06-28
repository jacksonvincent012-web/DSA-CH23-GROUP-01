"""
PHASE 3 — Background Market Data Simulator

PRODUCES price ticks at regular intervals (every ~2 s) and
pushes them through the IngestionQueue → HashMap pipeline.
Also checks AlertStack thresholds and maintains the TopKHeap.

Lifecycle:
  1. Simulator thread starts when the Flask app starts.
  2. Seeds 24 stocks with 90-day synthetic price history.
  3. Every 2 s: pick a random stock, generate a ±2% price move,
     enqueue a Tick, drain the queue, update the map + heap,
     check alerts.
  4. Runs until the server shuts down (daemon thread).
"""

import os
import sys
import random
import threading
import time
from datetime import datetime, timedelta

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from structures.stock_map import StockHashMap, StockRecord
from structures.ingestion_queue import IngestionQueue, Tick
from structures.alert_stack import AlertStack
from structures.top_k_heap import TopKHeap

# ------------------------------------------------------------------ #
# Seed data — 10,000 stocks across 10 sectors                         #
#  24 well-known tickers + 9,976 auto-generated                       #
# ------------------------------------------------------------------ #

NUM_STOCKS = 10_000
NUM_DAYS_HISTORY = 90
TICK_INTERVAL = 2.0  # seconds between simulated tick cycles

SECTORS = [
    "TECH", "FINANCE", "ENERGY", "HEALTHCARE", "CONSUMER",
    "MEDIA", "RETAIL", "TRANSPORT", "UTILITIES", "REAL_ESTATE",
]

SECTOR_EDGES = [
    ("TECH", "MEDIA"), ("TECH", "FINANCE"), ("FINANCE", "ENERGY"),
    ("ENERGY", "CONSUMER"), ("HEALTHCARE", "CONSUMER"),
    ("MEDIA", "CONSUMER"), ("FINANCE", "HEALTHCARE"),
    ("TECH", "CONSUMER"), ("CONSUMER", "ENERGY"),
    ("CONSUMER", "RETAIL"), ("TECH", "RETAIL"),
    ("ENERGY", "TRANSPORT"), ("RETAIL", "TRANSPORT"),
    ("REAL_ESTATE", "FINANCE"), ("UTILITIES", "ENERGY"),
    ("REAL_ESTATE", "CONSUMER"), ("UTILITIES", "REAL_ESTATE"),
]

# 24 well-known anchor stocks — always seeded first
ANCHOR_STOCKS = [
    ("AAPL", 178.50, 45_000_000, "TECH"),
    ("MSFT", 378.20, 22_000_000, "TECH"),
    ("GOOGL", 141.80, 18_000_000, "TECH"),
    ("NVDA", 880.00, 35_000_000, "TECH"),
    ("JPM", 198.40, 9_000_000, "FINANCE"),
    ("GS", 428.10, 3_000_000, "FINANCE"),
    ("V", 275.30, 8_000_000, "FINANCE"),
    ("BAC", 36.70, 15_000_000, "FINANCE"),
    ("XOM", 112.60, 7_000_000, "ENERGY"),
    ("CVX", 155.20, 4_000_000, "ENERGY"),
    ("COP", 128.90, 2_500_000, "ENERGY"),
    ("SLB", 52.40, 3_500_000, "ENERGY"),
    ("JNJ", 156.80, 5_000_000, "HEALTHCARE"),
    ("PFE", 27.50, 12_000_000, "HEALTHCARE"),
    ("UNH", 528.10, 2_000_000, "HEALTHCARE"),
    ("ABBV", 178.90, 4_500_000, "HEALTHCARE"),
    ("AMZN", 178.20, 25_000_000, "CONSUMER"),
    ("WMT", 172.40, 6_000_000, "CONSUMER"),
    ("KO", 61.30, 8_000_000, "CONSUMER"),
    ("PG", 164.50, 3_500_000, "CONSUMER"),
    ("META", 505.70, 12_000_000, "MEDIA"),
    ("DIS", 112.30, 7_000_000, "MEDIA"),
    ("NFLX", 625.40, 3_000_000, "MEDIA"),
    ("CMCSA", 42.10, 6_000_000, "MEDIA"),
]


def _generate_synthetic_symbols(count: int) -> list[str]:
    """Generate count synthetic ticker symbols like A0000, A0001, ... Z0374."""
    symbols = []
    letters = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
    per_letter = (count + 25) // 26
    for letter in letters:
        for i in range(per_letter):
            if len(symbols) >= count:
                break
            symbols.append(f"{letter}{i:04d}")
    return symbols[:count]


def _generate_stocks(hm: StockHashMap, heap: TopKHeap):
    """Seed the hash map with 10,000 stocks (24 anchors + 9,976 synthetic)."""
    import random
    from datetime import datetime, timedelta

    # Seed anchor stocks first
    for symbol, price, volume, sector in ANCHOR_STOCKS:
        record = StockRecord(symbol, price, volume, sector)
        base_price = price * (1 + random.uniform(-0.3, 0.3))
        hist = []
        for day in range(NUM_DAYS_HISTORY, 0, -1):
            date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d")
            daily_price = round(base_price * (1 + 0.02 * random.gauss(0, 1)), 2)
            hist.append((date, f"{daily_price:.2f}"))
        record.price_history = hist
        hm.put(symbol, record)
        heap.push(symbol, volume)

    # Generate remaining stocks
    needed = NUM_STOCKS - len(ANCHOR_STOCKS)
    symbols = _generate_synthetic_symbols(needed + 26)  # buffer
    for i, sym in enumerate(symbols):
        if hm.size() >= NUM_STOCKS:
            break
        if hm.contains(sym):
            continue
        sector = SECTORS[i % len(SECTORS)]
        price = round(random.uniform(5, 1200), 2)
        volume = random.randint(100_000, 60_000_000)
        record = StockRecord(sym, price, volume, sector)
        base_price = price * (1 + random.uniform(-0.3, 0.3))
        hist = []
        for day in range(NUM_DAYS_HISTORY, 0, -1):
            date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d")
            daily_price = round(base_price * (1 + 0.02 * random.gauss(0, 1)), 2)
            hist.append((date, f"{daily_price:.2f}"))
        record.price_history = hist
        hm.put(sym, record)
        heap.push(sym, volume)


class Simulator:
    """
    Background market data simulator.

    Holds direct references to all DSA structures and updates them
    in a loop running on a daemon thread.
    """

    def __init__(
        self,
        stock_map: StockHashMap,
        queue: IngestionQueue,
        alerts: AlertStack,
        heap: TopKHeap,
    ):
        self.stock_map = stock_map
        self.queue = queue
        self.alerts = alerts
        self.heap = heap
        self._thread: threading.Thread | None = None
        self._running = False
        self._tick_count = 0

    def seed(self):
        """Populate the hash map with 10,000 stocks and 90-day price history."""
        import time
        t0 = time.perf_counter()
        _generate_stocks(self.stock_map, self.heap)
        self._seed_graph()
        elapsed = time.perf_counter() - t0
        print(f"[Simulator] Seeded {self.stock_map.size()} stocks in {elapsed:.1f}s")

    def _seed_graph(self):
        """Build sector relationships on the TopKHeap's SectorGraph reference."""
        from structures.sector_graph import SectorGraph
        # The graph is accessed via a separate instance stored in the app context;
        # We store a reference for the demo.  The actual graph is built in server.py.
        # This method is kept for compatibility — seed is enough.
        pass

    def _tick_cycle(self):
        """
        One tick cycle:
          1. Pick a random stock.
          2. Generate a random ±2% price change.
          3. Enqueue a Tick.
          4. Drain the queue.
          5. Update HashMap records with drained ticks.
          6. Update the TopKHeap.
          7. Check alert thresholds.
        """
        symbols = self.stock_map.keys()
        if not symbols:
            return

        symbol = random.choice(symbols)
        record = self.stock_map.get(symbol)
        if not record:
            return

        change_pct = random.uniform(-0.02, 0.02)
        new_price = round(record.price * (1 + change_pct), 2)
        volume_delta = random.randint(-500_000, 500_000)
        new_volume = max(record.volume + volume_delta, 1_000)

        now = datetime.now()
        tick = Tick(symbol, new_price, new_volume, now)
        self.queue.enqueue(tick)

        # Drain all queued ticks
        batch = self.queue.drain()
        for t in batch:
            self.stock_map.update(t.symbol, t.price, t.volume)
            rec = self.stock_map.get(t.symbol)
            if rec:
                date_str = t.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                rec.price_history.append((date_str, f"{t.price:.2f}"))
                # Keep last 100k entries
                if len(rec.price_history) > 100_000:
                    rec.price_history = rec.price_history[-100_000:]

            self.heap.push(t.symbol, t.volume)

            # Check all alerts
            for alert in self.alerts.all_alerts():
                if alert.triggered:
                    continue
                if alert.symbol == t.symbol:
                    if alert.direction == "above" and t.price >= alert.threshold:
                        alert.triggered = True
                    elif alert.direction == "below" and t.price <= alert.threshold:
                        alert.triggered = True

        self._tick_count += len(batch)

    def _loop(self):
        """Main simulator loop — runs until _running is False."""
        self.seed()
        while self._running:
            self._tick_cycle()
            time.sleep(TICK_INTERVAL)

    def start(self):
        """Start the simulator in a daemon thread."""
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the simulator to stop."""
        self._running = False

    @property
    def tick_count(self) -> int:
        return self._tick_count
