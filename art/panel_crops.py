#!/usr/bin/env python3
"""Comic-panel variety from shipped art: tight, thumbnail-legible crops of existing renders.

The reuse audit (docs/image-reuse-audit.md) found the full-body cast cards doing speaker-icon
duty hundreds of times at 28px, where nothing reads. This tool cuts the close shots a comic
would use instead: face and eye headshots for speaker icons (96x96), and square action panels
(480x480) for inline beats, all cropped from art that already passed model-sheet QA, so no new
render can drift off-model. Boxes come from SAM 3.1 (art/sam_cutout.py, cached responses are
free) or from hand-placed relative boxes for banner panels.

Usage:
  export META_IMAGE_API_KEY=$(aws ssm get-parameter --name /heraldstack/shared/meta-model-api-key \
    --with-decryption --profile ops-reader --region us-west-2 --query Parameter.Value --output text)
  uv run --with pillow --with meta-sam-parser python3 art/panel_crops.py [name ...]

No arguments cuts every job below. Add a job by appending to JOBS.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from airpg_render import ART, ROOT, rel, sha256_file  # noqa: E402
from sam_cutout import segment, masks  # noqa: E402

from PIL import Image  # noqa: E402

# name, source, out, kind, concept-or-relative-box, expand (box padding factor), pick, note
JOBS = [
    # speaker headshots: cut to read at 28px, where the full cards turn to mush
    ("speaker-cordula-face", "images/cards/cast-cordula-640x640.webp", "images/icons/speaker-cordula-face-96x96.webp", "sam", "woman's face", 1.6, "conf", "Cordula default speaker headshot"),
    ("speaker-cordula-drill", "images/cards/cast-cordula-drill-640x640.webp", "images/icons/speaker-cordula-drill-96x96.webp", "rel", (0.24, 0.00, 0.68, 0.42), 1.0, "", "Cordula mid-dance with the paddle overhead, for action and drill lines"),
    ("speaker-cordula-benched", "images/cards/cast-cordula-benched-640x640.webp", "images/icons/speaker-cordula-benched-96x96.webp", "sam", "woman's face", 1.6, "conf", "Cordula tired, for post-round and cost lines"),
    ("speaker-barnaby-eye", "images/cards/cast-barnaby-640x640.webp", "images/icons/speaker-barnaby-eye-96x96.webp", "sam", "octopus eye", 2.2, "conf", "Barnaby's eye, for dry one-liners"),
    ("speaker-barnaby-head", "images/cards/cast-barnaby-640x640.webp", "images/icons/speaker-barnaby-head-96x96.webp", "sam", "octopus head", 1.25, "conf", "Barnaby default speaker headshot"),
    ("speaker-chonks-face", "images/cards/cast-chonks-640x640.webp", "images/icons/speaker-chonks-face-96x96.webp", "sam", "green fish", 1.15, "conf", "Chonks is all head; the whole fish is the headshot"),
    ("speaker-shelly-siphon", "images/cards/cast-shelly-640x640.webp", "images/icons/speaker-shelly-siphon-96x96.webp", "rel", (0.16, 0.08, 0.60, 0.58), 1.0, "", "Shelly's siphon and mist puff, the part that reads small"),
    # square action panels for inline story beats
    ("panel-barnaby-tentacle", "images/cards/cast-barnaby-640x640.webp", "images/panels/panel-barnaby-tentacle-480x480.webp", "sam", "curled octopus tentacle", 1.3, "area", "one curled arm, suckers up"),
    ("panel-cordula-karambits", "images/cards/cast-cordula-drill-640x640.webp", "images/panels/panel-cordula-karambits-480x480.webp", "rel", (0.22, 0.52, 0.78, 1.00), 1.0, "", "boots, splash and the sheathed calf karambits"),
    ("panel-paddle-twirl", "images/cards/cast-cordula-drill-640x640.webp", "images/panels/panel-paddle-twirl-480x480.webp", "rel", (0.06, 0.00, 0.72, 0.48), 1.0, "", "the paddle mid-twirl overhead, object in motion"),
    ("panel-dance-cordula", "images/banner-1680x720.webp", "images/panels/panel-dance-cordula-480x480.webp", "rel", (0.15, 0.04, 0.42, 0.98), 1.0, "", "Cordula's half of the hero dance-off"),
    ("panel-dance-barnaby", "images/banner-1680x720.webp", "images/panels/panel-dance-barnaby-480x480.webp", "rel", (0.48, 0.02, 0.84, 0.94), 1.0, "", "Barnaby's half: dance arms and chromatophore bands"),
    ("panel-chonks-pool", "images/banner-1680x720.webp", "images/panels/panel-chonks-pool-480x480.webp", "rel", (0.40, 0.68, 0.53, 1.00), 1.0, "", "Chonks watching from the tide pool"),
    ("panel-barnaby-suckers", "images/cards/cast-barnaby-legend-640x640.webp", "images/panels/panel-barnaby-suckers-480x480.webp", "rel", (0.42, 0.48, 1.00, 1.00), 1.0, "", "sucker rows at reading distance"),
]


def square_box(box, w: int, h: int, expand: float):
    l, t, r, b = box
    side = max(r - l, b - t) * expand
    cx, cy = (l + r) / 2, (t + b) / 2
    l2 = min(max(int(cx - side / 2), 0), max(int(w - side), 0))
    t2 = min(max(int(cy - side / 2), 0), max(int(h - side), 0))
    side = int(min(side, w, h))
    return l2, t2, l2 + side, t2 + side


def cut(job) -> None:
    name, src, out, kind, spec, expand, pick, note = job
    img = Image.open(ART / src).convert("RGB")
    w, h = img.size
    conf = None
    if kind == "sam":
        found = list(masks(segment(ART / src, spec)))
        if not found:
            print(f"FAIL {name}: SAM found no {spec!r} in {src}"); return
        key = (lambda m: (m[1].right - m[1].left) * (m[1].bottom - m[1].top)) if pick == "area" \
            else (lambda m: m[2] or 0)
        _, box, conf, *_ = max(found, key=key)
        box = (box.left, box.top, box.right, box.bottom)
    else:
        box = (int(spec[0] * w), int(spec[1] * h), int(spec[2] * w), int(spec[3] * h))
    crop = img.crop(square_box(box, w, h, expand))
    size = (96, 96) if out.startswith("images/icons/") else (480, 480)
    crop = crop.resize(size, Image.LANCZOS)
    outp = ART / out
    outp.parent.mkdir(parents=True, exist_ok=True)
    is_icon = size == (96, 96)
    crop.save(outp, "WEBP", quality=88 if is_icon else 90, method=6)
    side = {"file": outp.name, "size": list(size), "format": "webp lossy q88" if is_icon else "webp lossy q90",
            "source": {"image": src, "image_sha256": sha256_file(ART / src)},
            "crop": {"by": "art/panel_crops.py", "kind": kind, "spec": str(spec),
                     "box": list(box), "expand": expand, "confidence": conf, "note": note},
            "transforms": ["square crop to the panel box", "resize lanczos",
                           "no dots, no vignette (speaker headshot)"] if is_icon else
                          ["square crop to the panel box", "resize lanczos"],
            "sha256": sha256_file(outp)}
    Path(str(outp) + ".sidecar.json").write_text(json.dumps(side, indent=1) + "\n")
    print(f"OK {rel(outp)} {size} box={box} conf={conf}")


def main() -> int:
    want = sys.argv[1:]
    for job in JOBS:
        if not want or job[0] in want:
            cut(job)
    return 0


if __name__ == "__main__":
    sys.exit(main())
