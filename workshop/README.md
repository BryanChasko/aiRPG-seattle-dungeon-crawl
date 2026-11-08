# aiRPG Seattle Dungeon Crawl: Learn the Strands Agents SDK One Floor at a Time

![Cordula, in an orange drysuit with Barnaby the octopus in a water tank on her back and Chonks the lumpsucker on her forearm, strikes a dance pose with her kayak paddle while a startled accountant and an investment banker slip on the flooded floor of collapsed Pier 59. Shelly the geoduck puffs sea mist, bull kelp hangs overhead, and the Space Needle shows through the breach](../images/banner-1680x720.webp)

"Roll for Initiative... in Python!"

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Welcome, Crawlers, to the dungeon under Seattle. Pier 59 collapsed this morning, the Salish Sea came in, and you came with it: soaked, short one kayak, armed with a bare-bones terminal and a dream of building autonomous multi-agent systems before the next floor floods. Every script you run drops an achievement box. Write a clean loop and earn a Bronze Box. Burn through your token limit with an accidental infinite loop and earn a Desperation Box. The audience is watching. Try to be interesting."

## Who You Are

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** I am Cordula Vance. Core, to anyone who has shared a boat with me. Marine Corps Reserve, amphibious crew chief, and on weekends I run kayak patrols on the Sound. This morning I tied up under Pier 59 to say hello to the octopus, and the pier folded into Elliott Bay with both of us under it.
>
> He rides on my back now, in my kayak's dry bag with two bilge pumps, and he runs the party. His name is Barnaby. Eight arms, a doctorate's worth of opinions, and, since the System clamped a collar on him, a British accent. A geoduck named Shelly and a lumpsucker named Chonks joined later. Nobody asked them.
>
> The System that did this is broken. Its voice, its dice, its rule book and its memory washed out across eight floors under the Sound, and the only way out is to put it back together, one piece per floor. Every piece I rebuild, Barnaby's collar picks up, and he wakes up a little more. I build every piece with the Strands Agents SDK: the first floor is one agent and one call, the last is the whole party running on Amazon Bedrock AgentCore. I write all of it.
>
> Nobody gets hurt down here. A fight is a dance-off, the opponents are accountants, bankers and developer advocates at work, and the worst that happens is I get Benched and wake up in a Safe Room. I keep a log. The log is what happened. The steps are what I type next.

What the System, the party and the rules are made of:

- [World guide](world/README.md): everything the agents say about the world comes from these pages
- [The Story](world/story.md): the log, floor by floor; every floor's obstacle is its Strands lesson
- [The System](world/the-system.md): the LitRPG design, one layer per workshop floor
- [The Cast](world/cast.md) and [Seattle, Under the Sound](world/seattle.md)
- [The Crawl Handbook](world/crawl-handbook/): the rules, and the Rules Agent's knowledge base

Every floor ends its main exercise with a **SYSTEM DESIGN** callout: the LitRPG layer that the Strands concept you just learned makes possible.

## The Dungeon Map

The dungeon has nine floors and an exit. Each floor builds on the one above it - clear them in order or the stairs will not open. Floor 7 is optional: Floor 8 starts again from the Floor 5 code.

### [Floor 0: The Stairwell](floor-0.md)
Clone the repo, install uv and Python, run uv sync

### [Floor 1: Agent Summoning](floor-1.md)
Create and call your first agent

- Build an agent with `Agent(system_prompt=...)` and invoke it with a single call
- Enable DEBUG logs on the strands logger to watch the requests sent to the model

### [Floor 2: The Vending Machines](floor-2.md)
Give your agent tools that ship with the SDK

- Add a vended tool, `http_request`, and let the agent look up a giant octopus on the Open5e API
- See the agent decide on its own when a tool is needed
- Bonus: `shell` and `file_editor`, each call gated by a `HumanInTheLoop` approval prompt

### [Floor 3: The Crafting Table](floor-3.md)
Write your own tool

- Turn a Python function into a tool with `@tool`
- Write the docstring the model reads to know when and how to call it
- Watch the agent roll a 4d6-drop-lowest character in four calls, because the docstring told it how

