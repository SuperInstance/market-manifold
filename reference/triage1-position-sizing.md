# TRIAGE-1: Ternary+Continuous Position Sizing

**Addressing Critical Leak #1 — The Ternary Action Space Collapse**

> *"Ternary is discrete. Finance is continuous. No position sizing, no conviction magnitude, no cross-asset correlation awareness."* — Officer-Critic

---

## Executive Summary

The ternary substrate is retained for what it does well — **qualitative signal aggregation** (traffic lights). A continuous position sizing layer is layered on top to handle what ternary does poorly — **quantitative portfolio construction**.

The system architecture is:

```
Raw Signals → [Ternary Gate] → Act/Pass? → [Continuous Sizer] → Position Sizes
                    ↓                              ↑
           Consensus Vector           Covariance-Aware Allocation
```

The ternary gate answers *do we act?* The continuous sizer answers *how much?* They are separate layers with separate data structures, constraints, and update frequencies.

---

## 1. The Two-Layer Architecture

### Layer 1: Ternary Gate (Signal Aggregation)

**Purpose:** Determine direction and whether the system should take non-zero exposure.

The existing ternary substrate (signal maps, composite trits, scale coherence, conservation law) becomes the **gate layer only**. It answers:

| Question | How |
|----------|-----|
| Which direction? | Consensus trit: +1 (long), −1 (short), 0 (flat) |
| Is this actionable? | Composite confidence > confidence_threshold |
| Is the signal conflicted? | Signal dispersion < max_dispersion, scale_coherence > min_coherence |
| Is the stock at an extreme? | Conservation bound: \|E(t)\| < \|S\|/2 (not at extreme = safer entry) |

The gate output is:

```rust
struct TernaryGate {
    /// Net direction: +1, 0, -1
    direction: Trit,
    /// Probability the direction will persist over the holding period
    /// Derived from signal stability, not raw thresholding
    persistence_probability: f64,
    /// True if the gate passes (non-zero allocation warranted)
    is_active: bool,
    /// Why the gate closed (for audit/logging)
    close_reason: Option<GateCloseReason>,
}

enum GateCloseReason {
    ConsensusZero,         // Net trit = 0 (leminal)
    LowConfidence,         // Signal dispersion too high
    ScaleBreak,            // Timeframes disagree
    ConservationExtreme,   // |E(t)| at bound → mean reversion expected
    CorrelationConflict,   // Cross-asset correlation veto
}
```

**Gate passes only when** `is_active == true && direction != Trit::Zero`.

### Layer 2: Continuous Position Sizer

**Purpose:** Determine *how much* exposure to take, given gate approval, conviction magnitude, and portfolio constraints.

The continuous sizer is a **separate subsystem** that operates on the raw (pre-ternary) signal values, not the quantized trits. It has access to:

1. **Raw signal intensities** — the continuous values before ternary thresholding
2. **Signal histories** — for estimating conviction stability
3. **Portfolio covariance** — for cross-asset correlation awareness
4. **Risk budget** — global and per-asset constraints

```rust
struct ContinuousSizer {
    /// Per-stock raw signal intensities [0, 1]
    signal_intensities: HashMap<Symbol, HashMap<SignalType, f64>>,
    /// Per-stock conviction score [0, 1]
    conviction: HashMap<Symbol, f64>,
    /// Rolling covariance matrix (lookback: 63 trading days)
    covariance: CovarianceMatrix,
    /// Risk budget parameters
    risk_params: RiskBudget,
}
```

**Key design rule:** The sizer only produces non-zero allocations for symbols where the ternary gate says `is_active && direction != Zero`. Correlation-aware adjustments can *reduce* an allocation based on portfolio constraints but cannot *create* an allocation the gate denied.

---

## 2. Signal Intensity: Raw → Continuous (Pre-Quantization)

Each signal used in the ternary map has a **raw value** before ternary thresholding. The sizer captures these as normalized intensities in [0, 1].

### Normalization

For each signal type, map the raw value to an intensity:

```rust
struct SignalIntensity {
    /// Directional sign of the raw signal
    raw: f64,
    /// Normalized magnitude [0, 1]
    magnitude: f64,
    /// Direction implied by the raw signal
    direction: Trit,
}

fn normalize_rsi(rsi: f64) -> SignalIntensity {
    // RSI raw range: [0, 100]
    // Ternary threshold: <30 → +1, 30-70 → 0, >70 → -1
    // Intensity: how deep into the ternary region
    let (direction, magnitude) = if rsi < 30.0 {
        // Oversold → bullish. Intensity increases as RSI drops below 30
        (Trit::Pos, (30.0 - rsi) / 30.0)  // 0 at RSI=30, 1 at RSI=0
    } else if rsi > 70.0 {
        // Overbought → bearish. Intensity increases as RSI rises above 70
        (Trit::Neg, (rsi - 70.0) / 30.0)  // 0 at RSI=70, 1 at RSI=100
    } else {
        (Trit::Zero, 0.0)
    };
    SignalIntensity { raw: rsi, magnitude, direction }
}

fn normalize_volume(vol_ratio: f64) -> SignalIntensity {
    // vol_ratio = current_volume / average_volume
    let (direction, magnitude) = if vol_ratio > 2.0 {
        (Trit::Pos, (vol_ratio - 2.0).min(3.0) / 3.0)  // Cap at 5×
    } else if vol_ratio < 0.5 {
        (Trit::Neg, (0.5 - vol_ratio) / 0.5)
    } else {
        (Trit::Zero, 0.0)
    };
    SignalIntensity { raw: vol_ratio, magnitude, direction }
}
```

### Stock-Level Intensity Vector

Each stock produces a vector of signal intensities:

```rust
struct StockIntensity {
    symbol: Symbol,
    /// Per-signal intensities, only for signals where direction != Zero
    active_signals: Vec<(SignalType, SignalIntensity)>,
    /// Total number of active signals (non-zero direction)
    active_count: usize,
    /// Weighted average magnitude across all active signals
    weighted_magnitude: f64,
    /// Direction consensus (majority vote of active signal directions)
    consensus_direction: Trit,
}
```

**Critical difference from ternary map:** The ternary map discards magnitude (everything is ±1). The intensity vector preserves magnitude, enabling differentiation between:

| Signal | RSI Raw | Ternary Trit | Intensity Magnitude |
|--------|---------|--------------|-------------------|
| AAPL mild overshoot | RSI = 69 → not overbought | 0 | 0.0 |
| AAPL strong overshoot | RSI = 85 → overbought | −1 | 0.5 |
| AAPL extreme overshoot | RSI = 95 → overbought | −1 | 0.83 |

The ternary gate treats both overshoot cases identically (both are −1). The sizer differentiates them.

---

## 3. Conviction Score

Conviction answers: *how much weight should this stock's signal get?*

### Formula

```rust
struct Conviction {
    /// Composite score [0, 1]
    score: f64,
    /// Decomposed into sub-scores for analysis
    components: ConvictionComponents,
}

struct ConvictionComponents {
    /// Signal agreement: 1.0 = all signals agree, 0.0 = evenly split
    signal_unanimity: f64,
    /// Scale coherence: [0, 1] from TernaryMap
    scale_coherence: f64,
    /// Signal persistence: how long the current signal cluster has held
    signal_stability: f64,
    /// Raw signal strength: average intensity magnitude
    raw_strength: f64,
    /// Historical accuracy of this signal cluster for this stock
    signal_track_record: f64,
}
```

### Computation

```rust
fn compute_conviction(stock: &StockIntensity, ternary: &TernaryMap, hist: &SignalHistory) -> Conviction {
    // 1. Signal unanimity: are all non-zero signals pointing the same direction?
    let agreement_count = stock.active_signals.iter()
        .filter(|(_, si)| si.direction == stock.consensus_direction)
        .count();
    let signal_unanimity = agreement_count as f64 / stock.active_count.max(1) as f64;

    // 2. Raw strength: how deep into the signal region?
    let raw_strength = stock.weighted_magnitude;

    // 3. Scale coherence: does the story hold across timeframes?
    let scale_coherence = ternary.scale_coherence;

    // 4. Signal stability: how long has this configuration persisted?
    let signal_stability = hist.persistent_signal_duration(&stock.consensus_direction);

    // 5. Track record: historical Sharpe of this pattern for this symbol
    let signal_track_record = hist.pattern_accuracy(&stock);

    // Weighted combination
    let score = 0.25 * signal_unanimity
              + 0.20 * raw_strength
              + 0.20 * scale_coherence
              + 0.15 * signal_stability
              + 0.20 * signal_track_record;

    Conviction {
        score: score.clamp(0.0, 1.0),
        components: ConvictionComponents {
            signal_unanimity,
            scale_coherence,
            signal_stability,
            raw_strength,
            signal_track_record,
        },
    }
}
```

