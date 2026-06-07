#!/usr/bin/env python3
"""Summarize a baton's shard contents."""
import json, sys

with open(sys.argv[1]) as f:
    d = json.load(f)
shard = d.get('shard', {})
blockers = shard.get('blockers', [])
summary = {
    'artifacts': len(shard.get('artifacts', {})),
    'reasoning_steps': len(shard.get('reasoning', [])),
    'blockers': len(blockers),
    'clear_to_proceed': len(blockers) == 0
}
print(json.dumps(summary))
