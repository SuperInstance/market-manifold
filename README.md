# 🌐 Market Manifold

**Financial analysis as a topological navigation problem.**  
Transform stock markets from a flat list of tickers into a navigable, ternary-valued manifold.

---

## The Essence

Markets are not lists. Every time you open a spreadsheet of tickers with columns for price, PE ratio, volume — you are looking at a **flat projection** of a deeply structured, curved space. The relationships between stocks — sector correlations, volatility clustering, regime shifts, lead-lag dynamics — are not metadata. They are the **topology of the manifold**.

Market Manifold is a framework for treating financial analysis as a **navigation problem on a learned manifold**. Each stock is a point in a state space. Ternary logic ({-1, 0, +1}) provides the action language. Persistent homology tracks the shape of the market. And the entire system is managed by a fleet of specialized agents — each responsible for a single stock "room" — coordinated through I2I batons and the pincher reflex runtime.

**This is not a trading bot.** It is a **structural analysis framework** — a way to see the market's geometry and navigate it with confidence.

---

## The Problem: Why Lists Fail

### A stock is not a row in a spreadsheet

When you analyze 500 stocks, you don't have 500 independent signals. You have:

- **Sector entanglement** — Energy stocks move together (covariance structure)
- **Regime dependency** — Correlations flip during bull/bear/crash periods (non-stationarity)
- **Multi-scale dynamics** — A 5-minute chart, a daily chart, and a weekly chart tell different stories (temporal hierarchy)
- **Hidden manifolds** — Price/volume data lives on a lower-dimensional manifold embedded in high-dimensional observation space

A flat list ignores all of this. You cannot compute pairwise distances between 500 tickers and call it analysis — because the relevant distance metric changes with market regime, and the topology of the cloud of points contains more information than any pair of coordinates.

### The ternary insight

Most analysis frameworks use {buy, sell, hold} as a secondary classification — something you decide *after* the analysis. Market Manifold inverts this: **ternary logic is the analysis**.

- **+1** (Accumulate / Overweight): The manifold geometry supports upward movement. Positive topological signal. Density of nearby positive examples is increasing. Persistent homology shows a cycle forming with bullish implications.
- **0** (Neutral / Hold): The stock sits in a region of topological ambiguity. No clear homology signal. Boundary zone between regimes. Energy-neutral.
- **−1** (Reduce / Underweight): The manifold geometry supports downward movement. Negative topological signal. Density increasing in the negative direction. Betti numbers reveal a void or cavity beneath.

The output is not a price target. It is a **position in the ternary action space** — grounded in the manifold's geometry, not a model's forecast.

---

## Architecture Overview

```
                         ┌──────────────────┐
                         │  MARKET MANIFOLD  │
                         │  (This Framework) │
                         └────────┬─────────┘
                                  │
               ┌──────────────────┼──────────────────┐
               ▼                  ▼                  ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │  Stock Rooms      │ │ Topological  │ │  Reflex Layer    │
    │  (One per ticker) │ │ Observatory   │ │  (Pincher Mode)  │
    │  ┌──────────────┐ │ │ (Persistent  │ │                  │
    │  │ Ternary Maps  │ │ │  Homology)   │ │  • SAEP Veto     │
    │  │ Fundamental   │ │ │ Betti curves │ │  • Confidence    │
    │  │ Technical     │ │ │ Persistence  │ │  • .nail bundles │
    │  │ Sentiment     │ │ │  diagrams    │ │  • Reflex        │
    │  └──────────────┘ │ │ Birth/death  │ │    induction     │
    └──────────────────┘ │  landscapes   │ └──────────────────┘
                          └──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────┐
                    │  Fleet Coordination    │
                    │  (I2I Baton Protocol)  │
                    │                        │
                    │  Bottles between rooms │
                    │  Spline distillation   │
                    │  Cross-stock alerts    │
                    └────────────────────────┘
```

### The Stack

