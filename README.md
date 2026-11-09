# aiRPG Seattle Dungeon Crawl

<p align="center">
<img src="images/wordmark-1200x240.webp" alt="aiRPG: Seattle Dungeon Crawl" width="720">
</p>

<p align="center">
<a href="workshop/floor-0.md"><img src="images/banner-1680x720.webp" alt="Cordula in black on black on grey dancing with her paddle raised beside kraken-scale Barnaby, a wild Giant Pacific Octopus dwarfing her, his dark skin flashing crimson and white bands as he dances, on the flooded folded Pier 59 floor with the rainy Seattle skyline behind" width="100%"></a>
</p>

<p align="center"><em>Something lives in the wreck of Galloping Gertie. The divers call it the King Octopus. Its name is Barnaby.</em></p>

Rebuild the System AI of a LitRPG dungeon crawl under Seattle. Learn the Strands Agents SDK one floor at a time.

[Enter the dungeon: Floor 0](workshop/floor-0.md)

---

<img src="images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **SYSTEM NOTIFICATION**

**DUNGEON CRAWL: SEATTLE, SEASON ONE. LIVE TO A GALAXY OF VIEWERS.**

The Sound came in at 0551. My voice, my dice, my rules, my memory are scattered across eight floors under your feet. Rebuild me, Crawler. The audience is watching.

---

<!-- art slot: party row with kraken-scale Barnaby beside Cordula, 4x 160x160, art team -->

<table>
<tr>
<td align="center" width="25%"><a href="workshop/world/cast.md#cordula-vance"><img src="images/cards/cast-cordula-640x640.webp" alt="Cordula Vance grinning in a matte black drysuit, charcoal float vest and grey webbing, karambits sheathed on her calves, holding a black touring paddle upright, inside a violet card frame" width="160"></a><br><strong>Cordula Vance</strong><br>commits every change</td>
<td align="center" width="25%"><a href="workshop/world/cast.md#barnaby"><img src="images/cards/cast-barnaby-legend-640x640.webp" alt="Barnaby, a huge scarred Giant Pacific Octopus with barnacle-worn arms and a brass collar, spread across the girders of a sunken bridge" width="160"></a><br><strong>Barnaby</strong><br>eight arms, four stations at once</td>
<td align="center" width="25%"><a href="workshop/world/cast.md#shelly"><img src="images/cards/cast-shelly-anchor-640x640.webp" alt="Shelly, a geoduck: a small pale shell dug into dark mud with a long, thick, wrinkled siphon curling up out of it, a carabiner and rope clipped to the shell" width="160"></a><br><strong>Shelly</strong><br>geoduck anchor</td>
<td align="center" width="25%"><a href="workshop/world/cast.md#chonks"><img src="images/cards/cast-chonks-640x640.webp" alt="Chonks, a round green lumpsucker covered in bumpy tubercles with big black eyes and a suction disc" width="160"></a><br><strong>Chonks</strong><br>lumpsucker tank</td>
</tr>
</table>

---

## The Descent

<!-- art slot: floor map grid with labeled plates, 4 columns at 240px each, art team -->

