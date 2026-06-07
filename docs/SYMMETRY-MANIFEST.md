# 🧿 Symmetry Manifest

**The invariant structure of the Market Manifold.**

The Market Manifold framework is designed around four fundamental symmetries. These symmetries are not decorative — they are **constraints on the framework's internal logic** that ensure composability, provability, and structural consistency across all rooms, across all timeframes, and across all market regimes.

---

## Symmetry 1: Rotational (Cycle Invariance)

### Statement

The analysis is invariant under time shifts of one complete market cycle.

### Formal

Let $\mathcal{T}$ be the topological analysis function. For any stock state history $H$ and any cyclic time shift $\tau$:

$$\mathcal{T}(H) = \mathcal{T}(H_{\tau})$$

Where $H_{\tau}$ is $H$ shifted by one full market cycle (e.g., 252 trading days).

### What This Means

- A bull-bear-complete pattern in 2023 produces the same topological signature as the same pattern in 2026
- The persistence diagram of a 252-day window is stationary across cycles (barring structural market changes)
- Reflexes learned on historical data remain valid on future data if the topological regime repeats

### Implementation Guard

```rust
// When computing topological signature, always normalize to 
// a complete cycle window (252 sessions = 1 year, or 63 sessions = 1 quarter)
fn normalize_cycle_window(history: &[StockState]) -> Vec<StockState> {
    let cycle_length = if history.len() > 252 { 252 } 
                       else if history.len() > 63 { 63 }
                       else { history.len() };
    history[history.len() - cycle_length..].to_vec()
}
```

### Violation Detection

If $\mathcal{T}(H) \neq \mathcal{T}(H_{\tau})$ by more than Wasserstein 0.2, log a symmetry violation. This signals either:

1. A structural change in the market (new regulation, index reconstitution, sector redefinition)
2. A threshold calibration error in the ternary embedding

---

## Symmetry 2: Translational (Sector Invariance)

### Statement

The topological framework is sector-agnostic. The same analysis pipeline operates identically across all sectors.

### Formal

For any two sectors $S_1$, $S_2$, if a stock in $S_1$ has ternary embedding $E_1$ and a stock in $S_2$ has ternary embedding $E_2$, and $E_1 \cong E_2$ (identical up to sector-specific scaling), then:

$$\mathcal{T}(E_1) \cong \mathcal{T}(E_2)$$

Where $\cong$ denotes topological equivalence (same Betti number vector up to isomorphism).

### What This Means

- A technology stock and an energy stock with identical ternary embeddings produce the same topological analysis
- The framework does not hardcode sector-specific rules
- Splines learned in one sector may (or may not!) transfer to another sector — and the symmetry ensures the transfer is meaningful, not coincidental

### Implementation Guard

```rust
// Sector-specific scaling: normalize fundamental signals against 
// sector median, not market-wide median
fn normalize_fundamental(trit: f64, sector_median: f64, market_median: f64) -> Trit {
    let sector_relative = trit / sector_median;
    let market_relative = trit / market_median;
    // Use sector-relative for fundamental trits
    trit_to_value(sector_relative)  
}
```

### Conservation Law

**Topological complexity is conserved under sector rotation.**

Let total topological complexity $C$ of a sector be:

$$C = \sum_{\text{rooms} \in \text{sector}} E_{\text{topo}}(\text{room})$$

As stocks rotate in and out of favor, $C$ remains stable. If $C$ changes by more than 20% in 10 sessions, a sector-wide structural shift has occurred.

---

## Symmetry 3: Scale (Fractal Invariance)

### Statement

The manifold structure persists across time scales. A 5-minute chart, a daily chart, and a weekly chart reveal the same topological features at different resolutions.

### Formal

Let $\mathcal{T}_\Delta$ be the topological analysis at time resolution $\Delta$. Then for any resolution pair $(\Delta_1, \Delta_2)$ where $\Delta_2 \approx k \cdot \Delta_1$:

$$\mathcal{T}_{\Delta_1}(H) \sim \mathcal{T}_{\Delta_2}(H)$$

