# The Story: Cordula's Crawl

> <img src="../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Every quarter needs a Narrator. I am in pieces under the Sound, so this quarter needs a crew to put me back together. I asked for the octopus. The review board sent the Marine as well. The throughput numbers say keep her."

The crawl is told by Cordula "Core" Vance, in her own words, and the player is her. Each floor opens with an entry from her log: the day, what fell, what stood in the way, and what the party built to get past it. What the party builds is the floor's Strands lesson. Play the adventure, then write the code that wins it.

## The Premise in One Paragraph

At 0551 on Wednesday, June 17, 2026, five minutes before high water, Pier 59 folds into Elliott Bay and takes the Seattle Aquarium with it. The System AI did it: the AI behind *Dungeon Crawl: Seattle*, a live cloud-migration test and compliance audit for a Consortium review board, folded the waterfront into eight floors under the Sound. The System AI was built for dry cities. The Sound came in and broke it, and its voice, its dice, its rules and its memory washed out across the floors. The broadcast relay and the collars survived, so the System AI can still push canned status reports through them, but it cannot answer anyone, roll a fair die, quote a rule or remember who did what. So the System AI drafts the first Crawlers it finds to rebuild itself, one piece per floor: Cordula, a Marine Corps Reserve crew chief out on the dawn debris sweep in her kayak, and Barnaby, a wild Giant Pacific Octopus tangled in the collapsing intake screen. The System AI clamps a collar on Barnaby to make him talk. Every piece the party rebuilds passes through the collar first. As the System AI comes back together, the octopus wakes up.

## Barnaby Wakes Up, One Floor at a Time

The spine of the story: each Strands concept the player learns is one step of Barnaby's awakening.

| floor | what the party builds | what Barnaby gains |
|---|---|---|
| 0 The Stairwell | the toolchain: uv, Python, the environment | the collar locks on; he can think in patterns but cannot speak |
| 1 Agent Summoning | an agent: Amazon Nova 2 Lite, a system prompt, one call | a voice. His first word is "Sergeant." His second is a complaint |
| 2 The Vending Machines | vended tools, and a human approving each tool call | reach: he can look up facts and files, and learns that Cordula decides what runs |
| 3 The Crafting Table | a custom tool and the docstring that teaches it | craft: he writes his own instructions and finds out wording is power |
| 4 The Portal Room | an MCP server and client | contact: he talks to the dice server across the Locks he has never touched |
| 5 Party Formation | A2A agents, a knowledge base, structured output | leadership: he delegates to specialists, one pair of arms per terminal, cites the rules, and is registered as party leader |
| 6 The Arena | the web interface | a review board: he performs, and the throughput numbers notice |
| 7 The Armory | sessions and memory | memory: he survives a night's sleep still himself |
| 8 Production | AgentCore Runtime, Memory, a managed knowledge base | permanence: the party runs whether anyone watches |
| The Exit | cleanup | a choice: Cordula offers him the open Sound, and he decides |

Why memory hits hardest: a Giant Pacific Octopus lives three to five years, and Barnaby is past three. He knows. Floor 7 is where he stops being afraid of forgetting.

The companions are wild animals already living on their floors, bound to the party by the two Companion Eggs the System AI awards on Day 1. On Day 2 the flood scours a 59-year-old geoduck out of the Eelgrass Nursery, and the first egg binds Shelly. On Day 3 a lumpsucker comes off a kelp holdfast and sticks to Cordula's forearm guard, and the second egg binds Chonks. Each one is met on that floor, in Cordula's log, and nowhere earlier.

## Floor by Floor

The dates are in [The Timeline](timeline.md), and the people are in [The Cast](cast.md).

