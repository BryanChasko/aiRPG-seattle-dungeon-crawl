---
name: airpg-art
description: Visual art pipeline for the Seattle Strands Dungeon Crawl visual LitRPG: canon-safe image placement, render discipline, and publish verification.
---

# AirPG Art

Produce or place visual art for this repo without breaking story canon,
spoiler rules, or the docs gate. Art here means images (WebP cards,
plates, icons, wordmark), SVG marks and diagrams, and motion stills.
The play-page web styling lives elsewhere; this skill ends at the
image file and its markdown placement.

## When to use

Placing a rendered image on a page, requesting a new render, exporting
a sticker pack or sprite, drawing a diagram, editing the wordmark, or
writing art-direction sections. Read `docs/art-placements.md` first:
it is the ledger of every image, its page and spot, and its status
(`placed`, `ready to place`, `requested`).

## Canon and spoiler rules (hard)

- The cover (`README.md`) shows Cordula alone plus a one-arm Barnaby
  tease. No Shelly, no Chonks, no bosses, no sponsors, no HUD strip.
  Cordula there knows only Day 1: no names, no collar, no future crew.
- The pre-game landing teases companions (`Companions join the party
  on later floors`) but never names or faces them.
- Story art is bespoke and used once at its beat. Repeatable flair
  only: HUD chrome in `site/assets/hud`, dividers, textures, the 28px
  speaker glyphs. Never reuse a story plate as decoration.
- Banned: stock emoji meaning anything, color as the only carrier of
  meaning, full-body Barnaby before the dungeon earns him.
- Barnaby's collar glows faint violet at rest, brighter with temper;
  charcoal and slate at rest, crimson and white in a dance-off or fury.

## Slot dimensions

Cards `640x640` webp. Plates `1200x675` webp. Icons `96x96` webp.
Wordmark `1200x240` webp. Diagrams inline-friendly SVG (no scripts,
`viewBox` about `1200x675`). Alt text carries the words: SVG loaded
as `<img>` cannot fetch webfonts, so lettering is drawn paths or
generic families.

## Pipeline

1. Render or draw to `art/images/<slot>/` with a sidecar
   `<name>.webp.sidecar.json` (prompt, model, seed, date).
   Key discipline per `art/meta_api.py`: the OAuth credential has
   zero SAM quota; SAM renders need the Model API key, never print
   or write a key anywhere.
2. Diagnose quota with one shot first: `art/sam_probe.py` splits
   burst limit, usage cap, and zero-quota 429s. Respect Retry-After;
   never hammer.
3. Mirror with `art/publish_art.py` (repo-hosted files are canonical;
   S3 `bryanchasko.com/airpg-art/` is the mirror). Verify each URL
   returns 200.
4. Place with the exact snippet shape from `docs/art-placements.md`
   and record the row: image, page and spot, status. Speaker icons
   beside a bold name carry empty alt so readers hear the name once.
5. Run `python3 dungeon/check_docs.py --offline`: ASCII only, links
   resolve, anchors exist. Fix or revert; never bypass.

## Acceptance

Dimensions match the slot. S3 mirror 200. Placements row filed.
Docs gate clean. No spoiler, canon, or alt-text violation.
