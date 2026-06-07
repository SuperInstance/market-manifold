# 🧬 Spline Examples

**Real splines a Room Manager might distill from topological analysis.**

Each spline is a compact pattern that survives memory loss. They are the unit of intelligence in Market Manifold — shareable, testable, and composable.

---

## Example 1: Void Formation in Large-Cap Tech

**File:** `rooms/AAPL/splines/void-formation-tech.spline`

```json
{
  "spline_name": "void-formation-large-cap-tech",
  "author": "officer/scribe",
  "room": "AAPL",
  "created": "2026-06-07",
  "type": "REGIME_PATTERN",
  "sector_domain": "Technology",
  "market_cap_tier": "mega",
  "precondition": {
    "topological_state": {
      "betti_before": [1, 0, 0],
      "betti_during": [3, 0, 1],
      "betti_after": [1, 0, 0]
    },
    "duration": "5-7 sessions",
    "volume_pattern": "volume normal → volume contracts 30% → volume surges 2x"
  },
  "observation": {
    "narrative": "When H₀ smoothly transitions 1→3 and H₂ appears as a single 
                  void for 5-7 sessions, then H₀ collapses back to 1 and 
                  H₂ vanishes — the void was structural consolidation, 
                  not a price trap. Position can be maintained through the void.",
    "statistics": {
      "sample_size": 12,
      "true_positive_rate": 0.92,
      "false_positive_rate": 0.08,
      "avg_forward_return": 3.1,
      "return_unit": "percent",
      "avg_duration_sessions": 6
    }
  },
  "distinction": {
    "this_is_not": [
      "Crisis void (H₂ + H₀ stays > 3 — true fragmentation)",
      "Rotational void (H₂ + H₁ appears — cycle + trap)"
    ]
  },
  "confidence": 0.85,
  "action": "0 (Hold through void, wait for consolidation)" 
}
```

---

## Example 2: Earnings Compression Pattern

**File:** `rooms/MSFT/splines/earnings-compression.spline`

```json
{
  "spline_name": "earnings-compression-bullish",
  "author": "officer/scribe",
  "room": "MSFT",
  "created": "2026-06-07",
  "type": "EVENT_PATTERN",
  "sector_domain": "Technology",
  "event_type": "earnings",
  "precondition": {
    "topological_state": {
      "betti_before": [2, 1, 0],
      "betti_compressed": [1, 0, 0]
    },
    "timing": "3 sessions pre-earnings",
    "energy_threshold": {
      "before": 0.87,
      "after": 1.12
    }
  },
  "observation": {
    "narrative": "In the 3 sessions before earnings, H₀ compresses from 2→1 
                  (regime merging), H₁ vanishes (cycle breaks), and topological 
                  energy crosses 1.0. Post-earnings, the stock gaps up ~2.3% 
                  on average over 5 sessions.",
    "statistics": {
      "sample_size": 7,
      "true_positive_rate": 0.86,
      "false_positive_rate": 0.14,
      "avg_forward_return": 2.3,
      "return_unit": "percent"
    }
  },
  "confidence": 0.78,
  "action": "+1 (Accumulate pre-earnings when compression detected)"
}
```

---

## Example 3: Sector Rotation Signal

**File:** `rooms/GOOGL/splines/sector-rotation-detection.spline`

```json
{
  "spline_name": "sector-rotation-detection",
  "author": "officer/scribe",
  "room": "GOOGL",
  "created": "2026-06-07",
  "type": "CROSS_ROOM_PATTERN",
  "sector_domain": "Technology",
  "precondition": {
    "my_state": {
      "betti": [1, 0, 0],
      "energy": 0.42
    },
    "sector_state": {
      "cross_betti": 2,
      "sector_energy": 0.87,
      "participating_rooms": ["AAPL", "MSFT", "AMZN"]
    }
  },
  "observation": {
    "narrative": "When my room shows a quiet single-regime topology (H₀=1, energy=0.42) 
                  but the sector shows active cross-Betti cycles (H₁=2 across rooms), 
                  rotation is happening between OTHER stocks. I am being left behind. 
                  The sector moves, then I move 2-3 sessions later as the rotation 
                  reaches my ticker.",
    "statistics": {
      "sample_size": 5,
      "lag_sessions_avg": 2.4,
      "true_positive_rate": 0.80,
      "avg_rotation_capture": 1.4,
      "return_unit": "percent"
    }
  },
  "confidence": 0.72,
  "action": "Prepare for move — increase observation frequency. Position +1 if lagging behind sector rotation and sector direction is clear."
}
```

