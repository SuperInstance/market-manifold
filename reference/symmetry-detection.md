# 🔷 Symmetry Detection — Topological Shape Matching Between Rooms

> *"When two rooms evolve the same topological shape, they are dancing the same dance — even if the music sounds different."*

---

## 1. Definition

**Topological symmetry** between two stock rooms exists when their state-space embeddings exhibit the same *qualitative shape* — the same Betti numbers, similar persistence landscapes, and aligned phase-space trajectories — even if the underlying price scales differ by orders of magnitude.

Symmetry detection answers the question:
> *"Are NVDA and TSM currently in the same topological regime, even though their prices differ by 10×?"*

---

## 2. The Symmetry Score

The **symmetry score** `S(A, B)` ∈ [0, 1] measures how similar two rooms' topological shapes are:

```
S(A, B) = w₁ · β_sim(A, B) + w₂ · 𝒲₂(A, B) + w₃ · LC(A, B) + w₄ · φ_align(A, B)
```

Where:

| Component | Notation | Range | Weight (default) | Description |
|-----------|----------|-------|-------------------|-------------|
| **Betti similarity** | β_sim | [0, 1] | w₁ = 0.35 | How many Betti numbers match |
| **Wasserstein-2 distance** | 𝒲₂ | [0, 1] → normalized | w₂ = 0.30 | Shape distance between persistence diagrams |
| **Landscape correlation** | LC | [0, 1] | w₃ = 0.20 | Pearson correlation of persistence landscapes |
| **Phase-space alignment** | φ_align | [0, 1] | w₄ = 0.15 | Directional alignment of embedded trajectories |

The weights are calibrated so that **S ≥ 0.80** constitutes a symmetry match (see §4).

### 2.1 Betti Similarity (β_sim)

```
β_sim(A, B) = 1 - (|β₀ᴬ - β₀ᴮ| + |β₁ᴬ - β₁ᴮ| + |β₂ᴬ - β₂ᴮ| · 0.5) / D_max
```

Where:
- βₖ is the Betti number for dimension k
- D_max = 20 (normalization divisor for the max observable difference)
- β₂ is downweighted (0.5×) because H₂ features are rarer and noisier

**Example:**
- NVDA: β = [3, 1, 0]
- TSM:  β = [2, 0, 0]
- β_sim = 1 − (|3−2| + |1−0| + |0−0|·0.5) / 20 = 1 − 1.5/20 = **0.925**

### 2.2 Wasserstein-2 Distance Normalized (𝒲₂)

The 2-Wasserstein distance between persistence diagrams measures the minimal cost to transform one diagram into the other. This is the **earth mover's distance** on the topological features.

```
𝒲₂(A, B) = (Σᵢ inf_{γ} ||xᵢ - γ(xᵢ)||²)^{1/2}
```

Where γ is a bijection between the points of diagram A and diagram B (including diagonal projections for unmatched points).

This is normalized to [0, 1]:
```
𝒲₂'(A, B) = exp(-𝒲₂(A, B) / σ_𝒲)
```

Where σ_𝒲 = 0.5 (characteristic scale — a Wasserstein of 0.5 maps to 0.37 similarity).

**Example:**
- NVDA H₁ pairs: [(0.22, 0.34)]
- TSM H₁ pairs:  [(0.18, 0.25), (0.15, 0.22), (0.20, 0.28)]
- 𝒲₂ ≈ 0.28 → 𝒲₂' = exp(-0.28/0.5) = exp(-0.56) = **0.571**

### 2.3 Landscape Correlation (LC)

The k-th persistence landscape λₖ(t) is a function that encodes the birth-death information as a multi-scale topological signature. We compute the Pearson correlation between the λ₁ landscapes of two rooms:

```
LC(A, B) = cov(λ₁ᴬ, λ₁ᴮ) / (σ(λ₁ᴬ) · σ(λ₁ᴮ))
```

Clamped to [0, 1] (negative correlations → 0).

