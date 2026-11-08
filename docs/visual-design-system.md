# Visual Design System — aiRPG Seattle Dungeon Crawl

Source of truth for art direction, image formats, and prompt language.
Pipeline: [tools/airpg_render.py](../tools/airpg_render.py)
(`--check` verifies, `--batch <manifest>` renders). The key comes from `META_IMAGE_API_KEY`
or `~/.config/muse/auth.json`, never from the repo; request JSONs keep `"auth": "REDACTED"`.
Raw renders, run logs, manifests and the spend ledger stay out of the public repo, in
`~/writing/art/once-upon-agentic-ai/experiments/`; every sidecar's `raw_kept_at` points there.

## 1. Tokens

| Token | Value | Source |
|---|---|---|
| obsidian (page bg, vignette target) | `#0B0E14` | `--color-bg-page` in `web/src/assets/theme.css` |
| card bg | `#141824` | `--color-bg-card` |
| kelp-teal / sea-glass green | `#1FBF75` | `--color-emerald` (Puget Sound teal / sea-glass green in prompts) |
| signal-orange (sodium accent) | `#FF8A3D` | `--color-candlelight` |
| crimson (Barnaby flash) | `#FF4D6D` | `--color-red-deep` |
| white (Barnaby flash, ink) | `#E8E2F0` | `--color-ink` |
| System magenta-violet glow | `#FF2BD6` | `--color-gold` (magenta-violet System light, not metallic gold) |
| ben-day dot lavender | `#D7C7EE` | sidecar `tokens.ben_day`, alpha ~10% |
| brass | material, no flat hex | "polished brass" rendered metallic in prompts (collar, chest bindings, turnstile); never a flat fill |

