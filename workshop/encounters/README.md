# Side Passages: Optional Encounters

[Dungeon map](../README.md) | [Floor 1](../floor-1.md) | [Floor 2](../floor-2.md) | [Floor 3](../floor-3.md) | [Floor 4](../floor-4.md) | [Floor 5](../floor-5.md) | [Floor 6](../floor-6.md) | [Floor 7](../floor-7.md) | [Floor 8](../floor-8.md) <!-- floor-nav -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Side passages, Crawlers. Optional, unpaid, and the audience's favorite part. Every side passage starts where a floor ends and teaches a piece of the SDK the floor skipped. Skip the side passages if you like. The sponsors will notice."

Each encounter hangs off a floor: the encounter starts from that floor's finished code, teaches a Strands SDK module the floor does not cover, and runs on Amazon Nova 2 Lite like everything else in the crawl. Cordula logs each encounter, as she logs the floors. Encounter code follows the floor pattern: TODO markers on `main`, answers on the `solution` branch, a Show me the code block under each step, and offline tests on `solution`.

Every opponent of the crawl is playable in at least one floor or encounter. The floors run their own dance-offs through the Narrator (the Quarterly Close Accountant on Floor 5, the Pitch-Deck Founder on Floor 6, the Ferry-Line Commuter Horde on Floor 7, the investment banker, the swarm, the founder and the Keynote across Floor 8), and the boss battles and dance-offs below give each opponent its own code.

