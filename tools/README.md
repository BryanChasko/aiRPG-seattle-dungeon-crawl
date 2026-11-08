# tools

Maintainer tools for the workshop pages and art. Learners never need these.

| tool | what it does |
|---|---|
| [`check_docs.py`](check_docs.py) | docs gate: relative links, images and anchors resolve, external links answer 200, no banned words, ASCII prose, the study pack is current. `--offline` skips the network |
| [`airpg_render.py`](airpg_render.py) | art pipeline: a plan in [`../images/plans/`](../images/plans/) becomes request files, renders on Meta Muse Image 1.0, and is standardized to the house spec with a sidecar per image. `--check` verifies every shipped image |
| [`contact_sheet.py`](contact_sheet.py) | review sheets of renders, one grid per size class |

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
