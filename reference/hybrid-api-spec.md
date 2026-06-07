# HYBRID-API-SPEC: Rust Traits & Interface Definitions

**Hybrid Manifold — Matrix Engine ↔ Room Agents ↔ Veto Engine**
**Target Crate:** `hybrid-bridge` (new crate in pincher workspace)
**Dependencies:** `pincher-core`, `ternary-types`, `serde`, `ndarray`, `tokio`, `arrow`

---

## 1. Matrix Engine Interface

The Matrix Engine owns the feature tensor `X[n, m, h]` and exposes computation results to Room Agents.

```rust
use ndarray::{Array3, Array2, Array1};
use ternary_types::{Trit, TernaryVec};
use std::sync::Arc;
use tokio::sync::RwLock;

/// The core feature tensor: stocks × features × history.
/// Stored as Arc<RwLock<>> for concurrent read access by room agents.
pub type FeatureTensor = Arc<RwLock<Array3<f32>>>;

/// Topological snapshot of a single ticker's position in the manifold.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TopologicalSignature {
    pub ticker: String,
    pub betti_numbers: Vec<usize>,   // [β₀, β₁, β₂]
    pub persistence_landscape: Vec<f64>,
    pub wasserstein_distance_centroid: f64,
    pub regime_label: String,        // e.g., "rotation", "fragmentation", "stable"
    pub confidence: f64,             // [0.0, 1.0]
}

/// Result of a full matrix cycle.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatrixSnapshot {
    /// Timestamp (Unix millis)
    pub tick: u64,
    /// Number of active stocks
    pub n_stocks: usize,
    /// Top N eigenvalues (explained variance)
    pub eigenvalues: Vec<f64>,
    /// Top N eigenvectors (factor loadings), truncated to top_k
    pub eigenvectors: Array2<f64>,
    /// Per-stock topological signatures (for all active stocks)
    pub topologies: Vec<TopologicalSignature>,
    /// Matrix-level Betti counts (aggregated)
    pub universe_betti: [usize; 3],
    /// Global regime flag
    pub regime: String,
    /// Correlation matrix condition number (stability indicator)
    pub condition_number: f64,
}

#[async_trait]
pub trait MatrixEngine: Send + Sync {
    /// Ingest a new data point for ticker `t` at time `tick`.
    /// Updates the feature tensor X[t, :, :] with new row.
    async fn ingest(&self, ticker: &str, features: &[f64], tick: u64);

    /// Run the fast-path update (tensor ingest + simple statistics).
    /// Guaranteed < 5ms on ARM64 at n=5000.
    async fn fast_cycle(&self, tick: u64) -> MatrixMetadata;

    /// Run the medium-path update (correlation matrix + streaming PCA).
    /// ~200-500ms, run every 5 ticks.
    async fn medium_cycle(&self, tick: u64) -> PartialSnapshot;

    /// Run the full slow-path update (eigendecomposition + TDA).
    /// ~2-5 seconds, run every 20-60 ticks or on regime change.
    async fn full_cycle(&self, tick: u64) -> MatrixSnapshot;

    /// Provide a slice of the feature tensor for a single ticker.
    /// Used by Room Agents for per-stock analysis.
    async fn get_slice(&self, ticker: &str) -> Option<Array2<f32>>;

    /// Provide the cross-sectional view: all stocks, single feature, single time.
    async fn get_cross_section(&self, feature: &str, time_idx: usize) -> Option<Array1<f32>>;

    /// Register a new ticker. Appends a row to the tensor (O(1), ~10ms).
    async fn add_ticker(&self, ticker: &str, initial_features: Option<&[f64]>);

    /// Remove a ticker. Does not delete — marks inactive, reuses row.
    async fn remove_ticker(&self, ticker: &str);
}
```

---

## 2. Room Agent Interface

Room Agents consume Matrix Slices, add interpretation, and emit proposals.