### Role in Position Sizing

Conviction directly scales position size:

```
raw_position = base_weight * conviction
```

If conviction = 0, position = 0 regardless of gate state (low conviction overrides gate). If conviction = 1, position runs at full allocation.

---

## 4. Position Sizing: From Conviction to Allocations

### 4.1 Base Risk Weight

Each asset gets a **base risk weight** determined by volatility targeting:

```rust
fn base_risk_weight(symbol: Symbol, vol_target: f64, covariance: &CovarianceMatrix) -> f64 {
    let annualized_vol = covariance.volatility(symbol).sqrt() * 252.0_f64.sqrt();
    // Fraction of risk budget this asset can consume
    vol_target / annualized_vol
}
```

Example: If the global volatility target is 15% annually and AAPL's annualized vol is 25%, AAPL's base risk weight = 15%/25% = 0.60. This means a fully convinced position in AAPL would get 60% allocation.

### 4.2 Pre-Correlation Allocation

```rust
struct PreCorrelationAllocation {
    symbol: Symbol,
    direction: Trit,              // From gate
    conviction: f64,              // [0, 1]
    base_weight: f64,             // Risk-budget-based
    raw_allocation: f64,          // conviction * base_weight * direction_sign
}
```

### 4.3 Volatility-Modulated Conviction

Some signals carry more conviction when volatility is low (the pattern is "clean") and less when vol is high (the pattern is noisy):

```rust
fn volatility_adjusted_conviction(conviction: f64, volatility_regime: VolRegime) -> f64 {
    match volatility_regime {
        VolRegime::Low => conviction,          // Clean signal → full confidence
        VolRegime::Normal => conviction * 0.9,
        VolRegime::High => conviction * 0.6,   // Noisy → reduce conviction
        VolRegime::Extreme => 0.0,             // Market in distress → flat
    }
}
```

---

## 5. Covariance-Aware Allocation (Cross-Asset Correlation)

This is the most important innovation over the base ternary substrate. The base system treats each stock independently. The hybrid system allocates with full portfolio awareness.

### 5.1 Rolling Covariance Matrix

```rust
struct CovarianceMatrix {
    /// Symbols in the universe
    symbols: Vec<Symbol>,
    /// n×n covariance matrix (63-day rolling, daily returns)
    matrix: Array2<f64>,
    /// Correlation matrix (unit-diagonal, -1 to 1)
    correlation: Array2<f64>,
    /// Per-symbol annualized volatility
    volatility: HashMap<Symbol, f64>,
    /// Timestamp of last update
    last_updated: DateTime<Utc>,
}

impl CovarianceMatrix {
    /// Update with latest daily returns
    fn update(&mut self, returns: &[(Symbol, f64)]) { /* ... */ }
    
    /// Get the covariance between two symbols
    fn cov(&self, a: Symbol, b: Symbol) -> f64 { /* ... */ }
}
```

**Update frequency:** End-of-day at minimum. Intraday optional (every 30 min during market hours).

### 5.2 Risk Contribution Calculation

For a portfolio with weights **w**, the risk contribution of asset *i* is:

```
RC_i = w_i × (Σ w)_i / √(w^T Σ w)
```

where Σ is the covariance matrix and (Σ w)_i is the i-th element of Σw.

### 5.3 Correlation-Aware Allocation Algorithm

