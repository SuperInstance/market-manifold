# 🏛️ Room Structure — Stock Room Directory Layout & Identity

> *"Each stock room is a shell. The I2I batons are the calcium bridges that connect the shells into a coral reef."*

---

## 1. Directory Layout

Every stock ticker managed by Market Manifold gets a **room** — a self-contained directory that houses all data, reflexes, topology, and logs for that instrument. Rooms live under `rooms/<TICKER>/`.

```
rooms/<TICKER>/
├── identity.toml              # Room identity, metadata, active state
├── state.toml                 # Current ternary position, confidence, heartbeat
├── maps/                      # Ternary-encoded signal layers
│   ├── technical.map          #   Technical indicators → {−1, 0, +1}
│   ├── fundamental.map        #   Fundamental ratios → {−1, 0, +1}
│   ├── sentiment.map          #   Sentiment signals → {−1, 0, +1}
│   ├── options.map            #   Options flow / greeks → {−1, 0, +1}
│   ├── macro.map              #   Macro overlay → {−1, 0, +1}
│   ├── composite.map          #   Weighted ensemble of all maps
│   └── README.map             #   Map manifest (field definitions)
├── topology/                  # Persistent homology & geometric data
│   ├── persistence.json       #   Current persistence diagram snapshot
│   ├── persistence-history/   #   Snapshots over time (one per detection cycle)
│   │   └── YYYYMMDD_HHMMSS.persistence.json
│   ├── betti-curve.json       #   Betti number time series (β₀, β₁, β₂)
│   ├── phase-space.embedding  #   Current delay embedding coordinates
│   └── landmark-distances.json#   Hausdorff distances to peer rooms
├── splines/                   # Distilled insights (survive agent restarts)
│   └── *.spline               #   One file per spline (TOML format)
├── reflexes.db                # SQLite vector store for learned reflexes
├── journal/                   # Agent's narrative and decision records
│   ├── room-journal.md        #   Running narrative from the room keeper
│   └── decisions.log          #   Structured decision log (TSV)
├── portal/                    # I2I portal runtime state
│   ├── peers.toml             #   Known peer rooms & capabilities
│   ├── messages/              #   Staged outgoing/incoming I2I bottles
│   │   ├── outgoing/          #     Bottles awaiting dispatch
│   │   └── incoming/          #     Bottles received & pending processing
│   ├── symmetry-queue/        #   Symmetry match candidates (from portal scans)
│   └── vessel-link.toml       #   Link to the fleet I2I vessel
└── log/
    ├── heartbeat.log          #   Periodic health & connectivity log
    └── errors.log             #   Structured error records (JSON-lines)
```

### 1.1 Mandatory Files

Every room—upon creation—must contain at least:

| File | Purpose | Created By |
|------|---------|-----------|
| `identity.toml` | Room birth certificate | `create-room` script |
| `state.toml` | Current ternary position | Room keeper on first map build |
| `maps/technical.map` | Technical ternary signal | `build-maps` script |
| `maps/fundamental.map` | Fundamental ternary signal | `build-maps` script |
| `maps/sentiment.map` | Sentiment ternary signal | `build-maps` script |
| `topology/persistence.json` | Initial persistence diagram | `observatory` script (first run) |
| `portal/peers.toml` | Empty peer table | `join-fleet` script |

### 1.2 Optional Files

| File | Purpose | Created When |
|------|---------|-------------|
| `maps/options.map` | Options flow encoding | Options data available |
| `maps/macro.map` | Macro overlay (rates, CPI, etc.) | Macro context relevant |
| `topology/phase-space.embedding` | Delay-embedded coordinates | Phase space analysis active |
| `topology/landmark-distances.json` | Cross-room Hausdorff distances | Fleet coordination active |
| `portal/symmetry-queue/*` | Pending symmetry comparisons | Portal scan finds matches |

---

## 2. File Formats

### 2.1 Identity TOML (`identity.toml`)