```rust
/// The ternary gate: direction decision.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TernaryGate {
    Bullish,   // +1
    Neutral,   // 0 (leminal zone)
    Bearish,   // -1
}

/// A room's proposal to the Veto Engine.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoomProposal {
    pub ticker: String,
    pub gate: TernaryGate,
    pub conviction: f64,             // Continuous weight [0.0, 1.0]
    pub confidence: f64,             // Reflex confidence [0.0, 1.0]
    pub narrative_sig: String,       // Hash of the narrative (for audit)
    pub matrix_agreement: f64,       // How much does this agree with matrix consensus? [0,1]
    pub veto_override: bool,         // Agent flags this as "skeptical"
    pub timestamp: u64,
}

/// Feature suggestion — rooms can propose new matrix features.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FeatureSuggestion {
    pub ticker: String,
    pub feature_name: String,        // e.g., "lithium_correlation"
    pub source: String,              // e.g., "earnings_call_analysis"
    pub urgency: f64,                // [0, 1]
    pub sample_data: Vec<f64>,       // 20 data points for initialization
}

#[async_trait]
pub trait RoomAgent: Send + Sync {
    /// The main analysis tick. The room reads its slice from the matrix
    /// and produces a proposal.
    async fn analyze(
        &self,
        matrix_snapshot: &MatrixSnapshot,
        feature_slice: Option<Array2<f32>>,
        cross_section: Option<Array1<f32>>,
    ) -> RoomProposal;

    /// Receive a symmetry alert from the matrix.
    async fn on_symmetry_alert(
        &self,
        peer_ticker: &str,
        symmetry_score: f64,
        topology: &TopologicalSignature,
    );

    /// Suggest a new feature to the matrix engine.
    async fn suggest_feature(&self, suggestion: FeatureSuggestion);

    /// Set a stock-specific regime label.
    async fn set_regime(&mut self, label: String);

    /// Update the room's narrative (qualitative context).
    async fn update_narrative(&mut self, narrative: String);
}
```

---

## 3. Veto Engine Interface

The Veto Engine aggregates room proposals into a final position vector.

```rust
/// A single stock's final position (after veto).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FinalPosition {
    pub ticker: String,
    pub weight: f64,            // Final allocation [-1.0, 1.0]
    pub raw_gate: TernaryGate,  // What the room wanted
    pub veto_applied: Vec<String>, // Which SAEP constraints fired
    pub veto_severity: f64,     // [0 = no veto, 1 = full veto]
}

/// The final portfolio output.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PortfolioVector {
    pub positions: Vec<FinalPosition>,
    pub gross_exposure: f64,
    pub net_exposure: f64,
    pub sector_concentrations: HashMap<String, f64>,
    pub portfolio_var: f64,
    pub timestamp: u64,
}

/// A SAEP constraint pattern.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SaepConstraint {
    pub id: String,
    pub layer: GovernanceLayer,  // Room | Sector | Portfolio | Market
    pub check_fn: fn(&RoomProposal, &HashMap<String, f64>) -> Result<(), Violation>,
    pub action: SaepAction,      // Warn | Limit | Veto | Freeze
    pub escalate_to: Option<GovernanceLayer>,
}

#[async_trait]
pub trait VetoEngine: Send + Sync {
    /// Register a SAEP constraint.
    async fn register_constraint(&mut self, constraint: SaepConstraint);

    /// Process all room proposals and produce the final portfolio.
    async fn resolve(
        &self,
        proposals: &[RoomProposal],
        current_portfolio: Option<&PortfolioVector>,
    ) -> PortfolioVector;

    /// Get current portfolio state.
    async fn get_portfolio(&self) -> PortfolioVector;

    /// Emergency freeze — halts all actions.
    async fn freeze(&mut self, reason: &str);

    /// Unfreeze.
    async fn unfreeze(&mut self, reason: &str);
}
```

---

## 4. Hybrid Bridge (Communication Layer)

The bridge connects the three layers via a shared in-memory channel.

