# TRIAGE-4: Governance & Veto Layer

**Addressing Leak #4 — The SAEP/Veto Layer is an Afterthought**

> *"One sentence in the README. No portfolio constraints, no conflict resolution, no circuit breakers, no governance hierarchy."* — Officer-Critic

---

## Executive Summary

The Critic correctly identified the veto/governance layer as the single most dangerous gap in the architecture. A system making directional calls on 500 instruments without portfolio-level risk constraints is not a financial analysis framework — it's a collection of independent opinions with no aggregate accountability.

This document defines **SAEP** (Structured Agent Emergency Protocol) and builds a complete governance hierarchy with four layers: Room-level, Sector-level, Portfolio-level, and Market-level.

---

## 1. What is SAEP?

**SAEP** = **Structured Agent Emergency Protocol**

A SAEP is a **governance primitive** — a formalized constraint pattern that an agent must check before executing any market-relevant action. Unlike a veto (which blocks), a SAEP guides: it defines the envelope of acceptable behavior and escalates when the envelope is broached.

### SAEP Anatomy

```rust
struct SaepConstraint {
    /// Unique identifier
    id: String,
    /// Governance layer this constraint belongs to
    layer: GovernanceLayer,       // Room | Sector | Portfolio | Market
    /// The constraint function — returns Ok or Err with reason
    check: Box<dyn Fn(&ActionContext) -> Result<(), Violation>>,
    /// What happens on violation
    action: SaepAction,           // Warn | Limit | Veto | Freeze
    /// Escalation path when this constraint is violated
    escalate_to: Option<GovernanceLayer>,
    /// How long since last check before this constraint expires
    ttl_seconds: u64,
}

enum SaepAction {
    Warn,   // Log warning, allow action to proceed
    Limit,  // Scale down the action (e.g., halve position size)
    Veto,   // Block the action entirely
    Freeze, // Block all actions from this room until reviewed
}
```

---

## 2. Governance Hierarchy

```
┌─────────────────────────────────────────────────────┐
│              MARKET-LEVEL GOVERNANCE                 │
│  • Global circuit breaker                            │
│  • Systemic risk limit                               │
│  • Cross-asset correlation cap                       │
│  • Leverage ceiling                                  │
└────────────────────┬────────────────────────────────┘
                     │ escalates to
┌────────────────────▼────────────────────────────────┐
│              PORTFOLIO-LEVEL GOVERNANCE               │
│  • VaR / CVaR limits                                 │
│  • Sector concentration caps                         │
│  • Max drawdown                                      │
│  • Gross exposure limit                              │
│  • Conflict resolution between rooms                 │
└────────────────────┬────────────────────────────────┘
                     │ escalates to
┌────────────────────▼────────────────────────────────┐
│              SECTOR-LEVEL GOVERNANCE                  │
│  • Sector maximum allocation                          │
│  • Sector VaR contribution                            │
│  • Intra-sector correlation limits                    │
│  • Sector rotation velocity limit                     │
└────────────────────┬────────────────────────────────┘
                     │ escalates to
┌────────────────────▼────────────────────────────────┐
│              ROOM-LEVEL GOVERNANCE                    │
│  • Per-stock position limits                         │
│  • Per-stock VaR limits                              │
│  • Reflex confidence thresholds                      │
│  • Individual circuit breaker                        │
└─────────────────────────────────────────────────────┘
```

### 2.1 Room-Level Governance

Applied to each stock individually. These are the first line of defense.

```rust
struct RoomGovernance {
    ticker: String,
    constraints: Vec<SaepConstraint>,
    state: RoomState,
}

impl RoomGovernance {
    /// Check all constraints before allowing a reflex to fire
    fn check_action(&mut self, ctx: &ActionContext) -> GovernanceResult {
        for constraint in &self.constraints {
            match (constraint.check)(ctx) {
                Ok(()) => continue,
                Err(violation) => return self.handle_violation(constraint, violation),
            }
        }
        GovernanceResult::Allowed
    }
}
```

