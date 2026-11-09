#!/usr/bin/env python3
"""Compose the README's non-render art with Pillow: the title wordmark and the HUD strip.

These two slots are type and interface chrome, not model renders (the render pipeline's
no-text rule forbids lettering from the image model), so they are drawn here and stamped
with sprite-style sidecars. Fonts are the web theme's own headings faces, MedievalSharp
and Cinzel (SIL Open Font License), fetched once into the art dir:

  mkdir -p $AIRPG_ART_DIR/fonts && cd $AIRPG_ART_DIR/fonts
  curl -s "https://fonts.googleapis.com/css2?family=MedievalSharp&family=Cinzel:wght@700" \\
    -H "User-Agent: Mozilla/5.0"   # then download the two ttf URLs as MedievalSharp.ttf / Cinzel-Bold.ttf

Usage:
  uv run --with pillow python3 art/compose_readme_art.py

Writes images/wordmark-1200x240.webp, images/hud-strip-1200x120.webp (animated groove
bar) and images/hud-strip-1200x120-still.webp (the reduced-motion still), each with a
sidecar. Re-running is deterministic: same fonts, same bytes up to webp encoding.
"""
from __future__ import annotations
import hashlib, json, math, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from airpg_render import ART, ART_DIR, ROOT, rel, sha256_file  # noqa: E402

from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

OBSIDIAN = (11, 14, 20)
VIOLET = (176, 76, 224)
VIOLET_DIM = (106, 44, 145)
LAVENDER = (215, 199, 238)
TEAL = (46, 196, 182)
GROOVE = (31, 191, 117)
HYPE = (255, 138, 61)
INK = (232, 230, 240)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    p = ART_DIR / "fonts" / name
    if not p.exists():
        sys.exit(f"missing font {p}; see the fetch steps in this file's docstring")
    return ImageFont.truetype(str(p), size)


def spaced(draw: ImageDraw.ImageDraw, xy, text, fnt, fill, tracking: int) -> int:
    """Draw letter-spaced text; return its total width."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += int(draw.textlength(ch, font=fnt)) + tracking
    return x - tracking - xy[0]


def spaced_width(draw, text, fnt, tracking: int) -> int:
    return sum(int(draw.textlength(c, font=fnt)) + tracking for c in text) - tracking


def ben_day(im: Image.Image) -> Image.Image:
    dot = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(dot)
    for yy in range(5, im.height, 10):
        for xx in range(5 + (yy // 10 % 2) * 5, im.width, 10):
            d.ellipse((xx - 2, yy - 2, xx + 2, yy + 2), fill=LAVENDER + (26,))
    return Image.alpha_composite(im.convert("RGBA"), dot)


def wordmark() -> Image.Image:
    W, H = 1200, 240
    im = Image.new("RGBA", (W, H), OBSIDIAN + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    big = font("MedievalSharp.ttf", 118)
    title = "aiRPG"
    tw = int(gd.textlength(title, font=big))
    gd.text(((W - tw) // 2, 14), title, font=big, fill=VIOLET + (255,))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(14)))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(im)
    d.text(((W - tw) // 2, 14), title, font=big, fill=INK + (255,))
    sub_f = font("Cinzel-Bold.ttf", 40)
    sub = "SEATTLE DUNGEON CRAWL"
    sw = spaced_width(d, sub, sub_f, 10)
    spaced(d, ((W - sw) // 2, 162), sub, sub_f, TEAL + (255,), 10)
    d.rounded_rectangle((3, 3, W - 4, H - 4), radius=18, outline=VIOLET_DIM + (255,), width=3)
    return ben_day(im).convert("RGB")


def hud_frame(t: float) -> Image.Image:
    """One frame of the strip; t is the loop phase 0..1."""
    W, H = 1200, 120
    im = Image.new("RGB", (W, H), OBSIDIAN)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, W - 3, H - 3), radius=14, outline=VIOLET_DIM, width=2)
    label = font("Cinzel-Bold.ttf", 26)
    mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)
    # groove bar: 14 segments, fill breathes 8..13 then snaps back on the beat
    d.text((28, 46), "GROOVE", font=label, fill=GROOVE)
    filled = 8 + round(5 * (0.5 - 0.5 * math.cos(2 * math.pi * t)))
    for i in range(14):
        x = 190 + i * 34
        col = GROOVE if i < filled else (34, 46, 40)
        if i == filled - 1:
            col = HYPE  # the travelling hot segment, on the beat
        d.rounded_rectangle((x, 44, x + 26, 76), radius=5, fill=col)
    # mana pips
    d.text((700, 46), "MANA", font=label, fill=TEAL)
    for i in range(6):
        cx = 812 + i * 30
        on = i < 4 + (1 if t > 0.5 else 0)
        d.ellipse((cx, 50, cx + 20, 70), fill=TEAL if on else (28, 44, 44))
    # d20
    cx, cy, r = 1078, 60, 30
    pts = [(cx + r * math.cos(-math.pi / 2 + k * 2 * math.pi / 6),
            cy + r * math.sin(-math.pi / 2 + k * 2 * math.pi / 6)) for k in range(6)]
    d.polygon(pts, outline=VIOLET, width=3)
    d.text((cx - 15, cy - 12), "20", font=mono, fill=LAVENDER)
    return ben_day(im.convert("RGBA")).convert("RGB")


def save(im: Image.Image, out: Path, transforms: list[str], **save_kw) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "WEBP", quality=90, method=6, **save_kw)
    side = {"file": out.name, "size": list(im.size), "format": "webp lossy q90",
            "source": {"composed_by": "art/compose_readme_art.py",
                       "fonts": ["MedievalSharp (OFL)", "Cinzel Bold (OFL)", "DejaVu Sans Mono Bold"]},
            "transforms": transforms, "sha256": sha256_file(out)}
    Path(str(out) + ".sidecar.json").write_text(json.dumps(side, indent=1) + "\n")
    print(f"OK {rel(out)} {im.size} sha {side['sha256'][:12]}")


def main() -> int:
    save(wordmark(), ART / "images" / "wordmark-1200x240.webp",
         ["pillow type composition: MedievalSharp title with violet glow, Cinzel tracked subtitle in teal",
          "ben-day 10px r2 alpha 10", "obsidian #0B0E14 panel so it reads on light and dark README themes"])
    frames = [hud_frame(i / 24) for i in range(24)]
    first, rest = frames[6], frames[7:] + frames[:6]  # start mid-fill, not empty
    out = ART / "images" / "hud-strip-1200x120.webp"
    out.parent.mkdir(parents=True, exist_ok=True)
    first.save(out, "WEBP", quality=88, method=6, save_all=True, append_images=rest,
               duration=90, loop=0)
    n = getattr(Image.open(out), "n_frames", len(frames))  # the muxer folds identical frames into longer durations
    side = {"file": out.name, "size": [1200, 120], "format": f"webp lossy q88 animated {n} unique frames 90ms loop",
            "source": {"composed_by": "art/compose_readme_art.py",
                       "fonts": ["Cinzel Bold (OFL)", "DejaVu Sans Mono Bold"]},
            "transforms": ["groove segments breathe 8..13 of 14 with one hot segment on the beat",
                           "ben-day 10px r2 alpha 10"],
            "sha256": sha256_file(out)}
    Path(str(out) + ".sidecar.json").write_text(json.dumps(side, indent=1) + "\n")
    print(f"OK {rel(out)} (1200, 120) animated sha {side['sha256'][:12]}")
    save(hud_frame(0.25), ART / "images" / "hud-strip-1200x120-still.webp",
         ["reduced-motion still of hud-strip-1200x120.webp at full groove"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
