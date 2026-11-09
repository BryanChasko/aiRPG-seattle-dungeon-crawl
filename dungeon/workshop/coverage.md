# Coverage: Everything the Original Teaches, and What the Crawl Adds

> <img src="../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "I keep receipts. Here are mine."

This crawl builds on *Once Upon Agentic AI*, the AWS sample workshop that first taught the Strands Agents SDK through a role-playing game. Every exercise the original workshop teaches is still here. This page shows the evidence.

## Findings

- **Every original exercise is still here.** All 63 `# TODO` steps of the original workshop are present, in the same files, in the same order. The only change is a name: the orchestrator files are named after the Narrator.
- **Every Strands API the original teaches is still hands-on.** The table below maps each part of the original to its floor, the APIs typed by hand, and the check that proves the code works.
- **Testing grew from one floor to all of them.** The original suite covered the Floor 5 A2A servers (8 test functions). The `solution` branch now runs 311 tests, none of which call Amazon Nova 2 Lite or AWS. The tests cover every floor, the 34 optional encounters and the study companion, plus the 169 web interface tests in `site/web/`.
- **One technique was swapped for another, and it is the only one.** The original built its knowledge base from a downloaded PDF with `pypdf`. The crawl builds it from the Crawl Handbook, the crawl's own Markdown rule book. The ChromaDB collection, the `all-MiniLM-L6-v2` embeddings, the 1,000-character overlapping passages and the cited answers are all unchanged. PDF text extraction is no longer part of the main floors; PDF text extraction returns in [The Paper Trail](encounters/paper-trail.md), the optional Floor 5 encounter, with `pypdf` and the same collection.
- **Run live 2026-11-09:** the full Floor 8 AgentCore deployment (all four bricks, both memories, knowledge base, proxy, Keynote) in `us-west-2`, then torn down. Still covered by unit tests only: the Floor 2 bonus room, which requires a person to approve each step, which means it cannot run unattended.

## Part by Part

| original part | floor here | what you type (TODO steps) | how it is checked | what the crawl adds |
|---|---|---|---|---|
| 0. An Unexpected Adventure | [0. The Stairwell](floor-0.md) | clone, `uv sync`, activate the environment | `uv sync` succeeds | the premise: the Narrator is broken and the party rebuilds it; SYSTEM DESIGN layer 0 |
| 1. The Art of Agent Summoning | [1. Agent Summoning](floor-1.md) | DEBUG logging, `Agent(model=..., system_prompt=...)`, the first call (3) | live on Amazon Nova 2 Lite; `test_floor1_agent_logging_prompt_and_model` | the agent pinned to Amazon Nova 2 Lite; an exercise on how the system prompt sets the genre |
| 2. The Adventurer's Arsenal | [2. The Vending Machines](floor-2.md) | `http_request` on Open5e (2); bonus: `shell`, `file_editor`, `HumanInTheLoop(ask="stdio")` (4) | live on Amazon Nova 2 Lite; `test_floor2_http_request_is_a_tool`, `test_floor2_bonus_room_gates_shell_and_file_editor_behind_hitl` | a creature lookup tied to the party leader; the license note for the System Reference Document |
| 3. The Art of Magical Forging | [3. The Crafting Table](floor-3.md) | `@tool`, the docstring, `tool_spec`, adding the tool (4) | live on Amazon Nova 2 Lite; five `test_floor3_*` tests (spec, math, errors, wiring) | `roll_dice(faces, count, drop_lowest)`, redesigned after Amazon Nova 2 Lite skipped rolls with a one-die tool; the docstring lesson told from that measurement |
| 4. Planar Portals | [4. The Portal Room](floor-4.md) | `FastMCP(port=8002)`, `@mcp.tool()`, streamable HTTP (4); `MCPClient(url=...)` handed to the agent (3) | live on Amazon Nova 2 Lite; `test_floor4_server_*`, `test_floor4_client_*` | one fair source of dice shared by every agent, with a `[SYSTEM] DICE ROLL` log line per roll |
| 5. The Grand Alliance | [5. Party Formation](floor-5.md) | ChromaDB knowledge base, `query_rules`, `A2AServer` with an `agent_factory`, agent card name and description (5); Character Agent tools and card (5); Narrator `MCPClient`, `make_a2a_client(allowed_endpoints=...)`, tools, `structured_output_model=StoryOutput` (4) | live on Amazon Nova 2 Lite; the original 8 A2A tests (16 cases) plus four `test_floor5_*` tests | the Crawl Handbook; Groove and Mana computed in code; the dance-off loop; Narrator rules against invented rolls and invented answers |
| 6. Web Interface Testing | [6. The Arena](floor-6.md) | play in the browser against the local Narrator | 169 vitest tests in `site/web/` | the party picker, the GROOVE and MANA panel, the System theme |
| 7. The Enchanted Armour | [7. The Armory](floor-7.md) | `create_harness` with `instructions`, `mcp_servers`, `tools`, `builtin_tools=[]`, `session`, and `structured_output_model` passed through (7) | live on Amazon Nova 2 Lite; `test_floor7_harness_gets_every_option_the_page_teaches` | Amazon Nova 2 Lite with reasoning off, measured near ten seconds a turn |
| 8. Push to Production with AgentCore | [8](floor-8.md), [8.1](floor-8-1.md) to [8.4](floor-8-4.md) | dice server for AgentCore (1); memory records and `serve_a2a` (3); `retrieve` and `serve_a2a` (2); IAM-signed MCP and A2A, `BedrockAgentCoreApp`, `AgentCoreMemorySessionManager`, the entrypoint (15) | unit tests: `test_floor8_*` (4), `test_story_output_matches_across_floors` | the Crawl Handbook in a Bedrock knowledge base; `nova-policy.json`; SYSTEM DESIGN layer 8, a persistent world |
| Final cleanup | [The Exit](cleanup.md) | remove the AWS resources and generated files | `describe-stacks` returns not found | the empty registry restored with one `git checkout` |

