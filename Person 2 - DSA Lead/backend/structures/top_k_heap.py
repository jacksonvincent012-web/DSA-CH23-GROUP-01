"""
=============================================================
 PHASE 2 — DSA Structure 4: TopKHeap
 Rubric requirement: Heap / priority queue (top-k, ordering)
=============================================================

WHY A HEAP HERE?
  The dashboard needs "give me the top 5 stocks by trading
  volume" on every page load.  A naive approach — sort all
  10,000 stocks and take the first 5 — costs O(N log N) per
  request.  A size-bounded min-heap of exactly K entries
  reduces that to O(log K) per new data point (push) and
  O(K log K) to extract the final sorted top-K.

  At K=10 that is log₂(10) ≈ 3 comparisons per tick update,
  versus 10,000 × 13 ≈ 130,000 comparisons for a full sort.

HOW IT WORKS — MIN-HEAP OF SIZE K:
  We keep a min-heap where the ROOT is the SMALLEST value
  among the current top-K candidates.

  On every push(symbol, metric):
    • If the heap has fewer than K items → push unconditionally.
    • If metric > root (the current minimum of top-K):
        → Replace root with new item (heapreplace).
        → The new item bubbles up to its correct position.
    • If metric <= root:
        → New item cannot be in the top-K → discard.

  This means the heap always holds exactly the K largest
  values seen so far, and the root is always the
  smallest of those K values.

  Python's heapq is a min-heap — root = smallest.
  Items are stored as (metric_value, symbol) tuples so that
  heapq compares by metric_value first.

COMPLEXITY (Step 2 — Constraints):
  push          O(log K)        — sift up after insert / heapreplace
  top_k         O(K log K)      — sorted() on K items to return desc
  heapify_all   O(N)            — linear heap construction (heapq)
  peek_min      O(1)            — root access
  size          O(1)
"""

import heapq


class TopKHeap:
    """
    Size-bounded min-heap maintaining the top-K items by metric value.

    Internal storage: list of (metric_value, symbol) tuples.
    heapq maintains the min-heap property: heap[0] is always
    the (metric_value, symbol) pair with the LOWEST metric —
    which is also the smallest of the K current top-K entries.
    """

    def __init__(self, k: int = 10):
        if k < 1:
            raise ValueError("k must be >= 1")
        self.k:    int               = k
        self._heap: list[tuple]      = []
        # Track unique symbols in heap to prevent duplicates on repeated push
        self._symbols: dict[str, float] = {}

    # -------------------------------------------------------------- #
    # Write                                                            #
    # -------------------------------------------------------------- #

    def push(self, symbol: str, metric_value: float) -> None:
        """
        Offer a new (symbol, metric_value) pair to the top-K.

        If the symbol already exists in the heap, its entry is updated
        (removed + re-inserted) so no duplicates accumulate.

        If the heap is not yet full   → always accepted, O(log K).
        If metric > current minimum   → replaces the minimum, O(log K).
        If metric <= current minimum  → discarded, O(1).
        """
        # Remove previous entry for this symbol if it exists
        if symbol in self._symbols:
            old_val = self._symbols[symbol]
            self._remove_entry(old_val, symbol)

        item = (metric_value, symbol)

        if len(self._heap) < self.k:
            heapq.heappush(self._heap, item)
            self._symbols[symbol] = metric_value

        elif metric_value > self._heap[0][0]:
            heapq.heapreplace(self._heap, item)
            self._symbols[symbol] = metric_value

    def _remove_entry(self, metric_value: float, symbol: str) -> None:
        """
        Remove a specific (metric_value, symbol) entry from the heap.
        Linear scan O(K), which is acceptable since K ≤ 100.
        """
        for i, (v, s) in enumerate(self._heap):
            if s == symbol and v == metric_value:
                self._heap[i] = self._heap[-1]
                self._heap.pop()
                heapq.heapify(self._heap)
                del self._symbols[symbol]
                return

    def heapify_all(self, items: list[tuple]) -> None:
        """
        Build top-K from a list of (symbol, metric_value) tuples.
        Clears the current heap first.
        O(N) for heapify + up to N pushes at O(log K) each → O(N log K).

        Note: heapq.heapify on the full list would be O(N) but we'd
        need to then trim to K which costs O((N-K) log N).  The
        incremental push approach is simpler and still fast enough
        for our N=10,000 scale.
        """
        self._heap = []
        for symbol, metric_value in items:
            self.push(symbol, metric_value)

    # -------------------------------------------------------------- #
    # Read                                                             #
    # -------------------------------------------------------------- #

    def top_k(self) -> list[tuple]:
        """
        Return all current top-K items sorted DESCENDING by metric.
        Returns list of (metric_value, symbol) tuples.
        O(K log K).
        """
        return sorted(self._heap, reverse=True)

    def peek_min(self) -> tuple | None:
        """
        Return the (metric_value, symbol) pair with the LOWEST metric
        among the current top-K (the heap root), without removing it.
        Returns None if heap is empty.
        O(1).
        """
        return self._heap[0] if self._heap else None

    # -------------------------------------------------------------- #
    # Utility                                                          #
    # -------------------------------------------------------------- #

    def size(self) -> int:
        """Current number of items in the heap (≤ K). O(1)."""
        return len(self._heap)

    def is_full(self) -> bool:
        """True when the heap holds exactly K items. O(1)."""
        return len(self._heap) == self.k

    def get_all(self) -> list[tuple]:
        """All heap items (unordered). O(n)."""
        return list(self._heap)
