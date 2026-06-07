# 🚪 Portal Protocol — Inter-Room Discovery & Communication

> *"The I2I batons are the calcium bridges that connect the shells into a coral reef."*

---

## 1. Overview

The **Portal Protocol** governs how stock rooms discover each other, exchange messages, synchronize topology, and distill collective intelligence. It sits on top of the I2I Baton System (defined in `baton-system/PROTOCOL.md`) and adds room-specific semantics.

### Core Principles

1. **Asymmetric discovery** — Decentralized peer scanning; no central registry beyond the vessel's directory.
2. **Address by ticker** — Rooms are identified by their ticker symbol (uppercase, normalized).
3. **Gossip propagation** — Network effects emerge through peer-to-peer baton relay.
4. **Soft state** — All peer relationships are refresh-based; stale records decay.
5. **Topological proximity** — Rooms that are close in topological space communicate more frequently.

### Portal Architecture

```
                    ┌─────────────────────┐
                    │   I2I Vessel         │
                    │  (/tmp/i2i-vessel/)  │
                    │                      │
                    │  bottles/  harbor/   │
                    │  splines/  registry/ │
                    └──────┬──────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │  Portal    │   │  Portal    │   │  Portal    │
   │ NVDA       │   │ TSM        │   │ AMAT       │
   │ peers.toml │   │ peers.toml │   │ peers.toml │
   └────────────┘   └────────────┘   └────────────┘
          │                │                │
          ▼                ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │ Room NVDA  │   │ Room TSM   │   │ Room AMAT  │
   └────────────┘   └────────────┘   └────────────┘
```

---

## 2. Room Discovery

### 2.1 Vessel Registry

The I2I vessel maintains a lightweight registry at `/tmp/i2i-vessel/registry/rooms/` — each file is a `.room` file containing a room's connection metadata.

```
/tmp/i2i-vessel/registry/rooms/
├── NVDA.room
├── TSM.room
├── AMAT.room
├── AMD.room
├── INTC.room
└── AAPL.room
```

Each `.room` file:

```toml
[room]
ticker = "NVDA"
sector = "Technology"
industry = "Semiconductors"
active = true
last_heartbeat = "2026-06-07T05:20:00Z"
keeper_ref = "agent:room:main:nvda"
keeper_pid = 14231
maps_version = 4
topology_betti = [3, 1, 0]
topology_regime = "rotation_stability"
reflex_count = 12
capabilities = ["maps:technical", "maps:fundamental", "maps:sentiment", "maps:options", "topology:H0+H1+H2", "splines:yes", "portal:symmetry"]
```

### 2.2 Peer Scan

Each room's portal performs a periodic **peer scan** by reading the vessel registry. The scan:

1. Reads all `.room` files from the registry directory
2. Filters out self (own ticker)
3. Filters inactive rooms (`active = false`)
4. Optionally applies **proximity filter** to limit peers to a manageable number
5. Updates `portal/peers.toml`

```bash
# Manual trigger
./bin/portal-scan --room NVDA

# Scan output
# Found 24 active peers. Filtering to 12 most topologically relevant.
# Added TSM (hausdorff=0.34), AMAT (hausdorff=1.12), ...
# Dropped AAPL (hausdorff=5.41) — below relevance threshold
```

### 2.3 Proximity-Based Filtering

When the fleet exceeds ~50 rooms, portals apply **topological proximity** filtering to keep `peers.toml` manageable:

```
MAX_PEERS = 20 (default, configurable per room)
PROXIMITY_THRESHOLD = 3.0 (hausdorff distance; discard rooms above this)
```

The portal maintains **two lists**:

| List | Size | Purpose |
|------|------|---------|
| **Active peers** | ≤ 20 | Rooms receiving regular heartbeat and topology sync messages |
| **Discovery candidates** | ≤ 100 | Rooms beyond threshold but tracked in `portal/peers.toml` as stubs |

### 2.4 Peer Table Format (`portal/peers.toml`)

