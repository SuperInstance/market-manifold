# TRIAGE-2: Hardened TDA Pipeline for Financial Data

**Addressing Critical Leak #2 — Persistent Homology Assumption Violations**

> *"TDA was developed for point clouds from a fixed, low-noise manifold. Financial data satisfies none of the assumptions: non-stationary, extreme noise, unknown embedding, streaming recomputation cost."* — Officer-Critic

---

## Executive Summary

The Critic's assessment is correct: applying classical persistent homology to raw financial data is methodologically unsound without modifications. This document designs a **hardened TDA pipeline** that acknowledges each assumption violation and defends against it with principled countermeasures.

The pipeline is not "TDA on raw prices" — it is **TDA on a stabilized, denoised, regime-adapted embedding space**, with incremental computation to handle streaming data.

---

## 1. Assumption Violation Matrix

| # | TDA Assumption | Market Reality | Countermeasure | Confidence |
|---|---------------|----------------|---------------|------------|
| 1 | Stationary manifold | Regime shifts every 3–8 weeks | Adaptive window + regime detector | High |
| 2 | IID/Exchangeable points | Autocorrelated, heteroskedastic | Theiler window + variance stabilization | High |
| 3 | High signal-to-noise | SNR ~0.2 for daily returns | Spectral denoising + topological signal extraction | Medium |
| 4 | Known embedding parameters | (d, τ) not known a priori | Mutual info + FNN + ensemble across parameters | Medium |
| 5 | Offline computation | Requires streaming inference | Incremental homology via zigzag + landmarks | High |

---

## 2. Pipeline Architecture

```
Raw Data → ┌──────────────────────────────────────────────┐
           │  Denoising & Stabilization                   │
           │  • Wavelet threshold (VisuShrink)            │
           │  • Variance stabilization (Yeo-Johnson)      │
           │  • Theiler window for temporal decorrelation │
           └──────────────────┬───────────────────────────┘
                              ↓
           ┌──────────────────────────────────────────────┐
           │  Regime Detection & Window Selection          │
           │  • Online change-point detection (PELT)       │
           │  • Adaptive window (min 20, max 252 bars)     │
           │  • On regime change: flush, restart window    │
           └──────────────────┬───────────────────────────┘
                              ↓
           ┌──────────────────────────────────────────────┐
           │  Embedding (Takens' Theorem)                  │
           │  • τ via mutual information first minimum     │
           │  • d via false nearest neighbors (FNN)        │
           │  • Ensemble over (d±1, τ±5) for robustness    │
           └──────────────────┬───────────────────────────┘
                              ↓
           ┌──────────────────────────────────────────────┐
           │  Persistent Homology                          │
           │  • Vietoris-Rips on landmark subset            │
           │  • Zigzag homology for incremental update     │
           │  • Bootstrap confidence intervals on Betti    │
           └──────────────────┬───────────────────────────┘
                              ↓
           ┌──────────────────────────────────────────────┐
           │  Feature Extraction                            │
           │  • Persistence landscapes (Lipschitz-stable)   │
           │  • Persistence images (vector representation)  │
           │  • Betti curves with confidence bands          │
           └──────────────────────────────────────────────┘
```

---

## 3. Countermeasure Specifications

### 3.1 Denoising & Stabilization

**Problem:** Financial price data has microstructure noise (bid-ask bounce, stale prices) at high frequencies and heavy-tailed return distributions.

**Solution:** Multi-stage preprocessing:

```
x(t) = log(p(t)) - log(p(t-1))      # Log returns
x'(t) = wavelet_denoise(x(t), thr='VisuShrink', wavelet='db4')
y(t) = yeo_johnson(x'(t), λ=0.5)     # Variance stabilization
z(t) = y(t) - theiler_mean(y, W=5)   # Local mean subtraction (W = Theiler window)
```

**Theiler Window:** A critical but often-omitted step. TDA assumes exchangeable points. Financial returns are autocorrelated at short lags. The Theiler window excludes points closer than W in time from being connected in the Vietoris-Rips complex. This prevents **temporal autocorrelation from masquerading as topological structure**.

