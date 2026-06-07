#!/usr/bin/env python3
"""Write the promotion record JSON from gauntlet results."""
import json, hashlib, sys, os

results_dir = sys.argv[1]
agent_name = sys.argv[2]
agent_role = sys.argv[3]
agent_model = sys.argv[4]
agent_source = sys.argv[5]
target_level = sys.argv[6]
run_id = sys.argv[7]
gauntlet_profile = sys.argv[8]

from datetime import datetime, timezone
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Load scorecard
scorecard_path = os.path.join(results_dir, "overall-score.json")
if os.path.exists(scorecard_path):
    with open(scorecard_path) as f:
        scorecard = json.load(f)
else:
    scorecard = {"passed": 0, "total": 0, "pct": 0}

# Load reflex diff
diff_path = os.path.join(results_dir, "reflex-diff.json")
reflex_diff = {}
if os.path.exists(diff_path):
    with open(diff_path) as f:
        reflex_diff = json.load(f)

record = {
    "record_type": "I2I:PROMOTE",
    "protocol_version": "2.0",
    "agent": {
        "name": agent_name,
        "role": agent_role,
        "model": agent_model,
        "source": agent_source
    },
    "from_level": "L2" if target_level in ["L3", "L4"] else "L3",
    "to_level": target_level,
    "promoted_at": ts,
    "promoted_by": "market-manifold-ci",
    "run_id": run_id,
    "gauntlet_profile": gauntlet_profile,
    "gates_passed": scorecard.get("passed", 0),
    "gates_total": scorecard.get("total", 0),
    "score_pct": scorecard.get("pct", 0),
    "reflex_diff": reflex_diff
}

# Compute integrity
shard = {
    "artifacts": record["agent"],
    "reasoning": [f"Promoted to {target_level}"],
    "blockers": []
}
integrity = hashlib.sha256(
    json.dumps(shard, separators=(",", ":"), sort_keys=True).encode()
).hexdigest()
record["integrity"] = integrity

record_path = os.path.join(results_dir, "promotion-record.json")
with open(record_path, "w") as f:
    json.dump(record, f, indent=2)

print(json.dumps(record, indent=2))
