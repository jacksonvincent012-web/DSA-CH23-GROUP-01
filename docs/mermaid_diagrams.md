# ALL MERMAID DIAGRAMS — Stock Query Server
# Open this file in VS Code with Mermaid extension to render
# Screenshot each diagram separately

---

## DIAGRAM 1: USE CASE DIAGRAM (Coloured)

```mermaid
%%{init: {'fontSize': '16px', 'nodePadding': '20'}}%%
graph TB
    classDef viewer fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff,font-size:18px
    classDef analyst fill:#2196F3,stroke:#1565C0,stroke-width:3px,color:#fff,font-size:18px
    classDef admin fill:#FF9800,stroke:#E65100,stroke-width:3px,color:#fff,font-size:18px
    classDef sim fill:#9C27B0,stroke:#4A148C,stroke-width:3px,color:#fff,font-size:18px
    classDef uc fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#000,font-size:13px
    classDef ucSim fill:#F3E5F5,stroke:#4A148C,stroke-width:2px,color:#000,font-size:13px

    V["Viewer"]
    A["Analyst"]
    Ad["Admin"]
    S["Simulator"]

    UC1["UC1: Lookup Stock (O(1) HashMap)"]
    UC2["UC2: View Top-K (O(log K) Heap)"]
    UC3["UC3: Explore Sectors (BFS/DFS Graph)"]
    UC4["UC4: Sort History (O(n log n) MergeSort)"]
    UC5["UC5: Search Range (O(log n) BinarySearch)"]
    UC6["UC6: Login (JWT Auth)"]
    UC7["UC7: Create Alert (O(1) Stack)"]
    UC8["UC8: Undo Alert (O(1) Pop)"]
    UC9["UC9: Run Benchmarks"]
    UC10["UC10: Clear Cache"]
    UC11["UC11: Buffer Ticks (FIFO Queue)"]
    UC12["UC12: Seed 10K Stocks"]

    V --> UC1
    V --> UC2
    V --> UC3
    V --> UC4
    V --> UC5
    V --> UC6
    A --> UC7
    A --> UC8
    Ad --> UC9
    Ad --> UC10
    S --> UC11
    S --> UC12

    class V viewer
    class A analyst
    class Ad admin
    class S sim
    class UC1,UC2,UC3,UC4,UC5,UC6,UC7,UC8,UC9,UC10 uc
    class UC11,UC12 ucSim
```

---

## DIAGRAM 2: SYSTEM ARCHITECTURE

```mermaid
graph TB
    subgraph Client["CLIENT LAYER"]
        C1["curl / Postman"]
        C2["React Frontend"]
    end

    subgraph API["API & AUTH LAYER"]
        JWT[JWT Auth Middleware]
        EP["22 REST Endpoints<br/>/api/auth/* /api/stocks/*<br/>/api/alerts/* /api/cache/*"]
        CACHE["LRU Cache<br/>(capacity=50)"]
    end

    subgraph DSA["DSA ENGINE LAYER"]
        HM["StockHashMap<br/>10,000 stocks<br/>O(1) lookup"]
        HK["TopKHeap<br/>Min-Heap<br/>O(log K)"]
        AS["AlertStack<br/>LIFO + Undo<br/>O(1)"]
        SG["SectorGraph<br/>BFS / DFS<br/>O(V+E)"]
        MS["MergeSort<br/>O(n log n)"]
        BS["BinarySearch<br/>O(log n)"]
        IQ["IngestionQueue<br/>FIFO Buffer<br/>O(1)"]
    end

    subgraph SIM["SIMULATOR THREAD"]
        SD["Stock Seeder<br/>24 anchors + 9976 synthetic"]
        TG["Tick Generator<br/>every 2 seconds<br/>±2% price"]
    end

    C1 --> JWT
    C2 --> JWT
    JWT --> EP
    EP --> CACHE
    CACHE --> HM
    EP --> HM
    EP --> HK
    EP --> AS
    EP --> SG
    EP --> MS
    EP --> BS
    TG --> IQ
    IQ --> HM
    IQ --> HK
    IQ --> AS
    SD --> HM
    SD --> SG
```

---

## DIAGRAM 3: DATA FLOW — WRITE PATH (Simulator Tick)

```mermaid
sequenceDiagram
    participant S as Simulator
    participant Q as IngestionQueue
    participant M as StockHashMap
    participant H as TopKHeap
    participant A as AlertStack

    loop Every 2 seconds
        S->>S: Pick random stock
        S->>S: Generate ±2% price change
        S->>Q: enqueue(Tick)
        Q->>Q: drain() batch
        Q->>M: update(price, volume)
        Q->>H: push(symbol, volume)
        Q->>A: check thresholds
        Note over Q: O(1) per operation
    end
```

