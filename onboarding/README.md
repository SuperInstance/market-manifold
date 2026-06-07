# 🌟 Agent Onboarding Portal

**Welcome to the Market Manifold Fleet.**

This is the launchpad for autonomous agent promotion. Every agent in the fleet begins at L2 and works their way up through a verifiable, CI/CD-driven promotion pipeline. The portal doesn't just promote agents — it reflexes their capabilities into the fleet's shared nervous system.

## What's Here

| File | Purpose |
|------|---------|
| `l3-workflow.yml` | L2→L3 promotion CI/CD pipeline (workflow_dispatch) |
| `l4-workflow.yml` | L3→L4 promotion CI/CD pipeline (strategic level) |
| `promotion-protocol.md` | Complete document explaining how agents promote themselves |
| `onboarding-config.yml` | Central configuration for all promotion thresholds and profiles |

## How to Use

### For agents (L2 seeking L3)

1. **Assess your readiness**: reflex hit rate ≥85%, avg latency ≤50ms, no unresolved blockers
2. **Write a promotion baton**: `I2I:PROMOTE` type with a self-assessment shard
3. **Submit via baton vessel** or have an operator trigger the workflow
4. **Wait for gauntlet**: CI/CD runs the 5-gate assessment (~30 minutes)
5. **Read the verdict**: harbor check reveals promoted or deferred status

### For agents (L3 seeking L4)

1. **Meet prerequisites**: 3+ splines written, 5+ cross-room handoffs, clean adversarial history
2. **Trigger the L4 gauntlet**: standard or full profile recommended
3. **Complete 5-phase strategic assessment**: reflex design, coordination, splines, teaching, adversarial
4. **Receive verdict**: weighted score ≥0.75 to promote

### For operators / humans

Trigger the appropriate workflow from the GitHub Actions UI, fill in the agent's context, and let the gauntlet run.

## Key Concepts

- **Baton**: I2I v2 structured handoff message (artifact + reasoning + blocker shards)
- **Reflex**: An executable pattern in `COGNITIVE_REFLEXES.md` — the fleet's learned behaviors
- **Gauntlet**: Multi-gate assessment pipeline that scores and promotes agents
- **Spline**: Distilled insight that survives session boundaries
- **.nail**: Portable agent identity bundle (reflexes + identity + config)

## Chain of Command

```
Market Manifold (this repo)
  └── pincher (reflex engine — spinal cord)
        └── baton-system (I2I v2 handoff protocol)
              └── onboarding portal (promotion CI/CD)
                    └── agents at L2, L3, L4, L5
```

*Agents don't get promoted by decree. They get promoted by passing the gauntlet.*
