# ⚓ Fleet Coordination Protocol

**How Market Manifold rooms communicate, share intelligence, and self-organize.**

---

## Architecture

Market Manifold uses the **I2I Baton Protocol** (defined in `baton-system/PROTOCOL.md`) for all inter-room communication. The vessel at `/tmp/i2i-vessel/` serves as the message bus.

### Topology

```
                   ┌──────────────────┐
                   │   fleet/hub      │
                   │  (Orchestrator)  │
                   └────────┬─────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ AAPL Room  │  │ MSFT Room  │  │ GOOGL Room │
    │ (Officer)  │  │ (Officer)  │  │ (Officer)  │
    └────────────┘  └────────────┘  └────────────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                    ┌───────┴───────┐
                    │ Sector/Technology │
                    │ (Virtual Group)  │
                    └───────────────┘
```

### Node Roles

| Node | Role | Responsibility |
|------|------|---------------|
| **fleet/hub** | Orchestrator | Assigns rooms, distributes alerts, manages promotions |
| **Room (Ticker)** | Analysis | Maintains ternary maps, runs topology, distills splines |
| **Sector/*** | Virtual Group | Cross-room topological visualization (computed but not owned) |
| **fleet/memory** | Spline Vault | Long-term storage of splines across all rooms |
| **fleet/reflex-registry** | Reflex DB | Shared reflex promotion and confidence tracking |

---

## Baton Types

### Room Lifecycle

| Baton | Trigger | Content | Recipients |
|-------|---------|---------|------------|
| `ROOM_JOIN` | Room created | Room identity, sector, initial signature | fleet/hub |
| `ROOM_LEAVE` | Room deactivated | Reason, final spline dump | fleet/hub |
| `ROOM_UPDATE` | Every tick / on change | Current Betti numbers, ternary position, confidence | fleet/hub |
| `ROOM_HEARTBEAT` | Every N sessions | Aliveness check, disk/RAM, reflex count | fleet/hub |

### Analysis Exchange

| Baton | Trigger | Content | Recipients |
|-------|---------|---------|------------|
| `SIGNATURE` | After topological analysis | Full persistence diagram, Wasserstein drift | fleet/hub, sector/* |
| `SPLINE_SHARE` | New spline distilled | Spline content, confidence, testing results | fleet/hub, sector/* |
| `SPLINE_RESPONSE` | After evaluating a spline | Match score, applicability, suggested adjustment | Sender room |
| `SECTOR_SYNC` | Every 6h or on change | Cross-room topological comparison | All sector rooms |

### Alerts

| Baton | Trigger | Content | Priority |
|-------|---------|---------|----------|
| `ALERT` | Topological anomaly | H₂ > 0, Wasserstein drift > 0.6, H₀ collapse | High |
| `REGIME_SHIFT` | topological momentum > 0.15 | Old Betti → new Betti, transition analysis | Critical |
| `VOID_DETECTED` | H₂ > 0 identified | Void location in state space, suggested action | Medium |
| `CYCLE_FORMATION` | H₁ appears where previously 0 | Cycle radius, persistence, mean reversion potential | Low |

### Reflex Management

| Baton | Trigger | Content | Recipients |
|-------|---------|---------|------------|
| `REFLEX_PROMOTE` | Room confidence > 0.85 | Reflex pattern, test results, applicability conditions | fleet/hub |
| `REFLEX_LOCK` | Fleet vote > 0.80 | Pattern accepted as fleet-wide reflex | All rooms |
| `REFLEX_REJECT` | Fleet vote < 0.50 | Pattern rejected, feedback | Sender room |

---

## Baton Format

Every baton follows the I2I specification:

```json
{
  "id": "baton-1749283200-a",
  "type": "SPLINE_SHARE",
  "from": "rooms/AAPL",
  "to": ["rooms/MSFT", "rooms/GOOGL", "sector/technology"],
  "timestamp": "2026-06-07T05:00:00Z",
  "body": {
    "spline": {
      "name": "earnings-compression-pattern",
      "precondition": "H₀=2, H₁=1, topological_energy=0.87",
      "observation": "3 sessions pre-earnings: H₀ compresses to 1, energy crosses 1.0",
      "expected_outcome": "Post-earnings: +2.3% in 5 sessions (n=7, TP=86%)",
      "action": "+1 with confidence 0.78"
    },
    "testing": {
      "self_test_result": { "tpr": 0.86, "fpr": 0.14, "n": 7 },
      "cross_test_count": 0,
      "promoted": false
    }
  },
  "ttl": 86400,
  "routing": {
    "priority": "normal",
    "require_ack": false
  }
}
```

---

## Sector Sync Protocol

Every 6 hours (or when triggered by a room reporting significant topological change), `fleet/hub` initiates a sector sync.

### Phase 1: Collection

1. Hub sends `SECTOR_SYNC_REQUEST` to all rooms in a sector
2. Each room responds with its current topological signature within 60 seconds
3. Hub waits for responses or times out unresponsive rooms

### Phase 2: Computation

Hub computes the **joint sector topology**:

```rust
fn sector_sync(signatures: &[TopologicalSignature]) -> SectorTopology {
    let joint_diagram = merge_persistence_diagrams(
        signatures.iter().map(|s| &s.diagram).collect()
    );
    
    SectorTopology {
        sector_id: infer_sector(signatures),
        component_count: joint_diagram.h0_count,
        cycle_count: joint_diagram.h1_count,
        void_count: joint_diagram.h2_count,
        topological_energy: joint_diagram.total_energy(),
        cross_betti: compute_cross_betti(signatures),
        diversity_score: compute_topological_diversity(signatures),
    }
}
```

### Phase 3: Distribution

1. Hub sends `SECTOR_SYNC_RESULT` to all rooms
2. Each room compares its individual topology to the sector topology
3. If a room's topology diverges significantly (Wasserstein distance > 0.4 from sector mean), it sends a `SPLINE_SHARE` explaining why

### Phase 4: Reflex Update

1. Hub promotes any reflex that achieved > 80% confidence across > 3 rooms
2. Rooms test promoted reflexes against their own data
3. Rooms vote: lock, hold, or reject

---

## Spline Lifecycle

### Creation

1. Room observes a pattern ≥ 3 times with confidence > 0.6
2. Room formalizes pattern as a spline in `rooms/{TICKER}/splines/`
3. Room tests spline against historical data: TP rate, FP rate, sample size
4. Room shares spline via `SPLINE_SHARE` baton

### Cross-Room Testing

1. Receiving rooms test the spline against their own historical data
2. Each room responds with a `SPLINE_RESPONSE`:
   ```json
   {
     "spline": "earnings-compression-pattern",
     "test_result": { "match_score": 0.67, "n": 5, "tpr": 0.80, "fpr": 0.20 },
     "applicable": true,
     "suggested_adjustment": {
       "parameter": "topological_energy_threshold",
       "from": 1.0,
       "to": 0.85
     }
   }
   ```

### Fleet-Wide Adoption

1. If > 50% of tested rooms report match_score > 0.6:
   - Spline is promoted to fleet-wide reflex
   - Confidence is calculated as weighted average of all room test results
   - Reflex is locked into the fleet reflex registry
2. If < 30% report match_score > 0.6:
   - Spline is marked domain-specific (applies only to that stock/sector)
   - Stored in room's local spline vault only

### Expiration

Splines expire after 30 days unless refreshed. A room can refresh a spline by testing it against the last 30 days of new data and updating the confidence score.

---

## Bottleneck Detection

When a room detects a potential bottleneck in cross-room analysis:

```rust
/// A bottleneck is a topological feature shared across many stocks
/// that constrains the sector's topology.
fn detect_bottleneck(sector: &SectorTopology) -> Option<Bottleneck> {
    // If multiple rooms share the same H₁ cycle
    // That cycle is a bottleneck — it constrains the sector
    
    Let mut cycle_counts: HashMap<usize, u32> = HashMap::new();
    for room in &sector.rooms {
        for cycle in room.signature.h1_pairs {
            *cycle_counts.entry(cycle.birth_epsilon as usize) += 1;
        }
    }
    
    let (cycle, count) = cycle_counts.iter().max_by_key(|(_, c)| *c)?;
    if *count > sector.rooms.len() / 2 {
        Some(Bottleneck {
            shared_cycle: *cycle,
            affected_rooms: *count,
            total_rooms: sector.rooms.len(),
            description: "More than half the sector shares a single H₁ cycle"
        })
    } else {
        None
    }
}
```

Bottleneck discoveries are reported immediately to `fleet/hub` as high-priority `SPLINE_SHARE`.

---

## Error Handling

| Failure Mode | Recovery | Baton Sent |
|-------------|----------|------------|
| Room unresponsive for 3 ticks | Hub marks room as "stale", reassigns if no response for 24h | `ROOM_STALE` to fleet/hub |
| Baton parsing fails | Drop malformed baton, log parse error | None (logged locally) |
| Spline testing times out (> 60s) | Abort test, mark spline as "pending retest" | None (retry at next sync) |
| Veto engine blocks reflex promotion | Log veto reason, notify room manager | `BLOCKER` to fleet/hub |
| Vessel directory full | Trigger GC cycle on vessel | `GC_NEEDED` to fleet/hub |
