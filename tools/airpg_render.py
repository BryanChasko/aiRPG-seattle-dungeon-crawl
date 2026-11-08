#!/usr/bin/env python3
"""aiRPG image pipeline: Meta image API -> Pillow standardize -> webp + sidecar.

House spec (derived from shipped sidecars, enforced by --check):
  cards  640x640    : q84, vignette feather 36 to #0B0E14, ben-day 10px r2 alpha 10
  floors 1200x675 / banner 1680x720: q82 (banner q84 hero), vignette feather 50, ben-day
  icons  96x96      : q88 UI glyph, no dots/vignette by design

Usage:
  python3 tools/airpg_render.py --check                      every shipped webp meets its class spec
  python3 tools/airpg_render.py --plan images/plans/<run>.json   write requests + manifest, no API call
  python3 tools/airpg_render.py --render images/plans/<run>.json plan, then render the whole run
  python3 tools/airpg_render.py --batch <art dir>/<run>/manifest.json   render an existing manifest
  python3 tools/contact_sheet.py <webp files or dirs>        review sheet of renders

A plan names each render's class, output file and subject; the prompt is built from the frozen
blocks and the character model sheet in images/plans/style.json, so no request is hand-written.
Raw renders, manifests, run logs, replaced files and the spend ledger go to the art dir,
$AIRPG_ART_DIR or ~/writing/art/once-upon-agentic-ai/experiments, never into the repo.
Each billed render appends its cost ($0.01/image) to <art dir>/ledger.md; reused raws are free.
The key comes from META_IMAGE_API_KEY or ~/.config/muse/auth.json; request JSONs keep
"auth": "REDACTED".
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, re, shutil, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.meta.ai/v1/images/generations"
COST_PER_IMAGE = 0.01
ART_DIR = Path(os.environ.get("AIRPG_ART_DIR",
                              Path.home() / "writing" / "art" / "once-upon-agentic-ai" / "experiments"))
STYLE = ROOT / "images" / "plans" / "style.json"
RETRY_WAITS = (20, 60, 120)  # seconds between 429 retries; then the batch stops instead of grinding

CLASS_SPEC = {
    "card":   {"size": (640, 640),   "q": 84, "feather": 36, "dots": True},
    "floor":  {"size": (1200, 675),  "q": 82, "feather": 50, "dots": True},
    "banner": {"size": (1680, 720),  "q": 84, "feather": 50, "dots": True},
    "icon":   {"size": (96, 96),     "q": 88, "feather": 0,  "dots": False},
}

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def check() -> int:
    bad = 0
    for webp in sorted((ROOT / "images").rglob("*.webp")):
        if str(webp).endswith(".sidecar.json"):
            continue
        side = Path(str(webp) + ".sidecar.json")
        name = webp.name
        try:
            from PIL import Image
            w, h = Image.open(webp).size
        except Exception as e:
            print(f"FAIL {name}: cannot open ({e})"); bad += 1; continue
        if "96x96" in name:
            cls = "icon"
        elif "640x640" in name:
            cls = "card"
        elif "1680x720" in name:
            cls = "banner"
        elif any(t in name for t in ("1200x675",)):
            cls = "floor"
        else:
            print(f"WARN {name}: no size tag, is {w}x{h}"); continue
        spec = CLASS_SPEC[cls]
        if (w, h) != spec["size"]:
            print(f"FAIL {name}: is {w}x{h}, want {spec['size']}"); bad += 1
        if not side.exists():
            print(f"FAIL {name}: missing sidecar"); bad += 1; continue
        sc = json.loads(side.read_text())
        trans = sc.get("transforms", [])
        if cls == "icon":
            if sc.get("format") != "webp lossy q88":
                print(f"FAIL {name}: format={sc.get('format')}"); bad += 1
            if not any("no dots, no vignette" in t for t in trans):
                print(f"FAIL {name}: icon should declare no-dots-no-vignette"); bad += 1
        else:
            if sc.get("format") != f"webp lossy q{spec['q']}":
                print(f"FAIL {name}: format={sc.get('format')}"); bad += 1
            if not any(f"vignette feather {spec['feather']}" in t for t in trans):
                print(f"FAIL {name}: missing vignette feather {spec['feather']}"); bad += 1
            if not any("ben-day 10px r2 alpha 10" in t for t in trans):
                print(f"FAIL {name}: missing ben-day"); bad += 1
    print("check: all standard" if bad == 0 else f"check: {bad} problem(s)")
    return 1 if bad else 0

def post_process(raw: Path, out: Path, cls: str) -> dict:
    """Standardize one raw render. Returns sidecar transforms list."""
    from PIL import Image, ImageDraw, ImageFilter
    spec = CLASS_SPEC[cls]
    tw, th = spec["size"]
    im = Image.open(raw).convert("RGB")
    # cover-crop
    s = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s) + 1, round(im.height * s) + 1), Image.LANCZOS)
    x = (im.width - tw) // 2; y = (im.height - th) // 2
    im = im.crop((x, y, x + tw, y + th))
    transforms = [f"cover-crop {tw}x{th} lanczos"]
    if cls == "icon":
        transforms = ["center crop 12% margin", f"resize {tw}x{th} lanczos",
                      "no dots, no vignette (UI glyph)"]
    else:
        # vignette to #0B0E14
        f = spec["feather"]
        mask = Image.new("L", (tw, th), 0)
        d = ImageDraw.Draw(mask)
        d.ellipse((-f, -f, tw + f, th + f), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(f))
        vig = Image.new("RGB", (tw, th), (11, 14, 20))
        im = Image.composite(im, vig, mask)
        transforms.append(f"vignette feather {f} to #0B0E14")
        # ben-day dots lavender alpha ~10%
        dot = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        dd = ImageDraw.Draw(dot)
        for yy in range(5, th, 10):
            for xx in range(5 + (yy // 10 % 2) * 5, tw, 10):
                dd.ellipse((xx - 2, yy - 2, xx + 2, yy + 2), fill=(215, 199, 238, 26))
        im = Image.alpha_composite(im.convert("RGBA"), dot).convert("RGB")
        transforms.append("ben-day 10px r2 alpha 10")
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "WEBP", quality=spec["q"], method=6)
    return transforms

AUTH_FILE = Path.home() / ".config" / "muse" / "auth.json"


def rel(p: Path) -> str:
    """Repo-relative path when inside the repo, so sidecars do not carry one machine's home directory."""
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def api_key() -> str:
    """META_IMAGE_API_KEY wins; otherwise ~/.config/muse/auth.json (providers.meta.api_key). Never printed."""
    key = os.environ.get("META_IMAGE_API_KEY", "")
    if key:
        return key
    try:
        return json.loads(AUTH_FILE.read_text())["providers"]["meta"]["api_key"]
    except (OSError, KeyError, ValueError):
        return ""


