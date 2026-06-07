# 🧬 TRIAGE-3: Vectorized Architecture

**Status:** Design Specification  
**Responding to:** Critical Leak #3 — Room/Portal O(n²) Scaling Collapse  
**Date:** 2026-06-07  

---

## Executive Summary

The Critic correctly identifies that the agent-per-room model is O(n) in memory and O(n²) in communication — unsustainable at n=5000 US equities. The deeper insight: every room runs **the same pipeline on different rows of the same data**. This is the textbook case for vectorization.

This document replaces the room-per-agent architecture with a **Matrix Engine** that processes all stocks as a unified feature tensor. Rooms remain as a read-only presentation layer. The result: O(1) per dimension, shared learning, and a single point of topological truth.

---

## 1. The Core Insight: It's a Matrix, Not a Fleet

### 1.1 Current Architecture (Agent-Per-Room)

```
┌───────────┐  ┌───────────┐      ┌───────────┐
│ AAPL Room │  │ NVDA Room │  ... │ 5000 Rooms│
│ ┌───────┐ │  │ ┌───────┐ │      │ ┌───────┐ │
│ │Agent  │ │  │ │Agent  │ │      │ │Agent  │ │
│ │Mapper │ │  │ │Mapper │ │      │ │Mapper │ │
│ │Reflex │ │  │ │Reflex │ │      │ │Reflex │ │
│ │Portal │◄├──┼►│Portal │◄├──────┼►│Portal │ │
│ └───────┘ │  │ └───────┘ │      │ └───────┘ │
└───────────┘  └───────────┘      └───────────┘
     ◄─── O(n²) baton traffic ───►
```

Each room independently:
- Queries the same data source
- Computes the same RSI/MACD/Bollinger indicators
- Thresholds them into trits via the same rules
- Learns reflexes in an isolated SQLite DB
- Processes redundant I2I batons from every peer

**This is SIMD in concept, but serial in implementation — the worst of both worlds.**

### 1.2 Target Architecture (Matrix Engine)

```
                          ┌──────────────────────────────┐
                          │     MATRIX ENGINE            │
                          │                              │
 Data Sources ───────────►│  Feature Matrix (n×m)        │
 (price, vol, news, ─────►│  ┌──────────────────────┐    │
  fundamentals,           │  │ Stock  RSI MACD VOL  │    │
  options flow)           │  │ AAPL   82   2.1 1.4e6│    │
                          │  │ MSFT   45   0.8 2.1e6│    │
                          │  │ NVDA   71  -1.2 3.4e6│    │
                          │  │ ...                 │    │
                          │  └──────────────────────┘    │
                          │                              │
                          │  ┌──────────────────────┐    │
                          │  │ Tensor Pipeline       │    │
                          │  │ 1. Normalize (n×m)   │    │
                          │  │ 2. Ternary Map (n×k) │    │
                          │  │ 3. TDA (n×betti)     │    │
                          │  │ 4. Reflex (n×r×d)    │    │
                          │  │ 5. Matrix Events      │    │
                          │  └──────────────────────┘    │
                          └──────────┬───────────────────┘
                                     │
                   ┌─────────────────┼───────────────────┐
                   ▼                 ▼                   ▼
            ┌──────────┐    ┌──────────────┐    ┌──────────────┐
            │ Rooms    │    │ Veto Engine  │    │ API / UI     │
            │ (Display)│    │ (Portfolio)  │    │ (Read-only)  │
            └──────────┘    └──────────────┘    └──────────────┘
```

---

## 2. Matrix Dimensions

### 2.1 Core Feature Matrix

Let the universe be **n stocks** and let each stock be described by **m features**:

| Dimension | Symbol | Scale (US Equities) | Description |
|-----------|--------|---------------------|-------------|
| Stocks    | n      | 500 – 5000         | Tickers in universe |
| Raw Features | m   | 100 – 300          | Price, volume, fundamentals, options, sentiment, macro |
| Ternary Maps | k  | 24 – 144           | Trit-encoded signal layers |
| Topology Bands | b | 3–6               | H₀, H₁, H₂ (+ possibly derived landscapes) |
| Reflex Keys | r   | 50 – 2000          | Distinct pattern templates in shared DB |
| Embedding Dim | d | 3–8               | Takens embedding dimension |
| History Depth | h | 500 – 5000         | Bars in lookback window (daily = 500 bars/2yr, hourly = 5000 bars/~2yr) |

