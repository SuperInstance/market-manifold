# 🌐 Market Manifold — TUTORIALS

## The Hacker's la-link: From 0 to First Topological Analysis in 20 Minutes

---

### 🎯 Tutorial 1: "I want to set up a single stock room"

**Goal:** Create a room for `$AAPL`, run ternary maps, see the topological fingerprint.

**Time:** 10 minutes

```bash
# 1. Create the room
./bin/create-room --ticker AAPL --sector Technology

# 2. Inspect the room structure
tree rooms/AAPL/
# rooms/AAPL/
# ├── identity.toml
# ├── maps/
# │   ├── technical.map
# │   ├── fundamental.map
# │   └── sentiment.map
# ├── topology/
# └── log/
#     └── room-journal.md

# 3. Build ternary maps
./bin/build-maps --room AAPL --source yahoo --days 90

# 4. Run the topological observatory
./bin/observatory --room AAPL --dimensions 0:2

# Expected output:
# ════════════════════════════════════════════
#  Room: AAPL | Sector: Technology
#  ════════════════════════════════════════════
#  H₀: 3 connected components (3 regimes found)
#  H₁: 1 persistent cycle (sector rotation present)
#  H₂: 0 persistent voids
#  Topological signature: [H₀=3, H₁=1, H₂=0]
#  Regime: Boundary — sector rotation zone
#  ════════════════════════════════════════════

# 5. View the persistence diagram
./bin/observatory --room AAPL --visualize
# Opens: rooms/AAPL/topology/persistence.html
```

---

### 🎯 Tutorial 2: "I want to compare two stocks topologically"

**Goal:** Compare `$AAPL` and `$MSFT` using Wasserstein distance.

**Time:** 10 minutes

```bash
# 1. Set up both rooms (if not already)
./bin/create-room --ticker MSFT --sector Technology
./bin/build-maps --room MSFT --days 90

# 2. Compute topological distance
./bin/compare --rooms AAPL,MSFT --metric wasserstein

# Expected output:
# ════════════════════════════════════════════
#  Comparing: AAPL ↔ MSFT
#  Wasserstein distance: 0.34 (0.0 = identical)
#  Shared topology: 2/3 Betti numbers match
#   → These stocks share sector topology
#  ════════════════════════════════════════════

# 3. Check symmetry
./bin/compare --rooms AAPL,MSFT --symmetry

# If they're topologically symmetric, swapping them
# should yield the same analytical results
```

---

### 🎯 Tutorial 3: "I want to train a room reflex"

**Goal:** Teach pincher a reflex specifically for your room's common patterns.

**Time:** 5 minutes

```bash
# 1. Teach a reflex for the room
pincher teach \
  --room AAPL \
  --intent "detect pre-earnings topological contraction" \
  --action "observatory --room AAPL --focus homology --compared-to baseline"

# 2. Now when you query, it fires in 50ms
pincher do --room AAPL "is the topology contracting before earnings"

# 3. Check the reflex
pincher reflexes --room AAPL
```

---

### 🎯 Tutorial 4: "I want to share a spline across the fleet"

**Goal:** Distill an insight from `$AAPL` analysis and share it with other rooms.

**Time:** 10 minutes

```python
from market_manifold import Spline, SplineVault

# Create a spline from recent analysis
spline = Spline(
    room="AAPL",
    title="Q2-2026 Earnings Topology Shift",
    content="""
    Pre-earnings: H₀=1, H₁=0 → single-regime compression
    Post-earnings: H₀=4, H₁=2 → fragmented + rotational
    Gap: 4.2 Hausdorff distance
    → Rule: When H₀ < 2 pre-earnings, expect ≥ 3 new components post-earnings
    """
)

# Store it in the spline vault
vault = SplineVault()
vault.store(spline)

# Share via I2I baton
# This sends the spline to all connected rooms
./bin/share-spline --spline_id earnings-topology-shift
```

---

### 🎯 Tutorial 5: "I want to see the fleet coordination in action"

**Goal:** Watch rooms communicate via I2I batons.

**Time:** 5 minutes

```bash
# 1. Start the fleet dashboard
./bin/fleet-dashboard

# 2. In another terminal, trigger a sector sync
./bin/broadcast --type SECTOR_SYNC --rooms AAPL,MSFT,GOOGL

# 3. Watch the batons flow in the dashboard:
# ┌─────────────────────────────────────────────┐
# │ 📡 I2I Vessel                               │
# ├─────────────────────────────────────────────┤
# │ AAPL→MSFT sector-sync  ✓  2026-06-07 19:00 │
# │ AAPL→GOOGL sector-sync ✓  2026-06-07 19:00 │
# │ MSFT→AAPL alert        ✓  2026-06-07 19:01 │
# │ GOOGL→FLEET spline     ✓  2026-06-07 19:02 │
# └─────────────────────────────────────────────┘
```

---

### 🎯 Tutorial 6: "I want to create a custom ternary map"

**Goal:** Define a new signal → ternary encoding.

**Time:** 10 minutes

```python
from market_manifold import TernaryMap, Trit

# Define a custom map for options flow
class OptionsFlowMap(TernaryMap):
    def encode(self, data):
        put_call_ratio = data.put_volume / data.call_volume
        if put_call_ratio > 1.5:
            return Trit.NEG  # Bearish flow
        elif put_call_ratio < 0.5:
            return Trit.POS  # Bullish flow
        else:
            return Trit.ZERO  # Neutral

# Register it with your room
./bin/register-map --room AAPL --name options-flow \
  --module my_maps/options_flow.py

# Now it runs on every tick
./bin/build-maps --room AAPL --include options-flow
```

---

## 🔬 Quick Reference

| Tutorial | Skill | Commands/Scripts | Time |
|----------|-------|------------------|------|
| 1 | First room | `create-room`, `build-maps`, `observatory` | 10 min |
| 2 | Stock comparison | `compare --metric wasserstein` | 10 min |
| 3 | Room reflexes | `pincher teach --room` | 5 min |
| 4 | Spline sharing | `share-spline`, Python API | 10 min |
| 5 | Fleet dashboard | `fleet-dashboard`, `broadcast` | 5 min |
| 6 | Custom maps | Python `TernaryMap` subclass | 10 min |

---

## 🏆 From Here

- ➡️ [ONBOARDING.md](./TEMPLATES/ONBOARDING.md) — Day 1 → Day 5 plan
- ➡️ [README.md](./README.md) — Full docs & philosophy
- ➡️ [docs/TOPOLOGY-OF-VALUE.md](./docs/TOPOLOGY-OF-VALUE.md) — Deep theory
- ➡️ [docs/FLEET-COORDINATION.md](./docs/FLEET-COORDINATION.md) — Communication protocol
- ➡️ [onboarding/STOCK-ROOM-MANAGER.md](./onboarding/STOCK-ROOM-MANAGER.md) — Agent guide
