"""
PHASE 4 — 37+ pytest Unit Tests
Covers all 8 DSA structures + edge cases + LRU Cache
"""

import os
import sys
import pytest
import random
from datetime import datetime, timedelta

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from structures.stock_map import StockHashMap, StockRecord
from structures.ingestion_queue import IngestionQueue, Tick
from structures.alert_stack import AlertStack, Alert, MAX_SIZE
from structures.top_k_heap import TopKHeap
from structures.sector_graph import SectorGraph
from structures.merge_sort import merge_sort
from structures.binary_search import binary_search, lower_bound, upper_bound, range_search
from structures.lru_cache import LRUCache


# ================================================================== #
#  StockHashMap Tests  (7 tests)                                     #
# ================================================================== #

class TestStockHashMap:
    def test_put_and_get(self):
        hm = StockHashMap()
        r = StockRecord("AAPL", 150.0, 100000, "TECH")
        hm.put("AAPL", r)
        assert hm.get("AAPL") is r
        assert hm.size() == 1

    def test_get_missing(self):
        hm = StockHashMap()
        assert hm.get("NOTHING") is None

    def test_update_existing(self):
        hm = StockHashMap()
        hm.put("AAPL", StockRecord("AAPL", 150.0, 100000, "TECH"))
        assert hm.update("AAPL", 155.0, 200000) is True
        assert hm.get("AAPL").price == 155.0
        assert hm.get("AAPL").volume == 200000

    def test_update_missing(self):
        hm = StockHashMap()
        assert hm.update("NONE", 100.0, 1000) is False

    def test_remove(self):
        hm = StockHashMap()
        hm.put("AAPL", StockRecord("AAPL", 150.0, 100000, "TECH"))
        assert hm.remove("AAPL") is True
        assert hm.get("AAPL") is None
        assert hm.size() == 0

    def test_remove_missing(self):
        hm = StockHashMap()
        assert hm.remove("NONE") is False

    def test_case_insensitive(self):
        hm = StockHashMap()
        hm.put("aapl", StockRecord("aapl", 150.0, 100000, "TECH"))
        assert hm.get("AAPL") is not None
        assert hm.get("Aapl") is not None
        assert hm.contains("AAPL")
        assert hm.contains("aapl")


# ================================================================== #
#  IngestionQueue Tests  (5 tests)                                   #
# ================================================================== #

class TestIngestionQueue:
    def test_enqueue_dequeue(self):
        q = IngestionQueue()
        t = Tick("AAPL", 150.0, 1000, datetime.now())
        q.enqueue(t)
        assert q.size() == 1
        out = q.dequeue()
        assert out.symbol == "AAPL"
        assert q.size() == 0

    def test_fifo_order(self):
        q = IngestionQueue()
        t1 = Tick("AAPL", 150.0, 1000, datetime.now())
        t2 = Tick("MSFT", 300.0, 2000, datetime.now())
        q.enqueue(t1)
        q.enqueue(t2)
        assert q.dequeue().symbol == "AAPL"
        assert q.dequeue().symbol == "MSFT"

    def test_dequeue_empty_raises(self):
        q = IngestionQueue()
        with pytest.raises(IndexError):
            q.dequeue()

    def test_drain(self):
        q = IngestionQueue()
        for i in range(5):
            q.enqueue(Tick(f"SYM{i}", 100.0, 1000, datetime.now()))
        batch = q.drain()
        assert len(batch) == 5
        assert q.size() == 0

    def test_peek(self):
        q = IngestionQueue()
        assert q.peek() is None
        t = Tick("AAPL", 150.0, 1000, datetime.now())
        q.enqueue(t)
        assert q.peek().symbol == "AAPL"
        assert q.size() == 1


# ================================================================== #
#  AlertStack Tests  (6 tests)                                       #
# ================================================================== #

class TestAlertStack:
    def test_push_pop(self):
        s = AlertStack()
        a = Alert("AAPL", 200.0, "above")
        s.push(a)
        assert s.size() == 1
        popped = s.pop()
        assert popped.symbol == "AAPL"
        assert s.size() == 0

    def test_lifo_order(self):
        s = AlertStack()
        s.push(Alert("A", 100, "above"))
        s.push(Alert("B", 200, "above"))
        s.push(Alert("C", 300, "above"))
        assert s.pop().symbol == "C"
        assert s.pop().symbol == "B"
        assert s.pop().symbol == "A"

    def test_pop_empty_raises(self):
        s = AlertStack()
        with pytest.raises(IndexError):
            s.pop()

    def test_undo(self):
        s = AlertStack()
        s.push(Alert("AAPL", 200, "above"))
        s.push(Alert("MSFT", 300, "above"))
        s.pop()  # removes MSFT
        assert s.size() == 1
        assert s.undo() is True
        assert s.size() == 2
        assert s.peek().symbol == "MSFT"

    def test_undo_nothing(self):
        s = AlertStack()
        assert s.undo() is False

    def test_max_size(self):
        s = AlertStack()
        for i in range(MAX_SIZE):
            s.push(Alert(f"SYM{i}", 100, "above"))
        assert s.size() == MAX_SIZE
        with pytest.raises(ValueError):
            s.push(Alert("OVER", 100, "above"))


# ================================================================== #
#  TopKHeap Tests  (4 tests)                                         #
# ================================================================== #

