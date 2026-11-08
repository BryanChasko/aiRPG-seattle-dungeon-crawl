# aiRPG Seattle Dungeon Crawl: Learn the Strands Agents SDK One Floor at a Time

![Cordula, in an orange drysuit with Barnaby the octopus in a water tank on her back and Chonks the lumpsucker on her forearm, strikes a dance pose with her kayak paddle while a startled accountant and an investment banker slip on the flooded floor of collapsed Pier 59. Shelly the geoduck puffs sea mist, bull kelp hangs overhead, and the Space Needle shows through the breach](images/banner-1680x720.webp)

_"Roll for Initiative... in Python!"_

A hands-on workshop that teaches the [Strands Agents SDK](https://strandsagents.com/) through a LitRPG dungeon crawl under Seattle. The game AI that runs the crawl breaks on its first morning, and each floor rebuilds one piece of it in Python on Amazon Nova 2 Lite: one agent first, then tools, an MCP server, agents that talk over A2A, a web interface, Strands harness, and finally the whole game on Amazon Bedrock AgentCore.

## The Collapse

> <img src="images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, DAY 1, WEDNESDAY, JUNE 17, 2026, 0551, PIER 59.**
>
> High water was due at 0556. I was in my kayak under Pier 59 on the dawn debris sweep, tied up at the aquarium's intake screens, close enough to hear the pumps inside.
>
> At 0551 every phone on the waterfront lit up with the same blank violet box. Then the pier folded, down and in, the way a map folds, and Elliott Bay came in after it.
>
> I had about four seconds. I spent them going toward the aquarium instead of away from it, because the octopus inside was looking at me through cracked glass, and nobody else was awake to go get him.

> <img src="images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "GOOD MORNING, SEATTLE. Welcome to *Dungeon Crawl: Seattle*, season one, live to a galaxy of viewers. A small problem. The Narrator, the mind that runs this show, built your dungeon for a dry city, and the Sound came in. Its voice, its dice, its rules and its memory are scattered across eight floors under your feet. No Narrator, no show. So you will rebuild it, Crawler, one floor at a time. The audience is watching. Try to be interesting."

> <img src="images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** I have rebuilt engines with less to go on. I keep a log. The log is what happened. The steps are what I type next.

### [Begin the descent: Floor 0, The Stairwell](workshop/floor-0.md)

---

## Index

### The Workshop

- [Workshop guide](workshop/README.md): the dungeon map, every floor and every side passage
- [Floor 0: The Stairwell](workshop/floor-0.md): clone the repository, install uv and Python, and check access to Amazon Nova 2 Lite
- [Side Passages](workshop/encounters/README.md): 28 optional sidequests, dance-offs and boss battles, each one off a floor
- [The Exit](workshop/cleanup.md): stop the local services, remove the Floor 8 AWS resources and delete the generated files

### Quick Start

```bash
git clone https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl.git
cd aiRPG-seattle-dungeon-crawl
uv python install          # if Python 3.10 or later is missing
uv sync                    # creates .venv/ with every dependency
source .venv/bin/activate  # .venv\Scripts\activate on Windows
```

No `uv`? Install `uv` from [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/), or use plain pip: `pip install .` from the repository root.

Every agent on every floor runs on Amazon Nova 2 Lite on Amazon Bedrock (`us.amazon.nova-2-lite-v1:0`). The AWS credentials need permission to invoke Amazon Nova 2 Lite in us-west-2; [Floor 0](workshop/floor-0.md) checks them. Floor 8 deploys to AgentCore: the workshop Code Editor already has everything Floor 8 needs; in a personal AWS account, Floor 8 also needs Node.js 20 or later and the [AgentCore CLI](https://github.com/aws/agentcore-cli), which the Floor 8 instructions install.

### The Dungeon Map

| Floor | Folder | What gets built |
|---|---|---|
| 0. The Stairwell | [instructions](workshop/floor-0.md) | Python, uv and this repository |
| 1. Agent Summoning | [`1_strands_basics/`](1_strands_basics/) | First agent, a system prompt, debug logs |
| 2. The Vending Machines | [`2_vended_tools/`](2_vended_tools/) | Tools that ship with the SDK (vended tools): `http_request` on the Open5e API to look up a giant octopus; bonus: `shell` + `file_editor` gated by `HumanInTheLoop` |
| 3. The Crafting Table | [`3_custom_tools/`](3_custom_tools/) | A custom `@tool`: the dice roller |
| 4. The Portal Room - MCP | [`4_mcp_integration/`](4_mcp_integration/) | The same dice roller served over MCP, and an agent that calls the MCP server |
| 5. Party Formation - A2A | [`5_a2a_integration/`](5_a2a_integration/) | Rules Agent (searching the Crawl Handbook) + Character Agent over A2A, and the Narrator orchestrator with structured output that runs dance-offs |
| 6. The Arena - Web Interface | [web UI](https://bryanchasko.github.io/aiRPG-seattle-dungeon-crawl/) | Play the Narrator through the browser |
| 7. The Armory - Strands harness (optional) | [`7_strands_harness/`](7_strands_harness/) | The Narrator API rebuilt with `create_harness()` |
| 8. Production - AgentCore | [`8_agentcore_production/`](8_agentcore_production/) | The dice server, the Character Agent, the Rules Agent and the Narrator deployed to AgentCore Runtime with the `agentcore` CLI, IAM-signed MCP and A2A calls, characters and conversation in AgentCore Memory, rules in a managed knowledge base |
| The Exit | [instructions](workshop/cleanup.md) | Stop the local services, remove the Floor 8 AWS resources and delete the generated files |

Complete the floors in order: each one reuses what the previous one built. Floor 7 is optional: Floor 8 starts again from the Floor 5 code.

### The World

- [World guide](workshop/world/README.md): where everything the agents say about the world comes from
- [The Story](workshop/world/story.md): Cordula's crawl, floor by floor, and how each obstacle is a Strands lesson
- [The Timeline](workshop/world/timeline.md): the fourteen days of the crawl, with the tides
- [The Cast](workshop/world/cast.md): character sheets for the party and for the two minds that run the crawl, the Narrator and the System AI
- [The System](workshop/world/the-system.md): the LitRPG design, mapped to the floor that builds each layer
- [Seattle, Under the Sound](workshop/world/seattle.md): whose land this is, the eight dungeon floors and the Puget Sound plants and habitats the floors are built from
- [The Crawl Handbook](workshop/world/crawl-handbook/): the rules, and the knowledge base the Rules Agent searches

### Stuck? Ask the System

[`study/ask_the_system.py`](study/README.md) is a study companion built with Strands: ask it about any floor, TODO, error or Strands API, and it answers from this repository and the Strands API reference, with citations. It gives hints before answers.

### Branches

- `main`: the skeleton to clone, with `# TODO` markers to fill in.
- `solution`: the same files with the answers written below each TODO, run end to end on Amazon Nova 2 Lite. Floor 8 there is the end-of-8.4 state, served by AgentCore. Use it when a TODO blocks progress.

### Dependencies

The workshop ships no lockfile (`uv.lock` is gitignored), so `uv sync` installs the latest compatible releases. Three bounds are pinned in `pyproject.toml`, each with a comment explaining why: a floor on `strands-agents` (the release the instructions were written against), `strands-harness` for Floor 7, and a `mcp<2` ceiling because mcp 2.0 renamed the `FastMCP` server class Floor 4 teaches. If a floor breaks against a newer release, please open an issue.

### Tests

The tests live on the `solution` branch, because the tests import the finished Floor 5 agents:

```bash
git switch solution
uv sync --group dev
uv run pytest tests/
```

The tests cover every floor without calling Amazon Nova 2 Lite or AWS: the agent each floor builds, that agent's tools and the tool specs, the dice math, the MCP server, the Floor 5 A2A servers (module imports, the per-context `agent_factory` isolation, the agent card served over HTTP), Groove and Mana, the handbook knowledge base, the harness options, and the Floor 8 memory records, retrieval and entrypoint. The web interface has its own suite in `web/` (`npm ci`, then `npx vitest run`). [workshop/coverage.md](workshop/coverage.md) maps every exercise of the original workshop to the floor and the test that covers it.

### Credits

This crawl is built on *Once Upon Agentic AI*, the AWS sample workshop that first taught the Strands Agents SDK through a role-playing game. Every exercise of *Once Upon Agentic AI* is still here; the coverage page shows where. The Narrator does the job that workshop gives the agent that runs the game.

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

_"The best way to predict the future is to build the agents that will create it."_ - Modern Developer Wisdom

_The System is watching. Happy crawling, Agent Builder._
