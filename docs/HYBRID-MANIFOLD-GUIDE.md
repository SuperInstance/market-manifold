# 🗺️ THE HYBRID MANIFOLD GUIDE

**The Master Blueprint for Topological Financial Intelligence.**

---

## 1. The Core Idea

The Hybrid Manifold is a socio-technical architecture that separates **computational ground truth** (the Matrix Engine) from **interpretative fidelity** (Room Agents). It treats market state not as a series of prices, but as a point on a high-dimensional topological manifold whose "shape" predicts regime shifts. By mapping this shape into a ternary-continuous action space, the system transforms raw data into high-conviction execution with built-in topological safeguards.

---

## 2. The La-Links: The Interlock

The "la-link" is the connective tissue that prevents the system from becoming a collection of isolated tools.

**The Pipeline: Shape $\to$ Signal $\to$ Guard $\to$ Identity**

1. **TDA (Topological Data Analysis)** $\to$ **Ternary-Continuous**:
   TDA identifies the Betti numbers ($\beta_k$) of the point cloud. A stable $\beta_0=1$ (single component) identifies a trend; a persistent $\beta_1 > 0$ (hole) identifies a rotational cycle. These shapes are mapped directly to a **Trit Gate** $\{-1, 0, +1\}$ with a continuous **Conviction Weight** $[0, 1]$.

2. **Ternary-Continuous** $\to$ **SAEP (Symmetric Action Enforcement Protocol)**:
   A proposed action (e.g., "+1 Accumulate") is not executed immediately. It is passed through the **Veto Engine**. SAEP enforces 4-tier constraints (Room $\to$ Sector $\to$ Portfolio $\to$ Market). If the action violates a boundary, the Veto is applied, scaling the conviction weight down to zero.

3. **SAEP/Action** $\to$ **Symmetry Detection**:
   The system continuously monitors the Wasserstein distance between the persistence diagrams of different assets. When two assets exhibit **Symmetry**, the system links their vetoes. If Asset A is vetoed due to a sector-wide topological collapse, Asset B (its symmetric twin) is preemptively vetoed regardless of its individual signal.

```ascii
[ DATA ] 
    │
    ▼
[ TDA ENGINE ] ───────► Shape (β₀, β₁, β₂)
    │                      │
    ▼                      ▼
[ TERNARY MAP ] ◄────── [ MAPPING ]
    │                      │
    ▼                      ▼
[ VETO ENGINE ] ◄─── [ SAEP CONSTRAINTS ]
    │                      │
    ▼                      ▼
[ EXECUTION ] ◄────── [ SYMMETRY SKEPTIC ]
```

---

## 3. The Fleet Architecture

The fleet is a distributed hierarchy of specialized agents and runtimes.

- **`pincher`**: The reflex runtime. It is the "muscle" that executes a Teach $\to$ Match $\to$ Execute loop.
- **`flux-realm` (formerly `gno`)**: The A2A VM. It provides the bytecode environment where agents (as "Vessels") exchange Batons.
- **`plato-engine`**: The "hardened" C-substrate. It implements **C-Ternary**, moving the Veto logic into embedded firmware for microsecond-level safety.
- **`savanty`**: The intellectual bridge. It converts natural language (LLM) into formal constraints (ASP) that feed the SAEP Veto engine.
- **`c-ternary`**: The primitive header/library that allows the entire fleet (regardless of language) to communicate in $\{-1, 0, +1\}$.

---

## 4. How to Use It

### For C/Embedded Engineers
**Focus: The Hardened Edge.**
Implement the `c-ternary.h` primitives. Your goal is to move the Veto layer as close to the hardware as possible. Use the `plato-engine` model to transform sensor spikes into ternary gates and apply a-priori constraints before the order hits the wire.

### For Python/Data Scientists
**Focus: The Topological Observatory.**
Use the TDA wrappers to build persistence diagrams and landscapes. Do not look at price candles; look at **Betti curves**. Use the `wasserstein_distance` function to find symmetric twins in the universe and cluster them into manifolds.