```rust
/// Messages sent between the Matrix Engine and Room Agents.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum HybridMessage {
    /// From Matrix to all Rooms: new snapshot available
    SnapshotBroadcast(MatrixSnapshot),
    /// From Room to Veto: new proposal
    ProposalSubmission(RoomProposal),
    /// From Room to Matrix: feature suggestion
    FeatureSuggestion(FeatureSuggestion),
    /// From Veto to all: final portfolio vector
    PortfolioVectorBroadcast(PortfolioVector),
    /// From Matrix to specific Room: slice update
    SliceUpdate { ticker: String, data: Array2<f32> },
    /// Symmetry alert broadcast
    SymmetryAlert { tickers: Vec<String>, score: f64 },
    /// System event (freeze, error, etc.)
    SystemEvent { kind: String, payload: String },
}

/// The bridge manager.
pub struct HybridBridge {
    /// Channel to broadcast Matrix snapshots to all rooms.
    matrix_tx: broadcast::Sender<HybridMessage>,
    /// Channel for rooms to submit proposals to Veto.
    proposal_tx: mpsc::Sender<RoomProposal>,
    /// Channel for rooms to suggest features to Matrix.
    feature_tx: mpsc::Sender<FeatureSuggestion>,
    /// Channel for Veto to broadcast portfolio.
    veto_tx: broadcast::Sender<HybridMessage>,
}

impl HybridBridge {
    pub fn new() -> Self { /* ... */ }

    /// Subscribe a room agent to matrix broadcasts.
    pub fn subscribe_matrix(&self) -> broadcast::Receiver<HybridMessage> {
        self.matrix_tx.subscribe()
    }

    /// Submit a proposal (room → veto).
    pub async fn submit_proposal(&self, proposal: RoomProposal) {
        self.proposal_tx.send(proposal).await.ok();
    }

    /// Broadcast portfolio (veto → all).
    pub async fn broadcast_portfolio(&self, portfolio: PortfolioVector) {
        self.veto_tx.send(HybridMessage::PortfolioVectorBroadcast(portfolio)).ok();
    }
}

#[async_trait]
pub trait HybridEngine: Send + Sync {
    /// Run one full hybrid cycle: Matrix → Rooms → Veto.
    async fn hybrid_cycle(&self, tick: u64);

    /// Start the main event loop.
    async fn run(&self);

    /// Graceful shutdown.
    async fn shutdown(&self);
}
```

---

## 5. Error Handling

```rust
#[derive(Debug, thiserror::Error)]
pub enum HybridError {
    #[error("Ticker {0} not found in matrix")]
    TickerNotFound(String),

    #[error("Feature tensor dimension mismatch: expected {expected}, got {actual}")]
    DimensionMismatch { expected: usize, actual: usize },

    #[error("TDA computation failed: {0}")]
    TdaError(String),

    #[error("Matrix snapshot too old: {elapsed}ms")]
    StaleSnapshot { elapsed: u64 },

    #[error("Veto freeze active: {reason}")]
    Frozen { reason: String },

    #[error("Bridge channel closed")]
    ChannelClosed,

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}
```

---

## 6. Performance Targets

| Operation | Target | Hardware | Notes |
|-----------|--------|----------|-------|
| Matrix ingest (1 tick) | < 3ms | ARM64 | Memory-bound |
| Medium cycle | < 500ms | ARM64 | Every 5 ticks |
| Full cycle | < 5s | ARM64 | Every 20-60 ticks |
| Room analysis | < 100ms | ARM64 | Async LLM batch |
| Veto resolution (5000 rooms) | < 10ms | ARM64 | Pure logic |
| End-to-end hybrid cycle | < 1s | ARM64 | Fast path only |
| New ticker registration | < 100ms | ARM64 | Row append |

---

## 7. Cargo Integration

```toml
[package]
name = "hybrid-bridge"
version = "0.1.0"
edition = "2021"

[dependencies]
pincher-core = { path = "../pincher-core" }
ternary-types = { git = "https://github.com/SuperInstance/ternary-types" }
ndarray = "0.16"
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
thiserror = "1"
tracing = "0.1"
arrow = { version = "53", features = ["ipc"] }

[lib]
name = "hybrid_bridge"
path = "src/lib.rs"
```
