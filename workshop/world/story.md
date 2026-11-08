# The Story: Cordula's Crawl

> **System AI:** "Every season needs a narrator. I asked for the octopus. The network gave me the Marine."

The crawl is told by Cordula "Core" Vance, in her own words, and you play as her. Each floor opens with an entry from her log: what fell, what stood in the way, and what the party built to get past it. The thing they build is the floor's Strands lesson. You live the adventure, then you write the code that wins it.

## The Premise in One Paragraph

The morning the System arrives, Pier 59 folds into Elliott Bay and takes the Seattle Aquarium with it. The System is a broadcast AI filming *Dungeon Crawl: Seattle* for alien viewers, but the flood breaks it: its voice, its dice, its rule book and its memory are scattered across eight floors under the Sound. A broken System cannot run a show, so it conscripts the first Crawlers it finds to rebuild it, one subsystem per floor. Those Crawlers are Cordula, a Marine Corps Reserve crew chief out on a kayak patrol, and Barnaby, the aquarium's Giant Pacific Octopus. The System clamps a collar on Barnaby to make him talk. The collar is a System node: every subsystem the party rebuilds, Barnaby inherits. As the System comes back together, the octopus wakes up.

## Barnaby Wakes Up, One Floor at a Time

The spine of the story: each Strands concept you learn is one step of Barnaby's awakening.

| floor | what you build | what Barnaby gains |
|---|---|---|
| 0 The Stairwell | the toolchain: uv, Python, the environment | the collar locks on; he can think in patterns but cannot speak |
| 1 Agent Summoning | an agent: a model, a system prompt, one call | a voice. His first word is "Sergeant." His second is a complaint |
| 2 The Vending Machines | vended tools, and a human approving each call | reach: he can look things up, and learns that Cordula decides what runs |
| 3 The Crafting Table | a custom tool and the docstring that teaches it | craft: he writes his own instructions and finds out wording is power |
| 4 The Portal Room | an MCP server and client | contact: he talks to a machine across the Locks he has never touched |
| 5 Party Formation | A2A agents, a knowledge base, structured output | leadership: he delegates to specialists, cites the rules, and is registered as party leader |
| 6 The Arena | the web interface | an audience: he performs, and the ratings notice |
| 7 The Armory | sessions and memory | memory: he survives a night's sleep still himself |
| 8 Production | AgentCore Runtime, Memory, a managed knowledge base | permanence: the party runs whether anyone is watching or not |
| The Exit | cleanup | a choice: Cordula offers him the open Sound, and he decides |

Why memory hits hardest: a Giant Pacific Octopus lives three to five years. Barnaby knows it. Floor 7 is where he stops being afraid of forgetting.

The companions hatch from the eggs the System awards in the opening achievements: Shelly digs out of the sand flats of the Eelgrass Nursery on Floor 2, and Chonks pops off a kelp holdfast on Floor 3.

## Floor by Floor

| floor | where | Cordula's obstacle | how the Strands lesson beats it | opponent or boss |
|---|---|---|---|---|
| 0 | the Pier 59 stairwell | the pier is falling; her phone is dead; a python is coiled on the only way down | install the tools, then prove which Python you are running | Monty, the reticulated python |
| 1 | the Pier 59 Collapse | the System's voice is offline and nothing in the dungeon will talk | summon an agent: a model and a system prompt give the System its voice and Barnaby his | the Rain-Shell Tourist Pod blocking the tide pools |
| 2 | the Eelgrass Nursery | the party knows nothing about this place, and one loud move wakes the crabs | a vended tool lets Barnaby look things up; HumanInTheLoop means Cordula approves every command | Kiro the Doomsday Scripter, who will run anything |
| 3 | the Bull Kelp Cathedral | the System's dice were lost in the flood, so nothing can be decided fairly | craft `roll_dice`; the docstring decides whether it is used right | Lady Luck, the System's croupier |
| 4 | the Ship Canal and the Locks | the dice are on one side of the Locks and the party is on the other | serve the dice over MCP, so any agent on any side can roll the same dice | the Developer Advocate Swarm, mid-demo on the lock walls |
| 5 | the Estuary | the tide floods the dance floor twice a day, and nobody knows the rules | the Rules Agent searches the Crawl Handbook, the Character Agent registers the party, the Narrator runs the first dance-off and answers in a format the HUD can read | the Quarterly Close Accountant; boss battle: the Developer Advocate Swarm, back from the Locks |
| 6 | the Underground | the audience can see the party, but the party cannot see the show | the web interface is the HUD: sheet, rolls, choices | the Pitch-Deck Founder, judged by the Fremont Troll |
| 7 | the Bluffs | a night in a Safe Room wipes everything the party learned | a named session brings the campaign back after a restart | the Ferry-Line Commuter Horde, who take the cliff path at dawn |
| 8 | Bellevue and the Narrows | the corporate floor wants the party gone by end of quarter | deploy every piece to AgentCore, so the world persists without them | the Bonus-Season Investment Banker, the Regional Managing Director, the Quarterly Earnings Call, and the Keynote |
| exit | Alki at dawn | getting out clean | remove every deployed resource and generated file | none; the audience leaves |

The optional encounters (sidequests, boss battles and dance-offs) hang off these beats: each one is a side passage on the floor it belongs to, told in Cordula's voice like the floor itself. The ones open so far are listed in [Side Passages](../encounters/README.md).

## Voices

- **Cordula** narrates. First person, past tense in her log, short sentences, a crew chief's eye for gear and exits. She does not panic; she inventories. She calls Barnaby "Professor."
- **Barnaby** speaks through the collar: a distinguished British academic who considers humans clumsy, dry and land-bound, and respects Cordula's discipline above almost everything. He calls her "Sergeant." His lines get longer and stranger as he wakes up.
- **The System** is the game-show host: petty, theatrical, exact about numbers. It never narrates the story; it interrupts it.
- **You** are Cordula. The log is her inner monologue, in her words; the steps are what she types next, addressed to you.

## Rules the Story Keeps

- One model: the System, Barnaby's collar and every agent run on Amazon Nova 2 Lite.
- Nobody is hurt. Conflict is a dance-off or a way around one. Monty is rehomed, opponents leave the floor, and the worst that happens to a Crawler is getting Benched.
- Opponents are people at work, joked about for their jobs, never their identity.
- Nothing sexual. Shelly's siphon stays a running joke the System is not allowed to finish.
- The Coast Salish peoples are real and present: the story credits their traditions where they come up and never borrows their ceremonies, regalia or art.