The room's birth certificate. Created once, mutated rarely.

```toml
# ==============================================================================
# Room Identity - Market Manifold Stock Room
# ==============================================================================
[room]
ticker = "NVDA"
exchange = "NASDAQ"                     # Primary exchange
sector = "Technology"                   # GICS sector
industry = "Semiconductors"             # GICS industry
created_at = "2026-06-01T14:30:00Z"     # Room creation timestamp
modified_at = "2026-06-07T05:00:00Z"    # Last metadata change
version = 2                             # Identity schema version
active = true                           # false = archived/halted room

[room.classification]
market_cap = "MEGA"                     # MICRO | SMALL | MID | LARGE | MEGA
volatility_bucket = 3                   # 1 (low vol) → 5 (high vol)
liquidity_tier = "HIGH"                 # LOW | MEDIUM | HIGH
regime_sensitivity = 0.72               # [0,1] — how regime-reactive the ticker is

[room.provenance]
created_by = "fleet-worker-nebula-01"   # Agent who birthed this room
active_keeper = "agent:room:main:nvda"  # Current room keeper agent ref
keeper_pid = 0                          # 0 = no active keeper, >0 = PID of keeper process
last_keep_alive = "2026-06-07T05:22:00Z" # Last heartbeat from the keeper

[room.maps]
active_layers = ["technical", "fundamental", "sentiment", "options"]
composite_weights = { technical = 0.35, fundamental = 0.25, sentiment = 0.25, options = 0.15 }
composite_decay = 0.90                  # EMA decay factor for composite updates
last_composite = "2026-06-07T05:20:00Z"

[room.topology]
observatory_horizon = "90d"             # Lookback window for homology
embedding_dimension = 5                 # Takens embedding dimension
embedding_delay = 3                     # Takens embedding delay (bars)
last_homology_run = "2026-06-07T05:00:00Z"
persistence_history_limit = 1000        # Max snapshots to retain

[room.portal]
connected = true                        # Is this room connected to the fleet?
vessel_path = "/tmp/i2i-vessel/"        # Path to the fleet I2I vessel
peer_sync_interval_min = 360            # How often to re-scan for peers (minutes)
symmetry_scan_enabled = true            # Participate in symmetry detection?
last_peer_scan = "2026-06-07T04:00:00Z"
```

### 2.2 State TOML (`state.toml`)

Mutated frequently — represents the room's current ternary position.

```toml
# ==============================================================================
# Room Ternary State
# ==============================================================================
[state]
timestamp = "2026-06-07T05:20:00Z"
ticker = "NVDA"

# Composite ternary position (fused from all layers)
[state.composite]
position = 1                            # -1 | 0 | +1
confidence = 0.78                       # [0, 1] — aggregated confidence
momentum = "+"                          # Direction of change: + | 0 | -
since = "2026-06-06T14:00:00Z"          # How long in this position

# Per-layer positions
[state.layers.technical]
position = 1
confidence = 0.82
driver = "RSI_divergence_50min"

[state.layers.fundamental]
position = 0
confidence = 0.55
driver = "PE_ratio_in_neutral_zone"

[state.layers.sentiment]
position = 1
confidence = 0.73
driver = "options_call_volume_2sigma"

[state.layers.options]
position = 1
confidence = 0.80
driver = "put_call_ratio_bullish"

# Topological signature
[state.topology]
betti = [3, 1, 0]                       # [β₀, β₁, β₂]
regime_label = "rotation_stability"     # Derived from homology interpretation
topology_confidence = 0.68              # How stable the topological signature is
homology_change_since_last = "STABLE"   # STABLE | SHIFT | FRAGMENTATION | MERGE

# Health
[state.health]
map_freshness_ok = true                 # All maps updated within expected interval
topology_freshness_ok = true            # Homology run within expected interval
portal_connected = true                 # I2I vessel reachable
reflexes_active = 12                     # Number of loaded reflexes
last_error = null
```