**Default Room-Level Constraints:**

| Constraint | Check | SAEP Action |
|-----------|-------|-------------|
| Max position | $position\_value < 0.05 \times portfolio$ | Limit (scale to max) |
| Max daily loss | $PnL_{today} < -0.02 \times position\_value$ | Freeze (1 day) |
| Min reflex confidence | $confidence \geq 0.55$ | Veto |
| Max reflex age | $last\_taught < 7\_days$ | Warn (retrain) |
| Volume liquidity | $position\_size < 0.01 \times avg\_daily\_volume$ | Veto |

### 2.2 Sector-Level Governance

Applied across all rooms sharing sector classification. Prevents sector concentration.

```rust
struct SectorGovernance {
    sector: Sector,         // Technology, Energy, Healthcare, etc.
    rooms: Vec<String>,     // Tickers in this sector
    constraints: Vec<SaepConstraint>,
}
```

**Default Sector-Level Constraints:**

| Constraint | Check | SAEP Action |
|-----------|-------|-------------|
| Max sector allocation | $\sum weight_{sector} < 0.30$ | Limit (scale down all rooms) |
| Sector VaR contribution | $VaR_{sector} < 0.40 \times VaR_{portfolio}$ | Warn → Limit |
| Velocity limit | $|\Delta weight_{sector}|_{1h} < 0.05$ | Veto |
| Correlation warning | $\rho_{internal} > 0.90$ | Warn (diversification alert) |

### 2.3 Portfolio-Level Governance

The aggregate layer. Applied to the full portfolio across all sectors and rooms.

**Default Portfolio-Level Constraints:**

| Constraint | Check | SAEP Action |
|-----------|-------|-------------|
| Gross exposure | $\sum |position_i| < 2.0$ | Limit (scale proportionally) |
| Net exposure | $|\sum position_i| < 0.30$ | Limit |
| VaR (95%, 1d) | $VaR_{portfolio} < 0.02 \times NAV$ | Veto all new positions |
| CVaR (95%, 1d) | $CVaR_{portfolio} < 0.04 \times NAV$ | Freeze → reduce positions |
| Max drawdown | $drawdown_{peak} > 0.15$ | Freeze all (emergency) |
| Leverage | $gross / NAV < 2.0$ | Veto all leveraged actions |
| Sector count | $num\_sectors < 5$ | Warn (undiversified) |
| Cash reserve | $cash > 0.05 \times NAV$ | Warn only |

### 2.4 Market-Level Governance

The outermost layer. Triggered by extreme market-wide conditions.

```rust
struct MarketGovernance {
    /// If VIX > 30, tighten all limits by this factor
    vix_tightening: f64,        // 0.5 = cut all limits in half
    /// If daily move > this % across broad index, freeze
    market_crash_threshold: f64, // -0.05 = 5% drop
    /// If correlation across ALL positions > this, systemic risk alert
    systemic_correlation_threshold: f64, // 0.85
}

impl MarketGovernance {
    fn assess_market_state(&self, market_data: &MarketData) -> MarketState {
        if market_data.daily_return < self.market_crash_threshold {
            MarketState::CrashProtocol
        } else if market_data.vix > 30.0 {
            MarketState::HighVolatility
        } else {
            MarketState::Normal
        }
    }
}
```

---

## 3. Conflict Resolution

When two rooms disagree on correlated stocks, who wins?

### Resolution Protocol

