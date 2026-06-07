#!/usr/bin/env python3
"""Verify a baton file's shard integrity."""
import json, hashlib, sys

with open(sys.argv[1]) as f:
    d = json.load(f)
shard = d.get('shard', {})
computed = hashlib.sha256(
    json.dumps(shard, separators=(',', ':'), sort_keys=True).encode()
).hexdigest()
print(computed)