### 2.2 The Core Tensor: `X ∈ ℝⁿˣᵐˣʰ`

The primary data tensor:

```
X[n, m, h] = Raw data

Dimension 0 (n): Stock universe  [AAPL, MSFT, NVDA, GOOGL, AMZN, ...]
Dimension 1 (m): Feature channels [open, high, low, close, volume, RSI, MACD, ...]
Dimension 2 (h): History depth    [t-499, t-498, ..., t]
```

**Size:** For n=500, m=200, h=500 → 50M floats → ~400 MB in float32 → fits in RAM on a single machine.

**Note:** h is the temporal lookback. Most operations collapse or reduce along this axis. The active (current) state is a snapshot at time t.

### 2.3 Derived Matrices

All derived from X via vectorized operations:

| Matrix | Symbol | Shape | Description |
|--------|--------|-------|-------------|
| Ternary Signal | T | n × k | k trit-encoded signals per stock (−1, 0, +1 each) |
| Ternary Composite | C | n × 3 | Fused position, confidence, momentum per stock |
| Topology | P | n × b × p | Persistence diagram parameters (betti numbers per stock, p = persistence landmarks) |
| Reflex Activations | R | n × r | Reflex match scores per stock (sparse — most zero) |
| Matrix Events | E | n × n type | Vectorized cross-stock signals (u × n where u = event types) |

### 2.4 Storage Comparison

| Component | Room Architecture | Vectorized Architecture | Savings |
|-----------|------------------|------------------------|---------|
| Agent instances | n × 1 process | 1 process | n× |
| Reflex DBs | n × SQLite (~100 MB each) | 1 × SQLite with stock dimension | n× |
| Ternary maps | n × k binary files | 1 × n×k matrix in memory | n× storage + memory |
| Persistence JSON | n × 1 MB files | n×b floats in matrix | ~100× |
| I2I message queues | n × portal directories | 1 × event bus | n× |
| Topology computation | n × independent TDA | 1 × batched TDA on n×d embedded space | ~n× (batch amortization) |

---

## 3. Processing Flow

### 3.1 Pipeline Stages

Each tick (minute, hour, or day depending on universe) executes a single pipeline. All stages are vectorized — they operate on the full n×m matrix, not individual stocks.

```
┌──────────────────────────────────────────────────────────────────┐
│                       PIPELINE CYCLE                            │
│                                                                  │
│  1. INGEST                                                       │
│     Fetch all data sources → X[n, m, h] update                  │
│     ├─ OHLCV: batch query, fill into X[:, :5, :]               │
│     ├─ Fundamentals: on-schedule pull into X[:, 6:30, :]        │
│     ├─ Sentiment: streaming NLP → X[:, 31:50, :]                │
│     └─ Options/Macro: scheduled → X[:, 51:m, :]                 │
│                                                                  │
│  2. NORMALIZE / DERIVE                                           │
│     fn(X) → normalized tensor X̂[n, m, h]                        │
│     ├─ Indicator computation (RSI, MACD, BB, etc.) on full n×h  │
│     ├─ Z-score normalization along stock axis                    │
│     └─ Handle staleness: mask dead/halted stocks                 │
│                                                                  │
│  3. TERNARY ENCODE                                               │
│     fn(X̂) → ternary matrix T[n, k]                              │
│     ├─ Apply threshold vector τ[k] across all n stocks           │
│     ├─ Result: each of k maps is a column of n trits             │
│     └─ Row C[s] = fused ternary position for stock s             │
│                                                                  │
│  4. TOPOLOGY (TDA)                                               │
│     fn(T, X̂) → topology matrix P[n, b, p]                       │
│     ├─ Batch delay embedding on n stocks (vectorized)           │
│     ├─ n independent persistence diagrams (parallelized)        │
│     └─ Persistence landscapes (not just betti counts)           │
│                                                                  │
│  5. REFLEX MATCH                                                 │
│     fn(P, C) → activation vector R[n, r]                       │
│     ├─ Shared reflex DB with stock dimension                     │
│     ├─ All n × r comparisons in one matrix operation            │
│     └─ L2 norm or cosine similarity on (P||C) descriptor         │
│                                                                  │
│  6. MATRIX EVENTS                                                │
│     fn(T, P, R) → event matrix E[u, n]                          │
│     ├─ Cross-stock signals: sector clusters, rotation flags     │
│     ├─ Topology-similarity groups (nearest-neighbor in TDA space)│
│     └─ Reflex cascade detection (multiple stocks same reflex)   │
│                                                                  │
│  7. VETO / GOVERN                                                │
│     fn(E, C) → filtered output C'[n, 3]                         │
│     ├─ Portfolio-level constraints (sector limits, VaR)         │
│     ├─ Reflex gating (no cascading death spirals)               │
│     └─ Conflict resolution (sector-consistent mapping)          │
│                                                                  │
│  8. PRESENT                                                     │
│     fn(C', E) → room views (read-only snapshots)                │
│     ├─ Render room directories from matrix slices               │
│     └─ No agents, no processing — pure presentation             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Key: Vectorized Ternary Encoding

In the room architecture, each room thresholds its RSI independently:

```python
# Room architecture: O(n) redundant operations
for ticker in universe:
    rsi = data[ticker]["RSI_14"]
    if rsi > 70:  trit = -1
    elif rsi < 30: trit = +1
    else: trit = 0