```rust
fn correlation_aware_weights(
    // Pre-correlation allocations from the gate+sizer
    raw_allocations: &[PreCorrelationAllocation],
    covariance: &CovarianceMatrix,
    // Global constraints
    max_leverage: f64,
    max_sector_exposure: f64,
    max_single_name: f64,
) -> Result<Vec<f64>, AllocationError> {
    
    let n = raw_allocations.len();
    
    // Step 1: Start with raw allocations, normalized to sum of absolute weights = 1.0
    let total_abs: f64 = raw_allocations.iter()
        .map(|a| a.raw_allocation.abs())
        .sum();
    let mut weights: Vec<f64> = raw_allocations.iter()
        .map(|a| a.raw_allocation / total_abs.max(1e-10))
        .collect();
    
    // Step 2: Apply risk parity constraint
    // Target: equal risk contribution from each active position
    // We use a single-step approximation (not full iterative RP)
    let portfolio_vol = compute_portfolio_vol(&weights, &covariance.matrix);
    let risk_contributions: Vec<f64> = (0..n)
        .map(|i| weights[i] * (covariance.matrix.row(i).dot(&weights)) / portfolio_vol)
        .collect();
    
    // Step 3: Rebalance toward equal risk contribution
    // Scale down positions that dominate risk, scale up those under-contributing
    for i in 0..n {
        let target_rc = 1.0 / n as f64;
        let rc_ratio = risk_contributions[i] / target_rc;
        if rc_ratio > 1.5 {
            // This position contributes >50% more risk than its fair share → reduce
            weights[i] *= 1.0 / rc_ratio;
        }
    }
    
    // Step 4: Re-normalize
    let new_total: f64 = weights.iter().map(|w| w.abs()).sum();
    for w in &mut weights {
        *w /= new_total.max(1e-10);
    }
    
    // Step 5: Enforce constraints
    apply_constraints(&mut weights, raw_allocations, max_leverage, max_sector_exposure, max_single_name);
    
    // Step 6: Scale to risk budget
    let target_portfolio_vol = 0.15; // 15% annualized target
    let current_portfolio_vol = compute_portfolio_vol(&weights, &covariance.matrix) * 252.0_f64.sqrt();
    let scale = target_portfolio_vol / current_portfolio_vol.max(1e-10);
    for w in &mut weights {
        *w *= scale.min(2.0); // Cap scaling to 2× (avoid excessive leverage)
    }
    
    Ok(weights)
}
```

### 5.4 Correlation Veto

If two assets with the same ternary signal have correlation ρ > 0.90, the system applies a **correlation haircut**:

```rust
/// Reduce combined allocation of highly correlated same-direction positions
fn correlation_haircut(weights: &mut [f64], covariance: &CovarianceMatrix, symbols: &[Symbol]) {
    for i in 0..symbols.len() {
        for j in (i+1)..symbols.len() {
            let rho = covariance.correlation[symbols[i]][symbols[j]];
            if rho > 0.90 && weights[i].signum() == weights[j].signum() && weights[i] != 0.0 && weights[j] != 0.0 {
                // Both same-direction and highly correlated → haircut both
                let haircut = 1.0 - (rho - 0.90) / 0.10;  // Linear from 1.0 at ρ=0.90 to 0.0 at ρ=1.0
                weights[i] *= haircut;
                weights[j] *= haircut;
            }
            else if rho < -0.90 && weights[i].signum() != weights[j].signum() && weights[i] != 0.0 && weights[j] != 0.0 {
                // Opposite directions and highly anti-correlated → potential hedging, allow
                // but check net exposure
            }
        }
    }
}
```

---

## 6. Complete Data Flow

### 6.1 Per-Stock Pipeline

```
Raw Market Data
      ↓
  Signal Computation (RSI, MACD, Volume, etc.)
      ↓
  ┌─────────────────────────────────────┐
  │         TWO PATHS                   │
  │                                     │
  │  Path A: Ternary Gate               │
  │  - Threshold to {-1, 0, +1}        │
  │  - Compute composite trits          │
  │  - Check scale coherence            │
  │  - Check conservation bounds        │
  │  - Output: gate decision            │
  │                                     │
  │  Path B: Continuous Sizer           │
  │  - Normalize raw signals to [0,1]   │
  │  - Compute signal intensity vector  │
  │  - Compute conviction score         │
  │  - Output: intensity + conviction   │
  └──────────┬──────────────────────────┘
             ↓
      Is gate active AND direction != 0?
             ↓
         YES ──→ Raw allocation = conviction × base_weight × direction
         NO  ───→ Position = 0 (skip to next stock)
```

### 6.2 Portfolio-Level Pipeline

```
Per-stock raw allocations (only gate-passed symbols)
      ↓
  Covariance matrix (rolling, all symbols in universe)
      ↓
  Shortlist: gate-passed symbols only
      ↓
  Step 1: Normalize raw allocations to unit sum
      ↓
  Step 2: Compute risk contributions
      ↓
  Step 3: Apply correlation haircuts
      ↓
  Step 4: Constraint enforcement (sector, single-name, leverage)
      ↓
  Step 5: Scale to portfolio volatility target
      ↓
  Step 6: Output final weights
```