### [Floor 4: The Portal Room (MCP)](floor-4.md)
Serve a tool over MCP and consume it

- Expose the same `roll_dice` with FastMCP over streamable HTTP
- Connect an agent to it with `MCPClient`

### [Floor 5: Party Formation (A2A)](floor-5.md)
Make agents talk to each other

- Expose agents with `A2AServer` and an `agent_factory` per conversation
- Give the Rules Agent a ChromaDB knowledge base built from the Crawl Handbook
- Orchestrate them with the `a2a_client` tool and the MCP dice server, and run a dance-off
- Return typed JSON with `structured_output_model`

### [Floor 6: The Arena (Web Interface)](floor-6.md)
Play with your Narrator in the browser

- Connect the web UI to your orchestrator on http://127.0.0.1:8009
- Follow each tool call in the terminal

### [Floor 7 (Optional): The Armory (Strands harness)](floor-7.md)
Rebuild the Narrator in a few lines with Strands harness

- Assemble it with `create_harness()`: instructions, mcp_servers, tools, builtin_tools
- Resume a campaign across restarts with a named session
- Know when to pick the harness and when to stay on the SDK

### [Floor 8: Production (AgentCore)](floor-8.md)
Deploy the whole party to Amazon Bedrock AgentCore, one brick at a time

- Deploy the dice server, the Character Agent and the Rules Agent to AgentCore Runtime with the `agentcore` CLI
- Call them from the Narrator with IAM-signed clients: `aws_iam_streamablehttp_client` for MCP, `SigV4HTTPXAuth` for A2A
- Keep the characters and the conversation in AgentCore Memory (`AgentCoreMemorySessionManager`), the rules in a managed knowledge base
- Serve the Narrator with `BedrockAgentCoreApp` and follow one turn across runtimes in the traces
- Runs in your own AWS account

### [The Exit: Final Cleanup](cleanup.md)
Stop your services, remove the Floor 8 AWS resources and delete the harness state in `.agent/`

### [Side Passages: Optional Encounters](encounters/README.md)
Deeper into the SDK, off the main corridor, each one starting where its floor ends: 28 sidequests, dance-offs and boss battles

- Floor 1: [The Commentary Booth](encounters/commentary-booth.md), [Read the Receipt](encounters/read-the-receipt.md), boss battle [The Reasoning Dial](encounters/reasoning-dial.md)
- Floor 2: [The Tide Table](encounters/tide-table.md), [The Sandbox Tide Pool](encounters/sandbox-tide-pool.md), boss battle [The Policy Gatekeeper](encounters/policy-gatekeeper.md), [Ask the Player](encounters/ask-the-player.md)
- Floor 3: dance-off [The Concurrent Shuffle](encounters/concurrent-shuffle.md), [The Living Workbench](encounters/living-workbench.md)
- Floor 4: [The Locks Turnstile](encounters/locks-turnstile.md), [Trace the Portal](encounters/trace-the-portal.md)
- Floor 5: [The Paper Trail](encounters/paper-trail.md), boss battle [The Developer Advocate Swarm](encounters/developer-advocate-swarm.md), [Barnaby Takes the Call](encounters/barnaby-takes-the-call.md), dance-off [Read the Room, Typed](encounters/read-the-room-typed.md), [Subcontract the Paperwork](encounters/subcontract-the-paperwork.md)
- Floor 6: [The Hype Meter](encounters/hype-meter.md), [Sponsor Interrupt](encounters/sponsor-interrupt.md)
- Floor 7: boss battle [The Context Flood](encounters/context-flood.md), [The System Holds Grudges](encounters/system-holds-grudges.md), dance-off [Keyword versus Vector](encounters/keyword-versus-vector.md), [Save Points](encounters/save-points.md)
- Floor 8: boss battle [The Quarterly Earnings Call](encounters/quarterly-earnings-call.md), [The Ferry Manifest](encounters/ferry-manifest.md), [The Grudge Ledger in the Cloud](encounters/grudge-ledger.md), [The Broadcast Booth](encounters/broadcast-booth.md), boss battle [House Rules as Guardrails](encounters/house-rules-guardrails.md), [Mid-Song Save](encounters/mid-song-save.md)

