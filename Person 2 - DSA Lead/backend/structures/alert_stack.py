"""
=============================================================
 PHASE 2 — DSA Structure 3: AlertStack
 Rubric requirement: Stack (undo / history / backtracking)
=============================================================

WHY A STACK HERE?
  Analysts set price threshold alerts — "notify me when AAPL
  goes above $200".  Alerts are reviewed and dismissed in
  reverse creation order: the most recently added alert is
  the first candidate for review or removal.  That is exactly
  the LIFO (Last-In First-Out) access pattern a stack provides.

  The undo requirement ("remove the last alert I created") is
  the textbook use case for a secondary undo buffer alongside
  a stack.

HOW IT WORKS:
  Two Python lists act as the main stack and an undo buffer.
  list.append() pushes to the top  → O(1)
  list.pop()    removes from top   → O(1)

  Undo model:
    push(A) → push(B) → pop()   : B moves to undo_buffer
    undo()                       : B is restored to top of stack
    push(C)                      : undo_buffer is cleared
                                   (new push = new commit point,
                                    can no longer undo B)

COMPLEXITY (Step 2 — Constraints):
  push   O(1)
  pop    O(1)  raises IndexError on empty
  peek   O(1)  returns None on empty
  undo   O(1)  returns True if restored, False if nothing to undo
  size   O(1)
  all_alerts O(n)

CONSTRAINT: MAX_SIZE = 1,000 alerts (enforced in push).
"""

MAX_SIZE = 1_000


class Alert:
    """
    One price threshold alert stored in the stack.

    direction: "above" → trigger when price >= threshold
               "below" → trigger when price <= threshold
    triggered: set to True by the simulator when the condition fires
    """

    def __init__(
        self,
        symbol: str,
        threshold: float,
        direction: str = "above",
        note: str = "",
    ):
        self.symbol:    str   = symbol.upper()
        self.threshold: float = float(threshold)
        self.direction: str   = direction.lower()   # "above" | "below"
        self.triggered: bool  = False
        self.note:      str   = note

    def __repr__(self) -> str:
        state = "TRIGGERED" if self.triggered else "watching"
        return (f"Alert({self.symbol} {self.direction} "
                f"{self.threshold} [{state}])")


class AlertStack:
    """
    LIFO alert stack with single-level undo.

    The main stack (_stack) holds active alerts.
    The undo buffer (_undo_buf) holds the single most-recently
    popped alert so it can be restored in one undo() call.
    """

    def __init__(self):
        self._stack:    list[Alert] = []
        self._undo_buf: list[Alert] = []   # max 1 item at a time

    # -------------------------------------------------------------- #
    # Write                                                            #
    # -------------------------------------------------------------- #

    def push(self, alert: Alert) -> None:
        """
        Push a new alert onto the top of the stack.
        Clears the undo buffer — a new push is a new commit point.
        Raises ValueError if the stack is full (MAX_SIZE = 1,000).
        O(1).
        """
        if len(self._stack) >= MAX_SIZE:
            raise ValueError(
                f"AlertStack is full — maximum {MAX_SIZE} alerts allowed"
            )
        self._stack.append(alert)
        self._undo_buf.clear()   # new push voids any pending undo

    def pop(self) -> Alert:
        """
        Remove and return the TOP alert (LIFO order).
        The removed alert is saved in the undo buffer for one-step restore.
        Raises IndexError if the stack is empty.
        O(1).
        """
        if not self._stack:
            raise IndexError("Cannot pop from an empty AlertStack")
        removed = self._stack.pop()
        self._undo_buf.clear()
        self._undo_buf.append(removed)
        return removed

    def undo(self) -> bool:
        """
        Restore the last popped alert back to the top of the stack.
        Returns True if an alert was restored.
        Returns False if there is nothing to undo.
        O(1).
        """
        if not self._undo_buf:
            return False
        self._stack.append(self._undo_buf.pop())
        return True

    # -------------------------------------------------------------- #
    # Read                                                             #
    # -------------------------------------------------------------- #

    def peek(self) -> Alert | None:
        """
        Return the top alert WITHOUT removing it.
        Returns None if the stack is empty.
        O(1).
        """
        return self._stack[-1] if self._stack else None

    def all_alerts(self) -> list[Alert]:
        """
        Snapshot of all alerts from bottom (oldest) to top (newest).
        O(n).
        """
        return list(self._stack)

    # -------------------------------------------------------------- #
    # Utility                                                          #
    # -------------------------------------------------------------- #

    def is_empty(self) -> bool:
        """O(1)."""
        return len(self._stack) == 0

    def size(self) -> int:
        """O(1)."""
        return len(self._stack)
