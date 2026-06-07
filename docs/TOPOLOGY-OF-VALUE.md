# 🧬 Topology of Value

**How TDA and Ternary Logic Transform Stock Analysis from a List to a Manifold**

---

## The One-Sentence Thesis

A stock is not a time series. It is a **point on a manifold** whose local geometry encodes the interaction of all market forces acting upon it — and the global topology of all stocks reveals the market's hidden structure.

---

## Part I: The Manifold Hypothesis

### 1.1 What Is a Manifold?

A manifold is a space that **locally resembles Euclidean space** but **globally may be curved, twisted, or connected in non-trivial ways**. The surface of Earth is the classic example:

- **Locally**: Your backyard looks flat (2D Euclidean)
- **Globally**: The planet is a sphere (curved, closed, has no boundary)

Market data exhibits the same property. A short window of price action (say, 20 candles) looks like a simple 1D time series. But the full history of a stock lives on a **higher-dimensional, curved manifold** where:

- Price, volume, volatility, and momentum interact nonlinearly
- Regime changes correspond to topological phase transitions
- Support and resistance are not lines on a chart — they are **homology classes** in a persistence diagram

### 1.2 The Embedding

Every stock can be embedded in a high-dimensional observation space:

```
State vector at time t:
s(t) = [price(t), volume(t), volatility(t), RSI(t), 
        MACD(t), bid-ask spread(t), OI call/put(t), 
        sector weight(t), market cap rank(t), ...]
```

This is a point in ℝᵈ (d ~ 10-20). The collection of all points for a stock across time defines a **point cloud** in this space. The manifold hypothesis states that this point cloud lies on or near a **lower-dimensional manifold** (d_effective ~ 2-5).

**The goal of Market Manifold is to learn this manifold's topology and navigate it.**

### 1.3 Why Topology Over Geometry?

Geometry cares about exact distances. Topology cares about **connectedness, holes, voids, and boundaries** — properties that are **invariant under continuous deformation**.

This matters because:

1. **Distances are fragile** — two stocks might be 5% apart in price space but fundamentally identical in topological structure. A 10% price drop might not change the topological class at all.
2. **Topology is robust** — noise, outliers, and small perturbations don't change the homological structure. A $0.01 tick is invisible to persistent homology.
3. **Topology captures shape** — the "shape" of market data (trending, ranging, volatile, compressed, expanding) is a topological property, not a metric one.
4. **Topology is regime-aware** — the same distance metric fails in different regimes. Topological features (Betti numbers) change predictably with regime shifts.

---

## Part II: Persistent Homology for Markets

### 2.1 What Is Persistent Homology?

Persistent homology is a technique from **topological data analysis (TDA)** that computes the topological features of a point cloud at multiple scales. Imagine building a **filtration** — growing balls of radius ε around each data point — and tracking when topological features appear (are "born") and disappear ("die").

```
ε=0:     •    •         •        •    •       (30 disconnected points)
       (all points isolated — H₀ = number of points)

ε=small: •───•         •───•    •───•       (nearby points connect
       (H₀ decreasing as clusters form)       into clusters)

ε=medium: •───•───•───•───•    •───•───•    (clusters merge)
       (H₁ may appear — cycles form)

ε=large: •───•───•───•───•───•───•───•───•  (all connected)
       (H₀ = 1, H₁ = 0, H₂ = 0)
```

A **persistence diagram** plots each feature by its (birth, death) pair. Features that persist over a wide range of ε are considered **topologically significant**. Short-lived features are **noise**.

### 2.2 Betti Numbers

Betti numbers are the core output of persistent homology:

| Betti | What It Counts | Market Meaning |
|-------|---------------|----------------|
| β₀ | Connected components | Number of distinct regime clusters |
| β₁ | 1-dimensional cycles (loops) | Cycle or rotational patterns (e.g., sector rotation, mean reversion bands) |
| β₂ | 2-dimensional voids (cavities) | "Traps" or bounded regions — price can enter but may struggle to escape |
| β₃+ | Higher-dimensional holes | Multi-factor interaction surfaces |