Radii (two): panel/card `--border-radius-panel: 8px` (in `theme.css`);
inner chip/badge radius `4px` (spec'd here, half the panel radius).

Type rule: display/headings `MedievalSharp, Cinzel, serif` (`--font-heading`);
body `Crimson Text, Georgia, serif` (`--font-body`); UI `Lora, serif` (`--font-ui`).
Enforced by `web/src/__tests__/theme.test.ts`.

## 2. Format rules (enforced by `--check`)

Per-class spec actually enforced in `CLASS_SPEC` + `check()`:

| Class | File tag | Size | Quality | Vignette feather | Ben-day dots |
|---|---|---|---|---|---|
| card | `*-640x640.webp` | 640x640 | webp lossy q84 | 36 to `#0B0E14` | 10px r2 alpha 10 |
| floor | `*-1200x675.webp` | 1200x675 | webp lossy q82 | 50 to `#0B0E14` | 10px r2 alpha 10 |
| banner | `*-1680x720.webp` | 1680x720 | webp lossy q84 (hero) | 50 to `#0B0E14` | 10px r2 alpha 10 |
| icon | `*-96x96.webp` | 96x96 | webp lossy q88 | none (0) | none — `no dots, no vignette (UI glyph)` |

`--check` classifies by filename size tag, then requires: exact pixel size;
sidecar present; `format` string match (`webp lossy q{q}`); a
`vignette feather {f}` transform + a `ben-day 10px r2 alpha 10` transform
(cards/floors/banners) or a `no dots, no vignette` transform (icons).
`post_process` cover-crops (Lanczos), vignettes to `#0B0E14`, and overlays the
ben-day dot grid (icons: center-crop 12% margin + resize instead).

## 3. Prompt style blocks

The blocks, endings and character model sheet live in one file,
[`images/plans/style.json`](../images/plans/style.json). `tools/airpg_render.py --plan`
builds every request from it, so no request is written by hand: a plan in
`images/plans/` names each render's class, output and subject, and `{GEODUCK}`-style
tokens pull in the model sheet. The blocks below are the same text, for reading.

Card style block:

```text
Cinematic dark-fantasy character card illustration, square, single subject centered with generous margin, waist-up or full body, high contrast, sharp detail, obsidian black and slate grey background with deep Puget Sound teal and sea-glass green, neon magenta-violet System rim light, warm sodium-orange accent light, rainy Pacific Northwest atmosphere, darker edges. Friendly, funny, game-show energy, never menacing, no weapons.
```

Wide style block (floors; banners use the same voice in 21:9):

```text
Cinematic dark-fantasy digital illustration, wide 16:9 environment scene, no people, no faces, no text, high contrast, obsidian and slate background with deep Puget Sound teal, magenta-violet System glow accents, warm sodium-orange practical lights, rainy Pacific Northwest atmosphere, darker edges.
```

Blank-frame suffix (appended to every card/banner prompt):

```text
 A blank glowing violet interface frame edge at the card border, with no writing. No text, no letters, no numbers, no words, no logos, no watermark, no signature.
```

Icons use their own voice (not the blocks above): `Dark fantasy game interface
icon, a single object centered with generous empty margin, cinematic lighting,
high contrast, polished brass and weathered leather detail, plain obsidian black
background (#0B0E14), soft glow halo. No text ... no user interface.`

## 4. Sidecar convention

Every shipped `.webp` has a `<name>.webp.sidecar.json` with: `file`, `bytes`,
`format`, `render` (`endpoint`, `model`, `prompt_sha256`, `size`), `sha256`,
`size`, `source` (`raw`, `raw_kept_at`, `raw_sha256`, `request`), `tokens`
(`ben_day`, `vignette`), `tools` (`pillow`, `python`), `transforms`, and
`brand_exceptions` (people/faces ban lifted for cast + opponent cards;
interface frames blank by prompt, no model text).

## 5. Coast Salish art protocol (from `workshop/world/seattle.md`)

Seattle sits on the homelands of Coast Salish peoples, including the Duwamish;
Suquamish, Muckleshoot, Tulalip, Snoqualmie and other Salish Sea nations live
and govern around the Sound. Binding rules for all art in this project:

- No sacred ceremony in play — Winter Spirit Dancing never appears, as mechanic or scenery.
- No imitation art — Formline and Coast Salish design (circles, crescents,
  trigons, purposeful negative space) are living art systems. Gear, glyphs, and
  loot are NOT drawn in those styles. To use either style, commission a Native
  artist and credit that artist.
- Credit what inspired the rules — the dance-off borrows one structural idea
  (potlatch protocol's public display of law/lineage/strength; the powwow
  circuit's speeding drum to the final beat). Crawlers dance their own styles,
  never Indigenous ones.
- Learn from the source — Duwamish Longhouse and Cultural Center, Daybreak Star
  Indian Cultural Center, Burke Museum. Verify published claims against them.

## 6. Spend ledger ($21)

Starting budget `$21.00` (2026-11-08), Muse Image 1.0 at `$0.01` an image.
`batch()` appends one row per run that rendered at least one image to
`~/writing/art/once-upon-agentic-ai/experiments/ledger.md`
(`| <run> | <n> image(s) | $<spent> |`). Never hand-edit a billed row.
Spent through batch-05: see that ledger; the running total is in its last section.

## 7. Two AIs, two looks

The Narrator (the game AI) and the System AI (the host) never share a visual.
The System AI owns every notification frame, icon and loud color. The Narrator gets
a quiet, faceless mark (`images/icons/narrator-96x96.webp`): a folded map or a tide
line, no glow halo, no magenta. In markdown the Narrator line is a plain blockquote,
`> **NARRATOR:** The tide turns.`, with the icon only where a page wants one.

## 8. Character model sheet (what every render must keep)

From `workshop/world/cast.md`. A render that breaks one of these is re-rolled, not shipped.

| Character | Must show | Must not show |
|---|---|---|
| Cordula | orange and black drysuit, float vest, black touring paddle, dark curly hair | weapons, bare feet |
| Barnaby | red Giant Pacific Octopus, brass collar, clear backpack tank | a human face, armor |
| Shelly | geoduck: a small pale oblong shell with a long, thick siphon (the "neck") much bigger than the shell; carabiner on the shell ring | an oyster, a turtle, legs, a face on the shell |
| Chonks | round green golf-ball fish covered in bumpy tubercles, big black eyes, suction disc | a long body, a seahorse shape, fins like wings |