class TestTopKHeap:
    def test_top_k_returns_descending(self):
        h = TopKHeap(k=3)
        for val, sym in [(10, "A"), (30, "B"), (20, "C"), (5, "D"), (40, "E")]:
            h.push(sym, val)
        top = h.top_k()
        values = [v for v, _ in top]
        assert values == [40, 30, 20]

    def test_never_exceeds_k(self):
        h = TopKHeap(k=3)
        for i in range(100):
            h.push(f"SYM{i}", i)
        assert h.size() <= 3

    def test_push_small_ignored(self):
        h = TopKHeap(k=3)
        h.push("A", 100)
        h.push("B", 90)
        h.push("C", 80)
        h.push("D", 10)  # too small
        top = h.top_k()
        assert len(top) == 3
        assert top[0][1] == "A"  # 100 highest

    def test_peek_min(self):
        h = TopKHeap(k=3)
        h.push("A", 100)
        h.push("B", 50)
        h.push("C", 75)
        val, sym = h.peek_min()
        assert sym == "B"
        assert val == 50


# ================================================================== #
#  SectorGraph Tests  (4 tests)                                      #
# ================================================================== #

class TestSectorGraph:
    def test_add_node(self):
        g = SectorGraph()
        g.add_node("TECH")
        assert "TECH" in g.get_nodes()

    def test_add_edge(self):
        g = SectorGraph()
        g.add_edge("TECH", "FINANCE")
        assert "FINANCE" in g.get_neighbours("TECH")

    def test_bfs(self):
        g = SectorGraph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        path = g.bfs("A")
        assert path[0] == "A"
        assert set(path[1:3]) == {"B", "C"}
        assert path[-1] == "D"

    def test_dfs(self):
        g = SectorGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "D")
        path = g.dfs("A")
        assert path[0] == "A"
        assert len(path) == 4

    def test_dfs_iterative(self):
        g = SectorGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "D")
        path = g.dfs_iterative("A")
        assert path[0] == "A"
        assert len(path) == 4

    def test_bfs_empty_start(self):
        g = SectorGraph()
        assert g.bfs("NONE") == []

    def test_dfs_empty_start(self):
        g = SectorGraph()
        assert g.dfs("NONE") == []


# ================================================================== #
#  MergeSort Tests  (4 tests)                                        #
# ================================================================== #

class TestMergeSort:
    def test_sort_numbers(self):
        assert merge_sort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_already_sorted(self):
        assert merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_reverse_sorted(self):
        assert merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_empty_and_single(self):
        assert merge_sort([]) == []
        assert merge_sort([42]) == [42]

    def test_with_key(self):
        data = [(3, "c"), (1, "a"), (2, "b")]
        result = merge_sort(data, key=lambda x: x[0])
        assert result == [(1, "a"), (2, "b"), (3, "c")]


# ================================================================== #
#  BinarySearch Tests  (4 tests)                                     #
# ================================================================== #

class TestBinarySearch:
    def test_find_existing(self):
        assert binary_search([1, 3, 5, 7, 9], 5) == 2

    def test_find_missing(self):
        assert binary_search([1, 3, 5, 7, 9], 4) == -1

    def test_lower_bound(self):
        arr = [1, 3, 5, 5, 5, 7, 9]
        assert lower_bound(arr, 5) == 2
        assert lower_bound(arr, 6) == 5

    def test_upper_bound(self):
        arr = [1, 3, 5, 5, 5, 7, 9]
        assert upper_bound(arr, 5) == 5
        assert upper_bound(arr, 10) == 7


# ================================================================== #
#  LRUCache Tests  (7 tests)                                         #
# ================================================================== #

class TestLRUCache:
    def test_get_put(self):
        c = LRUCache(3)
        c.put("A", 1)
        assert c.get("A") == 1

    def test_get_miss(self):
        c = LRUCache(3)
        assert c.get("NONE") is None

    def test_eviction(self):
        c = LRUCache(3)
        c.put("A", 1)
        c.put("B", 2)
        c.put("C", 3)
        c.put("D", 4)  # evicts A (LRU)
        assert c.get("A") is None
        assert c.get("D") == 4
        assert c.get("B") == 2
        assert c.get("C") == 3

    def test_get_refreshes_lru(self):
        c = LRUCache(3)
        c.put("A", 1)
        c.put("B", 2)
        c.put("C", 3)
        c.get("A")       # A is now MRU
        c.put("D", 4)    # evicts B (was LRU)
        assert c.get("B") is None
        assert c.get("A") == 1

    def test_update_existing(self):
        c = LRUCache(3)
        c.put("A", 1)
        c.put("A", 99)
        assert c.get("A") == 99
        assert c.size == 1

    def test_remove(self):
        c = LRUCache(3)
        c.put("A", 1)
        assert c.remove("A") is True
        assert c.get("A") is None
        assert c.remove("NONE") is False

    def test_clear(self):
        c = LRUCache(3)
        c.put("A", 1)
        c.put("B", 2)
        c.clear()
        assert c.size == 0
        assert c.get("A") is None
        assert c.hits == 0

    def test_stats(self):
        c = LRUCache(3)
        c.put("A", 1)
        c.get("A")   # hit
        c.get("B")   # miss
        stats = c.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate_pct"] == 50.0