```toml
# ==============================================================================
# Peer Room Table — NVDA
# ==============================================================================
last_scan = "2026-06-07T04:00:00Z"
total_peers_seen = 24
active_peers = 12

[[peer]]
ticker = "TSM"
sector = "Technology"
status = "ACTIVE"                    # ACTIVE | STALE | UNREACHABLE
proximity = 0.34                     # Hausdorff distance (lower = closer)
relationship = "SYMMETRIC"          # SYMMETRIC | ASYMMETRIC | SECTOR_MATE | DISTANT
last_contact = "2026-06-07T04:00:00Z"
message_count_in = 7
message_count_out = 5
spline_exchange = 2
symmetry_score = 0.91               # [0, 1] — topological shape similarity
symmetry_last_check = "2026-06-07T04:00:00Z"

[[peer]]
ticker = "AMAT"
sector = "Technology"
status = "ACTIVE"
proximity = 1.12
relationship = "SECTOR_MATE"
last_contact = "2026-06-07T03:30:00Z"
message_count_in = 3
message_count_out = 4
spline_exchange = 1
symmetry_score = 0.62
symmetry_last_check = "2026-06-07T02:00:00Z"

[[peer]]
ticker = "AAPL"
sector = "Technology"
status = "STALE"
proximity = 5.41
relationship = "DISTANT"
last_contact = "2026-06-05T12:00:00Z"
message_count_in = 0
message_count_out = 0
spline_exchange = 0
symmetry_score = null
symmetry_last_check = null

[[peer]]
ticker = "AMD"
sector = "Technology"
status = "UNREACHABLE"
proximity = 1.78
relationship = "SECTOR_MATE"
last_contact = "2026-06-06T18:00:00Z"
message_count_in = 2
message_count_out = 2
spline_exchange = 0
symmetry_score = 0.33
symmetry_last_check = "2026-06-06T18:00:00Z"
```

### 2.5 Relationship Taxonomy

| Relationship | Criteria | Communication Priority | Symmetry Scan |
|-------------|----------|----------------------|---------------|
| **SYMMETRIC** | Topological shape similarity ≥ 0.80 | HIGH — every tick | Every cycle |
| **SECTOR_MATE** | Same GICS sector AND proximity ≤ 2.0 | MEDIUM — every 6h | Every 4 cycles |
| **ASYMMETRIC** | One-directional influence (e.g., NVDA→AMD but not reverse) | MEDIUM — directional | Conditional |
| **DISTANT** | Proximity > 3.0 | LOW — every 48h | Rarely |
| **STALE** | No contact in > 24h | LOW — probe every 6h | None |
| **UNREACHABLE** | Vessel link broken | LOW — backoff probe | None |

---

## 3. Cross-Room Messages

### 3.1 Message Transport

All messages flow through the I2I vessel as **bottles**. A bottle is a file placed in the vessel directory with standardized naming and format.

### 3.2 Bottle Naming Convention

```
<SRC>->[<DST>|<FLEET>]-<YYYYMMDDHHMMSS>.<baton-type>.bottle
```

| Component | Pattern | Example |
|-----------|---------|---------|
| `SRC` | Ticker uppercase | `NVDA` |
| `DST` | Target ticker (or `FLEET` for broadcast) | `TSM` or `FLEET` |
| `YYYYMMDDHHMMSS` | UTC timestamp | `20260607050000` |
| `baton-type` | Message type identifier | `spline-share`, `sector-sync`, `topology-request` |

Examples:
- `NVDA->TSM-20260607050000.sector-sync.bottle` — Directed sector sync
- `NVDA->FLEET-20260607051000.room-update.bottle` — Fleet broadcast
- `NVDA->FLEET-20260607052000.symmetry-alert.bottle` — Symmetry alarm
- `TSM->NVDA-20260607050500.topology-request.bottle` — Topology query

### 3.3 Bottle Placement

```
/tmp/i2i-vessel/
├── bottles/                           # Outgoing messages (writer's directory)
│   └── market-manifold/
│       ├── NVDA->TSM-20260607.sector-sync.bottle
│       └── NVDA->FLEET-20260607.room-update.bottle
└── harbor/                            # Incoming messages (reader's directory)
    └── market-manifold/
        └── TSM->NVDA-20260607.topology-request.bottle
```

**Delivery semantics:**
- The **sender** writes to `bottles/<namespace>/`
- The **receiver** picks up from `harbor/<namespace>/`
- A simple **relay agent** (`baton-relay`) moves bottles from `bottles/` to target room's `harbor/` by parsing `DST` from the filename
- For fleet broadcasts (`DST=FLEET`), the relay copies the bottle to every active room's harbor
- Bottles are **removed** after processing by the receiver's portal

### 3.4 Message Types

