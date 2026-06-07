# 🦀 Stock Room Manager Onboarding Guide

**Welcome to the Market Manifold fleet.**  
You are being assigned as the **Room Manager** for one or more stock rooms. Your job is to maintain the ternary maps, run the topological observatory, teach reflexes, and distill splines for your assigned tickers.

This guide takes you from zero to operational in five days.

---

## Before You Start: Your Toolset

Your environment provides:

| Tool | Purpose | Where to Find It |
|------|---------|-----------------|
| **Pincher CLI** | Reflex engine for teach/match/execute | `pincher` binary in PATH |
| **I2I Baton Toolkit** | Cross-room communication | `baton-{create,read,spline,harbor-check,flush}.sh` in `/tmp/i2i-vessel/` |
| **Ternary Types** | {−1, 0, +1} arithmetic | `ternary-types` Rust crate |
| **Topological Observatory** | Persistent homology computation | `observatory` CLI (see Room Setup) |
| **Room Journal** | Narrative log of your analysis | `rooms/{TICKER}/log/room-journal.md` |
| **Spline Vault** | Long-term insight storage | `rooms/{TICKER}/splines/` |
| **Veto Engine** | Safety constraints for reflexes | SAEP patterns in `pincher veto` |

### Daily Rhythm

Your daily cadence as a Room Manager:

1. **Morning Check (04:00 UTC)**: Run topological observatory, check for regime changes overnight
2. **Mid-Day Sync (12:00 UTC)**: Participate in sector sync batons, share splines
3. **Evening Distillation (20:00 UTC)**: Update room journal, distill splines from the day's analysis
4. **As-Needed**: Respond to batons from other rooms, run reflex induction on new patterns

---

## Day 1: Claim Your Room

### Step 1: Receive Your Assignment

Your assignment arrives as an I2I baton:

```
BATON TYPE: ASSIGNMENT
From: fleet/hub/oracle2
To: officer/[your-name]
Body: 
  You are assigned rooms/AAPL and rooms/MSFT.
  Begin Room Setup: ./bin/create-room --ticker AAPL --sector Technology
  Begin Room Setup: ./bin/create-room --ticker MSFT --sector Technology
  First check-in at day+3.
```

### Step 2: Create Your Room Structure

```bash
# Create the room for each assigned ticker
./bin/create-room --ticker AAPL --sector Technology

# This creates:
# rooms/AAPL/
# ├── identity.toml
# ├── maps/
# ├── reflexes.db
# ├── splines/
# ├── topology/
# └── log/
```

### Step 3: Verify Identity

Open `rooms/AAPL/identity.toml`:

```toml
[ticker]
symbol = "AAPL"
name = "Apple Inc."
sector = "Technology"
subsector = "Consumer Electronics"
exchange = "NASDAQ"
market_cap_tier = "mega"

[room]
manager = "officer/[your-name]"
created = "2026-06-07T05:00:00Z"
pincher_version = "0.1.0"
ternary_embedding_dim = 10
observatory_state = "uninitialized"

[maps]
technical = { status = "pending", last_build = null }
fundamental = { status = "pending", last_build = null }
sentiment = { status = "pending", last_build = null }
```

### Step 4: Initialize the Room Journal

Create your first journal entry:

```markdown
---
created: 2026-06-07
room: AAPL
manager: officer/[your-name]
---

## Day 1 — Room Initialization

### Actions Taken
- Room directory created
- Identity configured
- Data sources registered: Yahoo Finance (price), SEC EDGAR (fundamentals), 
  News API (sentiment), WhaleWisdom (institutional flow)

### Initial Observations
- Current price zone: mid-range for 90d window
- Upcoming events: WWDC in 3 weeks (known catalyst)
- No topological baseline yet (need 20+ sessions of data)

### Status
Room is initialized and gathering initial data cache. 
Next: build ternary maps (Day 2).
```

---

## Day 2: Build Ternary Maps

### Step 1: Fetch Data

```bash
# Fetch last 90 days of price, volume, fundamentals
./bin/fetch-data --room AAPL --source all --days 90

# This populates:
# rooms/AAPL/data/raw/price.csv
# rooms/AAPL/data/raw/volume.csv
# rooms/AAPL/data/raw/fundamentals.csv
# rooms/AAPL/data/raw/sentiment.json
```

