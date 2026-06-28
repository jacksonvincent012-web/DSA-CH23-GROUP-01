"""
PHASE 2 — DSA Structure 9: LRUCache
Composite structure: HashMap + Doubly Linked List

WHY LRU CACHE HERE?
  80% of API requests hit 20% of stocks (the "hot" ones — AAPL,
  MSFT, NVDA, GOOGL).  Without caching, every single read hits the
  StockHashMap.  With an LRU cache, the first read for AAPL fetches
  from the map and caches the result.  Subsequent reads for AAPL
  return in O(1) from the cache — no hash computation, no object
  construction, no memory allocation.

  When the cache is full, the Least Recently Used entry is evicted:
  the stock nobody has asked for in the longest time.  This keeps
  the cache populated with exactly the stocks users are actively
  viewing.

HOW IT WORKS — HashMap + Doubly Linked List:

        HashMap              Doubly Linked List
    { "AAPL" → node }      head (MRU) ⇄ ... ⇄ tail (LRU)
    { "MSFT" → node }
    { "NVDA" → node }

  get(key):
    1. HashMap.get(key) → node (O(1))
    2. Move node to head of linked list (O(1))
    3. Return node.value

  put(key, value):
    1. If key exists: update node.value, move to head
    2. If new: create node at head
    3. If over capacity: evict tail node, remove from HashMap

  The doubly linked list makes "move to head" O(1) because each
  node stores prev/next pointers — no scanning needed.

COMPLEXITY:
  get   O(1)  — HashMap lookup + pointer surgery
  put   O(1)  — same
  Space O(capacity)
"""


class _Node:
    """Doubly linked list node for LRU cache entries."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Fixed-capacity LRU cache backed by HashMap + Doubly Linked List.

    Parameters
    ----------
    capacity : int
        Maximum number of entries before eviction (default 100).
    """

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self._map: dict = {}          # key → _Node
        self._head: _Node | None = None   # Most Recently Used
        self._tail: _Node | None = None   # Least Recently Used
        self._size: int = 0
        self._hits: int = 0
        self._misses: int = 0

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def get(self, key) -> object | None:
        """
        Retrieve value by key.
        Moves accessed node to head (MRU position).
        Returns None if key not present.
        O(1).
        """
        node = self._map.get(key)
        if node is None:
            self._misses += 1
            return None
        self._hits += 1
        self._move_to_head(node)
        return node.value

    def put(self, key, value) -> None:
        """
        Insert or update a cache entry.
        If key exists: update value and move to head.
        If key is new: add to head; evict tail if over capacity.
        O(1).
        """
        node = self._map.get(key)
        if node:
            node.value = value
            self._move_to_head(node)
            return

        new_node = _Node(key, value)
        self._map[key] = new_node
        self._add_to_head(new_node)
        self._size += 1

        if self._size > self.capacity:
            self._evict_tail()

    def remove(self, key) -> bool:
        """
        Remove a specific key from cache.
        Returns True if removed, False if not found.
        O(1).
        """
        node = self._map.pop(key, None)
        if node is None:
            return False
        self._remove_node(node)
        self._size -= 1
        return True

    def clear(self) -> None:
        """Remove all entries. O(1) map clear + O(n) pointer cleanup."""
        self._map.clear()
        self._head = None
        self._tail = None
        self._size = 0
        self._hits = 0
        self._misses = 0

    def contains(self, key) -> bool:
        """O(1) membership check (does NOT affect recency)."""
        return key in self._map

    # ------------------------------------------------------------------ #
    # Stats                                                               #
    # ------------------------------------------------------------------ #

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def size(self) -> int:
        return self._size

    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = round(self._hits / total * 100, 1) if total > 0 else 0.0
        return {
            "capacity": self.capacity,
            "size": self._size,
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_rate_pct": hit_rate,
        }

    # ------------------------------------------------------------------ #
    # Internal — doubly linked list operations (all O(1))                 #
    # ------------------------------------------------------------------ #

    def _add_to_head(self, node: _Node) -> None:
        """Insert node at head (MRU position)."""
        node.prev = None
        node.next = self._head
        if self._head:
            self._head.prev = node
        self._head = node
        if self._tail is None:
            self._tail = node

    def _remove_node(self, node: _Node) -> None:
        """Detach node from its current position in the list."""
        if node.prev:
            node.prev.next = node.next
        else:
            self._head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self._tail = node.prev

        node.prev = None
        node.next = None

    def _move_to_head(self, node: _Node) -> None:
        """Move an existing node to head (MRU position)."""
        if node is self._head:
            return
        self._remove_node(node)
        self._add_to_head(node)

    def _evict_tail(self) -> None:
        """Remove the least recently used entry (tail)."""
        if self._tail is None:
            return
        evicted = self._tail
        self._map.pop(evicted.key, None)
        self._remove_node(evicted)
        self._size -= 1

    def keys(self) -> list:
        """All keys currently in cache (for inspection)."""
        return list(self._map.keys())
