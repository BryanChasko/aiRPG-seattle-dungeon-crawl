# Visual Design System: Seattle Strands Dungeon Crawl

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
| icon | `*-96x96.webp` | 96x96 | webp lossy q88 | none (0) | none - `no dots, no vignette (UI glyph)` |

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
Cinematic dark-fantasy character card illustration, square, single subject centered with generous margin, waist-up or full body, high contrast, sharp detail, obsidian black and slate grey background with deep Puget Sound teal and sea-glass green, neon magenta-violet System rim light, warm sodium-orange accent light, rainy Pacific Northwest atmosphere, darker edges. Friendly, funny, game-show energy, never menacing, no weapons drawn.
```

Wide style block (floors; banners have their own 21:9 block in `style.json` that allows the cast and dance-off action):

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

- No sacred ceremony in play - Winter Spirit Dancing never appears, as mechanic or scenery.
- No imitation art - Formline and Coast Salish design (circles, crescents,
  trigons, purposeful negative space) are living art systems. Gear, glyphs, and
  loot are NOT drawn in those styles. To use either style, commission a Native
  artist and credit that artist.
- Credit what inspired the rules - the dance-off borrows one structural idea
  (potlatch protocol's public display of law/lineage/strength; the powwow
  circuit's speeding drum to the final beat). Crawlers dance their own styles,
  never Indigenous ones.
- Learn from the source - Duwamish Longhouse and Cultural Center, Daybreak Star
  Indian Cultural Center, Burke Museum. Verify published claims against them.

## 6. Spend ledger ($21)

Starting budget `$21.00` (2026-11-08), Muse Image 1.0 at `$0.01` an image.
`batch()` appends one row per run that rendered at least one image to
`~/writing/art/once-upon-agentic-ai/experiments/ledger.md`
(`| <run> | <n> image(s) | $<spent> |`). Never hand-edit a billed row.
Spent through batch-05: see that ledger; the running total is in its last section.

## 7. One System AI, one look

The System AI is the only AI character: it runs the crawl and narrates it. "Narrator" is its
job and the name the code uses, never a second being, so there is no Narrator art, icon or
style. Every speaking line uses the System AI icon (`images/icons/system-ai-96x96.webp`) and
the label `**System AI:**`; its frames, glows and magenta-violet light are the one AI look.

The System (the game: rules, stats, notifications, HUD, battle log, loot tables) is never drawn
as a character. Its visuals are interface: the HUD SVGs in `assets/hud/`, the notification
icons and the loot and sponsor icons.

Speaker icons that sit in front of a bold name carry empty alt text (`alt=""`), so a screen
reader says the name once. Type voices for every speaker live in
`workshop/_snippets.md` (## Voices): GitHub strips color, so voices differ by
tag and shape, never by color, and the play page mirrors them with matching
`voice-*` classes in `web/src/assets/theme.css`.

## 7a. Sponsors and contractors (local Pacific Northwest tropes, never a real company)

| Name | Who they are | Badge direction |
|---|---|---|
| Bellevue Consortium | a tech monolith across the lake, famous for the Doors '94 operating system; sponsors the opponents, hates surprises, wants the party gone before the quarter closes June 30 | a half-open door glyph on cold steel enamel, glass towers over Lake Washington, brass rim; corporate, beige-desktop nostalgia; never a window grid or flag, never a real logo |
| Hydros-9 Aquatic Collective | a venture-funded South Lake Union water-tech startup on its ninth pivot (hence the 9); adores Barnaby | a glossy teal enamel water drop over nine stacked pivot arrows, startup-sticker sheen, brass rim |
| Benthic Collective | a Ballard fishing-and-kombucha cooperative; adores Barnaby | a fishing float and a kombucha jar on weathered brass, net texture |
| Cadabra, Inc. | the crawl's fulfillment contractor: delivery drones drop every loot box, it rents the dungeon its obstacles, and it published Strands as an open toolkit | a cardboard parcel with a rocket fin and a drone rotor, brass rim; never a smile arrow, never a real logo |

Never draw or name a real company, logo or trademark. Teaching text keeps real product names;
these names are story only.

## 8. Character model sheet (what every render must keep)

From `workshop/world/cast.md` and the canon in `workshop/world/story.md`, updated to canon revision 3 (2026-11-08): Cordula black on black on grey with calf karambits, Barnaby kraken-scale, dark at rest, never carried. A render that breaks one of these is re-rolled, not shipped.

| Character | Must show | Must not show |
|---|---|---|
| Cordula | matte black drysuit, charcoal float vest, grey webbing (black on black on grey), black touring paddle, dark curly hair, a sheathed karambit on the outside of each calf | orange or high-visibility color, a tank on her back, weapons drawn, bare feet |
| Barnaby | a wild Giant Pacific Octopus past every record (about 190 lb, about 22 ft arm tip to arm tip, kraken scale next to Cordula), dark charcoal and slate mottling at rest, old scars and barnacle-worn skin of a wild animal, the System AI's blackened brass collar with a faint violet glow; crimson and white chromatophore flashes only while dancing or furious (`BARNABY_DANCE`); on dry floors a black misting Hydration Harness on his mantle (`BARNABY_HARNESS`) and he moves under his own power, on wet floors he swims free | a human face, armor, an aquarium, glass walls, a monster, being carried, riding in a backpack tank, red-orange resting color, a polished brass collar |
| Shelly | geoduck: a small pale oblong shell with a long, thick siphon (the "neck") much bigger than the shell; carabiner on the shell ring | an oyster, a turtle, legs, a face on the shell |
| Chonks | round green golf-ball fish covered in bumpy tubercles, big black eyes, suction disc | a long body, a seahorse shape, fins like wings |

## 9. Visual Lit alignment: image beside the words it teaches

A page in this workshop is read, not scrolled past. The image and the text it
explains must be visible at the same time, so the eye can move between them
without losing its place. Five rules, in force for every new or revised page:

1. Beside, not below. Put the picture in a two-column table next to the brief,
   check or beat it belongs to. Never stack a lone image above or below its
   paragraph where one scroll hides the other. The boss layout in
   `workshop/_snippets.md` is the copy-paste form; `workshop/floor-0.md`
   Step 4 (Monty) is the worked example.
2. Image at reading size. A card shown as the subject of a beat renders large
   enough to read its detail: boss and cast cards at `width="320"` from the
   640x640 source. A 28px speaker icon is a label, not a picture; it never
   stands in for the card. Shrinking a subject card to thumbnail size
   (`width="240"` or less, alone on its own line) is the failure this rule ends.
3. One image per beat. One picture carries one story beat, one boss, or one
   check. Do not cluster three cards around one paragraph, and do not repeat
   the same card as icon, thumbnail and plate on one screen. If a beat has no
   art yet, leave the text clean and add a backlog row in
   `docs/art-placements.md`; never borrow a nearby picture that shows
   something else.
4. Alt that describes. Subject art carries alt text that says what is in the
   picture (who, where, doing what), never a filename, a caption repeated
   word for word, or empty alt. Only the 28px speaker icons in front of a
   bold name carry `alt=""`, so a screen reader says the name once (section 7).
5. Spoiler gating by floor. A character appears in art only on or after the
   floor where the party meets them. Shelly joins on Floor 2 and Chonks joins
   on Floor 3, so the cover, Floor 0 and Floor 1 never show or name them in
   art, captions or alt text. Barnaby on the cover is a cliffhanger tease
   only: the wreck, a shadow, one arm, an eye. His full dance reveal is
   earned later in the crawl and is never spent on the cover.

Layout follows the reading, never the reverse: when text and image compete
for width, keep the image at reading size and let the words take the other
half of the table. Code blocks, TODO markers and checks stay full width
under the table, unchanged.
