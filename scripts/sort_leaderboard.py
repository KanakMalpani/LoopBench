#!/usr/bin/env python3
"""Fix leaderboard sort order for CI."""
import json
from pathlib import Path

path = Path("leaderboard/entries.json")
data = json.loads(path.read_text(encoding="utf-8"))
data["entries"].sort(key=lambda e: e["composite"]["rank_score"], reverse=True)
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("sorted", [e["composite"]["rank_score"] for e in data["entries"]])