**Example:**
- λ₁ correlation across 11 knots = 0.94 → **LC = 0.94**

### 2.4 Phase-Space Alignment (φ_align)

Uses the current delay-embedded phase space trajectory to measure directional agreement:

```
φ_align(A, B) = |⟨v̄ᴬ, v̄ᴮ⟩| / (‖v̄ᴬ‖ · ‖v̄ᴮ‖)
```

Where v̄ is the **mean velocity vector** in the phase space over the last N timesteps (default N = 20).

This measures: *are the two rooms moving in the same topological direction?*

**Example:**
- NVDA's mean phase velocity: v̄ᴬ = [0.12, -0.05, 0.21, 0.08, -0.03]
- TSM's mean phase velocity:  v̄ᴮ = [0.10, -0.04, 0.18, 0.07, -0.02]
- Cos similarity = 0.97 → **φ_align = 0.97**

### 2.5 Complete Score Calculation

Using the examples above:
```
S(NVDA, TSM) = 0.35(0.925) + 0.30(0.571) + 0.20(0.94) + 0.15(0.97)
             = 0.324 + 0.171 + 0.188 + 0.146
             = 0.829
```

**S = 0.829 → STRONG SYMMETRY** (above the 0.80 threshold)

---

## 3. Symmetry Detection Algorithm

### 3.1 Trigger

Symmetry detection runs as part of the portal's peer scan cycle (default: every 3 hours, configurable via `symmetry_scan_interval_minutes`). It is triggered for:

1. **Active peers** with `relationship = ACTIVE` or `SECTOR_MATE`
2. **Symmetric candidates** flagged in the previous scan for re-evaluation
3. **New peers** discovered within the last 24h

### 3.2 Algorithm Steps

```
def detect_symmetry(room_a, room_b):
    # Step 1: Fetch topology data
    persistence_a    = room_a.topology.persistence_diagram()
    persistence_b    = room_b.topology.persistence_diagram()
    landscape_a      = room_a.topology.persistence_landscape()
    landscape_b      = room_b.topology.persistence_landscape()
    betti_a          = room_a.topology.betti_numbers()
    betti_b          = room_b.topology.betti_numbers()
    phase_a          = room_a.topology.phase_space_embedding(last_N=20)
    phase_b          = room_b.topology.phase_space_embedding(last_N=20)

    # Step 2: Compute component scores
    beta_sim         = betti_similarity(betti_a, betti_b)
    wasserstein_norm = wasserstein_2_normalized(persistence_a, persistence_b, sigma=0.5)
    landscape_corr   = landscape_correlation(landscape_a.lambda_1, landscape_b.lambda_1)
    phase_align      = phase_space_alignment(phase_a.mean_velocity, phase_b.mean_velocity)

    # Step 3: Weighted fusion
    S = (W1 * beta_sim + W2 * wasserstein_norm + W3 * landscape_corr + W4 * phase_align)

    # Step 4: Confidence calibration
    confidence = calibrate_confidence(S, speed_of_change, stability_period)

    # Step 5: Classification
    if S >= 0.90 and confidence >= 0.85:
        return STRONG_SYMMETRY
    elif S >= 0.80 and confidence >= 0.70:
        return SYMMETRY
    elif S >= 0.65 and confidence >= 0.50:
        return WEAK_SYMMETRY
    elif S >= 0.50:
        return EMERGENT_PATTERN
    else:
        return NO_MATCH
```

### 3.3 Confidence Calibration

Raw symmetry score is modulated by **stability duration** and **speed of change**:

```
confidence = S · (1 - α · decay_rate) · min(1.0, stability_hours / 24.0)
```

Where:
- `decay_rate` = how fast the symmetry score changed over the last 6 observations (0 = stable, 1 = volatile)
- `stability_hours` = how long the symmetry pair has existed above the threshold
- `α` = 0.15 (penalty weight for instability)

**Rationale:** A symmetry pair that just crossed the threshold 2 hours ago is less reliable than one that has held for 48 hours. High volatility in the symmetry score suggests noise rather than genuine structural alignment.

