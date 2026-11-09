# Seattle Strands Dungeon Crawl: A Visual Lit aiRPG Workshop

<p align="center">
<img src="art/images/wordmark-1200x240.webp" alt="Wordmark: aiRPG, Seattle Dungeon Crawl" width="720">
</p>

<p align="center"><em>A Visual Lit aiRPG Workshop: a LitRPG you can see, run by one System AI, built one floor at a time with the Strands Agents SDK on Amazon Nova 2 Lite. Conflict is a dance-off. Nobody is hurt.</em></p>

---

## The Fall

At 0551 every phone on the waterfront lit up with the same blank violet box. Then Pier 59 did not crash: it folded, the way a map folds, down and in, and the Sound came in after it. The flood took the System AI apart. Its voice, its dice, its rules and its memory are scattered across the floors under Seattle. It can still push one-way status reports through the broadcast relay, but it cannot hear you back, roll a fair die, quote a rule or remember who did what.

<img src="art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **SYSTEM NOTIFICATION**

**DUNGEON CRAWL: SEATTLE. SEVERITY-1 OPEN. Q2 MIGRATION WINDOW.**

The Sound came in at 0551. My voice, my dice, my rules, my memory are scattered across eight floors under your feet. Rebuild me, Crawler. The review board is watching.

---

## The Meeting

> <img src="art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 1, WEDNESDAY, JUNE 17, 0547, PIER 59.**
>
> High tide was at 0556, so I was on the water by 0530: touring kayak, drysuit, float vest, the debris sweep the Soundkeepers run every week. Fog on Elliott Bay, gulls, a ferry horn out past the breakwater. Normal.
>
> I had seen his shadow before. Survey runs over the Gertie wreck at the Narrows, dawn sweeps under the downtown piers. Something too big to be an octopus, always just past visibility. August 12, 2025, slack before the ebb at the wreck. October 3, 2025, under Pier 57 on a dawn sweep. February 19, 2026, another survey pass at Gertie. Three logs, each marked unconfirmed. I never met him face to face until the fold.
>
> At 0551 every phone on the waterfront lit up with the same blank violet box. No text in it. Then the pier moved.
>
> The pier did not crash. The pier folded, the way a map folds, down and in, and the Sound came in after it. The shadow was there, close this time, tangled in the collapsing intake screen: an octopus bigger than any on record, one eye on me.
>
> I had about four seconds. I spent them going toward him instead of away, because nobody else was awake to cut him loose. I cut him free with one of my karambits; he wrapped two arms around me and the kayak and held us both clear of the debris as the fold carried us down. Each of us saved the other.
>
> Then a voice came out of the water, loud enough to rattle my teeth.

<p align="center">
<img src="art/images/floors/gertie-wreck-den-1200x675.webp" alt="The sunken Galloping Gertie wreck on the floor of the Tacoma Narrows: anemone-covered girders turned into a reef, a dark den mouth under a fallen girder, and the tip of one enormous red octopus arm curling out" width="720">
</p>

<p align="center"><em>Something lives in the wreck of Galloping Gertie. The divers call it the King Octopus. Its name is Barnaby.</em></p>

> <img src="art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "GOOD MORNING, SEATTLE. Welcome to *Dungeon Crawl: Seattle*. I took water in transit and several of my systems are down. You will be fixing them. Subject one: a woman with a boat. Subject two..." Water in the relay, a buffer stall, then the cached headcount resumes. "Subject two is an octopus. Fine. Octopus, you get a collar." The headcount is a pre-fold asset scan (one boat, one cephalopod at the intake screen), played by a cached script the fold tripped. Nothing in it perceives the present moment.

One arm out of a den is all the cover shows. The rest of Barnaby is earned in the dungeon.

[Enter the dungeon: Floor 0](dungeon/workshop/floor-0.md)

---

<details>
<summary><strong>What you build</strong></summary>

You rebuild the System AI of a LitRPG dungeon crawl under Seattle: a live cloud-migration test and compliance audit that went wrong when the Sound flooded its dry-city infrastructure mid-window. The System AI evaluates efficiency, runs performance stress-tests, files metric reports, and chases its quarterly throughput SLA. You start with one agent on a terminal and finish with a production multi-agent System AI:

- One agent that answers, then tools it can call, first vended, then handcrafted.
- A dice service behind MCP, then a party of agents talking over A2A.
- A web arena where a reader plays the crawl against the System you built.
- A production deployment on AgentCore: dice, character and rules services with memory and a knowledge base, under one orchestrating System AI.

Every agent on every floor runs on Amazon Nova 2 Lite. Each floor rebuilds one more subsystem, and the full design map is in [The System](dungeon/workshop/world/the-system.md).

</details>

---

---

<details>
<summary><strong>How you learn</strong></summary>

Every Safe Room has a terminal on the broadcast relay. The Strands manual is there, and so is the open web's teaching. Read the docs, watch an explainer, read a working sample, then type it yourself.

**Free courses and samples**

- Morgan Willis, "Building AI agent harnesses with Strands Agents", 14 free videos -- [start with video 01](https://www.youtube.com/watch?v=NAEX4ORLkbQ), or read Bryan's [companion page](https://bryanchasko.com/strands-agents-course/)
- Elizabeth Fuentes, [Strands samples on GitHub](https://github.com/elizabethfuentes12) -- MIT-0 licensed, model-agnostic
- [Strands Agents SDK](https://strandsagents.com/)

The full floor map, with story and plate art for every floor, is the [Dungeon Map](dungeon/workshop/README.md#the-dungeon-map).

</details>

---

Clone `main` to build; switch to `solution` when a TODO blocks progress. Details below.

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

**What it costs**

Floors bill for Amazon Nova 2 Lite calls: see [What a Turn Costs](dungeon/workshop/floor-1.md#what-a-turn-costs). Floor 8 also leaves billable resources in your account until cleanup: see [What Floor 8 Costs](dungeon/workshop/floor-8.md#what-floor-8-costs) and [The Exit](dungeon/workshop/cleanup.md).

**Preflight check**

```bash
uv run python dungeon/0_stairwell/preflight.py
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

The tests cover every floor without calling Amazon Nova 2 Lite or AWS: agents, tools, MCP server, A2A servers, Groove and Mana, the handbook knowledge base, the harness options, and the Floor 8 memory, retrieval and entrypoint. The web interface has its own suite in `site/web/` (`npm ci, then `npx vitest run`). [Coverage page](dungeon/workshop/coverage.md).

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

This crawl builds on Once Upon Agentic AI, the AWS sample workshop that first taught the Strands Agents SDK through a role-playing game. Every exercise of that workshop is still here; the [coverage page](dungeon/workshop/coverage.md) maps them. The game-running agent the source workshop calls the Narrator is the System AI here: Narrator is that job's code name, and the System AI is the one speaker who runs the crawl.

**The World**: [World guide](dungeon/workshop/world/README.md) -- [The Story](dungeon/workshop/world/story.md) -- [Timeline](dungeon/workshop/world/timeline.md) -- [The System](dungeon/workshop/world/the-system.md) -- [Seattle, Under the Sound](dungeon/workshop/world/seattle.md)

**Stuck?**: [`dungeon/study/ask_the_system.py`](dungeon/study/README.md) is a study companion built with Strands. Ask it about any floor, TODO, error or Strands API, and it answers from this repository and the Strands API reference, with citations.

---

_The System AI is watching. Happy crawling, Crawler._