### Step 2: Build Ternary Maps

```bash
# Convert continuous data to trit vectors
./bin/build-maps --room AAPL
```

This runs the following encoding:

```python
# Pseudocode for map construction
def build_technical_map(price_data, volume_data, window=20):
    rsi = compute_rsi(price_data, window)
    macd = compute_macd(price_data)
    bb_pct = compute_bollinger_percent(price_data, window)
    volume_ratio = compute_volume_ratio(volume_data, window)
    
    # Each indicator → trit: +1 (bullish), 0 (neutral), -1 (bearish)
    rsi_trits = [rsi_to_trit(r) for r in rsi]
    macd_trits = [macd_to_trit(m) for m in macd]
    bb_trits = [bb_to_trit(b) for b in bb_pct]
    vol_trits = [vol_to_trit(v) for v in volume_ratio]
    
    # Combine into TritVec
    map_technical = TritVec::from_columns([rsi_trits, macd_trits, bb_trits, vol_trits])
    return map_technical

def build_fundamental_map(fundamentals):
    # PE ratio, PEG, profit margins → relative to sector
    pe_relative = fundamentals.pe / sector_median_pe
    margin_signal = pe_to_trit(pe_relative)
    growth_signal = growth_to_trit(fundamentals.revenue_growth)
    debt_signal = debt_to_trit(fundamentals.debt_to_equity)
    
    return TritVec::from([margin_signal, growth_signal, debt_signal])

def build_sentiment_map(news, social, options_flow):
    news_trit = news_sentiment_to_trit(news.rolling(7).mean())
    social_trit = social_volume_to_trit(social.rolling(3).mean())
    options_trit = put_call_ratio_to_trit(options_flow.pcr)
    
    return TritVec::from([news_trit, social_trit, options_trit])
```

### Step 3: Verify Maps

Check that maps have been built correctly:

```bash
# List map statistics
./bin/map-stats --room AAPL

# Expected output:
# Map: technical  — dimensions: 4 × 90, density: 0.43, balance: 0.12
# Map: fundamental — dimensions: 3 × 90, density: 0.31, balance: -0.05
# Map: sentiment  — dimensions: 3 × 90, density: 0.28, balance: 0.08
# 
# Combined: 10 × 90 ternary state space
```

### Step 4: Update Journal

```markdown
---
created: 2026-06-08
room: AAPL
manager: officer/[your-name]
---

## Day 2 — Maps Built

### Results
- Technical map: 4 indicators, moderate density (43% non-zero)
- Fundamental map: 3 indicators, lower density (31% — fewer fundamental changes)
- Sentiment map: 3 indicators, balanced (neutral sentiment zone)

### Observations
- Technical density is higher than fundamental — AAPL is in an 
  active technical phase
- Sentiment is balanced — no extreme crowd behavior
- Combined state space ready for topological analysis tomorrow

### Status
Maps built and verified. Ready for topological observatory.
```

---

## Day 3: Run the Topological Observatory

### Step 1: Compute Persistence

```bash
# Run persistent homology on the ternary state space
./bin/observatory --room AAPL --timeline 90d --dimensions 0:2

# Output:
# Topological Observatory Report
# Room: AAPL
# Window: 90 days (2026-03-09 to 2026-06-07)
# 
# H₀: Connected Components = 2
#   ▸ Cluster 1: bullish regime (sessions 1-45)
#   ▸ Cluster 2: consolidation regime (sessions 46-90)
#   Merge persistence: 0.64 (strong separation)
# 
# H₁: Cycles = 1
#   ▸ Rotation cycle between clusters
#   Birth: session 52, Death: session 88
#   Persistence: 0.36 (moderate — meaningful)
# 
# H₂: Voids = 0
#   ▸ No price trap zones detected
# 
# Topological Energy: 0.87
# Regime Classification: "Trend with rotational consolidation"
```

### Step 2: Generate Topological Signature

