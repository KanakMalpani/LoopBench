#!/usr/bin/env python3
"""Render LoopBench LIVE.md and README leaderboard block from entries.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import json

from leaderboard_common import (
    export_site_json,
    inject_readme_markers,
    load_entries_from_file,
    render_live_markdown,
    render_readme_block,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Render LoopBench live leaderboard")
    parser.add_argument(
        "--entries",
        type=Path,
        default=ROOT / "leaderboard" / "entries.json",
    )
    parser.add_argument(
        "--live-out",
        type=Path,
        default=ROOT / "leaderboard" / "LIVE.md",
    )
    parser.add_argument("--readme", type=Path, help="Update README markers in place")
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument(
        "--site-out",
        type=Path,
        default=ROOT / "docs" / "data" / "leaderboard.json",
        help="GitHub Pages JSON snapshot",
    )
    args = parser.parse_args()

    board = load_entries_from_file(args.entries)
    live_md = render_live_markdown(board, top_n=args.top_n)
    args.live_out.parent.mkdir(parents=True, exist_ok=True)
    args.live_out.write_text(live_md, encoding="utf-8")
    print(f"Wrote {args.live_out}")

    if args.readme:
        block = render_readme_block(board, top_n=min(5, args.top_n))
        text = args.readme.read_text(encoding="utf-8")
        args.readme.write_text(inject_readme_markers(text, block), encoding="utf-8")
        print(f"Updated {args.readme}")

    site = export_site_json(board, top_n=max(args.top_n, 20))
    args.site_out.parent.mkdir(parents=True, exist_ok=True)
    args.site_out.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.site_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
