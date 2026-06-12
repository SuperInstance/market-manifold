# 🌐 Market Manifold — Engineer Onboarding

**From 0 to topological market analyst in 5 days.**

---

## 🎒 Day 1: Room Setup & First Maps

### Morning (30 min)
- [ ] Read [README.md](../README.md) — understand the topological approach
- [ ] Read the [TUTORIALS.md](../TUTORIALS.md) — run Tutorial 1
- [ ] Explore the room structure: `tree rooms/`

### Afternoon (2 hours)
- [ ] Create rooms for 3 tickers in different sectors:
  ```bash
  ./bin/create-room --ticker AAPL --sector Technology
  ./bin/create-room --ticker XOM --sector Energy
  ./bin/create-room --ticker JPM --sector Financial
  ```
- [ ] Build maps for each: `./bin/build-maps --room <TICKER> --days 90`
- [ ] Run the topological observatory on each room

### Evening (optional)
- [ ] Read `docs/TOPOLOGY-OF-VALUE.md`
- [ ] Compare the topological signatures of different sectors

**🎯 Checkpoint:** You have 3+ rooms with working ternary maps and topological fingerprints.

---

## ⚡ Day 2: Topology Reading

### Morning (1 hour)
- [ ] Run Tutorial 2 — stock comparison
- [ ] Learn to read Betti numbers:
  - H₀ = number of connected components (regime clusters)
  - H₁ = number of persistent cycles (rotation patterns)
  - H₂ = number of persistent voids (gaps in the manifold)

### Afternoon (2 hours)
- [ ] Compare all 3 tickers pairwise
- [ ] Find which pairs are topologically symmetric
- [ ] Visualize persistence diagrams

### Evening (optional)
- [ ] Read `docs/TERNARY-SUBSTRATE.md`
- [ ] Experiment with different time windows (30d, 90d, 365d)

**🎯 Checkpoint:** You can read topological fingerprints and compare stocks by their manifold structure.

---

## 🧠 Day 3: Reflexes + Intelligence

### Morning (1.5 hours)
- [ ] Run Tutorial 3 — train room reflexes
- [ ] Train 3+ reflexes per room
- [ ] Test matching with varied natural language queries

### Afternoon (2 hours)
- [ ] Run Tutorial 6 — custom ternary map
- [ ] Create a map for a new signal (options flow, news sentiment, etc.)
- [ ] Register it with a room and rebuild maps

### Evening (optional)
- [ ] Read `onboarding/STOCK-ROOM-MANAGER.md`
- [ ] Review `docs/SYMMETRY-MANIFEST.md`

**🎯 Checkpoint:** Your rooms have reflexes and custom maps. The system is learning.

---

## 📡 Day 4: Fleet Integration

### Morning (1 hour)
- [ ] Run Tutorial 4 — spline creation and sharing
- [ ] Run Tutorial 5 — fleet dashboard
- [ ] Connect rooms with I2I batons

### Afternoon (2 hours)
- [ ] Create a spline from a real analysis
- [ ] Share it across the fleet
- [ ] Watch the fleet dashboard for cross-room alerts

### Evening (optional)
- [ ] Read `docs/FLEET-COORDINATION.md`
- [ ] Set up a sector-sync cron job

**🎯 Checkpoint:** Your rooms communicate via batons and share splines.

---

## 🚢 Day 5: Custom Application

### All Day
- [ ] Design your own Market Manifold application:
  - **Sector rotation detector**
  - **Earnings season topology tracker**
  - **Cross-asset correlation finder**
  - **Regime shift early warning**
- [ ] Use all components: rooms, maps, observatory, reflexes, splines, fleet
- [ ] Write a report from your analysis

### Stretch Goals
- [ ] Create a new metric or topological invariant
- [ ] Build a dashboard for multiple rooms
- [ ] Publish a spline that other fleet members use
- [ ] Integrate with a real trading or analysis platform

**🎯 Checkpoint:** You have a production topological analysis system.

---

## 📚 Quick Reference

| Resource | What It Is | Read When |
|----------|-----------|-----------|
| `README.md` | Hook, architecture, philosophy | Day 1 |
| `TUTORIALS.md` | 6 hands-on tutorials | Day 1–2 |
| `docs/TOPOLOGY-OF-VALUE.md` | Core theory | Day 1 evening |
| `docs/TERNARY-SUBSTRATE.md` | Ternary encoding | Day 2 evening |
| `onboarding/STOCK-ROOM-MANAGER.md` | Agent guide | Day 3 |
| `docs/FLEET-COORDINATION.md` | Communication protocol | Day 4 |
| `docs/SYMMETRY-MANIFEST.md` | Symmetry principles | Day 3 |
| `TEMPLATES/stock-room/` | Room boilerplate | Day 1 |
| `TEMPLATES/custom-map/` | Map boilerplate | Day 3 |
| `examples/` | Full example projects | Day 5 |

---

## ❓ Help

- **Bugs or features?** GitHub issues
- **Fleet coordination?** `construct-coordination` repo
- **Topology questions?** `docs/TOPOLOGY-OF-VALUE.md`

---

*Coral reefs start with one room. The rest is topology.*
