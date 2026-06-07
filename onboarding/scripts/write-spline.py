#!/usr/bin/env python3
"""Write a promotion spline."""
import json, sys, os

output_dir = sys.argv[1]
title = sys.argv[2]
insight = sys.argv[3]
anchors_raw = sys.argv[4] if len(sys.argv) > 4 else ""
resonates_raw = sys.argv[5] if len(sys.argv) > 5 else ""

anchors = [a.strip() for a in anchors_raw.split(",") if a.strip()]
resonates = [r.strip() for r in resonates_raw.split(",") if r.strip()]

from datetime import datetime, timezone
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
slug = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
filename_slug = title.lower().replace(" ", "-").replace("--", "-")

spline = {
    "title": title,
    "insight": insight,
    "anchors": anchors,
    "resonates_with": resonates,
    "origin": f"market-manifold CI/CD — {ts}",
    "negative_space": "This spline is NOT a certificate of omniscience. The promotion means competence in tested areas, not universal capability."
}

os.makedirs(output_dir, exist_ok=True)
filename = f"{slug}-{filename_slug}.spline"
path = os.path.join(output_dir, filename)
with open(path, "w") as f:
    json.dump(spline, f, indent=2)

print(f"Spline written: {path}")
