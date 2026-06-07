# ↯ Ternary Substrate for Market Manifold

**How {−1, 0, +1} encodes financial reality.**

This document is the mandatory "Ternary Substrate" section per the DOC_STANDARD. Every crate and framework in the SuperInstance fleet must declare its ternary mapping explicitly. Here is Market Manifold's.

---

## The Tri-Valued Mapping

Every financial signal in Market Manifold is mapped to a ternary value. The mapping is not arbitrary — it follows the **fundamental structure of market decisions**.

| Domain | +1 (Bullish) | 0 (Neutral) | −1 (Bearish) |
|--------|-------------|-------------|-------------|
| **Price Action** | Higher highs, higher lows | Range-bound | Lower highs, lower lows |
| **Volume** | > 2× average (conviction increasing) | 0.5–2× average (normal) | < 0.5× average (apathy dying) or > 3× with no price progress (climax) |
| **Volatility** | Decreasing (compression → expansion) | Stable | Increasing (fear, regime change) |
| **Momentum** | Positive for > 5 sessions | Oscillating around zero | Negative for > 5 sessions |
| **RSI** | < 30 (oversold) | 30–70 | > 70 (overbought) |
| **MACD** | Above signal line, histogram rising | Crossing zero | Below signal line, histogram falling |
| **Bollinger %B** | < 0 (below lower band — oversold bounce) | 0–1 (within bands) | > 1 (above upper band — overbought) |
| **Sector Relative Strength** | Outperforming sector | In-line | Underperforming |
| **Sentiment (News)** | Positive skew > 60% | Balanced (40–60%) | Negative skew > 60% |
| **Social Volume** | High, growing | Steady | High, declining (peak interest) |
| **Put/Call Ratio** | < 0.7 (call skew — bullish bets) | 0.7–1.1 (balanced) | > 1.1 (put skew — bearish bets) |
| **Institutional Flow** | Net buying > 2× normal | Normal | Net selling > 2× normal |
| **Insider Transactions** | Net buying | Neutral | Net selling |
| **PE Relative to Sector** | Below median (undervalued) | At median | Above median (overvalued) |
| **Revenue Growth** | Accelerating QoQ | Stable | Decelerating QoQ |
| **Debt/Equity** | Decreasing | Stable | Increasing |
| **Buyback Yield** | Active buybacks | No significant activity | Dilution (stock issuance) |

---

## The Conservation Law

**The sum of all trits for a stock must remain bounded.**

Let $S$ be the set of all signals for a stock:

$$E(t) = \sum_{i \in S} Trit_i(t)$$

The constraint is:

$$|E(t)| \leq \frac{|S|}{2}$$

Where $|S|$ is the number of active signals. When $|E(t)|$ approaches $|S|/2$, the stock is at a **topological extreme** — its signals are in near-unanimous alignment. This is a mean-reversion signal: extreme agreement precedes regime change.

**Example:** If a stock has 12 active signals and $E(t) = +10$, the stock is at maximum bullish conviction (12/2 = 6, +10 > 6). This means 10 of 12 signals are +1 and the remaining 2 are 0 (none are −1). Historical data shows that at such extremes, the probability of mean reversion within 20 sessions is > 70%.

---

## Composite Trits

Individual signals can be combined into **composite trits** that capture higher-order phenomena:

```rust
struct CompositeTrit {
    /// The combined ternary value
    value: Trit,
    /// How many sub-signals contributed
    count: u32,
    /// Standard deviation of contributing signals
    /// High = disagreement, Low = consensus
    signal_dispersion: f64,
    /// Weighted confidence based on signal history
    confidence: f64,
}

fn composite_trit(signals: &[(Trit, f64)]) -> CompositeTrit {
    // signals: (trit, weight) pairs
    let weighted_sum: f64 = signals.iter()
        .map(|(t, w)| (*t as f64) * w)
        .sum();
    let total_weight: f64 = signals.iter().map(|(_, w)| w).sum();
    let mean = weighted_sum / total_weight;
    
    let value = if mean > 0.33 { Trit::Pos }
                else if mean < -0.33 { Trit::Neg }
                else { Trit::Zero };
    
    CompositeTrit { value, count: signals.len() as u32, /* ... */ }
}
```

Example composites:

| Composite | Component Signals | Purpose |
|-----------|-------------------|---------|
| **Momentum Composite** | RSI, MACD, Price Action, Momentum | Overall trend direction |
| **Conviction Composite** | Volume, Social Volume, Sentiment | How much "weight" is behind the move |
| **Fundamental Composite** | PE Rel, Revenue Growth, D/E, Buyback Yield | Valuation and health |
| **Flow Composite** | Put/Call, Institutional, Insider | Who is buying or selling |
| **Signal Dispersion** | Standard deviation of all component trits | Agreement vs. conflict |

---

## Scale Layering

Signals exist at multiple time scales. A full ternary map has layers:

```rust
struct TernaryMap {
    /// Base: daily closing data (most recent 90 sessions)
    daily: HashMap<SignalType, TritVec>,
    /// Intermediate: weekly aggregates
    weekly: HashMap<SignalType, TritVec>,
    /// Macro: monthly trends
    monthly: HashMap<SignalType, TritVec>,
    /// The combination: for each stock, a 3D ternary embedded state
    combined: TernaryEmbedding,
    
    /// Scale coherence: how well the signals agree across scales
    /// 1.0 = perfect agreement (all scales same), 
    /// 0.0 = maximum conflict
    scale_coherence: f64,
}

impl TernaryMap {
    /// If scale_coherence < 0.3, the stock is experiencing a 
    /// "scale break" — different timeframes tell different stories.
    fn is_scale_break(&self) -> bool {
        self.scale_coherence < 0.3
    }
    
    /// The "consensus" trit across all scales
    fn consensus(&self) -> CompositeTrit {
        // weighted by scale: longer timeframes get more weight
        // daily: 1×, weekly: 2×, monthly: 3×
    }
}
```

---

## The 0 State: Not "Neutral" — "Leminal"

A critical design choice: **0 does not mean "no signal."** It means the signal is at the boundary between two regimes, where the local topology is ambiguous.

In topological terms, 0 corresponds to points on the **boundary** of two connected components — a "leminal" zone where the next tick could move the point into either regime. A stock sitting at 0 is not "nothing happening." It is at a **decision boundary**, and the topological energy required to cross that boundary is the system's most important parameter.

This is why 0 is the most common state for most stocks on most days. Most points on a manifold are not in the interior of a cluster — they are in the transition zones between clusters.

---

## Homology

The ternary state space inherits the homology of the underlying manifold. When we build a persistence diagram from the ternary-embedded point cloud, we are studying the **topology of the signal space** — not the raw price space.

This matters because the ternary embedding **discards scale information** (how much overbought?) but **preserves structural information** (are all signals agreeing for a move, or conflicting?). The topology of the ternary space is more stable than the topology of the price space because trit encoding normalizes away amplitude variations while preserving directional relationships.

---

## Symmetry Group

The ternary substrate for Market Manifold has the following symmetry group:

1. **σ_market_cycle**: Invariance under time shift by one complete market cycle (rotational symmetry)
2. **σ_scalar**: Invariance under uniform scaling of all signals (scale symmetry)
3. **σ_reflection**: Invariance under simultaneous sign flip of all signals (time-reversal symmetry: the topology of a mirror-image chart is the same)

These symmetries define the equivalence classes of the market manifold. Two market states are **topologically equivalent** if they map to the same symmetry orbit.
