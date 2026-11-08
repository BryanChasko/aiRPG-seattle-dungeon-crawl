# Workshop copy-paste snippets

Conventions match the floor-5.md template: `floor-nav`, `floor-files`,
`cordula-log` markers. Paths are relative to `workshop/`.

## System-AI quote

```markdown
> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Your taunt here. The audience is watching."
```

Variants: swap the icon for `warning-96x96.webp` (**SYSTEM WARNING:**),
`item-96x96.webp` (**ITEM ACQUIRED:**), `achievement-96x96.webp`
(**NEW ACHIEVEMENT UNLOCKED!**), `sponsor-96x96.webp`, `floor-boss-96x96.webp`,
`stairwell-96x96.webp`. All seven icons exist in `images/icons/`.

## Narrator line

```markdown
> **NARRATOR:** The tide turns. The east stairwell floods in nine minutes.
```

The Narrator is the game AI and speaks rarely: one plain present-tense line when the world changes, at most one per page. It has no icon in markdown and never uses the System AI icon.

## Cordula log

```markdown
<!-- cordula-log -->
> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, DAY N, WEEKDAY, MONTH D, FLOOR N.** One paragraph: where the party is, what broke, what the floor builds. Placeholder sentence about what the party does next.
<!-- /cordula-log -->
```

Days and dates come from `workshop/world/timeline.md`.

## Dungeon-map details checklist

Paste under the plate image when a floor references a shared location plate:

```markdown
![Floor N: Title](../images/floors/floor-N-1200x675.webp)
```

- Eelgrass nursery (Floor 2): `![Eelgrass nursery](../images/floors/eelgrass-nursery-1200x675.webp)`
- Kelp cathedral bulbs (Floor 3): `![Kelp cathedral bulbs](../images/floors/kelp-cathedral-bulbs-1200x675.webp)`
- Estuary dance floor (Floor 5): `![Estuary dance floor](../images/floors/estuary-dancefloor-1200x675.webp)`
- Estuary flooded (Floor 5): `![Estuary flooded](../images/floors/estuary-flooded-1200x675.webp)`
- Underground troll (Floor 6): `![Underground troll](../images/floors/underground-troll-1200x675.webp)`
- Safe Room (Floor 7): `![Safe Room](../images/floors/safe-room-1200x675.webp)`
- Bluffs cliff (Floor 7): `![Bluffs cliff](../images/floors/bluffs-cliff-1200x675.webp)`
- Bellevue lobby (Floor 8): `![Bellevue lobby](../images/floors/bellevue-lobby-1200x675.webp)`
- The Exit (cleanup): `![The Exit](../images/floors/exit-1200x675.webp)`

## Expected-output details block

```markdown
<details>
<summary>Show me the code for Step N</summary>

```python
# TODO: Step N - ...
result = "your answer here"
```

</details>
```

## Achievement toast

```markdown
> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[TITLE IN CAPS]**
>
> Reward: a [Bronze Box]. Inside: one sentence describing the loot.
```

## HUD image embed pattern

The HUD art lives in `assets/hud/` as script-free SMIL SVGs: `d20`, `final-beat-drum`, `groove-bar`, `hype-tick`, `mana-pips`, `tide-clock`, and the move icons `move-power`, `move-footwork`, `move-endurance`, `move-choreography`, `move-readroom`, `move-presence`.

```markdown
<img src="../assets/hud/groove-bar.svg" alt="Groove meter" width="120">
```

Move icons use `width="48"`. The SVGs honor `prefers-reduced-motion`.

## Art rules

- no images inside the crawl handbook: `workshop/world/crawl-handbook/` is the Rules Agent's knowledge base, so it stays text
- no Shelly art before her Floor 2 welcome, no Chonks art before his Floor 3 welcome
- new art comes from a plan in `images/plans/` rendered with `tools/airpg_render.py`, never a hand-written request