class RateLimited(Exception):
    """The API kept answering 429 after every retry; the batch stops so it can resume later."""


def call_api(body: bytes, key: str, name: str) -> bytes:
    rq = urllib.request.Request(API, data=body, headers={"Authorization": f"Bearer {key}",
                                                         "Content-Type": "application/json"})
    for attempt, wait in enumerate((0,) + RETRY_WAITS):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(rq, timeout=300) as rp:
                item = json.loads(rp.read())["data"][0]
            # the API answers with base64 or with a short-lived URL
            if item.get("b64_json"):
                return base64.b64decode(item["b64_json"])
            return urllib.request.urlopen(item["url"], timeout=300).read()
        except urllib.error.HTTPError as e:
            detail = e.read()[:300].decode("utf-8", "replace")
            if e.code != 429:
                raise RuntimeError(f"HTTP {e.code}: {detail}") from e
            retry_after = int(e.headers.get("Retry-After") or 0)
            print(f"429 on {name} (attempt {attempt + 1}, Retry-After={retry_after}s): {detail}")
            if retry_after > max(RETRY_WAITS):  # a usage cap, not a burst limit: waiting here is pointless
                resets = time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(time.time() + retry_after))
                raise RateLimited(f"{name}; usage cap resets about {resets}")
    raise RateLimited(name)