| floor | encounter | type | what gets built | modules |
|---|---|---|---|---|
| 1 | [The Commentary Booth](commentary-booth.md) | sidequest | a callback handler that streams the System AI's call of a dance-off and announces each tool call, then a receipt for the turn | `strands.handlers.callback_handler`, `strands.agent.agent_result` |
| 1 | [Read the Receipt](read-the-receipt.md) | sidequest | a receipt for each turn: why it stopped, the tokens of that turn alone and of each trip through the event loop, how often each tool ran, where the seconds went | `strands.agent.agent_result`, `strands.telemetry.metrics` |
| 1 | [The Reasoning Dial](reasoning-dial.md) | boss battle | a router over two settings of Amazon Nova 2 Lite: reasoning off for banter, reasoning on for a close Final Beat, a classifier that picks and a fallback that drops back to off | `strands.models.routing` |
| 2 | [The Tide Table](tide-table.md) | sidequest | today's real Seattle tides from NOAA, the party's notes in a notebook, and a ruling on whether the Estuary dance floor is underwater | `http_request`, `strands.vended_tools.notebook` |
| 2 | [The Sandbox Tide Pool](sandbox-tide-pool.md) | sidequest | Kiro the Doomsday Scripter's scroll cast inside a Docker sandbox instead of the local shell | `strands.sandbox.docker`, `strands.sandbox.posix_shell` |
| 2 | [The Policy Gatekeeper](policy-gatekeeper.md) | boss battle | a gate in front of Kiro: a ledger, a Cedar policy that allows or denies, and a risk classifier so a human sees only the risky calls | `strands.vended_interventions.cedar`, `strands.vended_interventions.hitl.classifier`, `strands.interventions.handler` |
| 2 | [Ask the Player](ask-the-player.md) | sidequest | a Narrator that pauses its turn to ask which Move Call to make, and resumes with the answer | `strands.vended_tools.handoff_to_user` |
| 3 | [The Concurrent Shuffle](concurrent-shuffle.md) | dance-off | the same round rolled by a sequential and a concurrent tool executor, timed | `strands.tools.executors` |
| 3 | [The Living Workbench](living-workbench.md) | sidequest | an agent that watches a `tools/` folder, and a `final_beat` tool that joins it while it runs | `strands.tools.watcher`, `strands.tools.decorator` |
| 4 | [The Locks Turnstile](locks-turnstile.md) | sidequest | an MCP router with a two-server allowlist, the dice and a tide server, that refuses every other server | `strands.vended_tools.mcp_router` |
| 4 | [Trace the Portal](trace-the-portal.md) | sidequest | every span of an MCP call printed to the console, the one made inside the server included | `strands.tools.mcp.mcp_instrumentation` |
| 5 | [The Paper Trail](paper-trail.md) | sidequest | a PDF audit report read with `pypdf` and added to the Rules Agent's knowledge base | `pypdf`, ChromaDB |
| 5 | [The Developer Advocate Swarm](developer-advocate-swarm.md) | boss battle | four advocates as a swarm, passing the mic themselves; the party beats whoever holds it | `strands.multiagent.swarm` |
| 5 | [Barnaby Takes the Call](barnaby-takes-the-call.md) | sidequest | both Floor 5 agents reached with an `A2AAgent`, every A2A event printed as it streams, and Barnaby's own A2A server | `strands.agent.a2a_agent`, `strands.multiagent.a2a.server` |
| 5 | [Read the Room, Typed](read-the-room-typed.md) | dance-off | the tempo and each Move Call picked as typed values by a decision model, then rolled against the accountant | `strands.decisions.llm_decision_model` |
| 5 | [Subcontract the Paperwork](subcontract-the-paperwork.md) | sidequest | a one-off clerk agent with fixed rules, one calculator tool and a pinned model | `strands.vended_tools.subagent` |
| 6 | [The Hype Meter](hype-meter.md) | sidequest | a hook that turns tool and model events into Hype, a `GET /hype` route, and a meter in the web interface | `strands.hooks.events`, `strands.hooks.registry` |
| 6 | [Sponsor Interrupt](sponsor-interrupt.md) | sidequest | a hook that stops the turn before a sponsor deal, a route that resumes it, and a dialog in the web interface to accept or refuse | `strands.interrupt` |
| 7 | [The Context Flood](context-flood.md) | boss battle | a 60-turn campaign squeezed into 20 messages, three ways, with the cast sheets pinned | `strands.agent.conversation_manager`, `compression.pin_message` |
| 7 | [The System Holds Grudges](system-holds-grudges.md) | sidequest | a memory manager over a folder of Markdown files, filled after every turn, and a second campaign that remembers the first | `strands.memory`, `strands.vended_memory_stores.file_memory_store` |
| 7 | [Keyword versus Vector](keyword-versus-vector.md) | dance-off | keyword search against vector search on the Crawl Handbook, scored on where each finds the Final Beat | `strands.storage.search.bm25`, ChromaDB |
| 7 | [Save Points](save-points.md) | sidequest | the same save point three ways, file, snapshot and S3, and a player who comes back from each | `strands.session` |
| 8 | [The Quarterly Earnings Call](quarterly-earnings-call.md) | boss battle | the accountant, the banker and the Regional Managing Director as a graph: one move each, in order, and the call only goes on if the party took the last round | `strands.multiagent.graph` |
| 8.3 | [The Ferry Manifest](ferry-manifest.md) | sidequest | the Rules Agent built from a configuration file, and a check that refuses any language model but Amazon Nova 2 Lite | `strands.experimental.agent_config` |
| 8.3 | [The Grudge Ledger in the Cloud](grudge-ledger.md) | sidequest | a Bedrock knowledge base as a writable memory store for the System AI's grudges | `strands.vended_memory_stores.bedrock_knowledge_base` |
| 8.4 | [The Broadcast Booth](broadcast-booth.md) | sidequest | span attributes for the round and the Move Call, read back in Amazon CloudWatch | `strands.telemetry.tracer`, `strands.telemetry.metrics` |
| 8.4 | [House Rules as Guardrails](house-rules-guardrails.md) | boss battle | an Amazon Bedrock guardrail that holds the broadcast's house rules on every Narrator turn, against the Regional Managing Director | `strands.types.guardrails` |
| 8.4 | [Mid-Song Save](mid-song-save.md) | sidequest | a dance-off round that pauses mid-round, saves where it stopped and picks up in a new process without throwing a die twice | `strands.experimental.checkpoint` |

Encounter code lives in [`encounters/`](../../encounters/), one folder per encounter, outside the floor folders: the floors stay exactly as their pages describe them. Dance-offs and boss battles roll through one shared file, [`encounters/dance_floor.py`](../../encounters/dance_floor.py), and that file scores every round by the [Crawl Handbook](../world/crawl-handbook/).

The crawl runs one language model, Amazon Nova 2 Lite. Two parts of the original plan reached past Amazon Nova 2 Lite: a cloud embedding service for Keyword versus Vector, and a third-party hosted decision service next to Read the Room, Typed. Neither part ships: Keyword versus Vector runs on local ChromaDB, and Read the Room, Typed decides on Nova 2 Lite.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Every floor down here has doors off the main corridor. Most doors lead to closets. Some open onto the System AI's best material. Barnaby wants to open every door. I want to finish the floor first. We compromise: finish the floor, then open one door.