### 6.3 Update Schedule

| Component | Frequency | Reason |
|-----------|-----------|--------|
| Ternary Gate | Per-bar (1 min +) | Direction changes happen at bar frequency |
| Signal Intensities | Per-bar | Raw signals update with each bar |
| Conviction Score | Every 6 bars (hourly) | Conviction changes slower than signals |
| Covariance Matrix | End-of-day | Correlation structure is daily |
| Position Rebalance | Every 6 bars or on gate change | Avoid churn on every tick |

---

## 7. Concrete Example Walkthrough

### Setup
- Portfolio: \$100,000
- Vol target: 15% annualized
- Gate passes for: AAPL (+1), MSFT (+1), XOM (−1)

### Per-Stock Data

| Symbol | Gate | Raw Signals | Intensity | Conviction | Base Weight |
|--------|------|-------------|-----------|------------|-------------|
| AAPL | +1 | RSI=25, Volume=3.2×, MACD=positive | 0.72 | 0.75 | 0.60 (vol=25%) |
| MSFT | +1 | RSI=28, Volume=1.8×, MACD=positive | 0.45 | 0.55 | 0.55 (vol=27%) |
| XOM | −1 | RSI=82, Volume=0.3×, MACD=negative | 0.50 | 0.65 | 0.75 (vol=20%) |

### Raw Allocations

| Symbol | Calculation | Raw Allocation |
|--------|-------------|----------------|
| AAPL | 0.75 × 0.60 × (+1) | +0.45 |
| MSFT | 0.55 × 0.55 × (+1) | +0.30 |
| XOM | 0.65 × 0.75 × (−1) | −0.49 |

Normalized (÷ total abs = 1.24): AAPL=0.36, MSFT=0.24, XOM=−0.39

### Correlation Check

| Pair | ρ | Action |
|------|---|--------|
| AAPL↔MSFT | 0.82 | High, but < 0.90 threshold. No haircut, but note concentration. |
| AAPL↔XOM | −0.15 | Low/negative. Natural hedge — OK. |
| MSFT↔XOM | −0.10 | Low/negative. Natural hedge — OK. |

### Risk Contribution Check

Assume portfolio vol = 12% (annualized):

| Symbol | RC | Target RC (1/3) | RC Ratio | Adjustment |
|--------|-----|--------|----------|------------|
| AAPL | 0.42 | 0.33 | 1.27 | Slight reduction |
| MSFT | 0.25 | 0.33 | 0.76 | Slight increase |
| XOM | 0.33 | 0.33 | 1.0 | No adjustment |

After adjustment: AAPL=0.33, MSFT=0.28, XOM=−0.39

### Scale to Portfolio Vol Target

Current portfolio vol = 12%. Target = 15%. Scale factor = 15/12 = 1.25.

Final weights: AAPL=0.41, MSFT=0.35, XOM=−0.49

### Dollar Allocations

| Symbol | Weight | Allocation | Shares (approx) |
|--------|--------|------------|-----------------|
| AAPL | +0.41 | \$41,000 long | ~205 @ \$200 |
| MSFT | +0.35 | \$35,000 long | ~117 @ \$300 |
| XOM | −0.49 | \$49,000 short | ~490 @ \$100 |

### Ternary-Only Counterfactual

Under the pure ternary system (no intensity, no covariance, equal weights):

| Symbol | Trit | Weight | Allocation |
|--------|------|--------|------------|
| AAPL | +1 | 0.33 | \$33,333 long |
| MSFT | +1 | 0.33 | \$33,333 long |
| XOM | −1 | 0.33 | \$33,333 short |

**Comparison:** The pure ternary allocates 2:1 long:short with equal long weights ($66.7K long, $33.3K short). The hybrid system allocates 1.6:1 long:short but with conviction-weighted different long sizes ($76K long, $49K short). The hybrid has:
- **Higher conviction allocation** for AAPL (stronger signal gets more capital)
- **Lower allocation for MSFT** (weaker conviction)
- **Higher allocation for XOM** (sizing based on different risk profile)
- **Correlation awareness** (prevented 82% correlated AAPL+MSFT from dominating)

---

## 8. Edge Cases and Failure Modes

### 8.1 All Signals = 0 (Leminal State)

