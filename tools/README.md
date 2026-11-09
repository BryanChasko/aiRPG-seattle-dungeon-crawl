# tools

Maintainer tools for the workshop pages and art. Learners never need these.

| tool | what it does |
|---|---|
| [`check_docs.py`](check_docs.py) | docs gate: relative links, images and anchors resolve, external links answer 200, no banned words, ASCII prose, the study pack is current. `--offline` skips the network |
| [`airpg_render.py`](airpg_render.py) | art pipeline: a plan in [`../images/plans/`](../images/plans/) becomes request files, renders on Meta Muse Image 1.0, and is standardized to the house spec with a sidecar per image. `--check` verifies every shipped image |
| [`contact_sheet.py`](contact_sheet.py) | review sheets of renders, one grid per size class |
| [`sam_cutout.py`](sam_cutout.py) | SAM 3.1 cutouts: a character or object from a render as a transparent sprite, for compositing and motion |
| [`sam_probe.py`](sam_probe.py) | one-shot SAM 3.1 diagnostic (no retries): prints status, Retry-After, request id and the parsed error; `--playground` uses the files-upload + streaming shape, `--control` calls a muse-* model on the same key |
| [`motion.py`](motion.py) | animated payoffs from shipped art (Off-Beat wobble, loot pop, Benched, Ink Cloud), each with a still for reduced motion; no model calls |
| [`publish_art.py`](publish_art.py) | uploads planned art to `s3://bryanchasko.com/airpg-art/` and writes [`../docs/art-placements.md`](../docs/art-placements.md): every image's S3 key, URL, page, spot, alt text and paste-ready line |
| [`meta_api.py`](meta_api.py) | shared Meta Model API client (key lookup, retries); `models` lists what the key can call |

The art rules, tokens and character model sheet are in [`../docs/visual-design-system.md`](../docs/visual-design-system.md); the prompt blocks in [`../images/plans/style.json`](../images/plans/style.json).

New art, start to finish:

```bash
# 1. write images/plans/<date>-batch-NN.json: run name, then one entry per render (name, class, out, subject)
python3 tools/airpg_render.py --plan images/plans/<run>.json     # requests and manifest, no API call
python3 tools/airpg_render.py --render images/plans/<run>.json   # render; rerun after a rate limit, raws are reused
python3 tools/contact_sheet.py --plan images/plans/<run>.json    # look at every image before linking it
python3 tools/airpg_render.py --check
python3 tools/check_docs.py
```

`airpg_render.py` and `contact_sheet.py` need Pillow (`uv run --with pillow python3 tools/...`). The Muse key comes from `META_IMAGE_API_KEY` or `~/.config/muse/auth.json` and never enters the repo. Raw renders, manifests, run logs, replaced images and the spend ledger stay outside the repo in `$AIRPG_ART_DIR` (default `~/writing/art/once-upon-agentic-ai/experiments`).