def render_one(req_file: Path, raw: Path, out: Path, cls: str, run_dir: Path) -> tuple[float, bool]:
    """Render (or reuse) one raw, standardize it, write the webp, its sidecar and a run log.
    Returns (dollars billed, done). Raises RateLimited so the caller can stop the batch."""
    spec = json.loads(req_file.read_text())
    billed = 0.0
    if raw.exists():  # resume: a raw kept from an earlier attempt is not billed again
        print(f"reuse {raw.name}")
    else:
        key = api_key()
        if not key:
            print(f"blocked: no key in META_IMAGE_API_KEY or {AUTH_FILE}"); return 0.0, False
        body = json.dumps({"model": spec["model"], "prompt": spec["prompt"], "n": 1, "size": spec["size"],
                           "output_format": spec.get("output_format", "png")}).encode()
        try:
            data = call_api(body, key, out.name)
        except RuntimeError as e:
            print(f"FAIL {out.name}: {e}"); return 0.0, False
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_bytes(data)
        billed = COST_PER_IMAGE
    if out.exists():  # a re-roll keeps the version it replaces, with its sidecar
        keep = run_dir / "replaced"
        keep.mkdir(parents=True, exist_ok=True)
        for p in (out, Path(str(out) + ".sidecar.json")):
            if p.exists() and not (keep / p.name).exists():
                shutil.copy2(p, keep / p.name)
    raw_sha = sha256_file(raw)
    transforms = post_process(raw, out, cls)
    out_sha = sha256_file(out)
    sidecar = {
        "file": out.name, "bytes": out.stat().st_size,
        "format": f"webp lossy q{CLASS_SPEC[cls]['q']}",
        "render": {"endpoint": API, "model": spec["model"],
                   "prompt_sha256": spec["prompt_sha256"], "size": spec["size"]},
        "sha256": out_sha, "size": list(CLASS_SPEC[cls]["size"]),
        "source": {"raw": raw.name, "raw_kept_at": str(raw),
                   "raw_sha256": raw_sha, "request": rel(req_file)},
        "tokens": {"ben_day": "#d7c7ee",
                   "vignette": "#0B0E14 (obsidian, banner spec base)"},
        "tools": {"pillow": __import__("PIL").__version__,
                  "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"},
        "transforms": transforms,
        "brand_exceptions": [
            "BRAND.md 3 people/faces ban lifted: character cards for the cast and the opponents of the crawl",
            "interface frame in the render is blank by prompt; no model text"],
    }
    Path(str(out) + ".sidecar.json").write_text(json.dumps(sidecar, indent=1))
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"{out.stem}.log").write_text(
        f"request={rel(req_file)}\nraw_sha256={raw_sha}\nout_sha256={out_sha}\nout_bytes={out.stat().st_size}\n")
    print(f"OK {out.name} ({out.stat().st_size}B) sha {out_sha[:12]}")
    return billed, True


def batch(manifest: str) -> int:
    m = json.loads(Path(manifest).read_text())
    run_dir = Path(manifest).parent
    spent, done = 0.0, 0
    try:
        for r in m["renders"]:
            cost, ok = render_one(ROOT / r["request"], Path(r["raw"]), ROOT / r["out"],
                                  r.get("class", "card"), run_dir)
            spent += cost; done += ok
    except RateLimited as e:
        print(f"stopped: rate-limited at {e}; rerun the same command later, finished raws are reused")
    n = round(spent / COST_PER_IMAGE)
    if n:  # only billed renders reach the ledger
        with open(run_dir.parent / "ledger.md", "a") as f:
            f.write(f"| {run_dir.name} | {n} image(s) | ${spent:.2f} |\n")
    print(f"batch: {done} of {len(m['renders'])} done, {n} billed, ${spent:.2f} this run")
    return 0 if done == len(m["renders"]) else 1


def plan(plan_file: str) -> Path:
    """Build every request in a plan from images/plans/style.json; write the manifest to the art dir."""
    style = json.loads(STYLE.read_text())
    p = json.loads(Path(plan_file).read_text())
    run_dir = ART_DIR / p["run"]
    renders = []
    for r in p["renders"]:
        kind = r.get("style", r["class"])
        subject = re.sub(r"\{([A-Z]+)\}", lambda mt: style["model_sheet"][mt.group(1)], r["subject"])
        prompt = style["blocks"][kind] + subject + style["endings"][kind]
        req = {"model": "muse-image-1.0", "prompt": prompt, "n": 1,
               "size": r.get("size", style["sizes"][kind]), "output_format": "png",
               "endpoint": "POST " + API, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
               "auth": "REDACTED", "output_sha256": None, "revised_prompt": None, "plan": rel(Path(plan_file))}
        req_file = ROOT / "images" / "src" / f"{r['name']}.request.json"
        req_file.write_text(json.dumps(req, indent=1) + "\n")
        renders.append({"request": rel(req_file), "raw": str(run_dir / "raw" / f"{r['name']}.png"),
                        "out": r["out"], "class": r["class"]})
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = run_dir / "manifest.json"
    manifest.write_text(json.dumps({"plan": rel(Path(plan_file)), "renders": renders}, indent=1) + "\n")
    print(f"plan: {len(renders)} request(s) in images/src/, manifest {manifest}")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--plan", metavar="PLAN_JSON")
    ap.add_argument("--render", metavar="PLAN_JSON")
    ap.add_argument("--batch", metavar="MANIFEST_JSON")
    a = ap.parse_args()
    if a.check:
        return check()
    if a.plan:
        plan(a.plan); return 0
    if a.render:
        return batch(str(plan(a.render)))
    if a.batch:
        return batch(a.batch)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