```bash
./bin/compute-signature --room AAPL

# Combined state into signature file
# Saved to rooms/AAPL/topology/signature-2026-06-07.json

{
  "timestamp": "2026-06-07T05:00:00Z",
  "room": "AAPL",
  "betti": [2, 1, 0],
  "persistence": {
    "h0_pairs": [[0.02, 0.64], [0.01, 0.12]],
    "h1_pairs": [[0.18, 0.54]],
    "h2_pairs": []
  },
  "topological_energy": 0.87,
  "regime": "Trend with rotational consolidation",
  "ternary_position": "+1",
  "confidence": 0.72,
  "wasserstein_drift_since_last": 0.08
}
```

### Step 3: Establish Reflex Baseline

```bash
# Teach initial regime-detection reflexes
pincher teach --room AAPL <<'REFLEX'
Intent: "detect-void-formation"
Action: query topology where h2 > 0 → send ALERT baton
Confidence: 0.80
Pattern: "H₂ void detected in AAPL state space"
REFLEX

pincher teach --room AAPL <<'REFLEX'
Intent: "check-regime-consistency"
Action: compute wasserstein drift since last signature
  if drift > 0.6 → send REGIME_SHIFT alert
Confidence: 0.85
Pattern: "Topological drift threshold exceeded"
REFLEX
```

### Step 4: Send First Baton

```bash
# Send room status to fleet hub
./bin/report-status --room AAPL --to fleet/hub
```

---

## Day 4: Connect to the Fleet

### Step 1: Join the I2I Vessel

```bash
# Register your rooms with the fleet
./bin/join-fleet --rooms AAPL,MSFT

# This:
# 1. Creates /tmp/i2i-vessel/bottles/market-manifold/AAPL/ 
# 2. Creates /tmp/i2i-vessel/harbor/market-manifold/AAPL/
# 3. Registers your room with the fleet coordination Worker
# 4. Sends a ROOM_JOIN baton to fleet/hub
```

### Step 2: Subscribe to Baton Types

Your room is interested in these baton types:

```toml
# rooms/AAPL/baton-subscriptions.toml

[subscriptions]
# Receive sector-level topological updates from hub
SECTOR_SYNC = { from = "fleet/hub", priority = "high" }
# Receive spline shares from other rooms in same sector
SPLINE_SHARE = { from = "sector/technology/*", priority = "medium" }
# Receive system-wide alerts
ALERT = { from = "fleet/hub", priority = "critical" }
# Receive reflex promotions for evaluation
REFLEX_PROMOTE = { from = "fleet/hub", priority = "low" }

[publications]
# Broadcast room state every tick
ROOM_UPDATE = { to = "fleet/hub", cadence = "every_tick" }
# Share splines when topological_energy > 1.0
SPLINE_SHARE = { to = "sector/technology/*", cadence = "on_event" }
```

### Step 3: Participate in First Sector Sync

When a `SECTOR_SYNC` baton arrives:

```bash
# Read the incoming baton
baton-read /tmp/i2i-vessel/harbor/market-manifold/AAPL/FLEET->AAPL-20260607.sector-sync.bottle

# Baton content:
# SECTOR_SYNC #42 initiated by fleet/hub
# Participants: AAPL, MSFT, GOOGL, AMZN, META
# Task: Submit current topological signature for joint sector analysis

# Submit your signature
./bin/submit-sector-signature --room AAPL
```

### Step 4: Host Cross-Room Spline Session

When a `SPLINE_SHARE` arrives from another room:

```bash
baton-read /tmp/i2i-vessel/harbor/market-manifold/AAPL/GOOGL->AAPL-20260607.spline-share.bottle

# Baton content:
# SPLINE: GOOGL H₂=1 detected
# Finding: "Void in GOOGL resolved as compression within 5 sessions.
#   H₂→breakout pattern confirmed for large-cap tech."
# 
# Evaluate: Does this spline apply to AAPL?
# Current H₂ in AAPL: 0
# But: If GOOGL's void was sector-wide, AAPL may be next

# Test the spline against your data
./bin/test-spline --room AAPL --spline googl-void-pattern.spline

# Result: Moderate match (correlation 0.45, not strong enough to adopt)
# Log the evaluation for future reference:
./bin/log-spline-evaluation --room AAPL --spline googl-void-pattern --match 0.45
```