## Preparing for the Crawl

Everything you need to install (Python, uv, the repository) is covered in Floor 0. Bring basic Python knowledge, a terminal, and a sense of adventure.

## How to Survive the Crawl

### The Rules of the Crawl

- The System AI: the omniscient, slightly unhinged dungeon administrator tracking your code output, your syntax errors and your desperate attempts to pass `uv sync`
- The Crawlers: you, Cordula, with Barnaby on your back running the party and Shelly and Chonks along as companions. You enter soaked, short one kayak, with a bare-bones terminal and a dream of building autonomous multi-agent systems before the next floor floods
- The Loot Boxes: every floor you clear drops an achievement box. Write a clean loop, earn a Bronze Box. Burn your token limit on an accidental infinite loop, earn a Desperation Box
- The Audience: billions of alien viewers. They are not on your side. Neither are the sponsors

### Clear the Floors in Order

> <img src="../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** Complete the floors in order. Each builds upon the previous one's knowledge and skills.

- Start with Floor 0 - Set up your environment (Python, uv, the repository)
- Progress through each floor - don't skip ahead, each floor introduces essential concepts
- Complete all TODOs - each floor has guided exercises to build the concepts
- Test your creations - run your agents and see them come to life
- Experiment and explore - try variations and push the boundaries

### Workshop Structure

Each floor follows the same pattern:

- README Guide: complete instructions and background lore
- TODO Exercises: hands-on coding challenges to complete
- Testing Instructions: how to verify your creations work
- Solution Reference: completed exercises on the `solution` branch of the repository

### Getting Help

- Strands Documentation: [Official Strands Docs](https://strandsagents.com/)
- Solution Branch: reference implementations for every floor, if you get stuck
- Experiment Freely: the best way to learn is by trying things

## What is Strands?

Strands is a framework for creating AI agents: think of it as the toolkit the System uses to run its crawl. Strands provides:

- Agent Creation: an agent is a model, a system prompt and a list of tools
- Tool Integration: vended tools and your own `@tool` functions
- Model Flexibility: support for multiple model providers (this crawl runs on Amazon Nova)
- External Connections: integration with services through MCP
- Multi-Agent Systems: coordinate multiple agents working together

### The System Glossary

- Agent: a model that can reason, decide, and use tools
- Tools: functions that agents can invoke to perform specific tasks
- System Prompt: the character sheet defining your agent's personality and behavior
- Model Provider: the source of intelligence (this crawl uses Amazon Nova 2 Lite on Amazon Bedrock)
- MCP: Model Context Protocol for connecting to external services
- A2A: Agent-to-Agent communication for multi-agent systems
- LitRPG: fiction where the story runs on a visible game System: stats, levels, loot and notifications. *Dungeon Crawler Carl* is the inspiration for this one's tone

## Learning Objectives

By completing this workshop, you'll learn:

- Agent Fundamentals: create, configure, and deploy AI agents
- Tool Craft: use vended tools and create custom ones
- External Integration: connect agents to external services via MCP
- Multi-Agent Systems: build complex applications with multiple cooperating agents
- Strands harness: rebuild the same system in a few lines with the pre-assembled agent
- Production with AgentCore: deploy the agents, their tools and their memory to Amazon Bedrock AgentCore
- Real-World Applications: create practical, production-ready agent systems
- LitRPG System design: the interface, stats, conflict loop, economy and consequences of a game, each one built by the agent capability that makes it possible

## Ready to Begin?

The stairwell is open. Start with [Floor 0: The Stairwell](floor-0.md) and begin your descent under the Sound.

## Additional Resources

- [Strands Framework Documentation](https://strandsagents.com/) - complete reference and guides
- [Kiro Agentic IDE](https://kiro.dev/) - professional IDE for agent development
- [Strands GitHub Repository](https://github.com/strands-agents) - source code and community
