# 📖 Market Manifold Glossary

**Terms, definitions, and the language of financial topology.**

---

## A

**Agent** — Any actor in the Market Manifold system. Room Managers are agents. `fleet/hub` is an agent. Reflex runners are agents. Agents communicate via I2I batons.

**A2A (Agent-to-Agent)** — Protocol for agent-to-agent communication within the SuperInstance fleet. The I2I baton protocol is the Market Manifold implementation of A2A.

---

## B

**Baton** — A structured message passed between Fleet agents via the I2I protocol. Contains typed payload, routing, TTL, and priority.

**Betti Number (βₖ)** — The rank of the k-th homology group. In persistent homology, counts the number of k-dimensional topological features at a given scale. β₀ = connected components, β₁ = cycles, β₂ = voids.

**Bottle** — A staged baton, typically in the I2I vessel's `bottles/` directory awaiting pickup.

**Bottleneck** — A topological feature (usually an H₁ cycle) shared across multiple stocks in the same sector. Indicates a structural constraint on the entire sector.

---

## C

**Composite Trit** — A derived ternary value combining multiple signals with weights. Represents a higher-order feature of the state space.

**Connected Component** — A region of the manifold where any two points can be connected by a path staying entirely within the region. One H₀ count.

**Conservation** — The constraint that the sum of all trits for a stock must remain bounded. When the absolute sum approaches the bound, mean reversion is expected.

**Cross-Betti** — Betti numbers computed on the joint persistence diagram of multiple stocks' state spaces. Measures sector-level topological structure.

**Cycle** — A 1-dimensional topological feature (H₁). In market terms, a rotational pattern that implies return to a prior price region.

---

## D

**Distillation** — The process of converting raw room observations into a compact spline. Analogous to training → inference: you observe n instances, distill into one spline.

---

## E

**Embedding** — The mapping from continuous financial signals into {−1, 0, +1} ternary space. Each stock's state becomes a point in a discrete lattice.

---

## F

**Filtration** — In persistent homology, a sequence of simplicial complexes (VR complexes) built at increasing radius ε. Features that persist across many ε values are topologically significant.

**Fleet** — The collective body of all Market Manifold rooms, hubs, reflex registries, and coordination infrastructure. Connected by I2I batons.

---

## H

**H₀** — The 0th homology group. Generators correspond to connected components. See Betti Number.

**H₁** — The 1st homology group. Generators correspond to 1-dimensional cycles (loops). In markets, often corresponds to mean-reversion or sector rotation patterns.

**H₂** — The 2nd homology group. Generators correspond to 2-dimensional voids (cavities). In markets, corresponds to "price traps" — regions the point cloud avoids.

**Hausdorff Distance** — The maximum distance from any point in one set to the nearest point in another. Used to measure topological drift between successive persistence diagrams.

---

## I

**I2I (Iron-to-Iron)** — The core communication protocol of the SuperInstance fleet. Market Manifold rooms send and receive I2I batons via the vessel at `/tmp/i2i-vessel/`.

---

## L

**Leminal Zone** — A region of {−1, 0, +1} state space where the trit is 0 — not as "neutral" but as "on the boundary between two regimes." The most common state for most stocks.

**LUT Matmul** — Look-Up Table Matrix Multiply. The ternary neural network operation where weights in {−1, 0, +1} mean each multiply becomes add/subtract/skip.

---

## M

**Manifold** — A topological space that locally resembles Euclidean space but globally may be curved, twisted, or non-trivially connected. The "shape" of market state space.

**Market Manifold** — The framework. A system for topological financial analysis using ternary logic, persistent homology, and agent-based room management.

Map — A collection of ternary-encoded signals for a stock. Three primary maps: technical, fundamental, sentiment.

---

## N

**.nail** — The portable agent bundle format. Reflexes, identity, and configuration packed into a single `tar.zst` archive with BLAKE3 checksum. The transport format for agents.

---

## P

**Persistence Diagram** — A plot of all topological features by their (birth, death) epsilon values. Features far from the diagonal are topologically significant.

**Persistent Homology** — A technique from TDA that computes the topological features of a point cloud at multiple scales. The mathematical core of Market Manifold.

**Phase Transition** — A regime change. The topological signature (Betti numbers) undergoes a sudden shift, analogous to water freezing.

**Pincher** — The reflex runtime that powers every stock room. Teach → Match → Execute loop with confidence feedback.

**Point Cloud** — A set of points in a state space. In Market Manifold, the collection of a stock's embedded states across time.

---

## R

**Reflex** — A learned pattern-action pair stored in the pincher reflex database. When the embedding of a new state matches a stored reflex above the confidence threshold, the reflex fires.

**Reflex Induction** — The process of learning new reflexes from observed patterns. If the topological signature X precedes outcome Y three times, a reflex is induced.

**Regime** — A persistent topological state of a stock or sector. Characterized by stable Betti numbers and low Wasserstein drift.

**Room** — The per-ticker analysis unit. Contains maps, topology, reflexes, splines, and a narrative journal. Managed by a Room Manager agent.

**Room Manager** — The agent responsible for maintaining a stock room. Duties: build maps, run topology, teach reflexes, distill splines, participate in sector sync.

---

## S

**Scale Break** — A condition where different time scales (daily, weekly, monthly) produce different ternary positions. Indicates regime transition in progress.

**Sector Sync** — A periodic (every 6h) cross-room topological comparison. `fleet/hub` collects signatures from all rooms in a sector and computes the joint topology.

**Signature** — The current topological state of a stock. Includes: Betti numbers (β₀, β₁, β₂), persistence diagram, Wasserstein drift, topological energy, ternary position, and confidence.

**Spline** — A distilled insight that survives memory loss. Compact, shareable, empirical. The unit of intelligence in Market Manifold.

**State Space** — The embedding space of all financial signals for a stock. Typically d-dimensional, ternary-valued. The arena in which topological analysis runs.

---

## T

**TDA (Topological Data Analysis)** — A branch of data science that studies the shape of data using tools from topology. Persistent homology is the most common TDA technique.

**Ternary** — The {−1, 0, +1} value system. The native arithmetic of Market Manifold. Not binary (too limited for nuance) and not continuous (too noisy).

**Ternary Position** — The composite recommendation for a stock: +1 (accumulate), 0 (hold), −1 (reduce). Derived from topological analysis.

**Tick** — The basic timing unit of a Room. One tick = one market session (approximately 6.5 hours for US equities).

**Topological Diversity** — The degree to which a portfolio's holdings occupy distinct topological regions. Maximized when holdings have different Betti number vectors.

**Topological Energy** — The sum of persistence values (death − birth) across all topological features, weighted by dimension. Measures the "amount of structure" in the market.

**Topological Momentum** — The rate of change of topological structure. Measured as Wasserstein drift per session. High topological momentum precedes regime change.

**Trit** — A ternary digit. Values: −1, 0, +1. The quantum of Market Manifold analysis.

**TritVec** — A vector of trits. The primary data structure for ternary maps.

---

## V

**Vessel** — The physical location of the I2I message bus: `/tmp/i2i-vessel/`. Contains `bottles/` (outgoing), `harbor/` (incoming), and `splines/`.

**Veto Engine** — The SAEP pattern-based safety system that blocks reflexive actions that violate boundaries. Enforced before any reflex executes.

**Void** — A 2-dimensional hole in the point cloud (H₂ feature). Market interpretation: a price trap zone that the stock's state space avoids. Strong resistance/support or structural dislocation.

---

## W

**Wasserstein Distance** — The Earth Mover's distance between two persistence diagrams. Measures topological difference in units of persistence. The standard metric for comparing market states.
