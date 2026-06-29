"""
=============================================================
 PHASE 2 — DSA Structure 2: IngestionQueue
 Rubric requirement: Queue (buffering, scheduling, BFS)
=============================================================

WHY A QUEUE HERE?
  The market simulator generates price ticks continuously —
  one tick every 2 seconds for a random stock.  Those ticks
  must be processed in the exact order they arrive (FIFO):
  the price at 10:00:01 must be applied before the price at
  10:00:03.  A queue enforces that ordering guarantee.

  The queue also acts as a decoupling buffer: the simulator
  PRODUCES ticks at its own rate; the hash-map update loop
  CONSUMES them in batches.  Neither side blocks the other.

HOW IT WORKS:
  Backed by collections.deque — Python's double-ended queue.
  deque.append()    adds to the RIGHT end  → O(1) amortised
  deque.popleft()   removes from LEFT end  → O(1) amortised

  IMPORTANT — Bottleneck fix (Step 4, B2):
    A plain list's pop(0) shifts every remaining element left
    making dequeue O(n).  deque.popleft() is O(1) because
    deque uses a doubly-linked list of fixed-size blocks.
    We always use popleft() — never pop(0).

COMPLEXITY (Step 2 — Constraints):
  enqueue   O(1) amortised
  dequeue   O(1) amortised
  peek      O(1)
  drain     O(n)  — intentional full-batch consume
  size      O(1)
"""

from collections import deque
from datetime import datetime


class Tick:
    """
    One price update produced by the simulator.

    A Tick is the unit of work that flows through the queue:
      simulator → enqueue(tick) → queue → drain() → hash map update
    """

    # __slots__ avoids per-instance __dict__, saves memory when
    # thousands of ticks are buffered simultaneously.
    __slots__ = ("symbol", "price", "volume", "timestamp")

    def __init__(
        self,
        symbol: str,
        price: float,
        volume: int,
        timestamp: datetime,
    ):
        self.symbol:    str      = symbol.upper()
        self.price:     float    = float(price)
        self.volume:    int      = int(volume)
        self.timestamp: datetime = timestamp

    def __repr__(self) -> str:
        ts = self.timestamp.strftime("%H:%M:%S")
        return f"Tick({self.symbol}, {self.price:.2f}, vol={self.volume}, t={ts})"


class IngestionQueue:
    """
    FIFO tick buffer backed by collections.deque.

    Lifecycle of a tick:
      1. Simulator calls enqueue(tick)       — added to back
      2. Every 2 s the server calls drain()  — removes all ticks
      3. Server loops over returned list and calls HashMap.update()

    Why drain() instead of dequeue() one-by-one?
      Draining in one shot (O(n) copy + O(1) clear) is faster than
      n individual popleft() calls when the batch is large, because
      it avoids n Python function-call overheads.
    """

    def __init__(self):
        self._queue: deque[Tick] = deque()

    # -------------------------------------------------------------- #
    # Write                                                            #
    # -------------------------------------------------------------- #

    def enqueue(self, tick: Tick) -> None:
        """
        Add a tick to the BACK of the queue.
        O(1) amortised.
        """
        self._queue.append(tick)

    # -------------------------------------------------------------- #
    # Consume                                                          #
    # -------------------------------------------------------------- #

    def dequeue(self) -> Tick:
        """
        Remove and return the FRONT tick (FIFO order).
        Raises IndexError if queue is empty.
        O(1) amortised.
        """
        if not self._queue:
            raise IndexError("Cannot dequeue from an empty IngestionQueue")
        return self._queue.popleft()   # ← O(1), NOT pop(0) which is O(n)

    def drain(self) -> list[Tick]:
        """
        Remove ALL ticks and return them as a list.
        Called by the simulator at the end of each 2-second tick cycle.
        O(n) — intentional: we want to process the whole batch at once.
        """
        batch = list(self._queue)   # snapshot O(n)
        self._queue.clear()         # clear   O(1)
        return batch

    def peek(self) -> Tick | None:
        """
        Return the front tick WITHOUT removing it.
        Returns None if queue is empty.
        O(1).
        """
        return self._queue[0] if self._queue else None

    # -------------------------------------------------------------- #
    # Utility                                                          #
    # -------------------------------------------------------------- #

    def is_empty(self) -> bool:
        """True if no ticks are waiting. O(1)."""
        return len(self._queue) == 0

    def size(self) -> int:
        """Number of ticks currently buffered. O(1)."""
        return len(self._queue)
