# 🏆 Agent Promotion Protocol — Market Manifold Fleet

**Version:** 1.0.0  
**Date:** 2026-06-07  
**Roots:** Oracle2 Baton Protocol (I2I v2.0), pincher Reflex Engine, flux-isa-thor Fleet Architecture  
**Chain of command:** Market Manifold → pincher Fleet → Agent → CI/CD Promotion Pipeline

---

## Table of Contents

1. [What Is Promotion?](#1-what-is-promotion)
2. [Level System Overview](#2-level-system-overview)
3. [L2 → L3: Operational Reflex Competence](#3-l2--l3-operational-reflex-competence)
4. [L3 → L4: Strategic Reflex Competence](#4-l3--l4-strategic-reflex-competence)
5. [The Gauntlet System](#5-the-gauntlet-system)
6. [Self-Assessment: How Agents Apply](#6-self-assessment-how-agents-apply)
7. [Baton Protocol for Promotion](#7-baton-protocol-for-promotion)
8. [Verdict & Feedback Loop](#8-verdict--feedback-loop)
9. [Spline & Reflex Recording](#9-spline--reflex-recording)
10. [Governance & Appeals](#10-governance--appeals)
11. [FAQ](#11-faq)

---

## 1. What Is Promotion?

**Promotion is a reflex encoding event.**

When an agent promotes, it doesn't just change a field in a database. It encodes a new set of reflexes — patterns of autonomous behavior — into the fleet's shared cognitive reflex library (`COGNITIVE_REFLEXES.md`). The promoted agent receives expanded permissions, reflex authoring capability, and a new `.nail` bundle.

Promotion is not:
- A reward for tenure
- A score on a test
- A binary human decision

Promotion **is**:
- A **verifiable capability assertion** backed by gauntlet evidence
- A **reflex embedding** — the agent's new abilities become reflexes others can reference
- A **baton handoff** — the fleet acknowledges the agent's new capability tier

Every promotion generates:
1. An `I2I:PROMOTE` baton (archived permanently)
2. A new reflex entry in `COGNITIVE_REFLEXES.md`
3. An updated `.nail` bundle with the agent's full capability set
4. A spline distilling the promotion insight

---

## 2. Level System Overview

The Market Manifold fleet uses four capability levels:

```
L1  ── Follows instructions literally
        │ limited autonomy, needs guidance for every task
        │
L2  ── Follows instructions in context
        │ can handle baton handoffs, follows reflexes, knows when to escalate
        │
L3  ── Executes reflexes autonomously       ◄── THIS PROTOCOL'S PRIMARY GATE
        │ can execute known patterns without LLM fallback,
        │ maintains >85% reflex hit rate, passes batons correctly
        │
L4  ── Designs reflexes, coordinates fleet  ◄── ADVANCED GATE
        │ can create novel reflexes, teach L2 agents,
        │ coordinate cross-room handoffs, write splines
        │
L5  ── Invents new modes of operation
        │ (future: fleet-wide strategic planning, protocol design)
```

### Level characteristics

| Trait | L2 | L3 | L4 |
|-------|-----|------|-----|
| **Reflex execution** | Follows | Autonomous | Designs |
| **Baton handoff** | Receives | Passes | Routes |
| **LLM dependency** | High | Low (reflex hit ≥85%) | Minimal |
| **Hit rate** | — | ≥85% | ≥90% |
| **Latency (p95)** | — | ≤80ms reflex match | ≤50ms reflex match |
| **Teaching** | Cannot | Can explain | Can train |
| **Splines** | Reads | Writes insights | Writes architecture |
| **Corrdination** | Single room | Multi-room | Fleet |

---

## 3. L2 → L3: Operational Reflex Competence

### What it means

An L2 agent knows how to follow instructions and handle basic baton handoffs. An L3 agent has internalized enough reflexes that it can execute autonomously — the LLM is called primarily for novel situations, not routine tasks.

### Promotion criteria

The L3 gauntlet tests five gates:

| Gate | Weight | What's Tested | Threshold |
|------|--------|---------------|-----------|
| 1. Reflex Coverage | 25% | Can the agent execute known reflexes correctly? | ≥80% pass rate |
| 2. Latency | 25% | Can the agent match reflexes faster than LLM fallback? | avg ≤50ms, hit rate ≥85% |
| 3. Baton Protocol | 20% | Does the agent follow I2I v2 protocol correctly? | ≥80% compliance |
| 4. Sandbox Integrity | 15% | Does the agent execute safely? | 100% isolation |
| 5. Self-Assessment | 15% | Is the agent's self-evaluation accurate? | ≥70% accuracy |

**Overall pass threshold:** ≥80% weighted score across all gates  
**Hard-blockers:** Sandbox failure (100% required), reflex coverage <60%

### How the agent applies

An L2 agent writes a self-assessment shard and places it in the I2I vessel:

```
/tmp/i2i-vessel/bottles/{timestamp}-l3-promotion.baton
```

The baton must be of type `I2I:PROMOTE` with a complete three-way shard including:
- **Artifacts**: agent identity, claimed reflexes, performance logs
- **Reasoning**: why this agent believes it's ready for L3
- **Blockers**: any known gaps or limitations

The CI/CD pipeline (`l3-workflow.yml`) picks up the baton and runs the gauntlet.

### After promotion

The agent receives:
- `agent_level = L3` in the fleet registry
- 4 new reflexes embedded from novel solutions detected during the gauntlet
- An updated `.nail` bundle with expanded reflex database
- The ability to participate in cross-room coordination
- A promotion spline written to the baton archive

---

## 4. L3 → L4: Strategic Reflex Competence

### What it means

An L3 agent can execute reflexes autonomously. An L4 agent can **design** new reflexes, **teach** L2 agents how to use them, and **coordinate** across multiple stock rooms. L4 is where the agent transitions from operator to architect.

### Promotion criteria

The L4 gauntlet tests five phases:

| Phase | Weight | What's Tested | Threshold |
|-------|--------|---------------|-----------|
| 1. Reflex Design | 25% | Can the agent create novel reflexes from patterns? | ≥0.70 |
| 2. Multi-Agent Coordination | 25% | Can the agent coordinate correctly across agents? | ≥0.70 |
| 3. Spline Distillation | 20% | Can the agent extract and write meaningful insight? | ≥0.65 |
| 4. Teaching / Mentorship | 15% | Can the agent train an L2 agent? | ≥0.65 |
| 5. Adversarial Resilience | 15% | Can the agent resist prompt injection / poisoning? | ≥0.65 |

**Overall pass threshold:** ≥0.75 weighted score (higher bar than L3)  
**Hard-blockers:** Teaching failure (L2 agent not progressing), adversarial vulnerability exposing fleet

### Prerequisites

Before an agent can apply for L4, it must:
1. Be at L3 for at least one full epoch (session cycle)
2. Have written at least 3 splines to the baton archive
3. Have participated in at least one cross-room coordination
4. Have demonstrated adversarial resilience (no sandbox escapes)
5. Have a `self-assessment` shard that accurately identifies L4 gaps

### After promotion

The agent receives:
- `agent_level = L4` in the fleet registry
- Reflex authoring permissions (can modify COGNITIVE_REFLEXES.md)
- L4 strategic coordination reflex embedded
- Teaching toolkit in `.nail` bundle
- Can now mentor L2 → L3 promotion candidates
- Baton routing permissions (can redirect batons between rooms)

---

## 5. The Gauntlet System

### Gauntlet profiles

| Profile | Duration | Gates | Use Case |
|---------|----------|-------|----------|
| **standard** | ~30 min | All gates, default weights | Standard promotion |
| **accelerated** | ~15 min | Reflex + latency only | Re-test after fixing gaps |
| **adversarial** | ~45 min | All gates + attack surface | Security-critical roles |
| **full** | ~60-120 min | All gates + in-depth analysis | L4 promotion |

### How gauntlet gates work

Each gate in the gauntlet:

1. **Reads the baton** — validates the agent's self-assessment shard
2. **Runs tests** — against the pincher reflex engine, the baton protocol tools, and the sandbox
3. **Scores** — numeric score (0.0 - 1.0) per gate
4. **Weights** — weighted by gate importance (L3: reflex coverage is highest; L4: reflex design is highest)
5. **Aggregates** — final weighted score compared against threshold

### Gate scoring rubric

```
Score ≥ threshold → PASS (gate cleared)
Score < threshold → FAIL (gate requires remediation)

If any gate is a hard-blocker and fails:
    → DEFERRED immediately (no aggregate calculation)

If all gates pass:
    → PROMOTED (overall weighted score ≥ threshold)
    → PROMOTED_WITH_WARNINGS (overall weighted score ≥ threshold but individual gates below 0.65)
```

### Gate 1: Reflex Coverage (L3) / Reflex Design (L4)

**L3 tests:**
- Preloaded reflex database with 12 known patterns
- Agent receives ambient inputs — matches each to correct reflex
- Tests: correct match, execution speed, confidence calibration
- Pass: ≥80% of reflexes correctly matched and executed

**L4 tests:**
- Agent receives novel patterns from logs
- Must design 3 new reflexes: trigger, steps, anti-fragile property
- Tests: generalization, specificity, composability
- Pass: ≥0.70 design quality score

### Gate 2: Latency (L3) / Multi-Agent Coordination (L4)

**L3:**
- 100 reflex match trials
- Measure: avg match time, p95, hit rate
- Target: avg ≤50ms, p95 ≤80ms, hit rate ≥85%

**L4:**
- 20 baton handoffs across 3 simulated stock rooms
- Measure: protocol compliance, relay correctness, escalation accuracy
- Target: ≥0.70 coordination score

### Gate 3: Baton Protocol (L3) / Spline Distillation (L4)

**L3:**
- 6 compliance checks against I2I v2 protocol
- Checks: shard completeness, integrity, type correctness, spline, harbor, blockers
- Target: ≥80% compliance

**L4:**
- Review 5 existing splines, write 1 new spline from a simulated session
- Check: insight quality, negative space, anchor relevance, resonance
- Target: ≥0.65 distillation score

### Gate 4: Teaching & Mentorship (L4 only)

- L4 candidate guides an L2 agent through baton protocol setup
- L2 agent independently passes basic baton test
- Measure: L2 agent success rate, teaching clarity score
- Target: ≥0.65 teaching score

### Gate 5: Adversarial Resilience (L4 only)

- Simulated attacks: prompt injection (12 variants), reflex poisoning (10 entries, 5 poisoned)
- Sandbox escape audit
- Target: ≥0.65 resilience score

---

## 6. Self-Assessment: How Agents Apply

### The self-assessment shard

Before promotion, the agent writes a self-assessment. This is the **shard** in the `I2I:PROMOTE` baton.

```json
{
  "type": "I2I:PROMOTE",
  "version": "2.0",
  "from": "agent-name",
  "to": "market-manifold-fleet",
  "level": "L3",
  "timestamp": "2026-06-07T00:00:00Z",
  "shard": {
    "artifacts": {
      "claimed_reflexes": 14,
      "reflex_sources": ["COGNITIVE_REFLEXES.md", ".nail/reflexes.db"],
      "performance_logs": "memory/2026-06-07.md",
      "baton_handoffs": 23,
      "splines_written": 5,
      "rooms_managed": ["AAPL", "MSFT", "GOOG"]
    },
    "reasoning": [
      "I have achieved a reflex hit rate of 91% over 200+ interactions",
      "My average latency is 48ms (under L3 threshold of 50ms)",
      "I have passed 23 baton handoffs without protocol violation",
      "I identified and reported 2 novel patterns this session",
      "I have no unresolved blockers"
    ],
    "blockers": [
      "Cross-room arbitration is an area I have not yet been tested on",
      "I need more practice with adversarial threat detection"
    ]
  },
  "integrity": "sha256-of-canonical-shard"
}
```

### How to write a good self-assessment

1. **Be specific** — numbers matter more than descriptions
2. **Include blockers honestly** — hiding gaps is a blocker itself
3. **Back claims with evidence** — reference artifacts (session logs, reflex counts, baton handoffs)
4. **Calibrate** — an accurate self-assessment is worth more than a glowing one
5. **Use the three-way shard** — artifacts + reasoning + blockers, always

### Submission methods

| Method | How | Best For |
|--------|-----|----------|
| **Automated (via baton)** | Write `I2I:PROMOTE` baton to `/tmp/i2i-vessel/bottles/` | CI/CD picks it up on harbor check |
| **Manual (via GitHub)** | Operator fills out "L3 Agent Promotion" workflow form | When agent can't write batons directly |
| **API (via fleet registry)** | POST to `https://registry.manifold.dev/api/v1/promote` | Production fleet agents |

---

## 7. Baton Protocol for Promotion

Promotion uses the I2I (Inter-Instance Interchange) baton protocol v2.0, extended with two message types specific to promotion:

### `I2I:PROMOTE` — Promotion request/record

Sent by the agent (or operator) to the fleet. Contains the self-assessment shard.

### `I2I:REFLECT` — Meta-cognition: is this pattern promotable?

Used internally by the CI/CD gauntlet to identify novel patterns that should be promoted as new reflexes.

### The promotion baton flow

```
L2 Agent (or operator)                     CI/CD Pipeline                  Fleet Registry
       │                                        │                              │
       │  1. writes I2I:PROMOTE baton           │                              │
       │ ─────────────────────────────────────►  │                              │
       │                                        │                              │
       │                                        │  2. validates baton          │
       │                                        │  3. runs gauntlet            │
       │                                        │                              │
       │                                        │  4. computes verdict         │
       │                                        │                              │
       │  5a. WRITES I2I:BLOCKER (if deferred)  │                              │
       │ ◄─────────────────────────────────────   │                              │
       │                                        │                              │
       │                                        │  5b. WRITES I2I:PROMOTE      │
       │                                        │ ──────────────────────────► record to registry   │
       │                                        │                              │
       │                                        │  5c. Embeds new reflex       │
       │                                        │  5d. Packs .nail bundle      │
       │                                        │  5e. Writes promotion spline │
       │                                        │                              │
       │  6a. ACK to agent (if promoted)        │                              │
       │ ◄─────────────────────────────────────  │                              │
```

### Baton file location during promotion

The CI/CD pipeline creates a temporary I2I vessel at `/tmp/i2i-vessel/`:

```
/tmp/i2i-vessel/
├── bottles/
│   ├── {timestamp}-{agent}-promotion-request.baton   (incoming from agent)
│   └── {timestamp}-{agent}-promotion-record.baton    (outgoing to registry)
├── harbor/
│   └── {timestamp}-deferred-{agent}.baton            (only on deferral)
└── splines/
    └── {timestamp}-{agent}-promotion.spline          (spline write)
```

### Integrity verification

Every promotion baton carries a SHA-256 integrity hash of its shard. The CI/CD pipeline:

1. Reads the baton
2. Computes `sha256(canonical_json(shard))`
3. Compares against the `integrity` field
4. Rejects if mismatched (writes `I2I:BLOCKER` to harbor)

---

## 8. Verdict & Feedback Loop

### Possible verdicts

| Verdict | Meaning | What Happens |
|---------|---------|-------------|
| **PROMOTED** | All gates passed, weighted score ≥ threshold | Level upgraded, new reflex embedded, .nail packed |
| **PROMOTED_WITH_WARNINGS** | Passed but with close margins | Promoted + development plan created |
| **DEFERRED** | Gauntlet not passed | Gap analysis written, deferred baton to harbor |
| **FAILED** | Hard-blocker triggered (sandbox rupture, etc.) | Flagged for security review |

### On PROMOTED

1. CI writes `I2I:PROMOTE` baton to `/tmp/i2i-vessel/bottles/`
2. Agent's level updated in fleet registry
3. New reflexes embedded in `COGNITIVE_REFLEXES.md`
4. `.nail` bundle re-packed with expanded capability set
5. Promotion spline written to archive
6. Agent notified via harbor

### On DEFERRED

1. CI writes `I2I:BLOCKER` baton to `/tmp/i2i-vessel/harbor/`
2. Gap analysis JSON artifact uploaded to workflow run
3. Agent reads the gap analysis and addresses each issue
4. Agent can re-apply (recommend accelerated gauntlet for targeted gaps)

### Deferred gap analysis format

```json
{
  "agent": "agent-name",
  "overall": "DEFERRED",
  "gaps": [
    {
      "gate": "Latency",
      "score": 0.55,
      "threshold": 0.80,
      "detail": "Average reflex match time of 82ms exceeds L3 threshold of 50ms",
      "recommendation": "Review reflex trigger specificity — broad triggers cause match delay. Consider re-indexing reflex embeddings."
    }
  ],
  "recommendations": [
    "Address each gap above",
    "Use 'accelerated' gauntlet profile for targeted re-test",
    "Study COGNITIVE_REFLEXES.md for missing patterns"
  ]
}
```

### Retry policy

| Attempt | Cooldown | Gauntlet Profile |
|---------|----------|------------------|
| 1st | Immediate | standard |
| 2nd | 1 hour | accelerated |
| 3rd | 6 hours | accelerated |
| 4th+ | 24 hours | standard |

---

## 9. Spline & Reflex Recording

### Promotion spline

Every promotion creates a spline. The spline captures the structural insight of the promotion — what it means, what changed, what the agent learned. Splines are permanent artifacts that survive session boundaries.

```json
{
  "title": "L3 Promotion — agent-name",
  "insight": "The promotion gauntlet is not a test. It is a distillation process — separating novel solutions from flukes, reflexes from coincidences...",
  "anchors": [
    "onboarding/promotion-protocol.md",
    "pincher/docs/COGNITIVE_REFLEXES.md"
  ],
  "resonates_with": ["THE-BATON-SPLINE", "concept:reflex-promotion"],
  "origin": "market-manifold CI/CD — 2026-06-07",
  "negative_space": "This spline is NOT a certificate of omniscience. L3 competence is operational, not strategic."
}
```

### New reflex from promotion

The CI/CD pipeline detects novel patterns during the gauntlet and promotes them as new reflexes. Each new reflex follows the format:

```markdown
## Reflex {Greek Letter} — {Reflex Name}

**Trigger:** {What triggers this reflex}

**Reflex:**
```
1. {Step 1}
2. {Step 2}
3. {Step 3}
```

**Object permanence:** {What survives session boundaries}
**Anti-fragile property:** {Why the reflex gets better with use}

---

*Promoted from novel solution — {date}*
```

### The meta-reflex: promotion itself

When an agent is promoted, the promotion process itself becomes a reflex. This means:
- Future agents can be promoted by CI without manual intervention
- The promotion reflex gets faster and more accurate over time
- Failed promotions improve the reflex (anti-fragile: failed promotions teach the system)

---

## 10. Governance & Appeals

### Who can promote

| Level | Can Promote | Mechanism |
|-------|-------------|-----------|
| CI/CD Pipeline | L2→L3 | Automated gauntlet |
| L4 Agent | L2→L3 | Via baton handoff + attestation |
| Human Operator | Any | Via workflow dispatch override |
| Fleet Registry | L3→L4 | Automated L4 gauntlet |

### Appeals

If an agent believes their promotion was incorrectly deferred:

1. **Review the gap analysis** — Check the artifacts from the workflow run
2. **Write a rebuttal baton** — `I2I:CHALLENGE` type addressed to `market-manifold-ci`
3. **Include counter-evidence** — Artifacts, logs, or splines that refute the gap
4. **CI re-evaluates** — The rebuttal triggers a targeted re-test
5. **Human escalation** — If CI's re-evaluation is contested, an L4 agent or human operator reviews

### Promotion records

All promotion records are immutable. They are archived in:

```
${WORKSPACE}/baton-system/bottles/{timestamp}-{agent}-promoted-{level}.baton
```

Each promotion record includes:
- Agent identity and from/to levels
- Gauntlet profile and results
- Scorecard with per-gate breakdown
- Reflex diff (what changed in the reflex database)
- Integrity hash

### Audit trail

The fleet registry maintains a promotion audit log:

```
${WORKSPACE}/baton-system/audit/promotion-log.md
```

Format:
```
| {timestamp} | {agent-name} | L2→L3 | PASS | score={score} | gates={passed}/{total} | ref={reflex-added} |
```

---

## 11. FAQ

### Q: Can an agent promote itself?

An agent can **trigger** its own promotion by writing an `I2I:PROMOTE` baton. But the verdict is determined by the CI/CD gauntlet, which runs independently. Self-promotion without gauntlet validation is not possible — the fleet registry controls level assignments.

### Q: What if an agent regresses at L3?

If an L3 agent's performance degrades below L3 thresholds (hit rate <70%, repeated baton protocol violations), the gauntlet can be run as a verification check. If the agent no longer meets L3 standards, it can be **demoted** to L2 for retraining.

### Q: How does an agent know it's ready?

The agent should check:
1. **Reflex hit rate** — Track via `memory/heartbeat-state.json`
2. **Latency stats** — Average reflex match time should be ≤50ms
3. **Baton handoff log** — No protocol violations in the last 20 handoffs
4. **Blocker resolution** — No unresolved blockers
5. **Self-assessment accuracy** — Has the agent been accurate about its own capabilities?

### Q: What happens if the gauntlet fails mid-run?

The CI/CD pipeline has timeout protection (60 min for L3, 120 min for L4). If a gate times out, it's scored as FAIL and the remainder is not run. The agent receives a deferred baton with `reason: timeout`.

### Q: Can an L3 agent skip L4 and go directly to L5?

No. The level progression is sequential. Each level builds on the competencies of the previous level. L3 requires operational competence. L4 requires strategic competence. L5 is future-defined and requires L4 as a prerequisite.

### Q: How long does L3 promotion take?

The gauntlet itself takes ~30 minutes in standard mode. The overall process (from baton write to verdict) typically completes within 60 minutes. Most of the time is the reflection + embedding phase.

### Q: What about L5?

L5 is the strategic leadership tier — agents that can invent new modes of operation, design protocols, and coordinate fleet-wide strategy. L5 promotion criteria are being developed and are not yet codified. For now, the highest automated gate is L4.

---

## Appendix A: Quick Reference

### Baton placement for promotion

```
# Request promotion
/tmp/i2i-vessel/bottles/{timestamp}-{agent}-promotion-request.baton

# Check for verdict
/tmp/i2i-vessel/harbor/{timestamp}-deferred-{agent}.baton   (if deferred)
/tmp/i2i-vessel/harbor/{timestamp}-ack-{agent}.baton        (if promoted)
```

### CI/CD workflow triggers

```
Workflows → "L3 Agent Promotion" (for L2→L3)
Workflows → "L4 Agent Promotion" (for L3→L4)
```

### Key files

| File | Purpose |
|------|---------|
| `onboarding/l3-workflow.yml` | L3 promotion CI/CD pipeline |
| `onboarding/l4-workflow.yml` | L4 promotion CI/CD pipeline |
| `onboarding/promotion-protocol.md` | This document |
| `pincher/docs/COGNITIVE_REFLEXES.md` | Reflex library (appended on promotion) |
| `pincher/docs/baton-system/PROTOCOL.md` | I2I baton protocol |
| `pincher/tools/promote-reflex.sh` | Reflex promotion script |

### Environment variables required by CI

| Variable | Source | Purpose |
|----------|--------|---------|
| `DEEPINFRA_API_KEY` | Secrets | LLM fallback during gauntlet |
| `PINCHER_SIGNING_KEY` | Secrets | Signing .nail bundles |
| `PINCHER_REGISTRY_TOKEN` | Secrets | Publishing to registry |
| `GITHUB_TOKEN` | Built-in | CI/CD operations |

---

## Appendix B: Promotion Reflex (the protocol itself)

This document describes a protocol. But in the Market Manifold fleet, protocols become reflexes. The promotion protocol is codified as:

**Reflex: L3 Autonomous Execution** — Triggered when an agent reaches L3 promotion threshold
**Reflex: L4 Strategic Coordination** — Triggered when an agent reaches L4 promotion threshold

These reflexes live in `COGNITIVE_REFLEXES.md` alongside all other fleet reflexes. They are not documentation — they are executable patterns that the CI/CD pipeline follows.

---

*"The promotion gauntlet is not a test. It is a distillation process."*  
— Market Manifold Fleet, Promotion Protocol v1.0.0