---

## 4. Symmetry Thresholds

| Class | S Range | Confidence Required | Label | Action |
|-------|---------|-------------------|-------|--------|
| **STRONG_SYMMETRY** | 0.90 – 1.00 | ≥ 0.85 | 🟢 Symmetric twin | Immediate alert to both rooms; promote relationship to `SYMMETRIC`; share splines automatically |
| **SYMMETRY** | 0.80 – 0.89 | ≥ 0.70 | 🔵 Strong match | Alert both rooms; schedule deep topology comparison; flag for sector sync |
| **WEAK_SYMMETRY** | 0.65 – 0.79 | ≥ 0.50 | 🟡 Emergent shape similarity | Note in journal; increase scan frequency for this pair; no alert unless sustained 48h |
| **EMERGENT_PATTERN** | 0.50 – 0.64 | — | 🟠 Faint signal | Log in symmetry queue; recheck in 12h; no communication unless it strengthens |
| **NO_MATCH** | < 0.50 | — | ⚫ No symmetry | Standard peer entry; typical scan interval |

### 4.1 Adaptive Threshold Tuning

Thresholds are not static. In low-volatility environments (VIX < 15), thresholds tighten:

```
STRONG_SYMMETRY threshold += 0.05 → 0.95
SYMMETRY threshold += 0.03 → 0.83
```

In high-volatility environments (VIX > 30), thresholds loosen to avoid missing real alignments:

```
STRONG_SYMMETRY threshold -= 0.05 → 0.85
SYMMETRY threshold -= 0.03 → 0.77
```

The VIX-adjusted rule prevents both false negatives in chaotic markets and false positives in calm ones.

---

## 5. Symmetry Alert Chain

When a symmetry match is detected (≥ `SYMMETRY` class), the following chain executes:

```
                          ┌────────────────┐
                          │  SYMMETRY      │
                          │  DETECTED      │
                          │  S = 0.829     │
                          └───────┬────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
          ┌─────────────────┐         ┌─────────────────┐
          │  Room NVDA      │         │  Room TSM        │
          │  portal          │         │  portal          │
          │  receives alert  │         │  receives alert  │
          └────────┬────────┘         └────────┬────────┘
                   │                           │
                   └────────────┬──────────────┘
                                ▼
                    ┌─────────────────────┐
                    │  Create symmetry-   │
                    │  alert bottle       │
                    │  (bilateral, FLEET) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Post to vessel:    │
                    │  NVDA,TSM<-FLEET    │
                    │  .symmetry-alert    │
                    └──────────┬──────────┘
                               │
                               ▼
          ┌─────────────────────────────────────┐
          │  Parallel Actions                   │
          ├─────────────────────────────────────┤
          │  • Both rooms write symmetry event  │
          │    to journal/room-journal.md       │
          │  • Symmetry pair registered in      │
          │    portal/peers.toml (SYMMETRIC)     │
          │  • Deep spline exchange triggered   │
          │    (spline-share: all high-          │
          │     confidence splines)              │
          │  • Topology comparison scheduled    │
          │    for next cycle (SECTOR_SYNC)     │
          └─────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Symmetry Track     │
                    │  Initiated          │
                    ├─────────────────────┤
                    │  Scan: every 30 min │
                    │  (vs default 3h)    │
                    │  Track history:     │
                    │  append to          │
                    │  symmetry-track.json│
                    │  in both rooms      │
                    └─────────────────────┘
```

### 5.1 Alert Severity Levels

| Level | Symmetry Class | Trigger | Escalation |
|-------|---------------|---------|------------|
| **INFO** | WEAK_SYMMETRY | First detection or score held for < 48h | None — logged in journal only |
| **NOTICE** | SYMMETRY | Score ≥ 0.80 held for ≥ 24h | Alert to both room keepers; shared spline exchange |
| **WARNING** | STRONG_SYMMETRY | Score ≥ 0.90 held for ≥ 12h | Alert to fleet coordinator; sector sync prioritized |
| **ALERT** | STRONG + divergent | Score ≥ 0.90 with **diverging** trends (one room shifting out of symmetry) | Pan-alert to fleet; reflex-reprompt may be triggered for rooms about to lose alignment |