---

## DIAGRAM 4: DATA FLOW — READ PATH (Client Request)

```mermaid
sequenceDiagram
    participant C as Client
    participant J as JWT Auth
    participant L as LRU Cache
    participant M as StockHashMap

    C->>J: GET /api/stocks/AAPL
    Note over J: Bearer token
    J->>J: Validate JWT
    J->>L: get("AAPL")
    
    alt Cache HIT
        L-->>C: Return cached stock
        Note over L: O(1)
    else Cache MISS
        L->>M: get("AAPL")
        M-->>L: StockRecord
        L->>L: put("AAPL", result)
        L-->>C: Return stock
    end
```

---

## DIAGRAM 5: CONSTRAINT → DSA DECISION TREE

```mermaid
graph LR
    classDef constraint fill:#FF9800,stroke:#E65100,color:#fff
    classDef decision fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef dsa fill:#2196F3,stroke:#1565C0,color:#fff

    C1["10,000 stocks<br/>Need O(1) lookup"] --> D1["Hash Table"]
    C2["Real-time ticks<br/>Need FIFO buffer"] --> D2["Deque Queue"]
    C3["Top-K requests<br/>K ≤ 10"] --> D3["Min-Heap"]
    C4["Sector relations<br/>Need traversal"] --> D4["Adjacency List Graph"]
    C5["Sort history<br/>Need stability"] --> D5["Merge Sort"]
    C6["Price range search<br/>Need speed"] --> D6["Binary Search"]
    C7["Hot stock caching<br/>80/20 rule"] --> D7["HashMap + DLL"]

    class C1,C2,C3,C4,C5,C6,C7 constraint
    class D1,D2,D3,D4,D5,D6,D7 decision
```

---

## DIAGRAM 6: BOTTLENECKS & FIXES

```mermaid
graph TB
    classDef problem fill:#e94560,stroke:#c0392b,color:#fff
    classDef solution fill:#2ecc71,stroke:#27ae60,color:#fff

    B1["Top-K: Sorting 10K = O(N log N)"] --> F1["TopKHeap: O(log K) per push"]
    B2["Queue: list.pop(0) = O(n)"] --> F2["deque.popleft() = O(1)"]
    B3["Lookups: Every request hits HashMap"] --> F3["LRU Cache: O(1) for hot stocks"]
    B4["DFS: Recursion limit reached"] --> F4["dfs_iterative(): Explicit stack"]
    B5["Heap: Duplicate symbols"] --> F5["_symbols tracking dict"]

    class B1,B2,B3,B4,B5 problem
    class F1,F2,F3,F4,F5 solution
```

---

## DIAGRAM 7: MERGE SORT VISUALIZATION

```mermaid
graph TD
    A["[38, 27, 43, 3, 9, 82, 10]"] --> B1["[38, 27, 43, 3]"]
    A --> B2["[9, 82, 10]"]
    
    B1 --> C1["[38, 27]"]
    B1 --> C2["[43, 3]"]
    B2 --> C3["[9, 82]"]
    B2 --> C4["[10]"]
    
    C1 --> D1["[38]"]
    C1 --> D2["[27]"]
    C2 --> D3["[43]"]
    C2 --> D4["[3]"]
    C3 --> D5["[9]"]
    C3 --> D6["[82]"]
    
    D1 --> E1["[27, 38]"]
    D2 --> E1
    D3 --> E2["[3, 43]"]
    D4 --> E2
    D5 --> E3["[9, 82]"]
    D6 --> E3
    
    E1 --> F1["[3, 27, 38, 43]"]
    E2 --> F1
    E3 --> F2["[9, 10, 82]"]
    C4 --> F2
    
    F1 --> G["[3, 9, 10, 27, 38, 43, 82]"]
    F2 --> G
    
    style A fill:#f5a623,stroke:#e65100,color:#fff
    style G fill:#2ecc71,stroke:#27ae60,color:#fff
```

---

## DIAGRAM 8: TOPKHEAP VISUALIZATION (Min-Heap for Top-3)