### 2.3 From Betti Numbers to Trading Signals

```rust
/// Topological signature of a stock's current market regime
struct TopologicalSignature {
    /// Connected components — number of distinct regime clusters
    betti_0: u32,
    /// Cycles — rotational patterns (sector rotation, mean reversion)
    betti_1: u32,
    /// Voids — bounded regions (price traps, consolidation zones)
    betti_2: u32,
    /// The filtration epsilon at which the most persistent 
    /// feature dies — global scale of topological structure
    max_persistence: f64,
    /// Hausdorff distance between current and previous signature
    /// — quantifies topological change
    drift: f64,
}

/// Ternary position derived from topological signature
fn topology_to_trit(sig: &TopologicalSignature) -> Trit {
    match (sig.betti_0, sig.betti_1, sig.betti_2, sig.drift) {
        // One regime, no cycles, no voids, stable = ACCUMULATE TREND
        (1, 0, 0, d) if d < 0.1 => Trit::Pos,
        
        // One regime, one cycle, stable = MEAN REVERT
        (1, 1, 0, d) if d < 0.1 => Trit::Neg,  // mean reversion risk
        
        // Multiple regimes, high drift = REGIME SHIFT IN PROGRESS
        (_, _, _, d) if d > 0.5 => Trit::Neg,   // uncertainty high
        
        // Fragmented with voids = AVOID (price trap zone)
        (c, _, v, _) if c > 3 && v > 1 => Trit::Neg,
        
        // Default = HOLD
        _ => Trit::Zero,
    }
}
```

### 2.4 The Persistence Landscape

A persistence landscape is a functional representation of the persistence diagram — it converts the (birth, death) pairs into a sequence of functions λ₁, λ₂, λ₃, ... that are continuous and easier to work with statistically.

```rust
/// Convert persistence diagram to a landscape function
struct PersistenceLandscape {
    /// Lambda-k functions — each is a piecewise-linear function
    lambdas: Vec<PiecewiseLinear<f64>>,
    /// Lp norm of the landscape — total topological energy
    topological_energy: f64,
    /// Hölder continuity — smoothness of the landscape
    smoothness: f64,
}

impl PersistenceLandscape {
    /// L² distance between two landscapes = topological similarity
    fn distance(&self, other: &Self) -> f64;
    
    /// Mean landscape across a sector = sector topology
    fn mean(landscapes: &[&Self]) -> Self;
}
```

---

## Part III: Ternary Logic as the Action Language

### 3.1 Why Ternary?

Financial decision-making is inherently ternary: you buy (+1), sell (−1), or do nothing (0). But most frameworks treat this as a *result* of analysis. Market Manifold uses ternary as the *medium* of analysis.

The three-valued system maps to the three fundamental topological states:

| State | Trit | Topology | Action | Risk Profile |
|-------|------|----------|--------|-------------|
| Bullish | +1 | H₀=1, no cycles, persistent | Accumulate | Low topology-derived risk |
| Bearish | −1 | Voids present, regime fragmenting | Reduce | High — trapped in cavity |
| Neutral | 0 | Multiple regimes, transitional | Hold / Wait | Ambiguous topology |

### 3.2 Ternary Scale Breaks

Ternary signals operate at multiple time scales, and they interact through **scale breaks** — moments where the short-term topology diverges from the long-term topology:

```rust
struct TernaryScaleBreak {
    /// Trit at daily scale
    daily: Trit,
    /// Trit at weekly scale
    weekly: Trit,
    /// Trit at monthly scale
    monthly: Trit,
    /// When all three disagree → maximum ambiguity
    consensus: Consensus,
}

enum Consensus {
    /// All scales agree → high conviction
    Aligned(Trit),
    /// Two scales agree, one disagrees → moderate
    TwoOfThree(Trit),
    /// All disagree → regime shift likely
    Fractured,
}
```

A scale break — where daily = +1, weekly = 0, monthly = −1 — is itself a signal. It suggests **short-term momentum against the long-term trend**, which is precisely the topological condition for a mean-reversion opportunity (H₁ appears).