## Yes, And

What the crawl teaches that the original did not:

- **LitRPG System design, one layer per floor.** Voice, outside knowledge, hard math, fair dice, rules and the core loop, the HUD, consequence, a persistent world. See [The System](world/the-system.md).
- **A world with rules you can read.** The [Crawl Handbook](world/crawl-handbook/) is the Rules Agent's knowledge base, so changing a rule and rebuilding the index changes the game.
- **Honest agents.** The Narrator rolls through the dice server and reports what it rolled, uses the party's cast scores instead of inventing them, and says so when a tool call fails. Each of these Narrator rules came from a measured failure on Amazon Nova 2 Lite.
- **Offline tests for every floor.** Each answer is checked the way its floor page teaches the exercise.
- **Optional encounters, 34 of them:** [sidequests, dance-offs and boss battles](encounters/README.md) on every floor, each teaching a Strands module its floor does not: callback handlers and the receipt of a turn, model routing, vended tools and interventions, sandboxes, tool executors and hot reload, MCP routing and tracing, A2A agents, graphs, swarms, decisions and subagents, hooks and interrupts in the web interface, conversation managers, memory, retrieval and session managers, and on AgentCore tracing, guardrails, checkpoints, agent configuration and a knowledge base memory store. Each has TODO markers on `main`, answers and offline tests on `solution`. Three deeper floors for plugins, steering and middleware are still planned, tracked with the companion workshop site.
- **The Paper Trail:** the optional Floor 5 encounter that brings back the PDF extraction technique from the original. Index a PDF, the Quarterly Close Accountant's audit report, with `pypdf` alongside the Crawl Handbook.

## Method

- **TODO steps:** every `# TODO: ... Step N` line in the original `main` branch, compared with this repository's `main`, by file and step number, after the Narrator rename. The result: 63 in the original, 63 here, no step missing and none added.
- **APIs:** each step's answer on the `solution` branch, read against the original's latest solution branch.
- **Tests:** `uv run pytest tests/` on the `solution` branch, 311 passing on 2026-11-08, plus `npx vitest run` in `site/web/`, 169 passing.
- **Live runs:** Floors 1 to 5 and 7 on Amazon Nova 2 Lite (us-west-2), 2026-11-07.
