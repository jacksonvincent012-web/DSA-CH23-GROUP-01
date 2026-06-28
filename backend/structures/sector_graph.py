"""
=============================================================
 PHASE 2 — DSA Structure 5: SectorGraph
 Rubric requirement: Graph (BFS/DFS; Dijkstra optional)
=============================================================

WHY A GRAPH HERE?
  Stock sectors don't operate in isolation — TECH performance
  often leads FINANCE which leads ENERGY, creating a chain of
  correlated movements.  We model these relationships as a
  DIRECTED GRAPH where an edge A→B means "sector A influences
  sector B".

  Two traversal strategies answer two different questions:
    BFS — "which sectors are closest to TECH in influence?"
           (breadth = proximity layers)
    DFS — "if TECH moves, what is the full chain of sectors
           eventually affected?"
           (depth = complete reachability)

HOW IT WORKS — ADJACENCY LIST:
  The graph is stored as a dict mapping each node (sector name)
  to a list of its neighbours (sectors it influences).

  adjacency_list = {
    "TECH":    ["FINANCE", "MEDIA"],
    "FINANCE": ["ENERGY"],
    "ENERGY":  ["RETAIL"],
    ...
  }

  Adjacency list chosen over adjacency matrix because:
    • Our graph is SPARSE (50 nodes, ~200 edges max)
    • Adjacency list: O(V + E) space
    • Adjacency matrix: O(V²) space → 50² = 2,500 cells for 200 edges

BFS (Breadth-First Search):
  Uses a deque as the frontier queue — deque.popleft() is O(1).
  Visits nodes level by level (nearest sectors first).
  Time: O(V + E).

DFS (Depth-First Search):
  Uses Python's call stack (recursive).
  Explores one full path before backtracking.
  Time: O(V + E).

COMPLEXITY (Step 2 — Constraints):
  add_node   O(1)
  add_edge   O(1)
  bfs        O(V + E)
  dfs        O(V + E)
  adjacency  O(1)  — returns the dict reference
"""

from collections import deque


class SectorGraph:
    """
    Directed adjacency-list graph of stock sector relationships.

    Nodes  = sector names (strings), e.g. "TECH", "FINANCE"
    Edges  = directed influence relationships, e.g. TECH → FINANCE
    """

    def __init__(self):
        # { sector_name: [neighbour_sector, ...] }
        self._adj: dict[str, list[str]] = {}

    # -------------------------------------------------------------- #
    # Build the graph                                                  #
    # -------------------------------------------------------------- #

    def add_node(self, node: str) -> None:
        """
        Add a sector node if it doesn't already exist.
        O(1).
        """
        if node not in self._adj:
            self._adj[node] = []

    def add_edge(self, from_node: str, to_node: str) -> None:
        """
        Add a directed edge from_node → to_node.
        Auto-creates either node if missing.
        Prevents duplicate edges.
        O(1) amortised.
        """
        self.add_node(from_node)
        self.add_node(to_node)
        if to_node not in self._adj[from_node]:
            self._adj[from_node].append(to_node)

    def remove_edge(self, from_node: str, to_node: str) -> bool:
        """
        Remove the directed edge from_node → to_node.
        Returns True if removed, False if not found.
        O(degree of from_node).
        """
        if from_node in self._adj and to_node in self._adj[from_node]:
            self._adj[from_node].remove(to_node)
            return True
        return False

    # -------------------------------------------------------------- #
    # Traversal — BFS                                                  #
    # -------------------------------------------------------------- #

    def bfs(self, start: str) -> list[str]:
        """
        Breadth-First Search from start node.
        Returns sectors in order of increasing distance from start.
        Returns [] if start not in graph.

        Algorithm:
          1. Enqueue start; mark visited.
          2. While frontier not empty:
               dequeue node n  (O(1) — deque.popleft)
               append n to result
               for each unvisited neighbour: enqueue + mark visited
          3. Return result.

        Time:  O(V + E)
        Space: O(V)
        """
        if start not in self._adj:
            return []

        visited: set[str]    = {start}
        frontier: deque[str] = deque([start])   # ← deque for O(1) popleft
        result: list[str]    = []

        while frontier:
            node = frontier.popleft()           # O(1) — NOT list.pop(0)
            result.append(node)

            for neighbour in self._adj[node]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    frontier.append(neighbour)

        return result

    # -------------------------------------------------------------- #
    # Traversal — DFS                                                  #
    # -------------------------------------------------------------- #

    def dfs(self, start: str) -> list[str]:
        """
        Depth-First Search from start node.
        Returns all reachable sectors in DFS visit order.
        Returns [] if start not in graph.

        Algorithm (recursive):
          _dfs_visit(node):
            mark node visited
            append to result
            for each unvisited neighbour: recurse

        Time:  O(V + E)
        Space: O(V)  — call stack depth = longest path
        """
        if start not in self._adj:
            return []

        visited: set[str] = set()
        result:  list[str] = []

        def _dfs_visit(node: str) -> None:
            visited.add(node)
            result.append(node)
            for neighbour in self._adj[node]:
                if neighbour not in visited:
                    _dfs_visit(neighbour)

        _dfs_visit(start)
        return result

    def dfs_iterative(self, start: str) -> list[str]:
        """
        Iterative DFS using an explicit stack (list) to avoid Python's
        recursion limit on very large graphs (n > 1,000).

        Time:  O(V + E)
        Space: O(V)
        """
        if start not in self._adj:
            return []

        visited: set[str] = set()
        stack: list[str] = [start]
        result: list[str] = []

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                result.append(node)
                for neighbour in reversed(self._adj[node]):
                    if neighbour not in visited:
                        stack.append(neighbour)
        return result

    # -------------------------------------------------------------- #
    # Inspection                                                       #
    # -------------------------------------------------------------- #

    def get_adjacency_list(self) -> dict[str, list[str]]:
        """
        Return a copy of the full adjacency list.
        O(V + E) — copies every node and edge list.
        """
        return {node: list(neighbours)
                for node, neighbours in self._adj.items()}

    def get_nodes(self) -> list[str]:
        """All sector nodes. O(V)."""
        return list(self._adj.keys())

    def get_neighbours(self, node: str) -> list[str]:
        """Neighbours of a single node. O(1)."""
        return list(self._adj.get(node, []))

    def node_count(self) -> int:
        """Number of nodes. O(1)."""
        return len(self._adj)

    def edge_count(self) -> int:
        """Total number of directed edges. O(V)."""
        return sum(len(nbrs) for nbrs in self._adj.values())