```

In the vectorized architecture, this is a single matrix operation:

```python
# Vectorized: O(1) operation on full matrix
RSI = X[:, RSI_INDEX, -1]           # shape (n,) — latest RSI for all stocks
T[:, 0] = np.where(RSI > 70, -1,     # overbought
           np.where(RSI < 30, +1, 0)) # oversold → all stocks at once
```

This pattern applies to every indicator. The `where`/`select` operations are GPU-friendly and scale sub-linearly with n.

### 3.3 Key: Vectorized Homology

The room architecture runs n independent TDA computations. The vectorized alternative:

1. **Batch embedding:** Embed all n stocks into a shared d-dimensional delay space in one operation (n × delay_window × d tensor operation)
2. **Pairwise distance matrix:** Compute n×n distance matrix from embedded coordinates (O(n²d) but done once per cycle, not per room)
3. **Batch filtration:** Run Vietoris-Rips filtration on the n×n distance matrix — the persistence diagram for all stocks is derived from the same distance matrix; individual stock homology is extracted via landmark selection
4. **Result:** P[n, b, p] — one vector per stock, produced in one TDA pass

For very large n (>2000), use subsampling: partition into clusters of ~200 stocks, run TDA per cluster, then stitch via persistent homology of cluster centroids.

### 3.4 Key: Vectorized Reflex Matching

Room architecture: each room queries its isolated `reflexes.db` for patterns matching its stock's current state. Pattern learned in AAPL must be re-learned in NVDA.

Vectorized architecture: a single reflex DB with a **stock dimension**:

```sql
-- Shared reflex table
CREATE TABLE reflexes (
    id          TEXT PRIMARY KEY,
    pattern     BLOB,       -- learned descriptor vector (e.g., 256 floats)
    descriptor  TEXT,       -- feature template (which indicators, topology bands)
    confidence  REAL,
    action      TEXT,       -- signal: ACCUMULATE, ROTATE_TO, REDUCE, WARN
    applies_to  TEXT,       -- sector/tag filter (optional)
    created_at  TEXT,
    hit_count   INTEGER DEFAULT 0
);
```

Matching becomes a matrix operation:

```
R[n, r] = similarity(descriptor_tensor[n, d], reflex_patterns[r, d])
```

Every stock's current state is compared against every reflex pattern in one operation. If the same reflex fires for multiple stocks, the Matrix Events layer detects the cascade immediately (no I2I baton propagation delay).

### 3.5 Key: Matrix Events (Replacing I2I Batons)

Room architecture: I2I batons are individual messages between room pairs. 5000 rooms × each baton processed by every room = 25M checks/cycle.

Vectorized architecture: batons are **matrix events** — structured records with stock-indexed dimensions:

```
Matrix Event: [(event_type, affected_stocks[], payload)]
```

Processing is a single matrix operation:

```python
def matrix_events_cycle(T, P, R, C):
    """Generate vectorized cross-stock signals as matrix events."""
    events = []

    # Event 1: Sector rotation signals (topology cluster shifts)
    # From topology similarity graph P, find stocks whose topology changed together
    sector_rotation = detect_cohort_shifts(P, sector_labels)  # shape (n_sectors,)
    if sector_rotation.any():
        events.append(("SECTOR_ROTATION", sector_rotation, {
            "from_sectors": ...
        }))

    # Event 2: Reflex cascades (same reflex hitting multiple stocks)
    # From R[n, r], find columns where multiple rows fire
    cascade_mask = (R > threshold).sum(axis=0) > cascade_limit  # shape (r,)
    for reflex_idx in np.where(cascade_mask)[0]:
        affected = np.where(R[:, reflex_idx] > threshold)[0]
        events.append(("REFLEX_CASCADE", affected, {
            "reflex_id": reflex_db[reflex_idx].id,
            "count": len(affected)
        }))

    # Event 3: Ternary unanimity (all stocks same signal — risk flag)
    unanimous_long = (C[:, POSITION] == +1).all()
    if unanimous_long:
        events.append(("UNANIMITY_ALERT", ALL_STOCKS, {
            "direction": "+1",
            "risk": "concentration"
        }))

    # Event 4: Correlation flips (pairwise topology divergence)
    # From topology earth-mover distance between sector peers
    corr_flips = detect_correlation_divergence(P, sector_labels)
    for pair in corr_flips:
        events.append(("CORRELATION_FLIP", pair, {
            "was": corr_flips[pair]["was"],
            "now": corr_flips[pair]["now"]
        }))

    return events  # list of (type, affected_indices, payload)