### 2.3 Map File Format (`.map`)

Binary format for efficient storage and fast vector operations.

```
┌──────────────────────────────────────────────────────┐
│  TritVec v1 — Binary Ternary Vector                  │
├──────────────────────────────────────────────────────┤
│  Magic bytes : "TV01" (4 bytes)                      │
│  Timestamp   : u64 unix millis (8 bytes)             │
│  Trit count  : u32 little-endian (4 bytes)           │
│  Packed trits: bit-packed (2 bits per trit)          │
│  Checksum    : CRC32 of packed trits (4 bytes)       │
└──────────────────────────────────────────────────────┘
```

Trit encoding (2-bit):
| Bits | Value |
|------|-------|
| `00` | −1    |
| `01` | 0     |
| `10` | +1    |
| `11` | (reserved / null) |

All map files produced by `build-maps` have the same trit count for the same room (the count is the room's **ternary resolution**). This enables element-wise operations between maps.

A companion **Map Manifest** (`maps/README.map`) documents each field:

```yaml
# maps/README.map — Map field definitions
format_version: 1
trit_count: 144
tick_interval: "1h"
layers:
  - name: "RSI_14"
    index: [0, 1]         # Two trits: short-term, medium-term
    source: "ta-lib RSI(14)"
    encoding: "overbought(>70)=-1, oversold(<30)=+1, else=0"
  - name: "MACD_histogram"
    index: [2]
    source: "MACD(12,26,9) histogram"
    encoding: "positive=+1, zero=0, negative=-1"
  - name: "BB_width"
    index: [3, 4]
    source: "Bollinger Band(20,2) % width"
    encoding: "expansion(>1.5)=+1, contraction(<0.5)=-1, else=0"
```

### 2.4 Persistence Snapshot (`.persistence.json`)

Topological observatory output — a persistence diagram in JSON.

```json
{
  "meta": {
    "room": "NVDA",
    "timestamp": "2026-06-07T05:00:00Z",
    "horizon": "90d",
    "embedding": [5, 3],
    "algorithm": "ripser_2.0",
    "max_dimension": 2,
    "max_radius": 0.85
  },
  "diagrams": {
    "H0": [
      {"birth": 0.0, "death": 0.12},
      {"birth": 0.0, "death": 0.08},
      {"birth": 0.0, "death": 0.45}
    ],
    "H1": [
      {"birth": 0.22, "death": 0.34}
    ],
    "H2": []
  },
  "betti_numbers": [3, 1, 0],
  "persistent_entropy": 1.87,
  "landscape": {
    "knots": [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5],
    "lambda_1": [1.20, 1.15, 0.95, 0.72, 0.48, 0.31, 0.18, 0.09, 0.03, 0.01, 0.0],
    "lambda_2": [0.45, 0.42, 0.35, 0.22, 0.10, 0.04, 0.01, 0.0, 0.0, 0.0, 0.0]
  }
}
```

### 2.5 Spline Format (`.spline`)

Distilled insight — compact, portable, self-describing.

```toml
# ==============================================================================
# Distilled Insight Spline
# ==============================================================================
[spline]
id = "nvda-earnings-q2-2026"            # Unique spline ID
type = "EARNINGS_DRIFT"                 # One of: EARNINGS_DRIFT | REGIME_SHIFT |
                                        #          SECTOR_ROTATION | VOL_BREAKOUT |
                                        #          TOPOLOGY_COLLAPSE | CORRELATION_FLIP
created_at = "2026-06-07T02:00:00Z"
origin_room = "NVDA"
version = 1
confidence = 0.85                        # How reliable the pattern appears

[summary]
headline = "NVDA earnings: topology-shattering event"
pre_event_betti = [1, 0, 0]             # Single component, no cycles
post_event_betti = [4, 2, 0]            # Fragmented + rotational
hausdorff_distance = 4.2                # Topological displacement
observation_count = 4                   # Seen across how many data windows

[rule]
if_condition = "H0 < 2 pre-earnings"
then_expect = "H0 >= 3 new components post-earnings"
confidence = 0.82
applies_to_sectors = ["Technology", "Semiconductors"]
applicability = 0.73                    # Cross-sector transferability score

[tags]
tags = ["earnings", "topology-shift", "shattering", "nvda-pattern"]
```

### 2.6 Landmark Distances (`landmark-distances.json`)

Cross-room topological proximity — used for portal discovery and symmetry detection.

```json
{
  "room": "NVDA",
  "timestamp": "2026-06-07T04:00:00Z",
  "peers_known": 24,
  "distances": {
    "AMAT": { "hausdorff": 1.12, "betti_earth_mover": 0.87, "wasserstein": 0.93, "last_synced": "2026-06-07T04:00:00Z" },
    "TSM":  { "hausdorff": 0.34, "betti_earth_mover": 0.22, "wasserstein": 0.28, "last_synced": "2026-06-07T04:00:00Z" },
    "AMD":  { "hausdorff": 1.78, "betti_earth_mover": 1.45, "wasserstein": 1.51, "last_synced": "2026-06-07T03:30:00Z" },
    "INTC": { "hausdorff": 3.12, "betti_earth_mover": 2.89, "wasserstein": 2.95, "last_synced": "2026-06-07T03:00:00Z" },
    "AAPL": { "hausdorff": 5.41, "betti_earth_mover": 4.30, "wasserstein": 4.78, "last_synced": "2026-06-07T04:00:00Z" }
  }
}
```

### 2.7 Betti Curve Time Series (`betti-curve.json`)

```json
{
  "room": "NVDA",
  "horizon": "90d",
  "resolution": "6h",
  "points": [
    {"timestamp": "2026-06-01T00:00:00Z", "betti": [1, 0, 0], "entropy": 0.45},
    {"timestamp": "2026-06-01T06:00:00Z", "betti": [2, 0, 0], "entropy": 0.62},
    {"timestamp": "2026-06-01T12:00:00Z", "betti": [2, 1, 0], "entropy": 0.83},
    {"timestamp": "2026-06-01T18:00:00Z", "betti": [3, 1, 0], "entropy": 1.12}
  ]
}
```

### 2.8 Decision Log (`journal/decisions.log`)

TSV format — one decision per row.

```
timestamp           ticker  action       status   confidence   driver                    reflex_id
2026-06-07T05:00Z   NVDA    COMPOSITE_1  EXECUTED 0.78         technical+options bullish   auto-composite-fusion
2026-06-07T04:30Z   NVDA    REFLEX_ALERT  SENT    0.82         earnings-drift-topology    nvda-earnings-drift-v1
2026-06-07T03:00Z   NVDA    PORTAL_SCAN   DONE    1.00         scheduled scan             portal-heartbeat
```

---

## 3. Room Lifecycle

```
BOOT ──► SEED ──► ACTIVE ──► ARCHIVED
          │                      ▲
          ▼                      │
        OFFLINE ◄────────────────┘
```

| Phase | Description | State |
|-------|-------------|-------|
| **BOOT** | Room directory created, `identity.toml` written, maps empty | Drift |
| **SEED** | First `build-maps` run, topology baseline established, portal handshake | Transient |
| **ACTIVE** | Normal operation — maps updating, topology running, portal connected, reflexes loaded | Steady |
| **OFFLINE** | Keeper agent disconnected, but room data preserved. Portal flags as stale | Degraded |
| **ARCHIVED** | Ticker delisted/halted, room data frozen. Can be resurrected | Frozen |

Transition triggers:
- **BOOT → SEED**: `build-maps --room <TICKER>` completes
- **SEED → ACTIVE**: `join-fleet --rooms <TICKERS>` succeeds + first `observatory` run completes
- **ACTIVE → OFFLINE**: Heartbeat timeout (configurable, default 3600s), error cascade, or explicit `roomctl offline`
- **OFFLINE → ACTIVE**: Reconnect via `roomctl revive` or keeper agent re-registration
- **ACTIVE/BOOT → ARCHIVED**: `roomctl archive` (manual or auto-triggered on delisting)

---

## 4. Naming Conventions & Constraints

### 4.1 Rooms Directory

- Path: `rooms/<TICKER>/` where `<TICKER>` is uppercase ASCII ticker (e.g., `AAPL`, `BRK.B` treated as `BRK_B`)
- Dot-containing tickers → underscore: `BRK.B` → `rooms/BRK_B/`
- Indexes/special instruments: `SPY` (US equities), `BTC-USD` (crypto → `rooms/BTC_USD/`)
- Max ticker length: 20 characters

### 4.2 File Extensions

| Extension | Format | Tooling |
|-----------|--------|---------|
| `.toml` | TOML | Standard configuration |
| `.map` | Binary trit vector | Custom `ternary-types` reader |
| `.json` | JSON | Standard JSON |
| `.spline` | TOML | Custom spline loader |
| `.db` | SQLite | Standard SQLite |
| `.md` | Markdown | Human-readable documentation |
| `.log` | Plain text | Human-readable logging |
| `.embedding` | JSON | Coordinates array |
| `.tsv` | Tab-separated | Machine-parsable structured data |

### 4.3 File Size Limits

| File | Max Size | Rationale |
|------|----------|-----------|
| `identity.toml` | 64 KB | Metadata only |
| `state.toml` | 32 KB | Frequently rewritten |
| Each `.map` file | 4 MB | ~16M trits at 2 bits each |
| Each `.persistence.json` | 1 MB | Homology data |
| `betti-curve.json` | 10 MB | Time series accumulation |
| Each `.spline` | 16 KB | Compact insight |
| `decisions.log` | 100 MB | Rotating, gzip on rotate |

### 4.4 Locking Semantics

- `state.toml` uses advisory file locking (`flock`) — only the active keeper writes
- `reflexes.db` uses SQLite WAL mode — concurrent readers OK, single writer
- Map files are append-only snapshots — never mutated in place
- Persistence snapshots are write-once — integrity verified on write

---

## 5. Room Creation Script Contract

The `create-room --ticker <T> --sector <S>` script must:

1. Create `rooms/<T>/` directory
2. Write `identity.toml` with provided metadata + current timestamp
3. Create empty stub files: `state.toml`, `topology/persistence.json`, each `maps/*.map` (zero-length or sentinel)
4. Create `portal/peers.toml` with empty `[[peers]]` table
5. Create `journal/room-journal.md` with bootstrap entry
6. Create `log/` with empty `heartbeat.log` and `errors.log`
7. Register the room with the fleet vessel (`baton-create registration bottle`)
8. Exit with code 0 on success, non-zero on failure (do not leave partial rooms)

---

## 6. Error States & Recovery

| Symptom | Likely Cause | Recovery |
|---------|-------------|----------|
| `state.toml` stale timestamp | Keeper crashed | Next keeper writes fresh state; logs warning |
| Map file CRC mismatch | Corruption during write | Re-build from raw data; log error |
| `reflexes.db` locked > 30s | Stale lock | Kill stale process, `reflexes.db-wal` recovery |
| `portal/vessel-link.toml` missing | Fleet vessel offline | Backoff retry: 30s, 60s, 120s, 300s; then flag offline |
| `identity.toml` missing | Room corrupted | Re-create from fleet backup at `vessel/rooms-backup/<TICKER>/` |

---

## 7. Schema Versioning

`identity.toml` contains `room.version`. When the schema evolves:

1. Bump `identity.toml` version
2. Write a migration script in `reference/migrations/V<new_version>__<description>.md`
3. The room keeper checks version on boot and runs pending migrations
4. Backward compatibility is maintained for ±1 version (V2 can write into a V3 room)

---

*"A tidy room is a navigable manifold."* — Fleet Proverb