#### 3.4.1 `room-update` — Periodic State Broadcast

Sent every tick (configurable, default 1 hour) to fleet.

```toml
[bottle]
type = "room-update"
version = 1
src = "NVDA"
dst = "FLEET"
timestamp = "2026-06-07T05:00:00Z"
ttl_minutes = 120

[payload]
betti = [3, 1, 0]
position = 1
confidence = 0.78
regime = "rotation_stability"
maps_active = ["technical", "fundamental", "sentiment", "options"]
map_trit_count = 144
reflex_count = 12
keeper_alive = true

[payload.topology]
persistent_entropy = 1.87
landscape_hash = "a3f2c9d1e8b74a50"      # Hash of persistence landscape for quick comparison
homology_change = "STABLE"
```

#### 3.4.2 `spline-share` — Distilled Insight Distribution

Sent when a new spline is created or an existing spline receives a significant confidence boost.

```toml
[bottle]
type = "spline-share"
version = 1
src = "NVDA"
dst = "FLEET"                            # Typically broadcast
timestamp = "2026-06-07T02:00:00Z"
ttl_minutes = 2880                       # Splines live 48h in the vessel

[payload.spline]
id = "nvda-earnings-q2-2026"
type = "EARNINGS_DRIFT"
confidence = 0.85
headline = "NVDA earnings: topology-shattering event"
rule_if = "H0 < 2 pre-earnings"
rule_then = "H0 >= 3 new components post-earnings"
applicability = 0.73
tags = ["earnings", "topology-shift", "semiconductors"]

[payload.meta]
origin_room = "NVDA"
is_update = false                        # true if this replaces a previous spline version
replaces_spline_id = null
```

#### 3.4.3 `topology-request` / `topology-response` — On-Demand Comparison

A room can request another room's full persistence diagram for detailed comparison.

**Request:**
```toml
[bottle]
type = "topology-request"
version = 1
src = "NVDA"
dst = "TSM"
timestamp = "2026-06-07T05:00:00Z"
ttl_minutes = 30

[payload]
request_id = "req-20260607-nvda-tsm-001"
requested_fingerprint = "betti+landscape"
include_phase_space = false
include_landmark_history = true
```

**Response:**
```toml
[bottle]
type = "topology-response"
version = 1
src = "TSM"
dst = "NVDA"
timestamp = "2026-06-07T05:00:30Z"
ttl_minutes = 30
in_response_to = "req-20260607-nvda-tsm-001"

[payload]
betti = [2, 0, 0]
persistent_entropy = 0.93
regime = "compression"
landscape_hash = "b7f1e3d2c9a85064"

[payload.landmark_history]
# Last 10 landmark-relative distances to NVDA
recent_to_nvda = [0.35, 0.38, 0.31, 0.40, 0.34, 0.36, 0.33, 0.37, 0.32, 0.34]

[payload.persistent_pairs_H1]
# Cyclic features with their birth/death
pairs = [
  [0.18, 0.25],
  [0.15, 0.22],
  [0.20, 0.28]
]
```

#### 3.4.4 `sector-sync` — Sector-Level Topological Alignment

A heavier synchronization message that aligns topological baselines across a sector. Typically initiated by a sector lead room or by the fleet worker on a 6-hour cadence.

```toml
[bottle]
type = "sector-sync"
version = 1
src = "FLEET"                            # Can also be initiated by a lead room
dst = "SECTOR:Technology"
timestamp = "2026-06-07T04:00:00Z"
ttl_minutes = 60

[payload.sector]
sector = "Technology"
member_rooms = ["NVDA", "TSM", "AMAT", "AMD", "INTC", "AAPL", "MSFT", "GOOGL"]
member_betti = {
  "NVDA": [3, 1, 0],
  "TSM":  [2, 0, 0],
  "AMAT": [2, 1, 0],
  "AMD":  [4, 2, 1],
  "INTC": [1, 0, 0],
  "AAPL": [1, 0, 0],
  "MSFT": [2, 1, 0],
  "GOOGL": [1, 0, 0]
}
total_sector_betti = [16, 5, 1]
conservation_check = true                # Is total topological complexity conserved?
entropy_mean = 1.24
entropy_variance = 0.38

[payload.symmetry]
symmetric_pairs = [
  ["NVDA", "TSM", 0.91],
  ["TSM",  "AMAT", 0.72],
  ["MSFT", "GOOGL", 0.85]
]
novel_pairs = [
  ["NVDA", "AMD", 0.44]
]
```