```rust
enum DisagreementLevel {
    /// Same sector, opposite signals
    IntraSector { ticker_a: String, ticker_b: String },
    /// Different sectors, same portfolio impact
    CrossSector { signal_a: PositionSignal, signal_b: PositionSignal },
    /// Market-level directional disagreement
    MacroDirectional { long_count: usize, short_count: usize },
}

fn resolve_conflict(disagreement: DisagreementLevel) -> Resolution {
    match disagreement {
        // Same sector, opposite signs: scale both down, investigate
        IntraSector { ticker_a, ticker_b } => {
            // Reduce both positions by 50%, escalate for investigation
            Resolution::ScaleDown { factor: 0.5, escalate: true }
        }
        // Different sectors: check conviction weights
        CrossSector { signal_a, signal_b } => {
            if signal_a.confidence > signal_b.confidence * 1.5 {
                Resolution::Follow(signal_a)
            } else if signal_b.confidence > signal_a.confidence * 1.5 {
                Resolution::Follow(signal_b)
            } else {
                // Close enough — reduce both to neutral
                Resolution::Neutralize
            }
        }
        // 70%+ of rooms say long or short: macro risk
        MacroDirectional { long_count, short_count } => {
            let total = long_count + short_count;
            if long_count as f64 / total as f64 > 0.7 {
                Resolution::ReduceDirectional { side: Direction::Long }
            } else if short_count as f64 / total as f64 > 0.7 {
                Resolution::ReduceDirectional { side: Direction::Short }
            } else {
                Resolution::NoAction
            }
        }
    }
}
```

### Tiebreaker Hierarchy

When a conflict cannot be resolved at the room level:

1. **Higher confidence wins** (if margin > 15 percentage points)
2. **More recent data wins** (within same window)
3. **Higher liquidity wins** (more reliable price discovery)
4. **Lower volatility wins** (less stochastic noise)
5. **Escalate to Portfolio Governor** (human-in-the-loop)

---

## 4. Circuit Breakers

### 4.1 Reflex Cascade Prevention

A reflex cascade occurs when one reflex triggers another in a chain reaction:
```
AAPL: "sell on drop" → executes → price drops → MSFT: "sell on volatility"
→ executes → price drops further → AAPL: "intensify sell" → ...
```

**Solution:** Reflex lockout timer + velocity check:

```rust
struct ReflexCircuitBreaker {
    /// Minimum seconds between reflex firings
    cooldown_seconds: u64,       // 60
    /// Maximum position change per hour (absolute %)
    max_velocity_per_hour: f64,  // 0.10
    /// Maximum number of reflex firings per hour
    max_firings_per_hour: u32,   // 10
    /// Tracking
    last_fire_timestamps: VecDeque<Instant>,
}
```

### 4.2 Escalation Ladder

| Condition | Action | Auto-reset |
|-----------|--------|------------|
| Room fires 3 reflexes in 5 minutes | Room-level freeze (15 min) | Yes, auto |
| Sector has 3+ frozen rooms | Sector freeze (1 hour) | Yes, auto |
| Portfolio drawdown > 10% | Portfolio freeze (end of day) | After review |
| Market drop > 5% in 1 hour | Market freeze (next open) | After review |

---

## 5. Governance Data Flow

```
Room Reflex fires
    ↓
Room-Level SAEP check
    ├── Allowed → execute
    ├── Warned → execute + log
    ├── Limited → modify + execute
    └── Veto-ed → block + escalate to Sector
            ↓
    Sector-Level SAEP check
        ├── Allow → override room veto (rare)
        ├── Confirm → uphold veto
        └── Escalate → Portfolio-level
                ↓
        Portfolio-Level SAEP check
            ├── Override → allow with flag
            ├── Confirm → veto stands
            └── Escalate → Market-level
                    ↓
            Market-Level SAEP check
                ├── Allow → override all (extreme circumstances only)
                └── Freeze → complete system halt
```

---

## 6. Governance Tuning

All thresholds are configurable per-instance. The defaults above assume:
- **Long-biased portfolio**: net exposure limit 0.30
- **Medium volatility regime**: VIX 15-25
- **Diversified mandate**: min 5 sectors
- **Moderate leverage tolerance**: gross 2.0x

For different strategies (e.g., market-neutral, sector-concentrated, high-turnover), the governance layer should be reconfigured at deployment time — not by individual rooms.
