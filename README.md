# Strands Dungeon Crawl: Learn the Strands Agents SDK One Floor at a Time

![The crawl: a brawler in heart boxers, a raptor-riding Persian cat casting magic, a screaming doll head, a tree elemental, a changeling assassin and an unimpressed show cat on a lava-lit obsidian floor](images/banner-1680x720.webp)

_"Roll for Initiative... in Python!"_

A hands-on workshop that teaches the [Strands Agents SDK](https://strandsagents.com/) by building a Narrator for a fantasy role-playing game: one agent first, then tools, an MCP server, remote agents over A2A, a web interface, the same system rebuilt with Strands harness, and finally the whole party deployed to Amazon Bedrock AgentCore.

**The instructions live in this repository: [workshop/](workshop/README.md).** The System AI will narrate them. This repository holds the code you complete along the way: each floor folder contains files with `# TODO` markers that the workshop walks you through.

## Quick Start

```bash
git clone https://github.com/BryanChasko/strands-dungeon-crawl.git
cd strands-dungeon-crawl
uv python install          # if you don't have Python yet (3.10+)
uv sync                    # creates .venv/ with every dependency
source .venv/bin/activate  # .venv\Scripts\activate on Windows
```

No `uv`? Install it from [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/), or use plain pip: `pip install .` from the repository root.

The agents run on Amazon Nova 2 Lite on Amazon Bedrock (`us.amazon.nova-2-lite-v1:0`, first-party Amazon, no third-party model access needed). You need AWS credentials allowed to invoke it in us-west-2, see [Floor 0](workshop/floor-0.md). Floor 8 deploys to AgentCore: in the workshop Code Editor everything it needs is already set up; in an AWS account of your own, it also needs Node.js 20+ and the [AgentCore CLI](https://github.com/aws/agentcore-cli), which its instructions install.

## The Dungeon Map

| Floor | Folder | What you build |
|---|---|---|
| 0. The Stairwell | [instructions](workshop/floor-0.md) | Set up Python, uv and this repository |
| 1. Agent Summoning | [`1_strands_basics/`](1_strands_basics/) | Your first agent, a system prompt, debug logs |
| 2. The Vending Machines | [`2_vended_tools/`](2_vended_tools/) | Tools that ship with the SDK (vended tools): `http_request` on the Open5e API; bonus: `shell` + `file_editor` gated by `HumanInTheLoop` |
| 3. The Crafting Table | [`3_custom_tools/`](3_custom_tools/) | Your own `@tool`: the dice roller |
| 4. The Portal Room - MCP | [`4_mcp_integration/`](4_mcp_integration/) | The same dice roller served over MCP, and an agent that consumes it |
| 5. Party Formation - A2A | [`5_a2a_integration/`](5_a2a_integration/) | Rules Agent + Character Agent over A2A, a Narrator orchestrator with structured output |
| 6. The Arena - Web Interface | [web UI](https://bryanchasko.github.io/strands-dungeon-crawl/) | Play with your Narrator through the browser |
| 7. The Armory - Strands harness (optional) | [`7_strands_harness/`](7_strands_harness/) | The Narrator API rebuilt with `create_harness()` |
| 8. Production - AgentCore | [`8_agentcore_production/`](8_agentcore_production/) | The dice server, the Character Agent, the Rules Agent and the Narrator deployed to AgentCore Runtime with the `agentcore` CLI, IAM-signed MCP and A2A calls, characters and conversation in AgentCore Memory, rules in a managed knowledge base |
| The Exit | [instructions](workshop/cleanup.md) | Stop your services, remove the Floor 8 AWS resources and delete the generated files |

Complete the floors in order: each one reuses what the previous one built. Floor 7 is optional: Floor 8 starts again from the Floor 5 code.

## Branches

- `main`: the skeleton you clone, with `# TODO` markers to fill in.
- `solution`: the same files with the answers written below each TODO, run end to end on Amazon Nova 2 Lite. Floor 8 there is the end-of-8.4 state, served by AgentCore. Use it if you get stuck.

## Dependencies

The workshop ships no lockfile (`uv.lock` is gitignored), so `uv sync` installs the latest compatible releases. Three bounds are pinned in `pyproject.toml`, each with a comment explaining why: a floor on `strands-agents` (the release the instructions were written against), `strands-harness` for Floor 7, and a `mcp<2` ceiling because mcp 2.0 renamed the `FastMCP` server class Floor 4 teaches. If a floor breaks against a newer release, please open an issue.

## Tests

The tests live on the `solution` branch, because they import the finished Floor 5 agents:

```bash
git switch solution
uv sync --group dev
uv run pytest tests/
```

They cover the Floor 5 A2A servers: module imports, the per-context `agent_factory` isolation, and the agent card served over HTTP. The web interface has its own suite in `web/` (`npm ci`, then `npx vitest run`).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

_"The best way to predict the future is to build the agents that will create it."_ - Modern Developer Wisdom

_The System is watching. Happy crawling, Agent Builder._
