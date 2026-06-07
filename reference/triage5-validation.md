# TRIAGE-5: Validation Framework

**Addressing Foundational Gap — Zero Evidence of Predictive Power**

> *"The architecture has zero evidence of predictive power. No backtesting framework, no validation, no benchmarks. If the topology can't beat a 50-day SMA, it doesn't matter how elegant the mathematics is."* — Officer-Critic

---

## Executive Summary

The Market Manifold has no empirical foundation. Before any code is deployed near real capital, the topological signals must demonstrate predictive power over a benchmark, across market regimes, and with statistical significance.

This document defines the minimal validation framework required before the framework can be considered "operational."

---

## 1. Validation Hierarchy

```
Synthetic Validation     ─→ Does TDA recover known topology?
    ↓
Randomized Benchmark     ─→ Is the signal better than random?
    ↓
Historical Backtest     ─→ Does it work on real historical data?
    ↓
Walk-Forward Analysis   ─→ Does it work out-of-sample?
    ↓
Regime Sensitivity      ─→ Does it work in all market conditions?
    ↓
Live Paper Trading      ─→ Does it work in real time?
```

Each level gates the next. No skipping.

---

## 2. Level 1: Synthetic Data Validation

**Purpose:** Verify that the TDA pipeline can recover known topological structure from data.

### Protocol

Generate synthetic point clouds with known homology:

```rust
fn generate_known_topology(case: SyntheticCase) -> Vec<[f64; 2]> {
    match case {
        // A circle: should produce H₁=1
        SyntheticCase::Circle => {
            let angles: Vec<f64> = (0..200).map(|i| 2.0 * PI * i as f64 / 200.0).collect();
            angles.iter().map(|θ| [θ.cos() + noise(), θ.sin() + noise()]).collect()
        }
        // Two clusters: should produce H₀=2, no H₁
        SyntheticCase::TwoClusters => {
            let c1: Vec<[f64; 2]> = (0..100).map(|_| [rand::thread_rng().gen_range(0.0..1.0), rand::thread_rng().gen_range(0.0..1.0)]).collect();
            let c2: Vec<[f64; 2]> = (0..100).map(|_| [rand::thread_rng().gen_range(5.0..6.0), rand::thread_rng().gen_range(5.0..6.0)]).collect();
            c1.into_iter().chain(c2).collect()
        }
        // A sphere surface: should produce H₂=1
        SyntheticCase::Sphere => { /* ... */ }
    }
}
```

**Pass Criteria:** The pipeline must recover Betti numbers within ±0.5 of expected for each case, at noise levels up to SNR=0.5.

### Noise Stress Test

Gradually increase noise until the pipeline fails:

| Noise Level (σ) | Expected H₁ | Recovered H₁ | Pass? |
|-----------------|-------------|--------------|-------|
| 0.01 | 1 | — | — |
| 0.05 | 1 | — | — |
| 0.10 | 1 | — | — |
| 0.25 | 1 | — | — |
| 0.50 | 1 | — | — |

**Failure point documentation:** At what noise level does the topological signal disappear?

---

## 3. Level 2: Randomization Benchmark

**Purpose:** Verify that topological signals are not spurious.

### Protocol

For a real stock (e.g., SPY, 10 years of daily data):

1. Compute the TDA-derived signal (e.g., Betti-1 count over rolling window)
2. Generate 1000 shuffled datasets (random permutation of returns)
3. Compute the same signal on each shuffled dataset
4. Does the real signal differ from the shuffled distribution?

### Statistical Test

```rust
fn randomization_test(real_signal: &[f64], n_permutations: usize) -> f64 {
    let mut n_extreme = 0;
    for _ in 0..n_permutations {
        let shuffled = shuffle(&real_returns); // permute returns
        let null_signal = compute_tda_signal(&shuffled);
        if null_signal.abs() >= real_signal.abs() {
            n_extreme += 1;
        }
    }
    // p-value: proportion of permutations with more extreme signal
    n_extreme as f64 / n_permutations as f64
}
```

**Pass Criteria:** p < 0.01 (the real topological signal is stronger than 99% of random permutations).

---

## 4. Level 3: Historical Backtest

**Purpose:** Measure predictive power on real historical data.

### Protocol

**Data Requirements:**
- Minimum 10 years of daily OHLCV data
- Minimum 500 stocks (SP500 universe ideally)
- Include 2008, 2020, 2022 crises

**Signal-to-Portfolio Mapping:**
```
Ternary signal +1 → Long (1.0x weight)
Ternary signal 0  → No position
Ternary signal -1 → Short (-1.0x weight)

Portfolio: equal-weighted among active positions
Rebalance: daily
Transaction cost: 0.10% per side
```

### Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Annualized return | > benchmark | Core value proposition |
| Sharpe ratio (0% risk-free) | > 0.8 | Risk-adjusted performance |
| Max drawdown | < benchmark | Risk management |
| Win rate | > 55% | Signal consistency |
| Average holding period | > 5 days | Not overtrading |
| Turnover (annual) | < 1000% | Transaction cost control |
| Hit ratio (by regime) | — | Regime sensitivity |

### Benchmark Suite

The system must outperform ALL of these on out-of-sample data:

| Benchmark | Description | Why It Matters |
|-----------|-------------|----------------|
| **Buy & Hold SPY** | Market return | Minimum viable product |
| **50-day SMA crossover** | Simple momentum | TDA must beat naive trend |
| **Equal-weight sector rotation** | Best sector monthly | TDA must beat simple diversification |
| **Random ternary classifier** | Coin flip with ±1 output | TDA must beat random signal |
| **Risk parity** | Volatility-weighted allocation | TDA must beat risk management alone |

---

## 5. Level 4: Walk-Forward Analysis

**Purpose:** Test out-of-sample without look-ahead bias.

### Protocol

```
Training Window (252 bars) → Test Window (63 bars)
              ↓
         Slide forward by 63 bars
              ↓
         Repeat 40 times (10 years)
```

Each test window is completely out-of-sample. The TDA pipeline parameters are fixed at training time and not updated during the test window.

```rust
struct WalkForwardResult {
    period: DateRange,
    in_sample_sharpe: f64,
    out_of_sample_sharpe: f64,
    decay: f64,  // out_of_sample / in_sample
}
```

**Pass Criteria:**
- Median out-of-sample Sharpe > 0.5
- Decay ratio > 0.5 (out-of-sample is at least 50% of in-sample performance)

---

## 6. Level 5: Regime Sensitivity

**Purpose:** Know where the system works and where it fails.

### Regime Classification

Classified using the CBOE Volatility Index (VIX):

| Regime | VIX Range | Expected Frequency | TDA Performance |
|--------|-----------|-------------------|-----------------|
| Low Vol | < 15 | ~25% | — |
| Normal | 15–25 | ~50% | — |
| High Vol | 25–40 | ~20% | — |
| Crisis | > 40 | ~5% | — |

Also test:
- **Bull market** (SPY > 200-day SMA)
- **Bear market** (SPY < 200-day SMA)
- **Sideways market** (SPY within ±5% of 200-day SMA)

**Pass Criteria:** The system must have positive Sharpe in at least 3 of 4 volatility regimes and 2 of 3 directional regimes. Zero regimes with Sharpe < -1.0.

---

## 7. Level 6: Live Paper Trading

**Purpose:** Test in real-time without real capital.

### Protocol
- 6 months minimum
- Real-time data feed (15-min delayed or better)
- Same signal and position sizing as production
- Daily reconciliation against benchmarks
- Weekly review of TDA pipeline parameters
- Monthly re-estimation of embedding parameters

**Failure Criteria (Paper Trading Phase):**
- Drawdown > 25% from peak → pause and review
- 3 consecutive months of negative returns → pause and review
- Sharpe < 0.0 over entire period → do not go live

---

## 8. Validation Dashboard

```rust
/// Single source of truth for validation status
struct ValidationStatus {
    synthetic: PassStatus,     // Pass / Fail / NotRun
    randomization: PassStatus,
    historical: PassStatus,
    walk_forward: PassStatus,
    regime_sensitivity: PassStatus,
    paper_trading: PassStatus,
    
    // Key metrics across all stages
    metrics: HashMap<String, MetricSnapshot>,
}

impl ValidationStatus {
    fn is_deployable(&self) -> bool {
        self.synthetic == Pass
        && self.randomization == Pass
        && self.historical == Pass
        && self.walk_forward == Pass
        && self.regime_sensitivity == Pass
    }
}
```

**The system is not deployable near real capital until all 6 levels pass.**

---

## 9. Honest Admission

It is entirely possible that the topological signals derived from the Market Manifold have **zero predictive power**. TDA is an exploratory tool, not a forecasting engine. The validation framework is designed to surface this possibility early — before time is wasted on production engineering.

If the TDA signals can't beat a 50-day SMA crossover after Level 3 validation, the topological approach to the Market Manifold should be **abandoned** in favor of simpler methods (momentum, mean reversion, factor models).

The elegance of the topology is not a substitute for the rigor of the backtest.