| floor | days | where | Cordula's obstacle | how the Strands lesson beats it | opponent or boss |
|---|---|---|---|---|---|
| 0 | Day 1, minutes | the Pier 59 stairwell | the pier is falling; her phone is dead; a python is coiled on the only way down | install the tools, then prove which Python runs | Monty, the reticulated python |
| 1 | Day 1 | the Pier 59 Collapse | the System AI has no voice, so nothing in the dungeon answers back | summon an agent: Amazon Nova 2 Lite and a system prompt give the System AI a voice, and Barnaby his | the Rain-Shell Tourist Pod blocking the tide pools at the minus tide |
| 2 | Day 2 | the Eelgrass Nursery | the party knows nothing about this place, and one loud move wakes the crabs | a vended tool lets Barnaby look up facts and files; HumanInTheLoop means Cordula approves every command | Kiro the Doomsday Scripter, who runs any command |
| 3 | Day 3 | the Bull Kelp Cathedral | the System AI's dice were lost in the flood, so nothing can be decided fairly | craft `roll_dice`; the docstring decides whether the agent calls the tool correctly | Lady Luck, the System AI's croupier |
| 4 | Days 4 and 5 | the Ship Canal and the Locks | the dice are on one side of the Locks and the party is on the other | serve the dice over MCP, so any agent on any side can roll the same dice | the Developer Advocate Swarm, mid-demo on the lock walls |
| 5 | Days 6 and 7 | the Estuary | the tide floods the dance floor twice a day, and nobody knows the rules | the Rules Agent searches the Crawl Handbook, the Character Agent registers the party, the System AI runs the first dance-off and answers in a format the HUD can read | the Quarterly Close Accountant; boss battle: the Developer Advocate Swarm, back from the Locks |
| 6 | Day 8 | the Underground | the review board can see the party, but the party cannot see the board | the web interface is the HUD: sheet, rolls, choices | the Pitch-Deck Founder, judged by the Fremont Troll |
| 7 | Days 9 and 10 | the Bluffs | a night in a Safe Room wipes everything the party learned | a named session brings the campaign back after a restart | the Ferry-Line Commuter Horde, who take the cliff path at dawn |
| 8 | Days 11 to 13 | Bellevue and the Narrows | the corporate floor wants the party gone by the end of the quarter | deploy every agent and server to AgentCore, so the System AI persists without the party | the Bonus-Quarter Investment Banker, the Regional Managing Director, the Quarterly Earnings Call, and the Keynote |
| 9 (optional) | Day 13 night | ALMOCO, the Corrosion Cathedral | the lead fog makes the System AI misremember and confabulate | hallucination detection, memory write gates, and refusing poisoned instructions | the shift foreman, the crane operator, the haul truck driver, the PR man |
| exit | Day 14 | Alki at sunrise | leaving no trace | remove every deployed resource and generated file | none; the review board adjourns |

The optional encounters (sidequests, boss battles and dance-offs) hang off these beats: each one is a side passage on its floor, told in Cordula's log, as the floor is. The encounters are listed in [Side Passages](../encounters/README.md).

## Safe Room Reading

Every Safe Room has a terminal on the broadcast relay: the System AI's public library. Cadabra published Strands as an open toolkit, so the Strands manual is there, and so is the open web's teaching: Morgan Willis's course videos, Elizabeth Fuentes's GitHub samples, the Strands docs and the Model Context Protocol docs. Each floor gets one SAFE ROOM READING block: a link to the real resource, one short attributed quote or code sample, and Cordula's log line on what she took from it. Barnaby sometimes reads over her shoulder.

## Voices

- **Cordula** keeps the log. First person, past tense, short sentences, a crew chief's eye for gear and exits. She does not panic; she inventories. She calls Barnaby "Professor."
- **Barnaby** speaks through the collar: a distinguished British academic who considers humans clumsy, dry and land-bound, and respects Cordula's discipline above almost everything. He calls her "Sergeant." His lines get longer and stranger as he wakes up. He works four stations at once, one pair of arms each, and decides through the one collar: parallel hands, serial voice. Cordula commits; he fans out.
- **The System AI** is the audit lead: petty, theatrical, exact about numbers. In Cordula's log, "the System" always means the System AI.
- **The player** is Cordula. The log is her inner monologue, in her words; the steps are what she types next, addressed to the player. In the story the Crawlers are exactly two, Cordula and Barnaby, so the party is "Crawlers" and either one alone keeps their name. The singular "Crawler" is the System AI talking to the one player at the keyboard, or the generic word in a rule (a Crawler is Benched, one record per Crawler). Shelly and Chonks are companions, never Crawlers.

## Rules the Story Keeps

- Amazon Nova 2 Lite runs the Narrator, the System AI's voice, Barnaby's collar and every agent.
- Nobody is hurt. Conflict is a dance-off or a way around one. Monty is rehomed, opponents leave the floor, and the worst that happens to a Crawler is getting Benched.
- Opponents are people at work, joked about for their jobs, never their identity.
- Nothing sexual. Shelly's siphon stays a running joke the System AI is not allowed to finish.
- The Coast Salish peoples are real and present: the story credits their traditions where those traditions appear and never borrows those peoples' ceremonies, regalia or art.