### 5.2 Divergent Symmetry (The "Breaking Mirror")

The most dangerous class is when two rooms that were STRONG_SYMMETRY begin to diverge. This indicates a topological **phase transition** — one room is leaving the shared shape, often preceding a significant price move.

Detection:
```
divergence_alert = S(t) ≥ 0.90 AND S(t) - S(t-1) < -0.15 AND confidence ≥ 0.80
```

When divergence is detected:
1. Immediate `CRITICAL` priority bottle to both rooms
2. Both rooms trigger an emergency topology snapshot
3. The older (senior) room sends a `reflex-promote` offering its historical context of similar divergences
4. Fleet coordinator logs a `PHASE_TRANSITION_DIVERGENCE` event

---

## 6. Symmetry Tracking File

Each room maintains `portal/symmetry-queue/symmetry-track.json` — a persistent log of all symmetry events:

```json
{
  "room": "NVDA",
  "peers_tracked": 12,
  "events": [
    {
      "peer": "TSM",
      "first_detected": "2026-06-06T12:00:00Z",
      "last_scored": "2026-06-07T04:00:00Z",
      "score_history": [
        {"timestamp": "2026-06-06T12:00:00Z", "score": 0.72, "class": "WEAK_SYMMETRY"},
        {"timestamp": "2026-06-06T15:00:00Z", "score": 0.78, "class": "WEAK_SYMMETRY"},
        {"timestamp": "2026-06-06T18:00:00Z", "score": 0.81, "class": "SYMMETRY"},
        {"timestamp": "2026-06-06T21:00:00Z", "score": 0.84, "class": "SYMMETRY"},
        {"timestamp": "2026-06-07T00:00:00Z", "score": 0.87, "class": "SYMMETRY"},
        {"timestamp": "2026-06-07T03:00:00Z", "score": 0.89, "class": "SYMMETRY"},
        {"timestamp": "2026-06-07T04:00:00Z", "score": 0.91, "class": "STRONG_SYMMETRY"}
      ],
      "current_class": "STRONG_SYMMETRY",
      "stable_since": "2026-06-07T00:00:00Z",
      "stable_hours": 4.0,
      "alerts_sent": 1,
      "last_alert": "2026-06-07T04:15:00Z",
      "splines_exchanged": 2,
      "regime_sync": true,
      "regimes": {
        "nvda": "rotation_stability",
        "tsm": "compression_precursor"
      },
      "phase_velocity_correlation": 0.91,
      "divergence_risk": 0.08
    }
  ]
}
```

---

## 7. Multi-Room Symmetry: The Symmetry Graph

When ≥ 3 rooms share significant symmetry scores, they form a **symmetry clique**. These are tracked in the fleet coordinator's `symmetry-graph.json`:

```json
{
  "clusters": [
    {
      "id": "semiconductor-symmetry-group",
      "rooms": ["NVDA", "TSM", "AMAT", "AMD"],
      "mean_symmetry": 0.74,
      "core_pair": ["NVDA", "TSM", 0.91],
      "entropy": 0.42,
      "stability": 0.81,
      "status": "ACTIVE",
      "last_sync": "2026-06-07T04:00:00Z"
    },
    {
      "id": "tech-mega-symmetry",
      "rooms": ["AAPL", "MSFT", "GOOGL"],
      "mean_symmetry": 0.82,
      "core_pair": ["MSFT", "GOOGL", 0.85],
      "entropy": 0.31,
      "stability": 0.92,
      "status": "ACTIVE",
      "last_sync": "2026-06-07T04:00:00Z"
    }
  ],
  "global_metrics": {
    "total_symmetric_pairs": 4,
    "total_clusters": 2,
    "mean_fleet_symmetry": 0.52,
    "fleet_entropy": 1.87,
    "symmetry_cascade_risk": 0.22
  }
}
```