### For Go/Distributed Systems Engineers
**Focus: The A2A Fabric.**
Implement `Vessel` and `Baton` protocols within the `flux-realm` VM. Your job is to ensure that a `SPLINE_SHARE` baton from `Room/AAPL` reaches `Room/MSFT` with minimal latency and that the `fleet/hub` can orchestrate sector syncs without deadlock.

### For Full-Stack Architects
**Focus: The Hybrid Loop.**
Connect the Matrix Engine (Tensor $\mathbf{X}$) to the Room Agents (Narrative). Ensure the "Narrative-to-Feature" pipeline is closed: when an agent finds a new driver, the Matrix should instantiate a new feature column across the fleet.

---

## 5. The Vocabulary

- **Vessel**: An isolated agent execution context (a "room" or a VM instance).
- **Baton**: The unit of communication. A structured message passed via the I2I protocol.
- **Trit**: A ternary digit $\{-1, 0, +1\}$. The quantum of decision in the system.
- **Conviction**: A continuous scalar $[0, 1]$ representing the strength of a signal.
- **Leminal Zone**: The "0" state. Not neutral, but a decision boundary between regimes.
- **SAEP**: The 4-tier Veto hierarchy guarding the portfolio.
- **Veto**: A governance override that halts a reflexive action.
- **Symmetry**: Topological identity between two assets (measured by Wasserstein distance).
- **Manifold**: The high-dimensional "shape" of the market state space.
- **Betti Numbers ($\beta_k$)**: Counts of connected components ($\beta_0$), cycles ($\beta_1$), and voids ($\beta_2$).

---

## 6. The Triangle Trade: A Topological Example

In traditional finance, a triangle trade (USD $\to$ EUR $\to$ JPY $\to$ USD) is about price discrepancies. In the Hybrid Manifold, it is a **$\beta_1$ Cycle**.

**The Topology:**
1. **Embedding**: Embed the three currencies into a state space.
2. **Filtration**: As we increase the radius $\epsilon$, the currencies connect. 
3. **Hole Formation**: Because the correlations are strong pairwise but not jointly, a **1-dimensional hole** ($\beta_1 = 1$) appears in the persistence diagram.
4. **Interpretation**: This hole is the "arbitrage gap." The persistence of the hole indicates the stability of the arbitrage.
5. **Action**: The system detects a high-persistence $\beta_1$ cycle. It generates a **Trit +1** for the rotational strategy and a **Trit -1** for the linear trend-follow.
6. **Veto**: The SAEP layer checks the portfolio's current $\beta_1$ exposure. If the portfolio is already "saturated" with cyclic risk, the Veto engine scales the conviction to 0.

---

## 7. Key Repos and Links

- **`market-manifold`**: The core TDA and ternary logic.
- **`pincher`**: The reflex execution framework.
- **`flux-realm`**: The A2A VM and bytecode spec.
- **`plato-engine`**: The C-Ternary embedded guard.
- **`savanty`**: The LLM-to-Constraint bridge.

---

## 8. The Path Forward

### L3/L4 Deployment
We are moving from "Cloud-first" to "Edge-first." 
- **L3**: Regional Hubs managing sector-specific TDA.
- **L4**: On-device Veto engines (Plato-level) delivering sub-millisecond safety.

### Hardware Targeting
Optimization for **ARM64 (Oracle/AWS Graviton)**. We are shifting from heavy FP64 tensors to **INT8 quantized ternary matrices**, reducing memory bandwidth requirements by $8\times$ for the Matrix Engine.

### Codespace Offloading
Moving the computationally expensive TDA (Ripser/Persistence) to remote high-memory clusters. Rooms will send "point-cloud snapshots" to the cloud, receive a "Betti signature" back, and then perform the interpretative analysis locally.

---

*Scribe's Note: If it doesn't map to a trit or a Betti number, it is noise. Discard it.*
