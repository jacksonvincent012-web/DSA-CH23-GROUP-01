"""Generate architecture diagram SVG for Stock Query Server."""
import os

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 750" font-family="Consolas, monospace" font-size="13">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#555"/>
    </marker>
    <linearGradient id="layer1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#16213e;stop-opacity:1"/>
    </linearGradient>
    <linearGradient id="layer2" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#0f3460;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#1a1a2e;stop-opacity:1"/>
    </linearGradient>
    <linearGradient id="layer3" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#533483;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#0f3460;stop-opacity:1"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="900" height="750" fill="#0d1117" rx="8"/>
  <text x="450" y="35" text-anchor="middle" fill="#e6edf3" font-size="18" font-weight="bold">Stock Query Server — System Architecture</text>
  <text x="450" y="55" text-anchor="middle" fill="#8b949e" font-size="11">Theme C (C3: Alerts + Event Queue) — Chapter 23 System Design</text>

  <!-- Layer 1: Client Layer -->
  <rect x="30" y="75" width="840" height="160" rx="6" fill="url(#layer1)" stroke="#30363d" stroke-width="1.5"/>
  <text x="50" y="98" fill="#58a6ff" font-size="14" font-weight="bold">CLIENT LAYER</text>

  <!-- React box -->
  <rect x="60" y="110" width="230" height="105" rx="4" fill="#161b22" stroke="#30363d"/>
  <text x="175" y="135" text-anchor="middle" fill="#e6edf3" font-size="13" font-weight="bold">React / TypeScript</text>
  <text x="175" y="153" text-anchor="middle" fill="#8b949e" font-size="11">Vite 5 · Recharts</text>
  <text x="175" y="170" text-anchor="middle" fill="#8b949e" font-size="11">6 Tab Components</text>
  <text x="175" y="187" text-anchor="middle" fill="#8b949e" font-size="11">AuthContext · apiFetch</text>
  <text x="175" y="204" text-anchor="middle" fill="#8b949e" font-size="11">Dark Finance Theme</text>

  <!-- Vanilla box -->
  <rect x="335" y="110" width="230" height="105" rx="4" fill="#161b22" stroke="#30363d"/>
  <text x="450" y="135" text-anchor="middle" fill="#e6edf3" font-size="13" font-weight="bold">Vanilla HTML / JS</text>
  <text x="450" y="153" text-anchor="middle" fill="#8b949e" font-size="11">Zero Dependencies</text>
  <text x="450" y="170" text-anchor="middle" fill="#8b949e" font-size="11">app.js · style.css</text>
  <text x="450" y="187" text-anchor="middle" fill="#8b949e" font-size="11">Static File Fallback</text>
  <text x="450" y="204" text-anchor="middle" fill="#8b949e" font-size="11">Double-click to Run</text>

  <!-- Postman box -->
  <rect x="610" y="110" width="230" height="105" rx="4" fill="#161b22" stroke="#30363d"/>
  <text x="725" y="135" text-anchor="middle" fill="#e6edf3" font-size="13" font-weight="bold">Postman / REST Client</text>
  <text x="725" y="153" text-anchor="middle" fill="#8b949e" font-size="11">15-API Test Suite</text>
  <text x="725" y="170" text-anchor="middle" fill="#8b949e" font-size="11">JWT Auth Flow</text>
  <text x="725" y="187" text-anchor="middle" fill="#8b949e" font-size="11">CRUD Operations</text>
  <text x="725" y="204" text-anchor="middle" fill="#8b949e" font-size="11">Edge Case Coverage</text>

  <!-- Layer 2: API Layer -->
  <rect x="30" y="255" width="840" height="190" rx="6" fill="url(#layer2)" stroke="#30363d" stroke-width="1.5"/>
  <text x="50" y="278" fill="#58a6ff" font-size="14" font-weight="bold">API &amp; AUTH LAYER</text>

  <!-- Server box -->
  <rect x="60" y="290" width="350" height="135" rx="4" fill="#161b22" stroke="#30363d"/>
  <text x="235" y="315" text-anchor="middle" fill="#e6edf3" font-size="13" font-weight="bold">Flask REST API (server.py)</text>
  <text x="235" y="335" text-anchor="middle" fill="#8b949e" font-size="11">15 Endpoints: Health · Stocks · History · Search</text>
  <text x="235" y="352" text-anchor="middle" fill="#8b949e" font-size="11">Top-K · Sector BFS/DFS · Alerts · Benchmarks</text>
  <text x="235" y="369" text-anchor="middle" fill="#8b949e" font-size="11">CORS · Flask-CORS · JSON Responses</text>
  <text x="235" y="386" text-anchor="middle" fill="#8b949e" font-size="11">LRU Cache Integration Layer</text>
  <text x="235" y="403" text-anchor="middle" fill="#8b949e" font-size="11">Error Handling · Rate Limiting Ready</text>

  <!-- Auth box -->
  <rect x="490" y="290" width="350" height="135" rx="4" fill="#161b22" stroke="#30363d"/>
  <text x="665" y="315" text-anchor="middle" fill="#e6edf3" font-size="13" font-weight="bold">Auth &amp; Simulator (auth.py / simulator.py)</text>
  <text x="665" y="335" text-anchor="middle" fill="#8b949e" font-size="11">JWT Access Token (1h) + Refresh Token (7d)</text>
  <text x="665" y="352" text-anchor="middle" fill="#8b949e" font-size="11">RBAC: admin · analyst · viewer</text>
  <text x="665" y="369" text-anchor="middle" fill="#8b949e" font-size="11">@require_auth · @require_role()</text>
  <text x="665" y="386" text-anchor="middle" fill="#8b949e" font-size="11">Simulator: 24 stocks · 2s ticks · ±2%</text>
  <text x="665" y="403" text-anchor="middle" fill="#8b949e" font-size="11">SHA-256 Password Hashing</text>

  <!-- Layer 3: DSA Engine -->
  <rect x="30" y="465" width="840" width="840" height="265" rx="6" fill="url(#layer3)" stroke="#30363d" stroke-width="1.5"/>
  <text x="50" y="488" fill="#58a6ff" font-size="14" font-weight="bold">CORE DSA ENGINE — backend/structures/</text>

  <!-- DSA boxes in a 3x3 grid -->
  <!-- Row 1 -->
  <rect x="55" y="500" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="180" y="522" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">1. StockHashMap</text>
  <text x="180" y="540" text-anchor="middle" fill="#8b949e" font-size="10">Hash Table — O(1) symbol lookup</text>
  <text x="180" y="556" text-anchor="middle" fill="#8b949e" font-size="10">Python dict · Open-addressing</text>

  <rect x="325" y="500" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="450" y="522" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">2. IngestionQueue</text>
  <text x="450" y="540" text-anchor="middle" fill="#8b949e" font-size="10">Queue — FIFO tick buffer</text>
  <text x="450" y="556" text-anchor="middle" fill="#8b949e" font-size="10">collections.deque · O(1) ops</text>

  <rect x="595" y="500" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="720" y="522" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">3. AlertStack</text>
  <text x="720" y="540" text-anchor="middle" fill="#8b949e" font-size="10">Stack — LIFO + Undo buffer</text>
  <text x="720" y="556" text-anchor="middle" fill="#8b949e" font-size="10">list.append/pop · O(1) all ops</text>

  <!-- Row 2 -->
  <rect x="55" y="578" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="180" y="600" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">4. TopKHeap</text>
  <text x="180" y="618" text-anchor="middle" fill="#8b949e" font-size="10">Min-Heap — Top-K ranking</text>
  <text x="180" y="634" text-anchor="middle" fill="#8b949e" font-size="10">heapq · O(log K) per push</text>

  <rect x="325" y="578" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="450" y="600" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">5. SectorGraph</text>
  <text x="450" y="618" text-anchor="middle" fill="#8b949e" font-size="10">Adjacency List — BFS/DFS</text>
  <text x="450" y="634" text-anchor="middle" fill="#8b949e" font-size="10">deque · O(V+E) traversal</text>

  <rect x="595" y="578" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="720" y="600" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">6. MergeSort</text>
  <text x="720" y="618" text-anchor="middle" fill="#8b949e" font-size="10">Divide &amp; Conquer — O(n log n)</text>
  <text x="720" y="634" text-anchor="middle" fill="#8b949e" font-size="10">Stable sort · O(n) space</text>

  <!-- Row 3 -->
  <rect x="55" y="656" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="180" y="678" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">7. BinarySearch</text>
  <text x="180" y="696" text-anchor="middle" fill="#8b949e" font-size="10">Divide &amp; Conquer — O(log n)</text>
  <text x="180" y="712" text-anchor="middle" fill="#8b949e" font-size="10">lower_bound · range_search</text>

  <rect x="325" y="656" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="450" y="678" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">8. LRUCache</text>
  <text x="450" y="696" text-anchor="middle" fill="#8b949e" font-size="10">HashMap + Doubly Linked List</text>
  <text x="450" y="712" text-anchor="middle" fill="#8b949e" font-size="10">O(1) get/put · Eviction</text>

  <rect x="595" y="656" width="250" height="65" rx="4" fill="#161b22" stroke="#58a6ff" stroke-width="1"/>
  <text x="720" y="678" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="bold">9. Benchmarks</text>
  <text x="720" y="696" text-anchor="middle" fill="#8b949e" font-size="10">Empirical Big-O at N=1K/10K/100K</text>
  <text x="720" y="712" text-anchor="middle" fill="#8b949e" font-size="10">time.perf_counter · Median of 5</text>

  <!-- Arrows between layers -->
  <line x1="450" y1="235" x2="450" y2="255" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="450" y1="445" x2="450" y2="465" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Arrow labels -->
  <text x="465" y="248" fill="#8b949e" font-size="10">HTTP + JWT</text>
  <text x="465" y="458" fill="#8b949e" font-size="10">Python Imports</text>
</svg>'''

path = os.path.join(os.path.dirname(__file__), "architecture.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write(SVG)
print(f"Architecture diagram written to {path}")