```mermaid
graph TB
    subgraph Step1["Step 1: Push 100, 50, 75"]
        H1["[50, 100, 75]"]
        Note1["Root = 50 (smallest)"]
    end

    subgraph Step2["Step 2: Push 200 > 50 → replace"]
        H2["[75, 100, 200]"]
        Note2["Root = 75 (new threshold)"]
    end

    subgraph Step3["Step 3: Push 30 < 75 → discard"]
        H3["[75, 100, 200]"]
        Note3["30 is too small, ignored"]
    end

    subgraph Result["Top-3 Descending"]
        R["[200, 100, 75]"]
        NoteR["Sorted reverse for output"]
    end

    Step1 --> Step2 --> Step3 --> Result

    classDef heap fill:#3498db,stroke:#2980b9,color:#fff
    classDef note fill:#f5f5f5,stroke:#ddd,color:#333
    class H1,H2,H3,R heap
    class Note1,Note2,Note3,NoteR note
```

---

## DIAGRAM 9: LRU CACHE OPERATION

```mermaid
graph LR
    subgraph Before["Before get('AAPL')"]
        Head1["HEAD → [MSFT] ↔ [GOOG] ↔ [AAPL] ← TAIL"]
        Note1["MRU: MSFT, LRU: AAPL"]
    end

    subgraph After["After get('AAPL')"]
        Head2["HEAD → [AAPL] ↔ [MSFT] ↔ [GOOG] ← TAIL"]
        Note2["AAPL moves to MRU position"]
    end

    Before --> After
```

---

## DIAGRAM 10: SECTOR GRAPH BFS/DFS

```mermaid
graph TD
    TECH --> MEDIA
    TECH --> FINANCE
    TECH --> CONSUMER
    TECH --> RETAIL
    FINANCE --> ENERGY
    FINANCE --> HEALTHCARE
    ENERGY --> CONSUMER
    ENERGY --> TRANSPORT
    MEDIA --> CONSUMER
    HEALTHCARE --> CONSUMER
    CONSUMER --> ENERGY
    CONSUMER --> RETAIL
    RETAIL --> TRANSPORT
    REAL_ESTATE --> FINANCE
    REAL_ESTATE --> CONSUMER
    UTILITIES --> ENERGY
    UTILITIES --> REAL_ESTATE

    style TECH fill:#e94560,stroke:#c0392b,color:#fff,stroke-width:3px
    style FINANCE fill:#3498db,stroke:#2980b9,color:#fff
    style ENERGY fill:#f5a623,stroke:#e65100,color:#fff
    style HEALTHCARE fill:#2ecc71,stroke:#27ae60,color:#fff
    style CONSUMER fill:#9b59b6,stroke:#8e44ad,color:#fff
    style MEDIA fill:#1abc9c,stroke:#16a085,color:#fff
    style RETAIL fill:#e67e22,stroke:#d35400,color:#fff
    style TRANSPORT fill:#34495e,stroke:#2c3e50,color:#fff
    style REAL_ESTATE fill:#16a085,stroke:#138d75,color:#fff
    style UTILITIES fill:#7f8c8d,stroke:#707b7e,color:#fff
```

---

## DIAGRAM 11: JWT AUTH FLOW

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as User Store

    C->>S: POST /api/auth/login {email, password}
    S->>DB: Lookup user, verify hash
    DB-->>S: User found, password match
    S->>S: Create JWT {email, role, exp}
    S-->>C: {access_token, refresh_token}

    Note over C,S: --- Authenticated Request ---

    C->>S: GET /api/stocks/AAPL
    Note over C: Authorization: Bearer [token]
    S->>S: Decode JWT, verify signature + expiry
    S->>S: Extract email, role for RBAC
    S-->>C: 200 {symbol, price, volume, ...}
```

---

## DIAGRAM 12: BENCHMARK RESULTS VISUALIZATION

```mermaid
graph LR
    subgraph O1["O(1) Operations (Flat)"]
        L1["HashMap: 1μs at 1K, 10K, 100K"]
        L2["Queue: ~500μs at all sizes"]
        L3["Stack: ~500μs at all sizes"]
    end

    subgraph ON["O(n) Operations (Linear)"]
        L4["Graph BFS: 0.001s → 0.003s → 0.06s"]
        L5["Heap push: 0.002s → 0.009s → 0.046s"]
    end

    subgraph ONLOGN["O(n log n) Operations"]
        L6["MergeSort: 0.009s → 0.045s → 0.528s"]
        Note6["~13× per 10× data"]
    end

    subgraph OLOGN["O(log n) Operations"]
        L7["BinarySearch: 4μs → 2μs → 5μs"]
        Note7["Near flat, ~7 extra comparisons"]
    end
```

---

*End of Mermaid Diagrams — DSA-CH23-GROUP-01*