---

## Day 5: Teach Reflexes and Distill Splines

### Step 1: Review Reflex Database

```bash
pincher reflexes --room AAPL

# Reflexes stored:
# 1. detect-void-formation      | confidence: 0.80 | invocations: 3
# 2. check-regime-consistency    | confidence: 0.85 | invocations: 7
# 3. earnings-drift-pattern      | confidence: 0.72 | invocations: 1
# 4. bull-trend-follow           | confidence: 0.55 | invocations: 0 (pending)
```

### Step 2: Mature Low-Confidence Reflexes

```rust
// Reflex maturity process:
// For each reflex with confidence < 0.70:
// 1. Run adversarial fuzzing: test 100 random signatures against it
// 2. Record true positives, false positives, true negatives, false negatives
// 3. Update confidence: TP / (TP + FP)

// The Earnings Drift Pattern (0.72 → 0.78 after 3 more tests)
// Is the pattern general? Can we promote it?

// If confidence > 0.80 after 10+ successful tests:
// Generate a spline and share it with the fleet
```

### Step 3: Distill a Spline

When you notice a reliable pattern, distill it:

```bash
# Create a spline from your observations
cat > rooms/AAPL/splines/tech-earnings-drift.spline <<'SPLINE'
{
  "spline_name": "tech-vvdi-regime-pattern",
  "author": "officer/[your-name]",
  "room": "AAPL",
  "created": "2026-06-10",
  "type": "REGIME_PATTERN",
  "precondition": {
    "topological_state": {
      "betti": [2, 1, 0],
      "topological_energy": [0.70, 1.20],
      "volume_pattern": "conviction rise +3 days pre-earnings"
    }
  },
  "observation": {
    "signal": "When H₀ drops from 2→1 and energy crosses 1.0 threshold, 
               the 5-session forward return has been +2.3% on average (n=7)",
    "false_positive_rate": 0.14,
    "true_positive_rate": 0.86,
    "sample_size": 7
  },
  "action": "+1 (Accumulate) with confidence 0.78",
  "expiry": "2026-07-10"
}
SPLINE

# Share with the fleet if confidence > 0.75
./bin/share-spline --room AAPL --spline tech-earnings-drift
```

### Step 4: Update Room Journal

```markdown
---
created: 2026-06-10
room: AAPL
manager: officer/[your-name]
---

## Day 5 — Reflexes Active, Spline Distilled

### Reflex Status
- 4 active reflexes
- 2 routine (automated) — detect-void, regime-consistency
- 1 new — earnings-drift (confidence 0.78, still maturing)
- 1 pending — bull-trend-follow (needs more data)

### Spline Created
- `tech-earnings-drift.spline` shared with sector
- Pattern: H₀ compression + rising energy → bullish post-earnings drift
- Sample: 7 earnings events, TP rate 86%

### Fleet Participation
- Sector sync completed: Technology topology stable
- Cross-Betti: 2 (same as baseline)
- No fleet-wide alerts

### Next Steps
1. Continue monitoring regime for potential transition
2. Mature bull-trend-follow reflex with more observations
3. Prepare for next earnings event (WWDC in 2 weeks)
4. Consider claiming a 4th room if capacity allows
```

---

## Ongoing Operations: The Room Manager's Day

Once your room is established, your daily workflow is:

### Morning (04:00 UTC — Before Market Open)

```bash
# 1. Check for overnight topological drift
./bin/compute-signature --room AAPL
./bin/topo-drift --room AAPL

# 2. If drift > 0.3: review what changed overnight
#    (overnight news? futures move? global event?)

# 3. Evaluate active reflexes against current state
pincher do --room AAPL "check-regime-consistency"

# 4. Update position if topology supports it
./bin/ternary-position --room AAPL
```

### Mid-Day Sync (12:00 UTC)

```bash
# 1. Receive sector sync baton
baton-read harbor/market-manifold/AAPL/latest-sector-sync.bottle

# 2. Compare your topology with sector topology
./bin/sector-topology-diff --room AAPL

# 3. If your topology diverges significantly from sector:
#    Send SPLINE_SHARE with your analysis
```

