#!/usr/bin/env python3
"""Animated payoffs for the markdown pages: small looping webp clips made from shipped art.

No model calls: every clip is built with Pillow from a card, icon or sprite already in images/.
Each clip ships with a still (its rest frame), so pages can honor prefers-reduced-motion with
the <picture> pattern in workshop/_snippets.md.

Effects (issue #6: at most 480 px, 6 to 12 frames, under 1.5 MB):
  offbeat   a card loses the beat: wobble, tilt and a desaturate pulse      (cards, sprites)
  loot-pop  a loot box or token pops in with a glow ring                    (icons)
  benched   a card drains to grey from the top and dims, then holds         (cards)
  ink       Barnaby's Ink Cloud: black smoke blooms over the image and clears (cards, plates)

Usage:
  python3 tools/motion.py offbeat images/cards/opponent-accountant-offbeat-640x640.webp
  python3 tools/motion.py loot-pop images/icons/loot-gold-96x96.webp
  python3 tools/motion.py --all            every effect listed in images/plans/motion.json

Writes images/motion/<stem>-<effect>.webp, <stem>-<effect>-still.webp and a sidecar each.
"""
from __future__ import annotations
import argparse, json, math, random, sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageSequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from airpg_render import ART_DIR, ROOT, rel, sha256_file  # noqa: E402

OBSIDIAN = (11, 14, 20)
MAGENTA = (255, 43, 214)
TEAL = (31, 191, 117)
OUT_DIR = ROOT / "images" / "motion"
PLAN = ROOT / "images" / "plans" / "motion.json"
FRAME_MS = 90


def base(src: Path, size: int) -> Image.Image:
    im = Image.open(src).convert("RGBA")
    s = size / max(im.size)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def on_canvas(im: Image.Image, size: tuple[int, int], dx=0, dy=0, angle=0.0, scale=1.0) -> Image.Image:
    c = Image.new("RGBA", size, OBSIDIAN + (255,))
    w = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    if angle:
        w = w.rotate(angle, resample=Image.BICUBIC, expand=True)
    c.alpha_composite(w, ((size[0] - w.width) // 2 + dx, (size[1] - w.height) // 2 + dy))
    return c


def offbeat(src: Path) -> list[Image.Image]:
    im = base(src, 400)
    size = (440, 440 * im.height // im.width + 40)
    frames = []
    for i in range(10):
        t = i / 10 * 2 * math.pi
        f = on_canvas(im, size, dx=round(7 * math.sin(t * 2)), dy=round(3 * math.sin(t)), angle=4 * math.sin(t))
        grey = ImageEnhance.Color(f).enhance(0.55 + 0.45 * (1 + math.cos(t)) / 2)  # loses color off the beat
        frames.append(grey)
    return frames


def loot_pop(src: Path) -> list[Image.Image]:
    im = base(src, 120)
    size = (192, 192)
    frames = []
    curve = [0.5, 0.8, 1.12, 1.2, 1.08, 0.98, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    for i, s in enumerate(curve):
        f = on_canvas(im, size, scale=s)
        ring = Image.new("RGBA", size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ring)
        r = 40 + i * 6
        a = max(0, 200 - i * 18)
        d.ellipse((96 - r, 96 - r, 96 + r, 96 + r), outline=MAGENTA + (a,), width=4)
        frames.append(Image.alpha_composite(f, ring.filter(ImageFilter.GaussianBlur(1.5))))
    return frames


def benched(src: Path) -> list[Image.Image]:
    im = on_canvas(base(src, 400), (400, 400))
    grey = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.0)).enhance(0.6)
    frames = []
    for i in range(12):
        k = min(1.0, i / 8)
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rectangle((0, 0, im.width, round(im.height * k)), fill=255)
        frames.append(Image.composite(grey, im, mask.filter(ImageFilter.GaussianBlur(12))))
    return frames


def ink(src: Path) -> list[Image.Image]:
    im = base(src, 440)
    size = im.size
    rnd = random.Random(7)  # fixed seed: the same clip every run
    blobs = [(rnd.uniform(0.2, 0.8) * size[0], rnd.uniform(0.3, 0.8) * size[1], rnd.uniform(0.4, 1.0)) for _ in range(9)]
    frames = []
    for i in range(12):
        k = math.sin(min(1.0, i / 11) * math.pi)  # bloom, then clear
        cloud = Image.new("L", size, 0)
        d = ImageDraw.Draw(cloud)
        for x, y, s in blobs:
            r = k * s * size[0] * 0.38
            d.ellipse((x - r, y - r, x + r, y + r), fill=235)
        cloud = cloud.filter(ImageFilter.GaussianBlur(18))
        black = Image.new("RGBA", size, (5, 6, 10, 255))
        frames.append(Image.composite(black, on_canvas(im, size), cloud))
    return frames


EFFECTS = {"offbeat": offbeat, "loot-pop": loot_pop, "benched": benched, "ink": ink}
REST = {"offbeat": 0, "loot-pop": -1, "benched": -1, "ink": 0}  # which frame the still uses


def make(effect: str, src: Path) -> Path:
    frames = [f.convert("RGB") for f in EFFECTS[effect](src)]
    stem = src.name.split("-640x640")[0].split("-1200x675")[0].split("-96x96")[0].split(".")[0]
    stem = stem.removesuffix("-" + effect)  # opponent-x-offbeat with offbeat -> opponent-x-offbeat
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{stem}-{effect}.webp"
    still = OUT_DIR / f"{stem}-{effect}-still.webp"
    hold = [FRAME_MS] * len(frames)
    if effect in ("benched", "loot-pop"):
        hold[-1] = 1400  # rest on the end state before the loop restarts
    frames[0].save(out, "WEBP", save_all=True, append_images=frames[1:], duration=hold, loop=0, quality=80, method=6)
    frames[REST[effect]].save(still, "WEBP", quality=84, method=6)
    side = {"file": out.name, "still": still.name, "effect": effect, "frames": len(frames),
            "size": list(frames[0].size), "frame_ms": hold, "bytes": out.stat().st_size,
            "source": {"image": rel(src), "image_sha256": sha256_file(src)},
            "tools": {"pillow": __import__("PIL").__version__}, "model_calls": 0, "sha256": sha256_file(out)}
    Path(str(out) + ".sidecar.json").write_text(json.dumps(side, indent=1) + "\n")
    assert out.stat().st_size < 1_500_000, f"{out.name} is over the 1.5 MB budget"
    print(f"OK {rel(out)} {frames[0].size} {len(frames)} frames {out.stat().st_size // 1024} KB")
    return out


def strip(paths: list[Path], dest: Path) -> Path:
    """Review strip: every other frame of each clip, one row per clip."""
    rows = [[f.convert("RGB").resize((160, 160)) for f in ImageSequence.Iterator(Image.open(p))][::2] for p in paths]
    sheet = Image.new("RGB", (max(map(len, rows)) * 164, len(rows) * 164), (40, 40, 40))
    for y, row in enumerate(rows):
        for x, f in enumerate(row):
            sheet.paste(f, (x * 164, y * 164))
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("effect", nargs="?", choices=sorted(EFFECTS))
    ap.add_argument("source", nargs="?")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.all:
        made = [make(item["effect"], ROOT / item["source"]) for item in json.loads(PLAN.read_text())["clips"]]
        print(strip(made, ART_DIR / "review" / "motion-strip.png"))
        return 0
    if not (a.effect and a.source):
        ap.print_help(); return 2
    make(a.effect, Path(a.source))
    return 0


if __name__ == "__main__":
    sys.exit(main())