**Implementation:**

```rust
/// Apply Theiler window to distance matrix: set distances between
/// points closer than W in time to infinity (excluded from VR complex).
fn apply_theiler_window(distance_matrix: &mut Array2<f64>, w: usize) {
    for i in 0..distance_matrix.nrows() {
        for j in 0..distance_matrix.ncols() {
            if i != j && (i as isize - j as isize).abs() <= w as isize {
                distance_matrix[[i, j]] = f64::INFINITY;
            }
        }
    }
}
```

### 3.2 Regime Detection & Adaptive Window

**Problem:** TDA assumes the point cloud comes from a single, stationary distribution. Markets regime-switch.

**Solution:** Online change-point detection using the PELT (Pruned Exact Linear Time) algorithm on a rolling basis.

**Window adaptation logic:**

```rust
enum RegimeState { Bull, Bear, Sideways, Transition }

struct AdaptiveWindow {
    min_bars: usize,    // 20 (1 month daily)
    max_bars: usize,    // 252 (1 year daily)
    current_bars: usize, // grows until regime change detected
    state: RegimeState,
}

impl AdaptiveWindow {
    fn ingest(&mut self, return_: f64) -> Option<RegimeChange> {
        // PELT-based change point detection
        // On detection: emit RegimeChange, reset current_bars to min_bars
        // On no detection: grow current_bars up to max_bars
    }
}
```

**Key principle:** When a regime change is detected, the TDA window resets. This means homology is **always computed within a single regime** — we never mix bull and bear points in the same persistence diagram.

### 3.3 Embedding Parameter Selection

**Problem:** Takens' embedding requires (d, τ) but these are not known for financial data. Different (d, τ) produce different persistence diagrams.

**Solution:** Principled selection via:
1. **τ**: First minimum of the mutual information function (not autocorrelation — MI captures nonlinear dependence)
2. **d**: False Nearest Neighbors (FNN) algorithm with tolerance
3. **Ensemble robustness**: Compute persistence diagrams for (d±1, τ±5) and take the **intersection of persistent features** — features that appear across all embeddings are real; features that appear in only one are artifacts.

**Implementation:**

```rust
struct EmbeddingParams { d: usize, tau: usize }

fn select_embedding(series: &[f64]) -> EmbeddingParams {
    let tau = mutual_information_first_minimum(series, max_lag=50);
    let d = false_nearest_neighbors(series, tau, threshold=0.01);
    EmbeddingParams { d, tau }
}

fn ensemble_persistence(series: &[f64], params: &EmbeddingParams) -> PersistenceDiagram {
    let mut diagrams = Vec::new();
    for d in (params.d-1)..=(params.d+1) {
        for tau in (params.tau-5)..=(params.tau+5) {
            let embedding = takens_embedding(series, d, tau);
            diagrams.push(compute_persistence(&embedding));
        }
    }
    // Take the intersection of features that persist across >80% of embeddings
    PersistenceDiagram::ensemble_intersection(&diagrams, threshold=0.8)
}
```

### 3.4 Incremental/Streaming Homology

**Problem:** Full recomputation of persistent homology at every new tick is computationally infeasible (720k recomputes/day for 500 stocks at 1-min resolution).

**Solution:** Two-tier approach:

**Tier 1: Landmark-based approximation** (every tick)
- Maintain a landmark subset of ~200 points (vs full ~130k window)
- Use max-min landmark selection for representative coverage
- Compute PH on landmarks only — O(n·k²) vs O(n³) where n=window_size, k=200

**Tier 2: Full recomputation** (every N ticks or on regime change)
- Full persistence on the complete window
- Used to recalibrate the landmark approximation