<table>
<tr>
<td align="center" width="25%"><a href="workshop/floor-0.md"><img src="images/floors/floor-0-1200x675.webp" alt="A flooded concrete stairwell descending under the collapsed waterfront, rain through a broken skylight, cracked aquarium glass on the landings" width="240"></a><br><strong>0. The Stairwell</strong><br>under Pier 59<br><code>setup</code></td>
<td align="center" width="25%"><a href="workshop/floor-1.md"><img src="images/floors/floor-1-1200x675.webp" alt="The shattered tanks of an aquarium pavilion folded into tide pools, barnacled pier pilings and anemones" width="240"></a><br><strong>1. Agent Summoning</strong><br>the Pier 59 Collapse<br><code>Agent()</code></td>
<td align="center" width="25%"><a href="workshop/floor-2.md"><img src="images/floors/floor-2-1200x675.webp" alt="A shallow underwater meadow of ribbon-like eelgrass over pale sand, sunlight filtering down" width="240"></a><br><strong>2. The Vending Machines</strong><br>the Eelgrass Nursery<br><code>vended tools</code></td>
<td align="center" width="25%"><a href="workshop/floor-3.md"><img src="images/floors/floor-3-1200x675.webp" alt="A towering underwater forest of bull kelp rising from black rocks to floating bulbs" width="240"></a><br><strong>3. The Crafting Table</strong><br>the Bull Kelp Cathedral<br><code>@tool</code></td>
</tr>
<tr>
<td align="center" width="25%"><a href="workshop/floor-4.md"><img src="images/floors/floor-4-1200x675.webp" alt="The Ballard Locks flooded, the two lock chambers glowing violet like portal gates, floating homes on the canal" width="240"></a><br><strong>4. The Portal Room</strong><br>the Ship Canal<br><code>MCP</code></td>
<td align="center" width="25%"><a href="workshop/floor-5.md"><img src="images/floors/floor-5-1200x675.webp" alt="A salt marsh at low tide where a river meets the Sound, red pickleweed and tall sedge" width="240"></a><br><strong>5. Party Formation</strong><br>the Estuary<br><code>A2A</code></td>
<td align="center" width="25%"><a href="workshop/floor-6.md"><img src="images/floors/floor-6-1200x675.webp" alt="The Seattle Underground beneath Pioneer Square turned into a dance floor, old brick arches and glowing purple sidewalk prisms" width="240"></a><br><strong>6. The Arena</strong><br>the Underground<br><code>web</code></td>
<td align="center" width="25%"><a href="workshop/floor-7.md"><img src="images/floors/floor-7-1200x675.webp" alt="A steep shoreline cliff above the tide, madrone trees with peeling red bark and wind-bent shore pines" width="240"></a><br><strong>7. The Armory</strong><br>the Bluffs<br><code>harness</code></td>
</tr>
<tr>
<td align="center" width="25%"><a href="workshop/floor-8.md"><img src="images/floors/floor-8-1200x675.webp" alt="Glass office towers across a dark Lake Washington with red laser-grid light, a suspension bridge in the distance" width="240"></a><br><strong>8. Production</strong><br>Bellevue and the Narrows<br><code>AgentCore</code></td>
<td align="center" width="25%"><a href="workshop/floor-8-1.md"><img src="images/floors/floor-8-1-1200x675.webp" alt="A brass and glass dice tower on a floating bridge deck at night, glowing dice tumbling inside" width="240"></a><br><strong>8.1 The Dice Server</strong><br>the floating bridge<br><code>MCP on Runtime</code></td>
<td align="center" width="25%"><a href="workshop/floor-8-2.md"><img src="images/floors/floor-8-2-1200x675.webp" alt="An empty ferry terminal at night with a long wooden registration counter, a stamp and stacks of character sheets" width="240"></a><br><strong>8.2 The Character Agent</strong><br>the ferry terminal<br><code>Memory</code></td>
<td align="center" width="25%"><a href="workshop/floor-8-3.md"><img src="images/floors/floor-8-3-1200x675.webp" alt="A sunken library of waterproof binders and scrolls lit teal, kelp drifting between the shelves" width="240"></a><br><strong>8.3 The Rules Agent</strong><br>the sunken library<br><code>knowledge base</code></td>
</tr>
<tr>
<td align="center" width="25%"><a href="workshop/floor-8-4.md"><img src="images/floors/floor-8-4-1200x675.webp" alt="A broadcast control booth high above the Tacoma Narrows at night, glowing monitors and a microphone, the suspension bridge through the windows" width="240"></a><br><strong>8.4 The Narrator in the Cloud</strong><br>above the Narrows<br><code>A2A on Runtime</code></td>
<td align="center" width="25%"><img src="images/floors/floor-9-1200x675.webp" alt="ALMOCO, the Corrosion Cathedral: three smoldering smelter stacks and mantis-like cranes over a black shoreline, fog, and teal runoff in the ditch water" width="240"><br><strong>9. ALMOCO</strong><br>the Corrosion Cathedral<br><em>optional, coming soon</em></td>
<td align="center" width="25%"><a href="workshop/cleanup.md"><img src="images/floors/exit-1200x675.webp" alt="A grey dawn on the beach at Alki, driftwood on the sand, the Seattle skyline and the Space Needle across Elliott Bay" width="240"></a><br><strong>The Exit</strong><br>Alki at sunrise<br><code>cleanup</code></td>
<td align="center" width="25%"></td>
</tr>
</table>

---

<p align="center">
<picture><source srcset="images/hud-strip-1200x120-still.webp" media="(prefers-reduced-motion: reduce)"><img src="images/hud-strip-1200x120.webp" alt="The HUD strip: a fourteen-segment Groove bar with one hot segment travelling on the beat, six Mana pips, and a d20 showing 20" width="720"></picture>
</p>

<p align="center">
<img src="assets/hud/groove-bar.svg" alt="" width="120">
<img src="assets/hud/hype-tick.svg" alt="" width="48">
<img src="assets/hud/mana-pips.svg" alt="" width="96">
<img src="assets/hud/d20.svg" alt="" width="48">
<img src="assets/hud/move-choreography.svg" alt="" width="48">
<img src="assets/hud/move-power.svg" alt="" width="48">
<img src="assets/hud/move-presence.svg" alt="" width="48">
<img src="assets/hud/move-footwork.svg" alt="" width="48">
<img src="assets/hud/tide-clock.svg" alt="" width="96">
</p>

<p align="center"><em>The LitRPG chrome: Groove, Hype, Mana, the d20, Move Calls, the tide</em></p>

---

## Bosses and Sponsors