Where $\sim$ means "has the same Betti number vector." The persistence values scale linearly with $\Delta$ but the topological structure (connected components, cycles, voids) is invariant.

### What This Means

- A range-bound stock on a daily chart is also range-bound on a weekly chart (both show H₁ = 1)
- A trending stock on a 5-minute chart is also trending on a daily chart (both show H₀ = 1, H₁ = 0)
- Reflexes learned at one time scale transfer to other scales (the reflex for "void detection" works on daily, hourly, and weekly data)

### Implementation Guard

```rust
// Verify fractal invariance: compute topology at 3 scales
fn verify_fractal_invariance(room: &str) -> bool {
    let daily = compute_topology(room, TimeScale::Daily);
    let weekly = compute_topology(room, TimeScale::Weekly);
    let monthly = compute_topology(room, TimeScale::Monthly);
    
    let daily_betti = (daily.h0, daily.h1, daily.h2);
    let weekly_betti = (weekly.h0, weekly.h1, weekly.h2);
    let monthly_betti = (monthly.h0, monthly.h1, monthly.h2);
    
    // Fail if any Betti number disagrees across scales
    // (modulo dimension reduction: monthly may have fewer features)
    daily_betti == weekly_betti && weekly_betti == monthly_betti
}
```

---

## Symmetry 4: Reductive (Compression Invariance)

### Statement

When a room's state is distilled into a spline, the essential topological information is preserved. The spline can be decompressed into a working analysis without loss of structural information.

### Formal

Let $D: \text{Room} \to \text{Spline}$ be the distillation function and $R: \text{Spline} \to \text{Room}$ be the reconstruction function. Then:

$$D(R(D(\text{room}))) \approx D(\text{room})$$

The second distillation produces a spline that is topologically close (Wasserstein < 0.1) to the first spline. The compression is **idempotent up to noise tolerance**.

### What This Means

- A spline is not a summary — it is a **compressed representation** with a valid decompression into analysis
- When a room manager leaves, their splines can reconstruct their analysis
- When the fleet hub needs to understand what a room is doing, it reads the splines, not the full room state

### Implementation Guard

```rust
// Spline round-trip verification
fn verify_spline_integrity(spline: &Spline) -> bool {
    let reconstructed = spline.reconstruct();
    let re_distilled = reconstructed.distill();
    
    let wasserstein = persistence_diagram_distance(
        &spline.persistence_diagram,
        &re_distilled.persistence_diagram
    );
    
    wasserstein < 0.1  // Compression is lossless up to noise
}
```

---

## Symmetry Group

The four symmetries form the symmetry group of the Market Manifold:

$$G = \{ \text{Rot}, \text{Trans}, \text{Scale}, \text{Reduct} \}$$

The group is abelian: the order of applying symmetries does not matter.

$$\text{Rot} \circ \text{Trans} = \text{Trans} \circ \text{Rot}$$

This means the framework is **coordinate-free** — you can analyze a stock in any sector at any time scale with any compression level, and the analysis is structurally consistent.

---

## Empirical Verification

Each room verifies the symmetry group on initialization and every 30 days:

```rust
fn verify_symmetry_group(room: &str) -> SymmetryReport {
    SymmetryReport {
        rotational: verify_rotational_symmetry(room),
        translational: verify_translational_symmetry(room),
        scale: verify_fractal_invariance(room),
        reductive: verify_spline_integrity(&room.current_spline()),
        // Overall: all four hold
        consistent: true,
        // If any falters: flag for operator review
        degraded: false,
    }
}
```

### What Happens If a Symmetry Breaks

| Broken Symmetry | Signal | Action |
|----------------|--------|--------|
| Rotational | Market structure has permanently changed | Re-calibrate ternary embedding thresholds |
| Translational | Sector is decoupling from broader market | Flag for fleet-wide sector sync |
| Scale | Timeframe disagreement — regime change imminent | Increase observation frequency |
| Reductive | Spline quality degraded — too much information loss | Reduce compression ratio, increase spline size limit |

Symmetry breakage is itself a signal — often the most informative one.