---

## Example 4: Regime Collapse Warning

**File:** `rooms/AMZN/splines/regime-collapse-warning.spline`

```json
{
  "spline_name": "regime-collapse-warning",
  "author": "officer/scribe",
  "room": "AMZN",
  "created": "2026-06-07",
  "type": "ALERT_PATTERN",
  "sector_domain": "Technology",
  "severity": "high",
  "precondition": {
    "signals": {
      "topological_momentum": "> 0.15/session × 3+ sessions",
      "wasserstein_drift": "> 0.6 from baseline",
      "betti_evolution": "H₀: 1→3→5 in 10 sessions"
    },
    "volume_confirmation": {
      "pre_condition": "normal",
      "during": "surges 3x",
      "post": "collapses to 0.3x (exhaustion)"
    }
  },
  "observation": {
    "narrative": "When topological momentum exceeds 0.15/session for 3+ consecutive 
                  sessions AND Wasserstein drift from baseline exceeds 0.6 AND 
                  H₀ expands from 1 to 5+ — the regime is collapsing. This is not 
                  a rotation. It is a structural change. Historical analogs: crash 
                  of 2020, sector de-rating of 2022.",
    "statistics": {
      "sample_size": 4,
      "all_correct": true,
      "avg_max_drawdown": -8.7,
      "avg_recovery_sessions": 42
    }
  },
  "confidence": 0.92,
  "action": "ALERT — reduce position. Alert fleet. Share spline immediately."
}
```

---

## Example 5: Cross-Stock Spline Transfer

**File:** `rooms/AAPL/splines/cross-stock-transfer.spline`

```json
{
  "spline_name": "pre-earnings-compression-cross-stock",
  "author": "officer/scribe",
  "room": "AAPL",
  "created": "2026-06-07",
  "type": "CROSS_VALIDATED_PATTERN",
  "original_source": "MSFT/earnings-compression-bullish",
  "test_results": [
    {
      "tested_on": "MSFT",
      "match_score": 0.92,
      "confidence": 0.85
    },
    {
      "tested_on": "AAPL",
      "match_score": 0.78,
      "confidence": 0.78
    },
    {
      "tested_on": "GOOGL",
      "match_score": 0.67,
      "confidence": 0.67
    },
    {
      "tested_on": "AMZN",
      "match_score": 0.45,
      "confidence": 0.45
    },
    {
      "tested_on": "META",
      "match_score": 0.71,
      "confidence": 0.71
    }
  ],
  "observation": {
    "narrative": "The earnings-compression pattern (H₀ 2→1 + energy crossing 1.0 
                  pre-earnings → bullish drift post-earnings) cross-validates 
                  across mega-cap tech. Strongest on hardware-oriented tech (MSFT, 
                  AAPL, GOOGL), weaker on e-commerce (AMZN). Recommendation: 
                  promote to fleet-wide reflex for Technology/Mega-Cap.",
    "fleet_status": "pending_promotion"
  },
  "confidence": 0.78,
  "action": "PROMOTE — cross-validated across 5 tickers, 3 at ≥ 0.67"
}
```

---

## Spline Anatomy

Every spline has:

| Field | Purpose | Required |
|-------|---------|----------|
| `spline_name` | Unique identifier | ✅ |
| `author` | Who distilled this | ✅ |
| `room` | Source room | ✅ |
| `created` | Timestamp | ✅ |
| `type` | Pattern type (REGIME, EVENT, CROSS_ROOM, ALERT) | ✅ |
| `precondition` | Conditions before the pattern | ✅ |
| `observation` | What was observed | ✅ |
| `confidence` | How sure we are (0-1) | ✅ |
| `action` | What to do | ✅ |
| `expiry` | When to re-evaluate | Optional |
| `sector_domain` | Sector applicability | Optional |
| `statistics` | Empirical backing | Recommended |
| `distinction` | What this IS NOT | Recommended |
| `fleet_status` | Promotion state | Optional |

### Rules for Good Splines

1. **Empirical**: Every spline must cite `sample_size`, `true_positive_rate`, `false_positive_rate`. No anecdotes.
2. **Falsifiable**: A spline must specify expiry. If it never expires, it's not testable.
3. **Shareable**: A spline must be understandable by another room without the original context.
4. **Actionable**: Every spline ends with an action (what to do).
5. **Distinguishable**: A spline must say what it IS NOT — prevent false matches.