<p align="center">
<img src="images/cards/boss-monty-640x640.webp" alt="Monty the python, a boss opponent" width="96">
<img src="images/cards/boss-earnings-call-640x640.webp" alt="The Quarterly Earnings Call, a boss opponent" width="96">
<img src="images/cards/boss-regional-director-640x640.webp" alt="The Regional Director, a boss opponent" width="96">
<img src="images/cards/boss-the-keynote-640x640.webp" alt="The Keynote, a boss opponent" width="96">
</p>

<p align="center"><em>Monty the python, the Quarterly Earnings Call, the Regional Director, the Keynote. Nonlethal. People at work, joked about for their jobs.</em></p>

<p align="center">
<img src="images/icons/sponsor-bellevue-96x96.webp" alt="" width="32"> <strong>Bellevue Consortium</strong> -- Doors '94 OS, sponsors the opponents, quarter closes June 30<br>
<img src="images/icons/sponsor-cadabra-96x96.webp" alt="" width="32"> <strong>Cadabra, Inc.</strong> -- delivery drones, rented obstacles, published Strands<br>
<img src="images/icons/sponsor-benthic-96x96.webp" alt="" width="32"> <strong>Benthic Collective</strong> -- Ballard fishing and kombucha co-op, adores Barnaby<br>
<img src="images/icons/sponsor-hydros9-96x96.webp" alt="" width="32"> <strong>Hydros-9 Aquatic Collective</strong> -- South Lake Union water-tech, ninth pivot, adores Barnaby
</p>

---

## How You Learn

Every Safe Room has a terminal on the broadcast relay. Cadabra published Strands as an open toolkit, so the Strands manual is there, and so is the open web's teaching. Read the docs, watch an explainer, read a working sample, then type it yourself.

**Free courses and samples**

- Morgan Willis, "Building AI agent harnesses with Strands Agents", 14 free videos -- [start with video 01](https://www.youtube.com/watch?v=NAEX4ORLkbQ), or read Bryan's [companion page](https://bryanchasko.com/strands-agents-course/)
- Elizabeth Fuentes, [Strands samples on GitHub](https://github.com/elizabethfuentes12) -- MIT-0 licensed, model-agnostic
- [Strands Agents SDK](https://strandsagents.com/)

---

<hr>

<details>
<summary><strong>Requirements</strong></summary>

Every agent on every floor runs on Amazon Nova 2 Lite on Amazon Bedrock:

```
model_id: us.amazon.nova-2-lite-v1:0
region: us-west-2
```

**What you need**

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) (or pip)
- AWS credentials with permission to invoke Amazon Nova 2 Lite in us-west-2
- Docker (the Sandbox Tide Pool encounter and the web build) and Node.js (Floor 6's web interface)
- Floor 8 only: Node.js 20 or later and the [AgentCore CLI](https://github.com/aws/agentcore-cli)

**Preflight check**

```bash
uv run python 0_stairwell/preflight.py
```

</details>

<details>
<summary><strong>Branches</strong></summary>

- `main`: the skeleton to clone, with `# TODO` markers to fill in
- `solution`: the same files with the answers written below each TODO, run end to end

Use `solution` when a TODO blocks progress.

</details>

<details>
<summary><strong>Tests</strong></summary>

The tests live on the `solution` branch:

```bash
git switch solution
uv sync --group dev
uv run pytest tests/
```

The tests cover every floor without calling Amazon Nova 2 Lite or AWS: agents, tools, MCP server, A2A servers, Groove and Mana, the handbook knowledge base, the harness options, and the Floor 8 memory, retrieval and entrypoint. The web interface has its own suite in `web/` (`npm ci`, then `npx vitest run`). [Coverage page](workshop/coverage.md).

</details>

<details>
<summary><strong>Dependencies</strong></summary>

The workshop ships no lockfile (`uv.lock` is gitignored), so `uv sync` installs the latest compatible releases. Three bounds are pinned in `pyproject.toml`, each with a comment explaining why: a floor on `strands-agents`, `strands-harness` for Floor 7, and a `mcp<2` ceiling because mcp 2.0 renamed the `FastMCP` server class Floor 4 teaches.

If a floor breaks against a newer release, please open an issue.

</details>

<details>
<summary><strong>Contributing</strong></summary>

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

</details>

---

This crawl builds on Once Upon Agentic AI, the AWS sample workshop that first taught the Strands Agents SDK through a role-playing game. Every exercise of that workshop is still here; the [coverage page](workshop/coverage.md) maps them. The game-running agent the source workshop calls the Narrator is the System AI here.

---

**The World**: [World guide](workshop/world/README.md) -- [The Story](workshop/world/story.md) -- [Timeline](workshop/world/timeline.md) -- [Cast](workshop/world/cast.md) -- [The System](workshop/world/the-system.md) -- [Seattle, Under the Sound](workshop/world/seattle.md) -- [Crawl Handbook](workshop/world/crawl-handbook/)

**Stuck?**: [`study/ask_the_system.py`](study/README.md) is a study companion built with Strands. Ask it about any floor, TODO, error or Strands API, and it answers from this repository and the Strands API reference, with citations.

---

_The System AI is watching. Happy crawling, Crawler._