**Gate:** Direction = 0, is_active = false.
**Sizer:** No allocation generated.
**Behavior:** Portfolio goes to cash / flat.
**Expected frequency:** 40-60% of stocks on any given day.

### 8.2 All Gate-Passing Signals Point Same Direction

**Example:** 10 stocks, all +1.
**Risk:** Sector concentration.
**Mitigation:** Correlation haircut kicks in for highly-correlated pairs. Sector exposure constraint limits total sector weight. Single-name constraint limits any one position.

### 8.3 Conflicting Ternary Signals (Dispersion High)

**Gate:** is_active = false (close_reason: LowConfidence).
**Sizer:** Conviction score will be low → even if gate were open, allocation would be minimal.
**Behavior:** Skips the stock. Returns to cash until signals converge.

### 8.4 Scale Break

**Gate:** is_active = false (close_reason: ScaleBreak).
**Behavior:** Daily says buy, weekly says sell, monthly says neutral. The system trusts the longer timeframe and stays flat until coherence returns.
**Note:** Scale breaks are themselves signals — they often precede regime changes. The system logs them for the veto engine.

### 8.5 Conservation Extreme (All Signals Unanimous)

**Gate:** is_active = false (close_reason: ConservationExtreme).
**Rationale:** Extreme agreement (E(t) near |S|/2) historically precedes mean reversion. The system avoids buying the top or selling the bottom.
**Override:** The veto engine can override this if conviction is extremely high and trend confirms across multiple regimes. Default behavior: stay out for 5 bars, then re-evaluate.

### 8.6 Covariance Matrix Singular or Near-Singular

**Situation:** Two positions have ρ > 0.99 (e.g., same ETF, different share classes).
**Behavior:** The correlation haircut reduces both to near-zero. The portfolio effectively takes a single position across the combined exposure.
**Implementation:** Regularize the covariance matrix before inversion (add εI with ε = 1e-6).

---

## 9. Data Structures Summary

```rust
// ─── Signal Layer ───

struct SignalIntensity {
    raw: f64,          // Raw signal value before quantization
    magnitude: f64,    // Normalized [0, 1]
    direction: Trit,   // Same ternary as gate, but from the raw value
}

struct StockIntensity {
    symbol: Symbol,
    active_signals: BTreeMap<SignalType, SignalIntensity>,
    active_count: usize,
    weighted_magnitude: f64,
    consensus_direction: Trit,
}

// ─── Conviction Layer ───

struct Conviction {
    score: f64,                        // [0, 1]
    components: ConvictionComponents,
}

struct ConvictionComponents {
    signal_unanimity: f64,              // [0, 1]
    scale_coherence: f64,               // [0, 1]
    signal_stability: f64,              // [0, 1]
    raw_strength: f64,                  // [0, 1]
    signal_track_record: f64,           // [0, 1]
}

// ─── Position Sizing Layer ───

struct PreCorrelationAllocation {
    symbol: Symbol,
    direction: Trit,
    conviction: f64,
    base_weight: f64,
    raw_allocation: f64,                // direction * conviction * base_weight
}

struct CovarianceMatrix {
    symbols: Vec<Symbol>,
    matrix: Array2<f64>,                // n×n
    correlation: Array2<f64>,           // n×n
    volatility: HashMap<Symbol, f64>,
    last_updated: DateTime<Utc>,
}

struct RiskBudget {
    target_volatility: f64,             // e.g., 0.15 (15% annualized)
    max_leverage: f64,                  // e.g., 2.0
    max_single_name: f64,               // e.g., 0.20 (20% max per name)
    max_sector_exposure: f64,           // e.g., 0.30 (30% max per sector)
    min_conviction_threshold: f64,      // e.g., 0.30 (skip below this)
}

// ─── Gate Layer ───

struct TernaryGate {
    direction: Trit,
    persistence_probability: f64,
    is_active: bool,
    close_reason: Option<GateCloseReason>,
}

// ─── Final Output ───

struct FinalAllocation {
    symbol: Symbol,
    weight: f64,                        // Portfolio weight [-max_single_name, +max_single_name]
    conviction: f64,                    // For audit trail
    gate: TernaryGate,                  // For audit trail
    risk_contribution: f64,             // Marginal risk contribution
}
```

---

## 10. Relationship to the Veto Engine (Leak #4 Bridge)

