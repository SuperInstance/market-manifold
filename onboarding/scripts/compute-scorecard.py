#!/usr/bin/env python3
"""Compute overall promotion scorecard from per-gate JSON results."""
import json, os, sys

results_dir = sys.argv[1] if len(sys.argv) > 1 else "promotion-results"

# Map of result files to gate names
gate_files = {
    "reflex-coverage": "reflex-coverage.json",
    "latency": "latency-benchmarks.json",
    "baton-protocol": "baton-compliance.json",
    "sandbox": "sandbox-integrity.json",
    "self-assessment": "self-assessment.json",
}

weight_map = {
    "reflex-coverage": 0.25,
    "latency": 0.25,
    "baton-protocol": 0.20,
    "sandbox": 0.15,
    "self-assessment": 0.15,
}

gates = {}
total_weighted = 0.0
total_weight = 0.0

for gate_name, filename in gate_files.items():
    path = os.path.join(results_dir, filename)
    if not os.path.exists(path):
        continue
    with open(path) as f:
        data = json.load(f)
    result = "PASS" if data.get("result") == "PASS" else "FAIL"
    weight = weight_map.get(gate_name, 0.2)
    score = data.get("score", 0)

    total_weighted += score * weight
    total_weight += weight

    gates[gate_name.replace("-", " ").title()] = result

passed = sum(1 for g in gates.values() if g == "PASS")
total = len(gates)
overall = "PASS" if (total > 0 and passed / total >= 0.8) else "FAIL"

scorecard = {
    "gates": gates,
    "passed": passed,
    "total": total,
    "overall": overall,
    "pct": round(passed / total * 100, 1) if total > 0 else 0.0,
    "weighted_score": round(total_weighted / total_weight, 3) if total_weight > 0 else 0.0,
}

with open(os.path.join(results_dir, "overall-score.json"), "w") as f:
    json.dump(scorecard, f, indent=2)

print(json.dumps(scorecard, indent=2))
