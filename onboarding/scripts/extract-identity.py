#!/usr/bin/env python3
"""Extract agent identity JSON from a baton file."""
import json, sys

with open(sys.argv[1]) as f:
    d = json.load(f)
shard = d.get('shard', {})
arts = shard.get('artifacts', {})
identity = {
    'name': arts.get('agent_name', d.get('from', 'unknown')),
    'role': arts.get('agent_role', 'unknown'),
    'model': arts.get('agent_model', 'unknown'),
    'source': arts.get('agent_source', 'unknown'),
    'level': d.get('level', 'L3')
}
print(json.dumps(identity))