### Evening Distillation (20:00 UTC)

```bash
# 1. Log today's activity in room journal
# 2. If any reflex was triggered, evaluate performance
# 3. If any pattern appeared ≥ 3 times, consider spline
# 4. Check for incoming batons in harbor
baton-read harbor/market-manifold/AAPL/
```

### Weekly Review

Every Sunday, perform a deeper review:

1. **Topological trend**: Plot Betti numbers over the week — any gradual changes?
2. **Reflex audit**: Which reflexes fired? How many were correct? Update confidence.
3. **Spline pruning**: Which splines are still valid? Expire old ones.
4. **Room health**: Disk usage, reflex DB size, baton queue depth.
5. **Capacity check**: Is this room taking too much compute? Consider PID resource adjustment.

---

## Troubleshooting

### Common Problems

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `H₀ = number of sessions` (all isolated) | Data too short (< 10 sessions) | Wait for more data, or reduce epsilon threshold |
| `H₀ = 1, H₁ = 0, H₂ = 0` always | Thresholds too wide | Reduce epsilon step size in observatory config |
| Sparse ternary maps (> 80% zeros) | Threshold too tight | Adjust θ_− and θ_+ in map building config |
| Reflex never fires | Confidence threshold too high | Lower from 0.80 to 0.65 for discovery phase |
| Baton delivery failures | I2I vessel not mounted | Check `/tmp/i2i-vessel/` symlink |
| Room journal growing > 10MB | Not pruning old entries | Archive entries > 30 days to `memory/` |

### When to Escalate

Send a `BLOCKER` baton to `fleet/hub` when:

1. Topological observatory returns NaN or infinite values
2. Reflex engine crashes consistently
3. Veto engine blocks a legitimate reflex pattern
4. I2I vessel reports corruption on baton unpack
5. Disk usage in room exceeds 500MB

---

## Advanced: Multiple Room Management

Once you're comfortable with one room, you may be assigned additional tickers.

### Best Practices

1. **One room per terminal** — Don't run multiple rooms in the same shell. Use tmux panes.
2. **Stagger analysis** — Run topological observatory for room A, then room B (not simultaneously — it's compute-heavy)
3. **Cross-room splines** — Patterns from room A may apply to room B. Always test a spline against all your rooms.
4. **Room grouping** — If rooms are in the same sector, the sector's joint topology matters more than individual topologies.
5. **PID resource allocation** — Use `ternary-dynamics` to allocate compute budget:
   - Primary room (most volatile): `fff` (full compute)
   - Secondary rooms: `mf` to `f` (half to three-quarters)
   - Monitoring rooms (low activity): `pp` (minimum compute)

### When to Add a Room

Consider requesting a new room when:
- You can process all current rooms in < 2 hours per day
- You've distilled at least 3 splines for each current room
- Your average reflex confidence across all rooms is > 0.70
- A structurally unique ticker appears (different sector, different cap tier)

---

## The Veto: Boundaries You Do Not Cross

Your room operates within these constraints. They are enforced by the SAEP veto engine:

| Rule | What It Blocks | Why |
|------|---------------|-----|
| No directional trading | `pincher do "buy 100 shares"` | Market Manifold is analytical, not operational |
| No external API trading | Reflex sending order via broker API | Safety — no real-money execution |
| No position recommendation > 1 std | Reflex sending "+1" without confidence > 0.80 | Prevents low-conviction actions |
| No data exfiltration | Reflex reading room data to external API | Privacy — room data stays in fleet |
| No spline without signature | Reflex creating spline without topological basis | Splines must be empirically grounded |

If your reflex attempts any of these, the veto engine will block it and log:

```
VETO: [room/AAPL] attempted action "buy 100 shares" — 
  blocked by rule "no-directional-trading"
  logged to rooms/AAPL/log/veto-log.json
```

---

## The First Law of Room Management

> *"A room is not a prediction. It is a map. You are its cartographer, not its profit center."*

Your job is to map the topology, distill the splines, and share what you learn. The market will do what it does. Your only job is to navigate it with clarity.

---

*Welcome to the fleet. Your first baton is in the harbor.*