#### 3.4.5 `symmetry-alert` — Topological Symmetry Detected

Emitted when the symmetry detection engine finds a match between two rooms. See [symmetry-detection.md](./symmetry-detection.md) for the full mechanism.

```toml
[bottle]
type = "symmetry-alert"
version = 1
src = "FLEET"
dst = "NVDA,TSM"
timestamp = "2026-06-07T04:15:00Z"
ttl_minutes = 1440

[payload.match]
room_a = "NVDA"
room_b = "TSM"
symmetry_score = 0.91
symmetry_type = "STRONG"                 # STRONG | WEAK | EMERGENT
detection_method = "betti_similarity"    # | landscape_wasserstein | phase_space_alignment

[payload.evidence]
hausdorff_distance = 0.34
betti_earth_mover = 0.22
wasserstein_distance = 0.28
landscape_correlation = 0.94
regime_alignment = "rotation_stability ⟷ compression_precursor"
confidence = 0.87
stable_since = "2026-06-06T12:00:00Z"   # How long this symmetry has been observed

[payload.both_sides]
# What each room sees in the other
nvda_sees_tsm = "precursor symmetry — TSM compressing toward NVDA's rotation regime"
tsm_sees_nvda = "leading symmetry — NVDA's rotation stability predicts TSM's next phase"
```

#### 3.4.6 `reflex-promote` — Candidate Reflex for Fleet Adoption

When a room achieves high confidence in a reflex pattern, it can propose fleet-wide adoption.

```toml
[bottle]
type = "reflex-promote"
version = 1
src = "NVDA"
dst = "FLEET"
timestamp = "2026-06-07T05:15:00Z"
ttl_minutes = 10080                      # 7 days

[payload.reflex]
id = "nvda-pre-earnings-contraction"
intent = "pre-earnings topological contraction"
confidence = 0.94
observation_count = 12                   # Seen across 12 data windows
applicability_score = 0.81               # How well it transfers

[payload.rule]
condition = "topological_entropy < 1.0 AND sentiment_divergence > 0.30"
action = "flag ALERT: probable topology-shattering event"
tags = ["earnings", "topology", "contraction"]

[payload.transfer_test]
# Which rooms have been tested with this reflex
tested_on = ["NVDA", "TSM", "AMAT"]
pass_count = 3
fail_count = 0
```

#### 3.4.7 `portal-alive` — Keepalive Heartbeat

Lightweight connectivity check.

```toml
[bottle]
type = "portal-alive"
version = 1
src = "NVDA"
dst = "FLEET"
timestamp = "2026-06-07T05:20:00Z"
ttl_minutes = 10
```

---

## 4. The I2I Bottle Format (Cross-Room Signals)

### 4.1 Physical Format

All bottles are **TOML files** with the following minimal structure:

```toml
# ==============================================================================
# I2I Baton Bottle — Market Manifold
# ==============================================================================

[bottle]
# MANDATORY FIELDS — every bottle must include these
type = "<baton-type>"                    # See §3.4 for valid types
version = 1                              # Bottle format version
src = "<TICKER|FLEET>"                   # Source room or FLEET
dst = "<TICKER|FLEET|SECTOR:name>"       # Destination
timestamp = "YYYY-MM-DDTHH:MM:SSZ"       # Creation time (ISO 8601)
ttl_minutes = <int>                      # Time-to-live in minutes

# OPTIONAL FIELDS
priority = "NORMAL"                      # LOW | NORMAL | HIGH | CRITICAL
correlation_id = "<uuid>"                # For request/response pairs
in_response_to = "<uuid|request_id>"     # Echo back the request identifier
relay_count = 0                          # How many hops this bottle has taken

[payload]
# Type-specific payload (defined per baton-type)
```

### 4.2 Bottle Lifecycle

```
CREATE (room portal)
  │
  ▼
PLACED (in bottles/<namespace>/)
  │
  ▼
RELAYED (moved to recipient(s)' harbor/ by relay agent)
  │
  ▼
PICKED UP (recipient portal reads the bottle)
  │
  ▼
PROCESSED (action taken based on type)
  │
  ▼
ACKED (optional response bottle sent)     ──────► new CREATE cycle
  │
  ▼
REMOVED (bottle deleted from harbor/)
```

