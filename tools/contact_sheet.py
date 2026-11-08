#!/usr/bin/env python3
"""Review sheet for rendered art: one labeled grid per size class (cards, floors, icons).

Usage:
  python3 tools/contact_sheet.py images/cards/cast-shelly-anchor-640x640.webp images/floors ...
  python3 tools/contact_sheet.py --plan images/plans/2026-11-08-batch-05.json

Writes <art dir>/<run or "review">/sheet-<class>.png ($AIRPG_ART_DIR, default
~/writing/art/once-upon-agentic-ai/experiments) and prints the paths. Needs Pillow.
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ART_DIR = Path(os.environ.get("AIRPG_ART_DIR",
                              Path.home() / "writing" / "art" / "once-upon-agentic-ai" / "experiments"))
LAYOUT = {"640x640": ("cards", 300, 300, 4), "1200x675": ("floors", 480, 270, 3),
          "1680x720": ("banners", 560, 240, 2), "96x96": ("icons", 96, 96, 8)}


def files_from(args: list[str]) -> list[Path]:
    out = []
    for a in args:
        p = Path(a)
        out += sorted(p.rglob("*.webp")) if p.is_dir() else [p]
    return [p for p in out if p.suffix == ".webp"]


def sheet(items: list[Path], tw: int, th: int, cols: int, dest: Path) -> Path:
    rows = (len(items) + cols - 1) // cols
    label = 14 if tw < 200 else 22
    im = Image.new("RGB", (cols * (tw + 8), rows * (th + label)), (40, 40, 40))
    d = ImageDraw.Draw(im)
    for i, p in enumerate(items):
        x, y = (i % cols) * (tw + 8), (i // cols) * (th + label)
        im.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y))
        d.text((x + 2, y + th + 2), p.stem.split("-640x640")[0].split("-1200x675")[0][: max(12, tw // 7)],
               fill=(255, 255, 255))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--plan", help="review the outputs a plan names")
    a = ap.parse_args()
    run = "review"
    files = files_from(a.paths)
    if a.plan:
        p = json.loads(Path(a.plan).read_text())
        run = p["run"]
        files += [ROOT / r["out"] for r in p["renders"] if (ROOT / r["out"]).exists()]
    if not files:
        ap.print_help(); return 1
    for tag, (name, tw, th, cols) in LAYOUT.items():
        group = [f for f in files if tag in f.name]
        if group:
            print(sheet(group, tw, th, cols, ART_DIR / run / f"sheet-{name}.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