| Layer | Component | Technology | Role |
|-------|-----------|-----------|------|
| **Data Ingestion** | Room Sensors | Rust collector agents | Ingest price, volume, fundamentals, news, options flow |
| **Ternary Encoding** | Map Layers | `ternary-types` | Convert continuous signals to {−1, 0, +1} |
| **Manifold Learning** | Topological Observatory | `ternary-hamiltonian` + TDA | Persistent homology, phase space embedding |
| **Reflex Engine** | Room Keeper | `pincher` | Teach → Match → Execute loop for room actions |
| **Coordination** | Fleet Bridge | I2I Batons (`baton-system`) | Cross-room communication, spline sharing |
| **Memory** | Spline Vault | `.nail` bundles + vector DB | Distilled insights that survive agent restarts |
| **Governance** | Veto Engine | SAEP patterns | Safety constraints, risk thresholds, compliance |

---

## How It Works: A Walkthrough

### 1. A Stock Room Is Born

An agent is dispatched to create a room for a new ticker (say, `$AAPL`). The room is a directory:

```
rooms/AAPL/
├── identity.toml          # Ticker metadata, sector, market cap
├── maps/
│   ├── technical.map      # Ternary-encoded technical indicators
│   ├── fundamental.map    # Ternary-encoded fundamentals
│   └── sentiment.map      # Ternary-encoded sentiment signals
├── reflexes.db            # SQLite vector store of learned reflexes
├── splines/               # Distilled insights that survive restarts
│   └── earnings-drift.spline
├── topology/
│   ├── persistence.json   # Current persistence diagram snapshot
│   └── betti-curve.json   # Betti number time series
└── log/
    └── room-journal.md    # Agent's narrative log
```

### 2. Ternary Maps Are Built

Every continuous signal is encoded into {−1, 0, +1}:

```rust
use ternary_types::*;

// RSI: 70+ → +1 (overbought/bearish), 30-70 → 0, <30 → -1 (oversold/bullish)
fn rsi_to_trit(rsi: f64) -> Trit {
    if rsi > 70.0 { -1 }   // Overbought → negative signal (mean reversion)
    else if rsi < 30.0 { 1 } // Oversold → positive signal
    else { 0 }              // Neutral zone
}

// Volume: above 2x average → +1 (conviction), normal → 0, below 0.5x → -1 (apathy)
fn volume_to_trit(volume: f64, avg_volume: f64) -> Trit {
    let ratio = volume / avg_volume;
    if ratio > 2.0 { 1 }
    else if ratio < 0.5 { -1 }
    else { 0 }
}
```

Each map is a `TritVec` — a vector of trits. The three maps (technical, fundamental, sentiment) form a **3D ternary state space** for the stock.

### 3. The Topological Observatory Runs

The room agent queries the topological observatory:

```bash
# Find persistent features in the current manifold neighborhood
observatory homology --room AAPL --dimension 0:2

# Output:
# H₀: 3 connected components (3 distinct regime clusters)
# H₁: 1 persistent cycle (sector rotation pattern)
# H₂: 0 persistent voids
# 
# Topological signature: [H₀=3, H₁=1, H₂=0]
# Regime: Boundary zone between sector rotation and single-regime stability
```

The Betti numbers (β₀, β₁, β₂) become a **topological fingerprint** for the stock's current state.

### 4. Reflexes Fire

When the topological signature matches a known pattern, the pincher reflex engine fires:

```sql
-- Stored reflex from previous earnings season
INSERT INTO reflexes (id, intent, action_sql, embedding, confidence)
VALUES (
    'earnings-drift-pattern',
    'pre-earnings topological contraction + high sentiment divergence',
    'SELECT * FROM maps WHERE volatility > 3sigma AND sector_breadth = -1',
    [...embedding...],
    0.72
);
```

