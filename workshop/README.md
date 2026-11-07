# Strands Dungeon Crawl: Learn the Strands Agents SDK One Floor at a Time

![The crawl: a brawler in heart boxers, a raptor-riding Persian cat casting magic, a screaming doll head, a tree elemental, a changeling assassin and an unimpressed show cat on a lava-lit obsidian floor](../images/banner-1680x720.webp)

"Roll for Initiative... in Python!"

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Welcome, Crawlers, to the dungeon. You enter with no shoes, a bare-bones terminal, and a dream of building autonomous multi-agent systems before the floor collapses. Every script you run drops an achievement box. Write a clean loop and earn a Bronze Box. Burn through your token limit with an accidental infinite loop and earn a Desperation Box. The audience is watching. Try to be interesting."

Welcome, Crawler, to the dungeon. This comprehensive workshop will transform you from a coding apprentice into a builder of AI agent orchestration. Floor after floor, you'll learn to create, equip, and command digital companions that can think, act, and collaborate like a legendary adventuring party.

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

- Add a vended tool, `http_request`, and let the agent query the Open5e API
- See the agent decide on its own when a tool is needed
- Bonus: `shell` and `file_editor`, each call gated by a `HumanInTheLoop` approval prompt

### [Floor 3: The Crafting Table](floor-3.md)
Write your own tool

- Turn a Python function into a tool with `@tool`
- Write the docstring the model reads to know when and how to call it
- Watch the agent plan sixteen rolls for a 4d6-drop-lowest character

### [Floor 4: The Portal Room (MCP)](floor-4.md)
Serve a tool over MCP and consume it

- Expose the same `roll_dice` with FastMCP over streamable HTTP
- Connect an agent to it with `MCPClient`

### [Floor 5: Party Formation (A2A)](floor-5.md)
Make agents talk to each other

- Expose agents with `A2AServer` and an `agent_factory` per conversation
- Give the Rules Agent a ChromaDB knowledge base built from the Basic Rules PDF
- Orchestrate them with the `a2a_client` tool and the MCP dice server
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

## Preparing for the Crawl

Everything you need to install (Python, uv, the repository) is covered in Floor 0. Bring basic Python knowledge, a terminal, and a sense of adventure.

## How to Survive the Crawl

### The Rules of the Crawl

- The System AI: the omniscient, slightly unhinged dungeon administrator tracking your code output, your syntax errors and your desperate attempts to pass `uv sync`
- The Crawlers: you. You enter with no shoes, a bare-bones terminal and a dream of building autonomous multi-agent systems before the floor collapses
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
- Solution Reference: completed exercises on the `solution-*` branches of the repository

### Getting Help

- Strands Documentation: [Official Strands Docs](https://strandsagents.com/)
- Solution Branches: reference implementations for each floor, if you get stuck
- Experiment Freely: the best way to learn is by trying things

## What is Strands?

Strands is a powerful framework for creating AI agents - think of it as your spellbook for summoning digital companions that can interact with tools and services. Like a well-equipped adventuring party, Strands provides:

- Agent Creation: easy summoning and configuration of AI companions
- Tool Integration: vended tools and custom enchantments
- Model Flexibility: support for multiple AI providers (different schools of magic)
- External Connections: integration with services through MCP
- Multi-Agent Systems: coordinate multiple agents working together

### The System Glossary

- Agent: a digital companion that can reason, decide, and use tools
- Tools: functions that agents can invoke to perform specific tasks
- System Prompt: the character sheet defining your agent's personality and behavior
- Model Provider: the source of intelligence (this crawl uses Amazon Nova 2 Lite on Amazon Bedrock)
- MCP: Model Context Protocol for connecting to external services
- A2A: Agent-to-Agent communication for multi-agent systems

## Learning Objectives

By completing this workshop, you'll learn:

- Agent Fundamentals: create, configure, and deploy AI agents
- Tool Craft: use vended tools and create custom ones
- External Integration: connect agents to external services via MCP
- Multi-Agent Systems: build complex applications with multiple cooperating agents
- Strands harness: rebuild the same system in a few lines with the pre-assembled agent
- Production with AgentCore: deploy the agents, their tools and their memory to Amazon Bedrock AgentCore
- Real-World Applications: create practical, production-ready agent systems

## Ready to Begin?

The stairwell is open. Start with [Floor 0: The Stairwell](floor-0.md) and begin your descent from coding apprentice to Agent Builder.

## Additional Resources

- [Strands Framework Documentation](https://strandsagents.com/) - complete reference and guides
- [Kiro Agentic IDE](https://kiro.dev/) - professional IDE for agent development
- [Strands GitHub Repository](https://github.com/strands-agents) - source code and community
- Example Projects - real-world implementations