### 3.3 The Ternary Substrate

Following the DOC_STANDARD, each {−1, 0, +1} mapping must be explicit:

| Signal | +1 | 0 | −1 |
|--------|----|----|----|
| RSI | < 30 (oversold → bullish) | 30-70 (neutral) | > 70 (overbought → bearish) |
| Volume | > 2x avg (conviction) | 0.5-2x avg (normal) | < 0.5x avg (apathy) |
| Betti drift | < 0.1 (stable) | 0.1-0.4 (transitional) | > 0.4 (fragmented) |
| Sentiment | Bullish skew | Mixed / neutral | Bearish skew |
| Options flow | Call skew + put wash | Balanced | Put skew + call wash |
| Sector correlation | In-line with sector | Decoupling | Anti-correlated |

**Conservation law:** The sum of all trits for a stock (across signals) must remain bounded between −N and +N. When the absolute sum approaches N, the stock is at a topological extreme — expect mean reversion.

---

## Part IV: Worked Example — $AAPL, $MSFT, $GOOGL Sector Topology

### 4.1 Setup

Three technology stocks, observed over a 90-day window. Each stock is embedded in a 10-dimensional state space and projected onto a 3D ternary manifold.

### 4.2 Individual Topology

```
$AAPL:  H₀=2, H₁=1, H₂=0   → Two regimes with one rotational pattern
                                (Bullish trend + consolidation loop)
        Topological energy:    0.87 (high — strong structure)
        Effective position:    +1 (Accumulate)

$MSFT:  H₀=1, H₁=0, H₂=0   → Single regime, no cycles
                                (Steady uptrend, no rotation)
        Topological energy:    0.42 (moderate — simpler structure)
        Effective position:    +1 (Accumulate, lower conviction)

$GOOGL: H₀=3, H₁=0, H₂=1   → Three regimes with one void
                                (Fragmented — price trap zone)
        Topological energy:    1.24 (high — but fragmented)
        Effective position:    0 (Hold — ambiguous)
```

### 4.3 Sector-Level Topology

When we compute the **joint persistence diagram** of all three stocks:

```
Sector Technology:
  H₀=3           → Three distinct clusters (each stock is its own regime zone)
  H₁=2           → Two rotational patterns (sector rotation between AAPL-MSFT and MSFT-GOOGL)
  H₂=0           → No sector-wide voids (no sector-level price traps)
  
  Cross-Betti:   β_cross = 2 (the H₁ cycles connect stocks, not isolate them)
  Topological covariance: 0.67 (moderate — stocks are connected but not identical)
```

### 4.4 Signals Generated

```toml
[room.AAPL]
position = "+1"
conviction = 0.78
topological_basis = "H₀=2, H₁=1 stable regime with rotational pattern"
reflex_fired = "bullish-trend-follow"
spline_sent = true

[room.MSFT]
position = "+1"
conviction = 0.55
topological_basis = "H₀=1, H₁=0 single regime, simpler structure"
reflex_fired = "none (confidence < 0.60 threshold)"
spline_sent = false

[room.GOOGL]
position = "0"
conviction = 0.82
topological_basis = "H₀=3, H₁=0, H₂=1 fragmented with void — price trap"
reflex_fired = "avoid-void-region"
spline_sent = true

[sector]
id = "Technology"
topological_energy = 1.87
cross_betti = 2
recommendation = "Overweight sector, rotate from GOOGL into AAPL/MSFT"
```

### 4.5 The Baton

The `$GOOGL` room sends a baton to the `$AAPL` room:

```
Baton type: SPLINE_SHARE
From: rooms/GOOGL
To: rooms/AAPL, rooms/MSFT, fleet/hub
Spline: 
  "When H₂=1 appears in a large-cap tech stock within a sector where 
   H₁=2 is cross-sector, the void typically resolves within 5-7 sessions 
   as a breakout. GOOGL H₂=1 is not a trap — it's a compression zone 
   before expansion. Re-evaluate position at next sector sync."
Confidence: 0.65 (pending verification)
```