```rust
struct StreamingHomology {
    landmarks: Vec<Point>,     // Max 200 landmark points
    window_buffer: Vec<Point>, // Full window (up to ~130k)
    tick_counter: u64,
    full_compute_interval: u64, // Every 1000 ticks
}

impl StreamingHomology {
    fn ingest(&mut self, point: Point) -> PartialHomologyResult {
        self.window_buffer.push(point);
        self.tick_counter += 1;
        
        // Landmark-based approximation (every tick)
        self.update_landmarks(point);
        let fast_result = self.compute_landmark_persistence();
        
        // Full recomputation (periodic + on regime change)
        if self.tick_counter % self.full_compute_interval == 0 {
            let full_result = self.compute_full_persistence();
            self.calibrate_landmarks(full_result, fast_result);
        }
        
        fast_result
    }
}
```

### 3.5 Bootstrap Confidence Intervals

**Problem:** TDA produces deterministic output from stochastic data. Without confidence intervals, we can't distinguish signal from noise.

**Solution:** Bootstrapped persistence:

```rust
fn bootstrap_persistence(points: &[Point], n_bootstrap: usize) -> BettiCurveWithCI {
    let mut betti_curves = Vec::new();
    for _ in 0..n_bootstrap {
        let sample: Vec<Point> = points.choose_multiple(&mut thread_rng(), points.len());
        let diagram = compute_persistence(&sample);
        betti_curves.push(extract_betti_curve(&diagram, dim=1));
    }
    
    // Compute pointwise median and 95% CI across bootstrap samples
    BettiCurveWithCI {
        median: pointwise_median(&betti_curves),
        lower_ci: pointwise_percentile(&betti_curves, 0.025),
        upper_ci: pointwise_percentile(&betti_curves, 0.975),
    }
}
```

**Usage:** A topological signal is only considered "real" if its persistence exceeds the 95% bootstrap confidence band. If a 1-cycle persists to ε=0.5 but the CI upper bound is 0.3, it's noise.

---

## 4. Computation Budget

| Component | Cost per Stock | 500 Stocks | Schedule |
|-----------|---------------|------------|----------|
| Denoising (wavelet) | O(n) | O(500n) | Every tick |
| Regime detection (PELT) | O(n) | O(500n) | Every tick |
| Embedding selection | O(n²) | O(500n²) | Every 20 ticks (reuse params) |
| Landmark PH (fast) | O(n·k²) k=200 | O(500·n·40k) | Every tick |
| Full PH (recalibration) | O(n³) | O(500·n³) | Every 1000 ticks (~weekly) |
| Bootstrap (stats) | O(n_boot · n³) | None — only when needed | On-demand |

**Estimated wall-clock per tick (500 stocks, 252-bar window):**
- Fast path (landmarks): ~50ms
- Full recompute: ~5s (every 1000 ticks, ~weekly)
- Bootstrap: ~30s (on-demand only)

---

## 5. What TDA Can and Cannot Tell Us

### Valid Uses
- **Structural similarity detection**: Comparing persistence landscapes of two stocks over the same window is a robust measure of behavioral similarity
- **Regime change confirmation**: A shift in persistence landscape is a lagging confirmation of a regime change detected by other methods
- **Dimensionality estimation**: The embedding dimension d provides insight into the complexity of factors driving a stock

### Invalid Uses (Not Supported)
- **Price prediction at tick resolution**: TDA operates on windows of 20+ bars. It cannot predict the next tick
- **Isolated signal extraction**: A single H₁ cycle at ε=0.3 is meaningless without bootstrap confidence
- **Cross-asset causal inference**: TDA reveals correlation in state space, not causation in fundamental drivers

---

## 6. Validation Strategy

Before any TDA-derived signal is used in production:

1. **Synthetic data test**: Generate data with known topology (e.g., a circle + noise). Verify the pipeline recovers H₁=1 at the correct scale
2. **Random shuffle test**: Shuffle returns and recompute. Topological features should disappear (or at least change significantly)
3. **Historical backtest**: Compute persistence diagrams on 10 years of SPY data. Do Betti numbers change at known regime boundaries (2008, 2020, 2022)?
4. **Benchmark vs naive**: Does the TDA-derived signal outperform a simple 50-day SMA crossover on out-of-sample data?

Pipeline is not ready for production until all four validations pass.
