#!/usr/bin/env python3
"""Cut a character or object out of a render with SAM 3.1 (Meta Model API): transparent sprites.

Sprites feed the motion pass (art/motion.py) and compositing: a cast member on an arena plate,
an Off-Beat wobble, a HUD avatar. One concept per call, as SAM wants: a short noun phrase.

Usage:
  python3 art/sam_cutout.py images/cards/cast-chonks-buckler-640x640.webp --concept "green fish"
  python3 art/sam_cutout.py <image> --concept octopus --all        every match, one sprite each
  python3 art/sam_cutout.py <image> --concept octopus --out images/sprites/barnaby.webp

Writes images/sprites/<image stem>-<concept>.webp (RGBA, trimmed to the mask box, 4 px feathered
edge) and a sidecar with the request, box, mask size and confidence. The SAM response text is kept
in the art dir ($AIRPG_ART_DIR/sam/) for re-use; a cached response is never billed again.
Needs Pillow and meta-sam-parser: uv run --with pillow --with meta-sam-parser python3 art/sam_cutout.py ...
"""
from __future__ import annotations
import argparse, base64, hashlib, io, json, sys, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meta_api  # noqa: E402  shared key lookup and HTTP client
from airpg_render import ART_DIR, ROOT, rel, sha256_file  # noqa: E402

from PIL import Image, ImageFilter  # noqa: E402
import meta_sam_parser as sam  # noqa: E402

MODEL = "sam-3.1"


def segment(img: Path, concept: str) -> str:
    """Return the SAM output text for one concept on one image, from cache when possible."""
    png = io.BytesIO()
    Image.open(img).convert("RGB").save(png, "PNG")
    data_url = "data:image/png;base64," + base64.b64encode(png.getvalue()).decode()
    cache = ART_DIR / "sam" / f"{img.stem}--{hashlib.sha256((concept + sha256_file(img)).encode()).hexdigest()[:16]}.txt"
    if cache.exists():
        return cache.read_text()
    body = {"model": MODEL, "stream": False, "metadata": {"include_confidence": "true"},
            "input": [{"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": concept},
                {"type": "input_image", "image_url": data_url}]}]}
    out = meta_api.request("POST", "/responses", body)
    text = "".join(c.get("text", "") for o in out.get("output", []) for c in o.get("content", []) or []
                   if c.get("type") == "output_text")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(text)
    return text


def masks(text: str):
    """Yield (object_id, box, confidence, raster bytes, mask w, mask h) per match."""
    parser = sam.image_segmentation_format().create_parser()
    parser.push(text)
    fin = parser.finish(sam.CompletedOutcome())
    recs = list(getattr(fin, "result", fin).records)
    boxes = {r.object_id: r for r in sam.records_of_kind(recs, "box")}
    for m in sam.records_of_kind(recs, "mask"):
        b = boxes.get(m.object_id)
        yield m.object_id, b, m.confidence, sam.decode_mask_to_raster(m.mask), m.mask.width, m.mask.height


def cut(img: Path, box, raster: bytes, mw: int, mh: int) -> Image.Image:
    src = Image.open(img).convert("RGBA")
    l, t, r, b = int(box.left), int(box.top), int(box.right), int(box.bottom)
    alpha = Image.frombytes("L", (mw, mh), bytes(v * 255 for v in raster)).resize((r - l, b - t), Image.LANCZOS)
    alpha = alpha.filter(ImageFilter.GaussianBlur(1.2))  # soften the stair-step edge of an upscaled mask
    sprite = src.crop((l, t, r, b))
    sprite.putalpha(alpha)
    return sprite


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--concept", required=True, help="a short noun phrase naming one thing")
    ap.add_argument("--all", action="store_true", help="one sprite per match instead of the most confident")
    ap.add_argument("--out", help="sprite path (single match only)")
    a = ap.parse_args()
    img = Path(a.image)
    try:
        text = segment(img, a.concept)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}"); return 1
    found = sorted(masks(text), key=lambda m: -(m[2] or 0))
    if not found:
        print(f"no '{a.concept}' in {img.name}"); return 1
    chosen = found if a.all else found[:1]
    slug = a.concept.lower().replace(" ", "-")
    for i, (oid, box, conf, raster, mw, mh) in enumerate(chosen):
        sprite = cut(img, box, raster, mw, mh)
        name = img.name.split("-640x640")[0].split("-1200x675")[0].split(".")[0]
        out = Path(a.out) if a.out and not a.all else \
            ROOT / "images" / "sprites" / f"{name}-{slug}{'-' + str(i) if a.all else ''}.webp"
        out.parent.mkdir(parents=True, exist_ok=True)
        sprite.save(out, "WEBP", quality=90, method=6, exact=True)
        side = {"file": out.name, "size": list(sprite.size), "format": "webp lossy q90 rgba",
                "source": {"image": rel(img), "image_sha256": sha256_file(img)},
                "segment": {"model": MODEL, "concept": a.concept, "object_id": oid, "confidence": conf,
                            "box": [box.left, box.top, box.right, box.bottom], "mask_raster": [mw, mh]},
                "transforms": ["crop to SAM box", "mask upscaled lanczos to box", "alpha blur 1.2"],
                "sha256": sha256_file(out)}
        Path(str(out) + ".sidecar.json").write_text(json.dumps(side, indent=1) + "\n")
        print(f"OK {rel(out)} {sprite.size} conf={conf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
