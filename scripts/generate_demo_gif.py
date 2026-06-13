"""Generate a terminal-style demo GIF for the LoopBench README."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demo.gif"

FRAMES = [
    "$ pip install git+https://github.com/KanakMalpani/LoopGym.git",
    "$ pip install git+https://github.com/KanakMalpani/LoopBench.git",
    "$ loopbench list",
    "LoopBench tasks:",
    "  LB-CR-1",
    "  LB-RS-1",
    "  LB-MA-1",
    "$ loopbench run --task LB-CR-1 \\",
    "    --spec submissions/examples/spec-fast-loop.yaml \\",
    "    --seeds 0,1 -o results.json",
    "Running LB-CR-1 via LoopGym (backend=sim)...",
    "Wrote results.json",
    "$ loopbench validate results.json",
    "VALID: results.json",
    "$ loopbench rank leaderboard/entries.json",
    "Rank  Submitter                LES  Display  Backend",
    "1     Team Thorough           0.89     89.0      sim",
    "2     Team Fast               0.84     84.0      sim",
]


def _font(size: int = 16):
    for name in ("Consolas.ttf", "cour.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_frame(lines: list[str], width: int = 920, height: int = 420) -> Image.Image:
    img = Image.new("RGB", (width, height), (13, 17, 23))
    draw = ImageDraw.Draw(img)
    font = _font(15)
    y = 24
    for line in lines:
        color = (125, 211, 252) if line.startswith("$") else (201, 209, 217)
        draw.text((24, y), line, fill=color, font=font)
        y += 26
    return img


def capture_live_lines() -> list[str] | None:
    """Try to append real loopbench list output when installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "loopbench.cli", "list"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=30,
            check=False,
        )
        if result.returncode == 0 and result.stderr.strip():
            return FRAMES[:4] + result.stderr.strip().splitlines()
    except Exception:
        pass
    return None


def main() -> None:
    lines = capture_live_lines() or FRAMES
    OUT.parent.mkdir(parents=True, exist_ok=True)
    images: list[Image.Image] = []
    visible: list[str] = []
    for line in lines:
        visible.append(line)
        images.append(render_frame(visible))
        images.append(render_frame(visible))  # hold frame
    images[-1].save(
        OUT,
        save_all=True,
        append_images=images[1:],
        duration=450,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT} ({len(images)} frames)")


if __name__ == "__main__":
    main()