The `$AAPL` room evaluates this spline through its veto engine. If the pattern matches prior observations (e.g., `$AMZN` exhibited the same H₂→breakout pattern in Q1), the confidence increases and the spline is promoted to a fleet-level reflex.

---

## Part V: Advanced Topology

### 5.1 Wasserstein Distance Between Market States

The Wasserstein-1 (Earth Mover's) distance between two persistence diagrams quantifies how much topological "work" is required to transform one market state into another:

```rust
fn wasserstein_distance(dgm_a: &PersistenceDiagram, dgm_b: &PersistenceDiagram) -> f64;

// Market interpretation:
// d < 0.1 :  Same regime, noise-level change
// 0.1-0.3 :  Regime evolution (normal drift)
// 0.3-0.6 :  Regime transition (significant)
// > 0.6   :  Regime collapse / phase transition (extreme)
```

A portfolio manager could monitor the Wasserstein distance between today's sector topology and yesterday's. When it exceeds 0.6, it's time to rebalance — not because of price targets, but because the **topology of the sector has fundamentally changed**.

### 5.2 Topological Mixing

When two stocks' persistence diagrams share significant features (Wasserstein distance < 0.2), they can be said to be **topologically mixed** — their market structures are entangled. This is stronger than correlation:

- **Correlation**: $r = 0.80$ means linear relationship
- **Topological mixing**: WD < 0.2 means shared homology structure

Two stocks can be uncorrelated but topologically mixed (nonlinear relationship) or correlated but topologically distinct (linear but structurally different).

```rust
/// Detect topological mixing between two stocks
fn topological_mixing(
    dgm_a: &PersistenceDiagram, 
    dgm_b: &PersistenceDiagram
) -> MixingResult {
    let wd = wasserstein_distance(dgm_a, dgm_b);
    let shared_features = count_shared_persistent_features(dgm_a, dgm_b);
    
    MixingResult {
        wasserstein: wd,
        shared_features,
        mixed: wd < 0.2 && shared_features > 3,
        mixing_type: if wd < 0.1 { "strong" }
                     else if wd < 0.2 { "moderate" }
                     else { "none" }
    }
}
```

### 5.3 Topological Momentum

Just as price momentum measures the rate of price change, **topological momentum** measures the rate of topological change:

```rust
fn topological_momentum(
    history: &[PersistenceDiagram],
    window: usize  // e.g., 20 sessions
) -> f64 {
    // Compute the total topological drift over the window
    let mut total_drift = 0.0;
    for i in 1..window {
        total_drift += wasserstein_distance(&history[i-1], &history[i]);
    }
    total_drift / window as f64
}

// Market interpretation:
// Low momentum (< 0.05/session):  Stable regime — trend-follow
// High momentum (> 0.15/session): Topological flux — avoid
// Increasing momentum:            Regime change approaching
```

---

## Part VI: Practical Applications

### 6.1 Portfolio Construction via Topological Optimization

Instead of optimizing for mean-variance (Markowitz), optimize for **topological diversity**:

```rust
fn topological_portfolio(
    universe: &[StockTopology],
    target: PortfolioConstraints
) -> Portfolio {
    // For each candidate portfolio:
    // 1. Compute joint persistence diagram of all holdings
    // 2. Maximize H₀ (diversification = many disconnected regime clusters)
    // 3. Minimize H₁ (avoid rotational traps that concentrate risk)
    // 4. Set H₂ = 0 (no price trap zones in the portfolio topology)
    // 5. Subject to: max 30% in any H₁ cycle, max 15% in any H₂ void
}
```

### 6.2 Regime Detection

Regime changes are topological phase transitions. Monitor the Betti number vector (β₀, β₁, β₂) and flag changes:

| Regime | H₀ | H₁ | H₂ | Topological Signature |
|--------|----|----|----|----------------------|
| Strong Trend | 1 | 0 | 0 | Single connected component |
| Range Bound | 1 | 1 | 0 | One component, one cycle |
| Sector Rotation | 2-3 | 1-2 | 0 | Multiple components with interconnecting cycles |
| Fragmented (Crisis) | 4+ | 0 | 1-2 | Many isolated components with voids |
| Compression (Pre-Breakout) | 1 | 0 | 0 | Single component, low topological energy |
| Expansion (Post-Breakout) | 1-2 | 0-1 | 0 | Increasing topological energy |

### 6.3 Reflex Library

The following reflexes are pre-defined for topological analysis:

| Reflex Name | Trigger | Action | Confidence |
|-------------|---------|--------|------------|
| `void-detect` | H₂ > 0 in room | Alert: price trap zone detected, reduce position | 0.80 |
| `regime-merge` | H₀ drops from 3 to 1 in < 5 sessions | Alert: convergence detected, adjust position | 0.70 |
| `cycle-formation` | H₁ goes from 0 to 1 | Alert: range forming, prepare for mean reversion | 0.65 |
| `sector-sync` | Cross-Betti drops by > 50% | Sector decoupling — review inter-stock topology | 0.75 |
| `topo-drift` | Topological momentum > 0.15/session | Regime change in progress — reduce exposure | 0.85 |
| `compression-expansion` | Topological energy < 0.3 then increases 2x | Breakout imminent — monitor for confirmation | 0.60 |

---

## Part VII: The Mathematical Foundations

### 7.1 Persistent Homology (Formal)

Given a point cloud $X \subset \mathbb{R}^d$, construct the Vietoris–Rips complex $VR_\varepsilon(X)$ for a sequence of $\varepsilon = \varepsilon_1 < \varepsilon_2 < \dots < \varepsilon_n$. The inclusion $VR_{\varepsilon_i}(X) \hookrightarrow VR_{\varepsilon_{i+1}}(X)$ induces maps on homology groups $H_k(VR_{\varepsilon_i}) \to H_k(VR_{\varepsilon_{i+1}})$. A persistent homology class is born at $\varepsilon_{\text{birth}}$ and dies at $\varepsilon_{\text{death}}$, producing a persistence pair (b, d).

The **persistence diagram** is the multiset of all such pairs, plus the diagonal (counted with infinite multiplicity).

### 7.2 Ternary Embedding

The mapping from continuous $x \in \mathbb{R}^d$ to $\{-1, 0, +1\}$ is:

$$f(x_i) = \begin{cases}
+1 & |x_i - \mu_i| > \sigma_i \cdot \theta_+ \\
0  & \sigma_i \cdot \theta_- \leq |x_i - \mu_i| \leq \sigma_i \cdot \theta_+ \\
-1 & |x_i - \mu_i| < \sigma_i \cdot \theta_- \\
\end{cases}$$

Where $\mu_i$ and $\sigma_i$ are the rolling mean and standard deviation of dimension $i$, and $\theta_-, \theta_+$ are thresholds (typically $\theta_- = 0.5, \theta_+ = 1.0$).

### 7.3 Topological Energy

The total topological energy of a stock is:

$$E_{\text{topo}} = \sum_{k=0}^{D} \sum_{j} (d_j^{(k)} - b_j^{(k)}) \cdot w_k$$

Where $(b_j^{(k)}, d_j^{(k)})$ is the $j$th persistence pair in dimension $k$, and $w_k$ is a dimension-dependent weight (typically $w_0 = 1, w_1 = 2, w_2 = 4$ to reflect the increasing complexity of higher-dimensional features).

---

## References

1. Edelsbrunner, Letscher, Zomorodian (2002). "Topological Persistence and Simplification."
2. Carlsson (2009). "Topology and Data."
3. Bubenik (2015). "Statistical Topological Data Analysis using Persistence Landscapes."
4. Chazal, Berthelot, et al. (2013). "Persistence-based clustering in Riemannian manifolds."
5. Gidea, Katz (2018). "Topological data analysis of financial time series: Landscapes of crashes."
6. Ternary Types — SuperInstance [0x01] — The foundational trit arithmetic

---

> *"The market is not a random walk. It is a manifold with topology, and every stock is a traveler on that manifold. Learn its shape, and you stop guessing.*"