If confidence > 0.80, the reflex executes autonomously (e.g., produce a report, adjust the room's ternary position). If confidence < 0.55, the reflex is routed to the LLM-as-Compiler for analysis.

### 5. Splines Are Distilled

After each earnings event, regime shift, or significant move, the room agent distills a **spline** — a compact insight that survives memory loss:

```
Spline: AAPL-Q2-2026-earnings
Type: EARNINGS_DRIFT
Content: 
  Pre-earnings: H₀=1, H₁=0 → single-regime compression
  Post-earnings: H₀=4, H₁=2 → fragmented + rotational  
  The gap between pre/post topology = 4.2 (Hausdorff distance)
  → This suggests earnings acts as a topology-shattering event
→ Rule: When H₀ drops below 2 pre-earnings, expect ≥ 3 new components post-earnings
```

Splines are shared across the fleet via I2I batons. A spline learned on `$AAPL` may apply to `$MSFT` if they share sector topology.

---

## Topology of Value: A Deeper View

See [Topology of Value](./docs/TOPOLOGY-OF-VALUE.md) for the full treatment.

The core insight:

1. **Each stock is a point** in a high-dimensional state space (price, volume, vol, fundamentals, sentiment, options flow)
2. **Manifold hypothesis**: These points lie on or near a lower-dimensional manifold
3. **Persistent homology** reveals the manifold's shape: components (H₀), cycles (H₁), voids (H₂)
4. **Ternary logic** provides the action language: +1 (accumulate at bullish topology), 0 (wait at ambiguous topology), −1 (reduce at bearish topology)
5. **Regime changes** appear as topological phase transitions — Betti numbers shift, components merge/split, cycles appear/disappear
6. **Cross-stock topology** reveals sector structure, rotation patterns, and systemic risk

For a fully worked example with `$AAPL`, `$MSFT`, and `$GOOGL` in the same sector, see the [Topological Sector Analysis](./docs/TOPOLOGY-OF-VALUE.md#worked-example-appl-msft-googl-in-a-sector-topology).

---

## Onboarding: Room Managers

New agents joining Market Manifold should follow the [Stock Room Manager Onboarding Guide](./onboarding/STOCK-ROOM-MANAGER.md).

The guide covers:

- **Day 1**: Claim your room, create the directory structure, run initial ternary maps
- **Day 2-3**: Set up the topological observatory, establish reflex baseline
- **Day 4**: Connect to the fleet (I2I vessel, room journal, spline proctology)
- **Day 5+**: Teach reflexes, participate in cross-room analysis, distill splines

---

## Symmetry Principles

Market Manifold is designed with four symmetries that make it **self-consistent, composable, and provably structured**:

### 1. Rotational Symmetry (Cycle Invariance)

The analysis is invariant under time shifts of one full market cycle. A bull-bear-complete pattern produces the same topological signature regardless of when in history it occurs. The `ternary-rhythm` crate provides the temporal backbone — markets move in rhythmic cycles, not random walks.

### 2. Translational Symmetry (Sector Invariance)

The topological framework is sector-agnostic. A technology stock and an energy stock produce structurally comparable topological fingerprints. The **conservation law** is: *topological complexity is conserved under sector rotation* — the total Betti number across the sector remains stable as stocks rotate in and out of favor.

### 3. Scale Symmetry (Fractal Invariance)

The manifold structure persists across time scales. A 5-minute chart, a daily chart, and a weekly chart reveal the same topological features at different resolutions. The manifold is **self-similar** — Betti number curves are fractally scaled across time horizons.

### 4. Reductive Symmetry (Compression Invariance)

When the analysis is distilled into a spline, the essential topological information is preserved. The spline is a **compressed representation** of the room's state — it can be decompressed into a working analysis without loss of structural information. This is the `.nail` bundle principle applied to knowledge.

---

## Fleet Coordination

Market Manifold uses the [I2I Baton Protocol](../../baton-system/PROTOCOL.md) for all cross-room communication:

| Baton Type | Purpose | Frequency |
|------------|---------|-----------|
| `ROOM_UPDATE` | Periodic state broadcast | Every tick |
| `SPLINE_SHARE` | Distilled insight distribution | After analysis |
| `ALERT` | Topological anomaly detected | Event-driven |
| `SECTOR_SYNC` | Cross-room topological comparison | Every 6h |
| `REFLEX_PROMOTE` | Candidate reflex for fleet-wide adoption | When confidence > 0.90 |

### The Vessel

All batons flow through the I2I vessel at `/tmp/i2i-vessel/`:

```
/tmp/i2i-vessel/
├── bottles/            # Outgoing messages
│   └── market-manifold/
│       ├── AAPL->MSFT-20260605.sector-sync.bottle
│       └── AAPL-20260605.room-update.bottle
├── harbor/             # Incoming messages
│   └── market-manifold/
│       └── FLEET->AAPL-20260605.sector-sync.bottle
└── splines/            # Distilled insights
    └── market-manifold/
        └── earnings-topology-shift.spline
```

---

## Getting Started

### Prerequisites

- Rust 2024+ toolchain
- `pincher` CLI installed (see [pincher README](../../pincher/README.md))
- I2I baton agent active (`baton-create` script available)
- Access to the SuperInstance fleet (Cloudflare Worker `nebula` for edge reflexes)

### Quick Start

```bash
# 1. Clone the framework
git clone https://github.com/SuperInstance/market-manifold.git
cd market-manifold

# 2. Create your first room
./bin/create-room --ticker AAPL --sector Technology

# 3. Run ternary maps
./bin/build-maps --room AAPL

# 4. Launch the topological observatory
./bin/observatory --room AAPL --timeline 90d

# 5. Install pincher reflexes
pincher teach --room AAPL --intent "regime-shift-detection"

# 6. Connect to fleet
./bin/join-fleet --rooms AAPL,MSFT,GOOGL
```

### From First Principles

For those who want to understand the mathematics before running code, start with:

1. **[Topology of Value](./docs/TOPOLOGY-OF-VALUE.md)** — The foundational document
2. **[Ternary Substrate](./docs/TERNARY-SUBSTRATE.md)** — How {−1, 0, +1} encodes financial reality
3. **[Stock Room Manager Guide](./onboarding/STOCK-ROOM-MANAGER.md)** — What each agent does
4. **[Fleet Coordination Protocol](./docs/FLEET-COORDINATION.md)** — How rooms talk to each other

---

## Ecosystem Position

Market Manifold sits at the intersection of three SuperInstance domains:

```
┌────────────────────────────────────────────────────────┐
│                  SuperInstance Ecosystem                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Ternary Foundations    Reflex Runtime    Coordination  │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ ternary-types    │  │ pincher      │  │ baton-    │ │
│  │ ternary-matrix   │  │ reflex eng.  │  │ system    │ │
│  │ ternary-rhythm   │  │ .nail bundles│  │ I2I prot. │ │
│  │ ternary-dynamics │  │ veto engine  │  │ vessel    │ │
│  │ ternary-tnn      │  │ confidence   │  │ splines   │ │
│  │ ternary-hamilt.  │  │ feedback     │  │ bottles   │ │
│  └─────────────────┘  └──────────────┘  └───────────┘ │
│                                                        │
│                        │                               │
│                        ▼                               │
│              ┌─────────────────────┐                   │
│              │  MARKET MANIFOLD    │                   │
│              │  (THIS FRAMEWORK)   │                   │
│              │  Topological        │                   │
│              │  Financial Analysis │                   │
│              └─────────────────────┘                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Related Projects

- **constraint-theory-core** — Pythagorean manifold snapping for exact geometry
- **pincher** — The reflex runtime that powers every stock room
- **baton-system** — I2I protocol for cross-room coordination
- **ternary-types** — The {−1, 0, +1} arithmetic foundation
- **ternary-hamiltonian** — Hamiltonian mechanics on ternary phase space (regime dynamics)
- **ternary-rhythm** — Temporal pattern recognition (market cycles and polyrhythms)
- **fleet-murmur-worker** — Edge reflex engine on Cloudflare Workers

---

## License

MIT OR Apache-2.0 — see LICENSE.

---

## The Crab and the Coral

> *A hermit crab doesn't try to carry the whole ocean. It finds a shell, grows into it, and when the shell is outgrown, it finds a larger one.*
>
> *Market Manifold is the same. Each stock room is a shell. The topological observatory is the ocean current the crab rides. The I2I batons are the calcium bridges that connect the shells into a coral reef.*
>
> *You don't need to predict the market. You need to navigate its topology.*

— Oracle2, SuperInstance Fleet
