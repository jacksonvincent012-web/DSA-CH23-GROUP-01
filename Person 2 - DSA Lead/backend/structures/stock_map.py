"""
=============================================================
 PHASE 2 — DSA Structure 1: StockHashMap
 Rubric requirement: Hash table / map (fast lookup)
=============================================================

WHY A HASH MAP HERE?
  Every API request starts with "give me the record for symbol X".
  With 10,000 stocks in memory a linear scan (O(n)) would add
  ~10 ms of pure comparison work per request.  A hash map reduces
  that to O(1) average — the symbol string is hashed to a bucket
  index and the record is retrieved directly.

HOW IT WORKS:
  Python's built-in dict uses open-addressing with a hash of the
  key object and a load-factor threshold of 2/3 before resize.
  We wrap it in a domain-specific API so the rest of the system
  (Flask routes, simulator, tests) never touches the dict directly.
  Swapping to a custom hash function or an external store only
  requires changes inside this one file.

COMPLEXITY (Step 2 — Constraints):
  put         O(1) average,  O(n) worst-case (table resize, rare)
  get         O(1) average
  update      O(1) average
  remove      O(1) average
  contains    O(1) average
  size        O(1)
  all_records O(n)
"""


class StockRecord:
    """
    One stock entry stored inside the hash map.

    Fields:
      symbol        — ticker, e.g. "AAPL"
      price         — latest trade price (float)
      volume        — latest trade volume (int)
      sector        — sector label, e.g. "TECH"
      price_history — chronological list of (date_str, price_str) tuples
    """

    def __init__(self, symbol: str, price: float, volume: int, sector: str):
        self.symbol: str        = symbol.upper()
        self.price: float       = float(price)
        self.volume: int        = int(volume)
        self.sector: str        = sector
        self.price_history: list = []   # [(date_str, price_str), ...]

    def __repr__(self) -> str:
        return (f"StockRecord(symbol={self.symbol!r}, "
                f"price={self.price:.2f}, sector={self.sector!r})")


class StockHashMap:
    """
    Hash-map keyed by ticker symbol → StockRecord.

    All symbols are normalised to uppercase on write so that
    'aapl', 'AAPL', and 'Aapl' all resolve to the same bucket.
    """

    def __init__(self):
        # The underlying hash table
        self._map: dict[str, StockRecord] = {}

    # -------------------------------------------------------------- #
    # Write operations                                                 #
    # -------------------------------------------------------------- #

    def put(self, symbol: str, record: StockRecord) -> None:
        """
        Insert or replace a StockRecord for the given symbol.
        O(1) average.
        """
        self._map[symbol.upper()] = record

    def update(self, symbol: str, price: float, volume: int) -> bool:
        """
        Update price and volume for an existing symbol.
        Returns True on success, False if symbol not found.
        O(1) average.
        """
        key = symbol.upper()
        if key not in self._map:
            return False
        self._map[key].price  = float(price)
        self._map[key].volume = int(volume)
        return True

    def remove(self, symbol: str) -> bool:
        """
        Delete a symbol from the map.
        Returns True on success, False if not found.
        O(1) average.
        """
        key = symbol.upper()
        if key in self._map:
            del self._map[key]
            return True
        return False

    # -------------------------------------------------------------- #
    # Read operations                                                  #
    # -------------------------------------------------------------- #

    def get(self, symbol: str) -> StockRecord | None:
        """
        Retrieve a StockRecord by ticker symbol.
        Returns None if not found.
        O(1) average.
        """
        return self._map.get(symbol.upper())

    def contains(self, symbol: str) -> bool:
        """Membership test. O(1) average."""
        return symbol.upper() in self._map

    def all_records(self) -> list[StockRecord]:
        """
        Return a snapshot list of every record in the map.
        O(n).
        """
        return list(self._map.values())

    def size(self) -> int:
        """Number of entries currently in the map. O(1)."""
        return len(self._map)

    def keys(self) -> list[str]:
        """All ticker symbols currently stored. O(n)."""
        return list(self._map.keys())
