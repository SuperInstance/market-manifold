# 🃏 Market Manifold Quick Reference Card

**For Room Managers in the field. Print and tape to your terminal.**

---

## Essential Commands

```bash
# Room Lifecycle
./bin/create-room --ticker SYM --sector "Sector Name"
./bin/destroy-room --ticker SYM

# Data & Maps
./bin/fetch-data --room SYM --source all --days 90
./bin/build-maps --room SYM
./bin/map-stats --room SYM

# Topology
./bin/observatory --room SYM --timeline 90d --dimensions 0:2
./bin/compute-signature --room SYM
./bin/topo-drift --room SYM

# Reflexes (via pincher)
pincher teach --room SYM
pincher do --room SYM "check-regime-consistency"
pincher reflexes --room SYM

# Splines
./bin/share-spline --room SYM --spline my-spline.spline
./bin/test-spline --room SYM --spline received-spline.spline

# Fleet
./bin/join-fleet --rooms SYM1,SYM2,SYM3
./bin/report-status --room SYM –to fleet/hub
./bin/sector-topology-diff --room SYM

# Batons
baton-read /tmp/i2i-vessel/harbor/market-manifold/SYM/
baton-create --type SPLINE_SHARE --from rooms/SYM --to rooms/OTHER
```

---

## Betti Number Quick Reference

| Betti | Counts | Market Meaning | Action |
|-------|--------|---------------|--------|
| β₀ = 1 | One regime cluster | Strong trend | +1 with conviction |
| β₀ = 2-3 | Multiple regime clusters | Regime transitions active | 0 — wait for merge |
| β₁ = 0 | No cycles | Directional movement | Follow trend |
| β₁ = 1 | One cycle | Range / Mean reversion | −1 at edges |
| β₂ = 0 | No voids | Normal topology | Safe |
| β₂ ≥ 1 | Price traps present | Structural barrier | −1 — avoid |

---

## Ternary to Action

```
+1 → Accumulate (Topology supports upward)
 0 → Hold (Boundary zone — ambiguous)
−1 → Reduce (Topology supports downward)
```

**Conservation:** $|E_{sum}| \leq |S|/2$  
When absolute sum approaches $|S|/2$, expect mean reversion.

---

## Scale Break Detection

```
daily  weekly  monthly  →  Action
+1     +1      +1      →  Full conviction accumulate
+1     +1       0      →  Accumulate with caution
+1      0      -1      →  SCALE BREAK — regime change imminent
 0      0       0      →  True neutral — wait
-1     -1      -1      →  Full conviction reduce
```

---

## Wasserstein Distance Thresholds

| Distance | Meaning | Action |
|----------|---------|--------|
| < 0.1 | Same regime | Normal ops |
| 0.1-0.3 | Regime evolution | Monitor |
| 0.3-0.6 | Regime transition | Reduce position |
| > 0.6 | Regime collapse | ALERT |

---

## Reflex Confidence

```
< 0.55  →  Novel pattern — route to LLM-as-Compiler
0.55-0.80 → Similar pattern — confirm then execute
> 0.80  →  Exact match — execute directly (~50ms)
```

---

## Spline Template

```json
{
  "spline_name": "",
  "room": "",
  "created": "",
  "type": "REGIME_PATTERN",
  "precondition": {},
  "observation": "",
  "match_score": 0.0,
  "confidence": 0.0,
  "action": "",
  "expiry": "+30d"
}
```

---

## Sector Sync Cadence

```
04:00 UTC — Morning topology check
12:00 UTC — Mid-day sector sync
20:00 UTC — Evening distillation
Sunday    — Weekly room audit
```

---

## Emergency Alerts

Send `ALERT` baton to fleet/hub when:

```
1. H₂ ≥ 1 appears where previously 0
2. Wasserstein drift > 0.6 in < 5 sessions
3. H₀ drops from N → 1 in < 3 sessions
4. Topological momentum > 0.15/session for 3+ sessions
5. Reflex engine crashes repeatedly
6. Veto engine blocks a high-confidence reflex
```

---

## Three Laws of Room Management

1. **A room is not a prediction. It is a map.**  
   You are a cartographer, not a profit center.

2. **Splines outlive agents.**  
   What you distill today will inform rooms you never manage.

3. **The topology is the signal.**  
   If the Betti numbers say one thing and your gut says another, trust the Betti numbers.