The veto engine (SAEP layer, per Leak #4) sits above both the gate and the sizer:

```
Ternary Gate → Continuous Sizer → Covariance Allocation → Veto Engine → Execution
                                    ↑                           ↑
                              Risk Budget              SAEP Patterns
```

The veto engine can:
- **Override** the gate (force flat on a stock regardless of signals)
- **Override** the sizer (force a max allocation cap)
- **Override** the covariance allocation (force a sector cap)
- **Trigger circuit breakers** (force entire portfolio to cash)

This design is compatible with the veto engine being specified in a future triage response.

---

## 11. Implementation Roadmap

### Phase 1: Foundation (Day 1-2)
- [ ] Implement `SignalIntensity` normalization for all signal types in the ternary substrate
- [ ] Implement `Conviction` scoring
- [ ] Implement `PreCorrelationAllocation` computation
- [ ] Wire into existing `TernaryMap`

### Phase 2: Covariance (Day 3-4)
- [ ] Implement `CovarianceMatrix` with 63-day rolling window
- [ ] Implement risk contribution calculation
- [ ] Implement correlation haircut
- [ ] Implement constraint enforcement

### Phase 3: Integration (Day 5-6)
- [ ] Implement the full pipeline: Gate → Sizer → Covariance → Output
- [ ] Add audit logging (every allocation decision is traceable)
- [ ] Add performance attribution (what drove each position's weight?)
- [ ] Unit tests for all formulas

### Phase 4: Validation (Day 7+)
- [ ] Backtest on 5-year historical window
- [ ] Compare: pure ternary vs ternary+continuous vs benchmark (60/40)
- [ ] Walk-forward optimization of conviction weights
- [ ] Stress test: high-correlation environment (2020 COVID)
- [ ] Stress test: low-correlation environment (2022 rate hikes)

---

## Appendix A: Formula Reference

### A.1 Signal Intensity
```python
intensity = (threshold_boundary - raw_value) / threshold_boundary
# Clamped to [0, 1]
# direction = sign of deviation from neutral zone
```

### A.2 Conviction Score
```python
conviction = 0.25 * signal_unanimity
           + 0.20 * raw_strength
           + 0.20 * scale_coherence
           + 0.15 * signal_stability
           + 0.20 * signal_track_record
# Clamped to [0, 1]
```

### A.3 Base Risk Weight
```python
base_weight = target_portfolio_vol / asset_vol
# Where: target_portfolio_vol = 0.15 (15% annualized)
#        asset_vol = annualized volatility of the asset
```

### A.4 Raw Allocation
```python
raw_allocation = direction * conviction * base_weight
# direction = -1, 0, or +1
```

### A.5 Risk Contribution
```python
RC_i = w_i * (Σ @ w)_i / sqrt(w @ Σ @ w)
# Where: w = portfolio weight vector
#        Σ = covariance matrix
#        (Σ @ w)_i = i-th element of matrix-vector product
```

### A.6 Correlation Haircut
```python
if rho > 0.90 and sign_i == sign_j:
    haircut = 1.0 - (rho - 0.90) / 0.10
    w_i *= haircut
    w_j *= haircut
# haircut ranges from 1.0 (at ρ=0.90) to 0.0 (at ρ=1.0)
```

### A.7 Portfolio Vol Target Scaling
```python
scale = target_vol / current_vol
scale = min(scale, 2.0)  # Cap
weights *= scale
```

---

## Appendix B: Comparison to Pure Ternary

| Property | Pure Ternary | Ternary+Continuous Hybrid |
|----------|-------------|--------------------------|
| Signal aggregation | Ternary {-1,0,+1} only | Ternary gate + continuous intensity |
| Position sizing | Equal trit weights | Conviction-weighted × risk-budgeted |
| Conviction | Binary (in or out) | Continuous [0, 1] |
| Cross-asset correlation | None | Full covariance matrix |
| Risk management | None (unconstrained) | Risk budgets, haircuts, constraints |
| Differentiation between strong/mild signals | None (all ±1 same) | Full intensity preservation |
| Scalability | O(n) independent stocks | O(n²) covariance, but still fast for n < 500 |
| Update frequency | Per-bar | Per-bar (gate), hourly (sizer), daily (covariance) |
| Implementation complexity | Low | Medium (well-defined math) |
| Financial validity | Poor (lossy) | Good (standard portfolio theory) |