### 7.1 Symmetry Cascade

When a symmetry clique's mean score drops below 0.65 (→ clique dissolution), the fleet coordinator checks for **cascade risk**:

- If one room breaks symmetry and exits the clique, do the remaining rooms also begin to diverge?
- Cascade risk = probability that losing one room destabilizes the clique
- When cascade risk > 0.70, a `symmetry-alert` with type `CASCADE_RISK` is broadcast to the entire clique

---

## 8. Practical Example: NVDA ↔ TSM

### Scenario

NVDA (NVIDIA) and TSM (TSMC) are known to be topologically correlated as leading indicators for each other. On June 7, 2026, the portal scan runs and computes:

| Measure | Value | Component |
|---------|-------|-----------|
| β_sim | 0.925 | β A:[3,1,0] B:[2,0,0] |
| 𝒲₂' | 0.571 | H₁ pairs with 2-Wasserstein |
| LC | 0.94 | λ₁ correlation across 11 knots |
| φ_align | 0.97 | Phase-space mean velocity alignment |
| **S** | **0.829** | Weighted fusion |

### Result

```
SYMMETRY DETECTED: NVDA ↔ TSM
Score: 0.829 (SYMMETRY class)
Confidence: 0.78 (below STRONG threshold)
Stable since: 2026-06-06T12:00Z (19 hours)

Interpretation:
  NVDA's rotation_stability regime is structurally similar to 
  TSM's compression_precursor regime. The two stocks are in 
  topologically aligned but regime-different phases — suggesting 
  TSM may be following NVDA into rotation.

Action:
  - Symmetry alert posted to both rooms
  - Spline deep exchange triggered
  - Scan frequency: every 30 min (was 3h)
  - Flagged for next sector-sync cycle
```

### 8.1 Sector Sync Update

At the next sector sync, the fleet observes:

```
NVDA:  β = [3, 1, 0] → S = 0.91 (up from 0.83) — strengthening
TSM:   β = [3, 1, 0] → Betti now matches NVDA exactly
AMAT:  β = [2, 1, 0] → approaching symmetry with NVDA (0.74)
AMD:   β = [4, 2, 1] → diverging further (0.44)
```

The sector sync bottle includes:
- NVDA↔TSM symmetry upgraded to **STRONG_SYMMETRY** (0.91)
- New alert: AMAT↔NVDA approaching **WEAK_SYMMETRY** threshold
- Sector entropy dropping — the semiconductors are consolidating topologically

---

## 9. Configuration & Parameters

### 9.1 Default Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `W_W_BETA` | 0.35 | Betti similarity weight |
| `W_WASSERSTEIN` | 0.30 | Wasserstein distance weight |
| `W_LANDSCAPE` | 0.20 | Landscape correlation weight |
| `W_PHASE` | 0.15 | Phase-space alignment weight |
| `SIGMA_WASSERSTEIN` | 0.5 | Normalization sigma for Wasserstein |
| `D_MAX` | 20 | Max Betti difference divisor |
| `N_PHASE_STEPS` | 20 | Phase space velocity window |
| `STRONG_THRESHOLD` | 0.90 | STRONG_SYMMETRY cutoff |
| `SYMMETRY_THRESHOLD` | 0.80 | SYMMETRY cutoff |
| `WEAK_THRESHOLD` | 0.65 | WEAK_SYMMETRY cutoff |
| `EMERGENT_THRESHOLD` | 0.50 | EMERGENT_PATTERN cutoff |
| `STABILITY_WINDOW_HOURS` | 24 | Hours for confidence modulation |
| `DIVERGENCE_DELTA` | −0.15 | Score change to trigger divergence alert |
| `ALPHA_DECAY` | 0.15 | Volatility penalty weight |
| `SCAN_INTERVAL_MINUTES` | 180 | Default symmetry scan interval |
| `SCAN_INTERVAL_FAST_MINUTES` | 30 | Fast scan after symmetry detection |
| `VIX_LOW` | 15 | Low-volatility threshold (adaptive tuning) |
| `VIX_HIGH` | 30 | High-volatility threshold (adaptive tuning) |