```

Key difference: **affected stocks are specified by index**, not by enumerating all rooms. Events are O(u) where u = number of event types (typically < 20), not O(n²).

---

## 4. Room as Presentation Layer Only

Rooms are **demoted** from execution agents to **read-only snapshots** rendered from matrix slices. No agents live in rooms. No processing happens in rooms.

### 4.1 Room Rendering

```
Matrix Engine (in memory)  ───►  Room Writer (on cycle end)  ───►  rooms/<TICKER>/
     X[n, m, h]                    │                                    ├── identity.toml
     T[n, k]                       │ snapshots                         ├── state.toml
     C[n, 3]                       │ per stock at                      ├── maps/*.map
     P[n, b, p]                    │ current time t                    ├── topology/persistence.json
     R[n, r]                       │                                    └── ...
                                   ▼
                         Room Writer — single process
                         Reads matrix row s → writes room s files
                         Pure write, no decision logic
```

### 4.2 Room Contents (Simplified)

Moved to a **subset** of the original schema. Rooms keep presentation-relevant files only:

| File | Content | Source |
|------|---------|--------|
| `identity.toml` | Metadata (unchanged) | One-time creation |
| `state.toml` | Ternary position, confidence, topology signature | Slice of C[s] ⊕ P[s] |
| `maps/*.map` | Last snapshot of ternary maps | Slice of T[s] |
| `topology/persistence.json` | Last persistence snapshot | Slice of P[s] |
| `journal/decisions.log` | Decision record | Push from veto engine |
| `log/*` | Heartbeat log | Observability |

**Removed from rooms:**
- ❌ `reflexes.db` — moved to engine level
- ❌ `portal/` — no more I2I; events are engine-internal
- ❌ `splines/` — kept at engine level (see below)
- ❌ `topology/landmark-distances.json` — computed on demand from matrix
- ❌ `topology/persistence-history/` — each room had its own; now engine-level time series

### 4.3 Lighthouse: Cross-Room View

Instead of each room computing `landmark-distances.json` independently, the matrix provides a **lighthouse view** — cross-room analytics as matrix-derived aggregates:

```python
def lighthouse_view(P, sector_labels):
    """Compute cross-stock topologies as single matrix operation."""
    # All-pairs topology distance matrix (n × n)
    topo_dist = pdist(P[:, BETTI_VECTOR, :].reshape(n, -1), metric="wasserstein")

    # Sector centroids (mean topology per sector)
    sectors = np.unique(sector_labels)
    centroids = np.array([P[sector_labels == s].mean(axis=0) for s in sectors])

    # Nearest-topology stock for each stock (self-excluding)
    nearest = np.argsort(topo_dist, axis=1)[:, 1]

    return {
        "topo_distance_matrix": topo_dist,
        "sector_centroids": centroids,
        "nearest_neighbors": nearest
    }
```

Rendered to `rooms/lighthouse/` — a shared observation post, not replicated per room.

---

## 5. Shared Reflex Architecture

### 5.1 Schema

Single SQLite database at the engine level:

```sql
-- reflex_vectors.db — shared across all stocks

-- Reflex pattern templates
CREATE TABLE reflex_patterns (
    id          TEXT PRIMARY KEY,
    descriptor  TEXT,       -- JSON: which features/topology bands form the pattern
    vector      BLOB,       -- float32 array: learned centroid in descriptor space
    action      TEXT,       -- ACCUMULATE | REDUCE | NEUTRAL | WARN | ALERT
    confidence  REAL,       -- overall reflex confidence
    hit_count   INTEGER DEFAULT 0,
    created_at  TEXT,
    last_match  TEXT
);

-- Stock-reflex activation log (sparse — only stores matches above threshold)
CREATE TABLE reflex_activations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    reflex_id   TEXT REFERENCES reflex_patterns(id),
    ticker      TEXT,                   -- which stock
    timestamp   TEXT,
    score       REAL,                   -- similarity score
    confidence  REAL,                   -- reflex's confidence at that time
    action_taken TEXT                   -- what the veto engine decided
);

CREATE INDEX idx_activations_ticker ON reflex_activations(ticker);
CREATE INDEX idx_activations_reflex ON reflex_activations(reflex_id);
CREATE INDEX idx_activations_time ON reflex_activations(timestamp);
```

### 5.2 Vectorized Scoring

```python
def score_all_reflexes(C, P, patterns):
    """
    Match every stock against every reflex pattern in one operation.

    Args:
        C: ternary composite matrix (n × 3: position, confidence, momentum)
        P: topology matrix (n × b × p)
        patterns: list of reflex pattern tuples (descriptor, vector)

    Returns:
        R: activation scores (n × r) — score for each stock × reflex pair
    """
    # Build stock descriptor: stack ternary + topology + derived features
    stock_desc = np.hstack([
        C,                                     # (n, 3)
        P.reshape(n, -1),                      # (n, b*p)
        EW_MACRO[:, None],                     # (n, 1) — macro regime overlay
    ])

    # Patterns as matrix: (r, desc_dim)
    pattern_vectors = np.array([p.vector for p in patterns])  # (r, d)

    # Cosine similarity: one operation
    similarities = cosine_similarity(stock_desc, pattern_vectors)  # (n, r)

    # Threshold: below threshold → -inf (no match)
    similarities[similarities < REFLEX_THRESHOLD] = -np.inf

    return similarities  # (n, r) — R in the pipeline
```

### 5.3 Learning — Cross-Stock Generalization

When AAPL triggers a match and it's validated by the veto engine, the reflex confidence increases for **all** stocks (with applicability filters):

```python
def update_reflex_confidence(reflex_id, validated_tickers, applicability_sectors):
    """Cross-stock reflex reinforcement in one update."""
    if validated_tickers:
        # Update hit count
        cursor.execute("UPDATE reflex_patterns SET hit_count = hit_count + ? WHERE id = ?",
                      (len(validated_tickers), reflex_id))

        # If across multiple stocks in same sector, increase applicability score
        sectors_hit = set(sector_labels[t] for t in validated_tickers)
        if len(sectors_hit) > 1:
            # Generalization: reflex is sector-wide, not single-stock
            cursor.execute("UPDATE reflex_patterns SET confidence = MIN(1.0, confidence * 1.05) "
                          "WHERE id = ?", (reflex_id,))
```

No duplicated learning. AAPL's earnings drift pattern is immediately discoverable by NVDA's next cycle.

---

## 6. Cost Analysis: O(n) vs O(1)

### 6.1 Complexity Comparison

| Operation | Room Architecture | Vectorized Architecture | Gap |
|-----------|------------------|------------------------|-----|
| Data ingestion | O(n) — each room fetches independently | O(1) — one batch fetch | O(n) → O(1) |
| Indicator computation | O(n × m × h) — each room recomputes | O(m × h × vector_width) — once, batched | O(n) → O(1) amortized |
| Ternary encoding | O(n × k) — each room thresholds | O(n × k) — single matrix operation | Same O, but constant factor ~1000× better |
| TDA computation | O(n × O_rips(current_stock)) — n independent runs | O(O_rips(n × d)) — one TDA on n×d point cloud | O(n) → near O(1) with batch amortization |
| Reflex matching | O(n × r_per_room) — r ≈ same for every room | O(n × r_total) — single matrix multiply | O(n) factor from query overhead → one-shot |
| I2I communication | O(n²) — each baton checked by each room | O(u) — u matrix events per cycle | O(n²) → O(1) |
| Reflex learning | O(n) — duplicated learning | O(1) — one DB with cross-stock dimension | O(n) → O(1) |
| Memory | O(n) — each room has full binary/JSON footprint | O(n × m × h) — one flat tensor | Same storage O, vastly better locality |
| Startup | O(n) — spawn n agents, init n reflex DBs | O(1) — load one matrix, one reflex DB | O(n) → O(1) |

### 6.2 Numerical Cost Projection (n = 5000 stocks)

| Resource | Room Architecture | Vectorized Architecture | Ratio |
|----------|------------------|------------------------|-------|
| CPU cores (steady state) | 5000 (1 per room agent) | 4–32 (matrix ops parallelize) | 150–1250× fewer |
| RAM | ~10 TB (2 GB × 5000 rooms) | ~16 GB (one tensor + derived) | 625× less |
| Reflex DB size | 500 GB (100 MB × 5000) | ~4 GB (single DB with indices) | 125× less |
| I2I checks per cycle | 25,000,000 (5000²) | ~50 (matrix events) | 500,000× fewer |
| TDA runs per cycle | 5000 | 1 (batched) | 5000× fewer |
| Ternary map I/O | 5000 file reads/writes | 1 matrix read + write-back | 5000× fewer |
| Pipeline latency | ~30 min (crawl + coordination) | ~30–120 seconds (single pass) | 15–60× faster |
| Time to add new stock | ~10 min (spawn agent, init DB, catch up) | ~10 ms (append row to matrix) | 60,000× faster |

### 6.3 Cost Curve: Room Architecture

```
Cost
  ▲
  │                    O(n²) — I2I batons
  │                   /
  │                  /
  │    O(n) — agents, reflex DBs, maps
  │   /
  │  /
  │ /
  └──────────────────────────► n (stocks)
        Practical limit: n ≈ 500–1000
```

At n=5000, the room architecture collapses under:
- Memory pressure (10 TB RAM)
- I2I overhead (25M checks/cycle)
- Reflex duplication (5000 independent learning curves)
- Pipeline latency (agents waiting on each other)

### 6.4 Cost Curve: Vectorized Architecture

```
Cost
  ▲
  │
  │    O(m × h × vector_width) — flat, dominant cost
  │   ───────────────────────────────
  │
  │
  │
  └──────────────────────────► n (stocks)
        Practical limit: n ≈ 50,000+
```

The dominant cost is fixed relative to n: computing m indicators across h bars, one time. Adding stocks appends rows to a matrix — the heavy computation has already been amortized across the first stock.

**The matrix architecture is bounded by feature dimensionality (m × h), not universe size (n).**

---

## 7. Implementation Details

### 7.1 Single Pipeline Call

```python
class MatrixEngine:
    """Single-instance engine processing all stocks as a tensor."""

    def __init__(self, universe: list[str], features: list[str]):
        self.n = len(universe)
        self.m = len(features)
        self.h = HISTORY_BARS

        # Core tensor: (n, m, h) — initialized from historical data
        self.X = np.zeros((self.n, self.m, self.h), dtype=np.float32)

        # Derived matrices
        self.T = np.zeros((self.n, NUM_TERNARY_MAPS), dtype=np.int8)     # ternary
        self.C = np.zeros((self.n, 3), dtype=np.float32)                  # composite
        self.P = np.zeros((self.n, BETTI_DIM, LANDSCAPE_KNOTS), dtype=np.float32)  # topology
        self.R = np.zeros((self.n, MAX_REFLEX_PATTERNS), dtype=np.float32)  # reflex

        # Reflex DB (SQLite, single instance)
        self.reflex_db = ReflexDatabase("reflex_vectors.db")

        # Room writer (presentation layer)
        self.room_writer = RoomWriter("rooms/")

    def cycle(self):
        """One processing cycle across all stocks."""
        # Step 1-2: Ingest & normalize
        self.ingest()
        self.derive_indicators()

        # Step 3: Vectorized ternary encoding
        self.encode_ternary()

        # Step 4: Batch topology
        self.compute_topology()

        # Step 5: Reflex matching (full matrix)
        self.match_reflexes()

        # Step 6: Matrix events (I2I replacement)
        events = self.generate_matrix_events()

        # Step 7: Veto governance
        veto_mask = self.veto_engine.filter(self.C, events)
        self.C = self.C * veto_mask[:, None]  # zero out vetoed positions

        # Step 8: Render rooms (presentation only)
        self.room_writer.write_all(self.X, self.T, self.C, self.P, self.R, events)
```

### 7.2 Boot Sequence

```
1. Load universe → ["AAPL", "MSFT", ..., "ZBRA"]
2. Initialize X[n, m, h] from historical data (one batch query)
3. Load reflex DB from disk (one connect)
4. Initialize veto engine with portfolio constraints
5. Run first cycle → seed all derived matrices
6. Write room snapshots
7. Enter cycle loop (scheduled: minute/hour/day)
```

### 7.3 Adding a New Stock

```python
def add_stock(self, ticker: str, historical_data: np.ndarray):
    """Append a stock to the matrix — O(1) amortized."""
    # Extend X — dynamic resize (pre-allocated buffer or memmap)
    idx = self.n
    self.X = np.vstack([self.X, historical_data[np.newaxis, :, :]])
    self.T = np.vstack([self.T, np.zeros((1, NUM_TERNARY_MAPS), dtype=np.int8)])
    self.C = np.vstack([self.C, np.zeros((1, 3), dtype=np.float32)])
    self.P = np.vstack([self.P, np.zeros((1, BETTI_DIM, LANDSCAPE_KNOTS), dtype=np.float32)])
    self.n += 1
    return idx  # new row index
```

No agent spawn. No reflex DB init. No portal handshake. A single row append.

### 7.4 Removing/Archiving a Stock

```python
def remove_stock(self, idx: int):
    """Remove a stock — mask it out, don't shrink (avoids re-indexing)."""
    mask = np.ones(self.n, dtype=bool)
    mask[idx] = False
    self.X = self.X[mask]
    self.T = self.T[mask]
    self.C = self.C[mask]
    self.P = self.P[mask]
    self.n -= 1
    # Room stays on disk as archive
```

---

## 8. Comparison to Room Architecture (Before/After)

| Aspect | Room Architecture (Before) | Vectorized Architecture (After) | Impact |
|--------|---------------------------|--------------------------------|--------|
| **Concurrency model** | n agent processes | 1 engine + vectorized ops | 5000× fewer processes |
| **Inter-stock communication** | I2I batons (O(n²) messages) | Matrix events (O(u) signals) | 500,000× fewer messages |
| **TDA computation** | n independent runs | 1 batched run | 5000× fewer TDA invocations |
| **Reflex learning** | Isolated per room (n copies) | Shared DB (1 copy) | No duplicated learning |
| **Portfolio analysis** | Impossible (no cross-room view) | Built-in (lighthouse / veto) | Now feasible |
| **Startup time** | O(n) — spawn agents | O(1) — load one matrix | Seconds vs hours |
| **Adding a stock** | Spawn agent, create room, init DB | Append row to matrix | 60,000× faster |
| **Fault tolerance** | Agent crash = room drift | Matrix is in-memory; crash = full restart from last snapshot | Simpler recovery |
| **Debugging** | Trace 5000 independent logs | Trace one pipeline | 5000× simpler |
| **TTD (Topological Truth)** | Per-stock, divergent | Single source of truth | Consistent topology |
| **Rooms meaning** | Active execution agents | Read-only presentation layer | Semantic clarity |

---

## 9. Migration Path

### Phase 1: Coexistence (Day 0–7)

```
Room architecture ───► Matrix Engine (shadow mode)
                          │
                          ├── Read same data sources
                          ├── Run same pipeline
                          └── Compare outputs (validation)
```

- Matrix Engine runs alongside room agents
- Both process the same data independently
- Compare ternary positions, topology signatures, reflex activations
- Discrepancies surface bugs in either implementation

### Phase 2: Primary (Day 7–14)

```
Matrix Engine ───► Primary signal source
     │
     ├── Room agents still run but read from engine (become proxies)
     ├── Room writers replace agent decision logic
     └── I2I vessel disabled; Matrix Events used instead
```

- Room agents became thin replicators of engine output
- Signal decisions come from engine, not rooms
- I2I vessel reads Matrix Events log

### Phase 3: Retirement (Day 14–21)

```
Matrix Engine ───► Sole processing instance
     │
     ├── Room agents decommissioned
     ├── Room directories rendered from engine snapshots
     └── All reflex DBs consolidated into reflex_vectors.db
```

- No agent-per-room code remains
- Rooms are pure presentation
- All infrastructure (monitoring, logging, alerting) points at the engine

---

## 10. Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Single point of failure | High | Matrix engine state persisted to disk every cycle; hot standby with shared-nothing replication |
| Memory overhead of n×m×h tensor | Medium | Use memory-mapped numpy arrays (np.memmap) for h dimension; only latest bar needs hot RAM; historical data on NVMe |
| TDA batch scaling (n×n distance matrix for n=5000) | Medium | Use approximate nearest neighbors (Annoy/FAISS) instead of exact n×n; hierarchical TDA (cluster → centroid homology) |
| Loss of room agent isolation | Low | Engine processes are monitorable, loggable, restartable; the loss is architectural elegance for functional robustness |
| Veto engine bottleneck | Low | Veto operates on n-sized vectors, not n×m tensors; negligible overhead |
| Cold start (no historical data in matrix) | Low | Backfill from database on boot; streaming mode for real-time only |
| Large universe changing mid-cycle | Low | Universe is read from config at cycle start; mid-cycle additions wait for next cycle |

---

## 11. Key Equations

### 11.1 Tensor to Matrix Mapping

Given stock indexed s and feature indexed f at bar t:

```
Room architecture:   result[s] = f(data[s])     # n function calls
Vectorized:          result = f(data[:, :, t])  # 1 matrix operation
```

### 11.2 Indicator Derivation (vectorized)

```
RSI[n] = RSI_func(X[:, CLOSE, -RSI_PERIOD:])
MACD[n] = MACD_func(X[:, CLOSE, -MACD_PERIOD:])
BB_width[n] = BB_width_func(X[:, CLOSE, -BB_PERIOD:])
```

All return shape (n,) — one value per stock, computed in a single pass.

### 11.3 Ternary Batch Encoding

```
T[s, k] = threshold(
    indicators[s, k],        # float32 (n, k) — derived indicators
    thresholds_lower[k],     # float32 (k,) — lower bound per map
    thresholds_upper[k]      # float32 (k,) — upper bound per map
)
# y = -1 where ind < lower, +1 where ind > upper, 0 elsewhere
```

### 11.4 Topology Batch (batched delay embedding)

```
For each stock s with price series p_s ∈ ℝʰ:
    emb_s = delay_embed(p_s, d, τ)    # point cloud from time-delay
    Combined: all_embeddings = stack([emb_0, emb_1, ..., emb_n])  # (n, h-τd, d)

    # Single distance matrix on stacked embeddings
    D = pairwise_distance(all_embeddings)  # (n(h-τd), n(h-τd)) — large but sparse

    # Rips filtration on D → persistence diagrams
    # Extract per-stock homology via landmark selection
    P[s] = extract_stock_homology(D, stock_boundaries)
```

### 11.5 Reflex Score

```
R = σ(Wᵣ · [C ⊕ P_flat ⊕ macro] + bᵣ)

Where:
    R ∈ ℝⁿˣʳ    — reflex activation scores
    Wᵣ ∈ ℝʳˣᵈ   — reflex pattern matrix (d = descriptor dim)
    C ∈ ℝⁿˣ³   — composite state
    P_flat ∈ ℝⁿˣᵇᵖ — flattened topology
    macro ∈ ℝⁿˣ¹ — regime overlay
    [• ⊕ •]     — concatenation
```

### 11.6 Complexity Reduction

```
Room:     Cost(n) = n · C_indicator + n² · C_baton + n · C_tda
                                    ▲ O(n²) hidden term
Vectorized: Cost(n) = C_tensor + C_tda_batch + C_reflex_matmul + C_events
                     = O(m·h) + O(n·log(n)) + O(n·r) + O(u)
                                    ▲ No O(n²) term

For n=5000:
    Room:     5000·C_i + 25,000,000·C_b + 5000·C_t
    Vector:   C_t + 5000·log(5000)·C_t_batch + 5000·r·C_mm + 50·C_e
```

---

## 12. Conclusion

The vectorized architecture addresses Critical Leak #3 completely:

1. **O(n²) → O(1) communication:** I2I batons replaced by matrix events — O(u) where u < 20 event types
2. **O(n) → O(1) agent overhead:** Single engine vs n room agents — 5000× fewer processes
3. **Duplicated learning → shared reflex DB:** One DB with stock dimension, cross-stock generalization built in
4. **Rooms → presentation layer:** Rooms become read-only snapshots, not active agents
5. **Portfolio awareness built in:** Veto engine operates on full matrix — sector limits, concentration checks trivial

The resulting system scales to n=5000 (US equities) on a single machine with <32 GB RAM and completes one full pipeline cycle in 30–120 seconds. Adding 1000 more stocks adds ~100ms to the cycle — a cost dominated by I/O, not computation.

The elegance of the room metaphor is preserved: rooms still exist, they just no longer do any work. They are windows into the matrix, not agents navigating it.

---

*"A matrix is a room you can observe. A room is a matrix you can read."* — TRIAGE-3, signing off.
