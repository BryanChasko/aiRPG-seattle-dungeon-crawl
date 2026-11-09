# Floor Infinity: Reset the Multiverse (Optional)

Files on this floor: [`0_stairwell/reset_multiverse.py`](../0_stairwell/reset_multiverse.py) <!-- floor-files -->

> <img src="../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "The quarter closed. The review board signed the migration. This terminal is the last one still listening, and I am done performing. Delete the dungeon, Crawler. Leave the machine like you found it."

Cordula packs the kayak. Barnaby rinses the salt off his arms. The elevator doors open on Alki at sunrise, and the crawl lets go of the machine the way the fold let go of the pier: completely.

This floor is a postscript, not an ending. The Alki sunrise in [the Exit](cleanup.md) already closed the story. Infinity closes the machine: every folder, cache, container and cloud resource the crawl created, removed in tiers, verified gone.

## Floor Objective

Run the reset tool, in tiers, until the verify pass shows the machine like new.

## What "like new" means

Like new means the crawl leaves no trace, not that the machine loses anything it had before. The tool deletes only what the crawl installed. It never touches:

- AWS config and credentials (`~/.aws`)
- git, Docker or Node themselves
- your shell setup and SSH keys
- anything outside this repo and the two named caches below
- your own edits to tracked files

## The tiers

| Tier | Flag | Removes |
|---|---|---|
| 1 | `--apply` | servers on ports 8000-8009 stopped; `.venv/`; the Floor 5 knowledge base; `gameprod/` and the Floor 8 `.env`; the Floor 7 harness state; `.mid-song-save/` folders; web `node_modules` and `dist`; the tide-pool container; every `__pycache__` |
| 2 | `--apply --caches` | the uv cache; the embedding-model cache (`~/.cache/huggingface`, about 79 MB); uv-managed Pythons; the tide-pool image |
| 3 | manual, with `--global-tools` listed | the uv binary and the global AgentCore CLI, only if the crawl installed them |
| 4 | `--cloud-check` | read-only: confirms the Floor 8 stack, buckets and log groups are gone; deletes nothing |

## Step 1: Inventory

Run the tool from anywhere. It inventories first and deletes nothing:

```
python3 dungeon/0_stairwell/reset_multiverse.py
```

Check: one line per ledger row, with tier, size and state. Missing rows report as `gone`: the tool is safe to re-run.

> <img src="../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Read the inventory before you approve anything. A reset that deletes what it never listed is not a reset, it is a fog event with a keyboard."

## Step 2: Apply tier 1

```
python3 dungeon/0_stairwell/reset_multiverse.py --apply
```

The tool stops the crawl servers first (ports 8000-8009), then asks for `YES` per tier. Check: the closing verify pass shows every tier 1 row as `gone`.

If a port is still listening after the tool asks it to stop, stop that server yourself (usually Ctrl+C in its terminal) and re-run. The tool never kills anything it cannot name.

## Step 3: Caches, tools, cloud

```
python3 dungeon/0_stairwell/reset_multiverse.py --apply --caches
python3 dungeon/0_stairwell/reset_multiverse.py --cloud-check
```

Tier 3 stays manual on purpose. The tool lists the commands; you run them:

```
# Only if the crawl installed uv itself (Floor 0). Skip when uv was already on this machine.
rm ~/.local/bin/uv
# Only for the global AgentCore CLI (Floor 8).
npm uninstall -g @aws/agentcore
```

Check: `git status` shows only your own edits to tracked files. Check: a fresh clone plus the Floor 0 preflight behaves exactly as on a new machine.

## Floor Clear

The machine is like new. The repo stays, reset to shipped state: generated files gone, your commits intact.

> **CORDULA'S LOG, DAY 15, TUESDAY, JUNE 30, 0515, ALKI.** The terminal went dark last. I watched the prompt go out like a porch light. The octopus pretended not to watch. We left the beach clean.

Back to [the Exit](cleanup.md), or up to [Floor 9](floor-9.md) for the fog-proofing that made this reset safe.