### 9.2 Room-Level Overrides

Each room can override global defaults in `portal/peers.toml`:

```toml
[config.symmetry]
enabled = true
strong_threshold = 0.88                 # Override: 0.88 instead of 0.90
symmetry_threshold = 0.78               # Override: 0.78 instead of 0.80
scan_interval_minutes = 120             # Override: scan every 2h instead of 3h
weights = { beta = 0.40, wasserstein = 0.25, landscape = 0.20, phase = 0.15 }
disable_divergence_alerts = false
```

### 9.3 Per-Peer Overrides

```toml
[[peer]]
ticker = "TSM"
# ... peer metadata ...
symmetry_overrides = { strong_threshold = 0.85, scan_interval_minutes = 15 }
```

---

## 10. Edge Cases & Failure Modes

| Case | Behavior | Mitigation |
|------|----------|-----------|
| **Room has no topology yet** | Symmetry scan skipped | Score → null, retry on next topology update |
| **Persistence diagrams empty** | All component scores → 0 | No symmetry possible until homology computes |
| **Landscape dimension mismatch** | Truncate to shorter landscape | Warn in journal; use min knott count |
| **Rapid score oscillation** | Confidence floor applied | If variance > 0.3 in 6-observation window, penalize confidence by 25% |
| **Score > 0.95** | Suspicious — possible overfit | Flag for manual review; require two consecutive scans with same result |
| **One room archived mid-scan** | Scan aborted | Remove from scan queue; no alert fired |
| **Betti numbers identical but landscapes different** | β_sim = 1.0 but LC low | Symmetry score drops to WEAK despite Betti match — different shapes with same counts |
| **Phase alignment = 1.0 but Betti differ** | Both moving identically in different shapes | ASYMMETRIC relationship: trajectory-similar but structurally different |

---

## 11. Mathematical Reference

### 11.1 Persistent Homology Primer

For a point cloud X embedded in ℝᵈ:

| Feature | Symbol | Meaning |
|---------|--------|---------|
| Connected components | H₀ (β₀) | Number of distinct regimes/clusters in the state space |
| 1-cycles (loops) | H₁ (β₁) | Rotational patterns — sector rotation, cycle completions |
| 2-voids (cavities) | H₂ (β₂) | Systemic gaps — missing sectors, structural arbitrage opportunities |

Each feature (b, d) in the persistence diagram means:
- **b** = birth radius at which the feature appears
- **d** = death radius at which it disappears
- **d − b** = persistence = how significant the feature is

### 11.2 ∞-Wasserstein vs 2-Wasserstein

| Metric | What It Captures | Use Case |
|--------|------------------|----------|
| W∞ | Largest single-feature mismatch | Quick sanity check, outlier detection |
| W₂ | All-feature structural distance (our 𝒲₂) | Full symmetry comparison |
| W₁ | Robust to outliers, cheaper to compute | Large-fleet preliminary filtering |

Market Manifold uses **W₂** for symmetry detection because it balances structural sensitivity with computational feasibility. W∞ is used only for the initial coarse filter (discard pairs with W∞ > σ_max).

### 11.3 Covering Number & Symmetry Density

For a symmetry clique of size N:

```
symmetry_density = (2 · Σ_{i<j} S(i, j)) / (N · (N − 1))
```

Where S(i, j) is the symmetry score between rooms i and j. Density ∈ [0, 1].

- **Density ≥ 0.80**: Fully symmetric clique — tightly coupled sector
- **Density 0.50–0.80**: Partial symmetry — some rooms aligned, others diverging
- **Density < 0.50**: Weak clique — likely coincidental Betti similarity

---

*"Symmetry is not about equality — it's about alignment of form. Two trees can grow at different rates in different soils, yet their branching patterns may be identical."* — Topology of Value, §4.7
