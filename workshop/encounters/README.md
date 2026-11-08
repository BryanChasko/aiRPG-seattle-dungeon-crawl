# Side Passages: Optional Encounters

[Dungeon map](../README.md) | [Floor 1](../floor-1.md) | [Floor 3](../floor-3.md) | [Floor 5](../floor-5.md) | [Floor 7](../floor-7.md) <!-- floor-nav -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Side passages, Crawlers. Optional, unpaid, and the audience's favorite part. Every one of them starts where a floor ends and teaches a piece of the SDK the floor skipped. Skip them if you like. The sponsors will notice."

Each encounter hangs off a floor: it starts from that floor's finished code, teaches a Strands module the floor does not, and runs on Amazon Nova 2 Lite like everything else in the crawl. Cordula tells each one, like the floors. The code works the same way as a floor: TODO markers on `main`, answers on the `solution` branch, a Show me the code block under every step.

Every opponent of the crawl is playable somewhere. The floors run their own dance-offs through the Narrator (the Quarterly Close Accountant on Floor 5, the Pitch-Deck Founder on Floor 6, the Ferry-Line Commuter Horde on Floor 7, the investment banker, the swarm, the founder and the Keynote across Floor 8), and the boss battles below give the executives and the advocates code of their own.

| floor | encounter | type | what you build | modules |
|---|---|---|---|---|
| 1 | [The Commentary Booth](commentary-booth.md) | sidequest | a callback handler that streams the System's call of a dance-off and announces each tool call, then a receipt for the turn | `strands.handlers.callback_handler`, `strands.agent.agent_result` |
| 3 | [The Concurrent Shuffle](concurrent-shuffle.md) | dance-off | the same round rolled by a sequential and a concurrent tool executor, timed | `strands.tools.executors` |
| 5 | [The Paper Trail](paper-trail.md) | sidequest | a PDF audit report read with `pypdf` and added to the Rules Agent's knowledge base | `pypdf`, ChromaDB |
| 5 | [The Developer Advocate Swarm](developer-advocate-swarm.md) | boss battle | four advocates as a swarm, passing the mic themselves; the party beats whoever holds it | `strands.multiagent.swarm` |
| 7 | [The Context Flood](context-flood.md) | boss battle | a 60-turn campaign squeezed into 20 messages, three ways, with the cast sheets pinned | `strands.agent.conversation_manager`, `compression.pin_message` |
| 8 | [The Quarterly Earnings Call](quarterly-earnings-call.md) | boss battle | the accountant, the banker and the Regional Managing Director as a graph: one move each, in order, and the call only goes on if the party took the last round | `strands.multiagent.graph` |

Encounter code lives in [`encounters/`](../../encounters/), one folder per encounter, outside the floor folders: the floors stay exactly as their pages describe them.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Every floor down here has doors off the main corridor. Most of them are closets. Some of them are where the System keeps the good stuff. Barnaby wants to open all of them. I want to finish the floor first. We compromise: finish the floor, then open one door.