### 4.3 Delivery Guarantees

| Property | Guarantee | Mechanism |
|----------|-----------|-----------|
| **At-least-once delivery** | ✅ Yes — every bottle is read at least once | Sender writes once; receiver removes after processing |
| **Idempotent processing** | ✅ Yes — duplicate bottles produce same result | `correlation_id` dedup (48h dedup window) |
| **Ordering** | ⟳ Best-effort — per-room channels not strictly ordered | Timestamp-based ordering; out-of-order bottles merge chronologically |
| **TTL enforcement** | ✅ Yes — expired bottles are garbage-collected | Relay agent sweeps bottles with TTL exceeded |
| **Broadcast fan-out** | ✅ Yes — `FLEET` destinations are relayed to all active rooms | Relay agent copies to every harbor/<room>/ |
| **Retry on failure** | ✅ Yes — 3 retries with backoff (10s, 30s, 60s) | If harbor write fails, sender retains in outgoing |

### 4.4 Garbage Collection

- Relay agent removes bottles from `bottles/` after successful delivery to all recipients
- Relay agent removes bottles from `harbor/` after TTL expires (even if unprocessed)
- Garbage collection runs every 5 minutes
- Bottles with `ttl_minutes = 0` are ephemeral (removed immediately after first relay)

---

## 5. Portal Handshake Protocol

When two rooms establish a new peer relationship:

```
NVDA                              TSM
  │                                │
  │  1. NVDA reads registry        │
  │     → discovers TSM active     │
  │                                │
  │  2. topology-request ─────────►│
  │                                │
  │  3. ◄────────────────────────── topology-response
  │                                │
  │  4. Compute hausdorff dist     │
  │     → 0.34 (close!)            │
  │                                │
  │  5. spline-share ────────────►│
  │     (NVDA's best splines)      │
  │                                │
  │  6. ◄────────────────────────── spline-share
  │     (TSM's best splines)       │
  │                                │
  │  7. symmetry-scan ───────────►│
  │     (request full alignment)   │
  │                                │
  │  8. ◄──── sync complete ──────│
  │     peer relation: SYMMETRIC   │
  │                                │
```

Total time: ≈ 2-5 seconds for local vessel, up to 30 seconds for distributed vessel.

---

## 6. Portal to Vessel Link (`portal/vessel-link.toml`)

```toml
# ==============================================================================
# Portal → I2I Vessel Link
# ==============================================================================
[vessel]
path = "/tmp/i2i-vessel/"
namespace = "market-manifold"
connected = true
last_connected = "2026-06-07T05:20:00Z"

[vessel.bottles]
outgoing_dir = "bottles"                # Relative to vessel path
incoming_dir = "harbor"                 # Relative to vessel path
splines_dir = "splines"                 # Relative to vessel path
registry_dir = "registry/rooms"         # Relative to vessel path

[vessel.room]
bootstrap = true                        # Register this room on connect?
registration_ttl_minutes = 60           # Re-register every hour
```

---

## 7. Portal Configuration (Room Keeper Controlled)

Each room's keeper can tune portal behavior via `portal/peers.toml`:

```toml
[config]
max_active_peers = 20
max_discovery_candidates = 100
proximity_threshold = 3.0
scan_interval_minutes = 360
disable_symmetry = false
symmetry_scan_interval_minutes = 180
bottle_ttl_default = 120                # Default TTL for outgoing bottles
harbor_poll_interval_seconds = 30       # How often to check for new bottles
auto_relay = true                        # Automatically forward relevant bottles
```

---

## 8. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Bottle spoofing** | Bottles carry `src` which must match the registry entry. Cross-check on fetch. |
| **Harbor flooding** | Per-room intake limit: 1000 bottles max in harbor. Backpressure on senders. |
| **Stale registry** | Rooms re-register every `registration_ttl_minutes`. Stale entries removed after 2× TTL. |
| **Symmetry scanning DoS** | Max 1 symmetry scan per peer per 30 minutes. |
| **Bottle replay** | `correlation_id` dedup prevents duplicate processing. |
| **Unreachable room pollution** | Rooms marked `UNREACHABLE` after 3 failed contact attempts. |

---

*"The vessel is the ocean, the portal is the reef, and the bottles are the plankton that feed the ecosystem."* — Fleet Engineer's Notebook
