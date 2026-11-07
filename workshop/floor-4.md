# Floor 4: The Portal Room (MCP)

[Previous: Floor 3](floor-3.md) | [Dungeon map](README.md) | [Next: Floor 5](floor-5.md) <!-- floor-nav -->

![Floor 4: The Portal Room (MCP)](../images/floors/floor-4-1200x675.webp)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 4. You will move your dice out of the agent's pocket and into a server. They are still my dice. They are just somewhere else now, being rolled in public, in front of everybody."

## Floor Objective

Serve `roll_dice` through the Model Context Protocol: build an MCP server that exposes the dice service, then connect the Narrator to it with Strands' MCP client.

What is MCP? The [Model Context Protocol](https://modelcontextprotocol.io/) is an open standard that defines how an AI application talks to external tools and data sources. An MCP server exposes tools (functions with a name, a description and a JSON schema, exactly what you saw in `tool_spec`) over a standard transport: stdio for a local process, streamable HTTP for a remote one. An MCP client, your agent, connects to the server, lists its tools and calls them, without any custom code for that particular server. In Floor 3 the `roll_dice` tool lived inside the agent's process; with MCP it runs in its own server, possibly on another machine or written in another language, and any number of agents can share it. Think of it as a universal plug between agents and tools.

Make sure you are at the root of Floor 4 in your terminal:

```bash
cd aiRPG-seattle-dungeon-crawl/4_mcp_integration
```

Create an MCP system with two components:

- An MCP Server (`4_mcp_integration/dice_roll_mcp_server.py`) - exposes the dice rolling service
- An MCP Client (`4_mcp_integration/narrator_mcp_client.py`) - connects to the server and uses its tools

The `roll_dice` function is exactly the one you built in Floor 3: same signature, same docstring. Only the way it is served changes, from `@tool` to `@mcp.tool()`.

## Part 1: Setting Up the MCP Server (dice_roll_mcp_server.py)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Same dice, new address. FastMCP serves roll_dice to anyone who connects. Anyone. Remember that on [Floor 8](floor-8.md), when IAM shows up."

### Step 1: Create the MCP Server

```python
# TODO: Step 1 - Import FastMCP from mcp.server
```

```python
# TODO: Step 1 - Create an MCP server on port 8002
```

Import the `FastMCP` class (the `random` and `logging` modules are already imported), then create a `FastMCP` instance on port 8002. The server needs no name: the model only ever sees the tools it serves, never the server itself. Check the documentation for an example.

### Step 2: Expose roll_dice as an MCP Tool

```python
# TODO: Step 2 - Add the decorator to expose roll_dice as an MCP tool
```

Decorate `roll_dice` with `@mcp.tool()`. This is the Floor 3 move again: there `@tool` turned the function into a tool for one agent, here `@mcp.tool()` (note the parentheses, it is called) registers it on the server for any MCP client. The function and its docstring are unchanged, so FastMCP builds the specification from the same name, the same parameters and the same docstring, and sends it over the network to whoever connects. One difference shows up when you compare: Strands moved the `Args:` lines into each parameter's description, while FastMCP keeps the whole docstring, `Args:` included, as the tool description. The model gets the same facts either way. See the documentation for an example.

### Step 3: Choose the Transport

> <img src="../images/icons/item-96x96.webp" alt="Item" width="28" height="28"> **ITEM ACQUIRED: [streamable-http]**
>
> Turns your server into its own process with its own URL. Rarity: Uncommon. Pairs well with a second terminal and mild paranoia.

```python
# TODO: Step 3 - Run the MCP server with the streamable-http transport
```

In the main section, start the MCP server with the `streamable-http` transport, as in this example. MCP defines two standard transports. With stdio, the client launches the server as a child process and talks to it through stdin/stdout: simple, but the server lives and dies with that one client. With streamable HTTP, the server is an independent process listening on a URL, here `http://localhost:8002/mcp`, and any number of clients can connect over the network, from another terminal, another machine or the cloud. That is what we need: the Narrator runs in a second terminal, and in Floor 5 several agents share the same dice server.

### Step 4: Launch the Server

> <img src="../images/icons/sponsor-96x96.webp" alt="Sponsor" width="28" height="28"> **SPONSOR MESSAGE:** This portal is brought to you by port 8002. Port 8002: it was free.

```bash
python dice_roll_mcp_server.py
```

You should see "Starting Dice Roll MCP Server..." followed by Uvicorn running on `http://127.0.0.1:8002`. Leave this terminal open: the server has to stay up while the client talks to it.

## Part 2: Creating the MCP Client (narrator_mcp_client.py)

### Step 1: Create the MCP Client

```python
# TODO: Step 1 - Import MCPClient from strands.tools.mcp
```

```python
# TODO: Step 1 - Create an MCPClient with the url "http://localhost:8002/mcp"
```

Import `MCPClient` (`Agent` is already imported), then create an `MCPClient` that connects to the dice server: give it the server address with `url="http://localhost:8002/mcp"`. From a `url`, Strands builds the streamable HTTP transport itself, the one your server runs (Part 1, Step 3). Refer to the documentation on creating clients.

### Step 2: Add MCP Tools to Your Agent

```python
# TODO: Step 2 - Add the MCP tool to the narrator agent
```

Pass `mcp_dice_client` itself in `tools=[...]`. No `with` block is needed: `MCPClient` is a tool provider, so when the agent receives it this way Strands manages the connection, opening it as soon as the agent is created to list the tools and closing it when the agent shuts down. That is why the server must already be running when you start the client: without it, creating the agent fails with `MCPClientInitializationError`. This is the managed integration the documentation recommends. The `with mcp_client:` form shown on the transports page is the manual variant, only required when you call `list_tools_sync()` or `call_tool_sync()` yourself.

### Step 3: Launch the Client

> <img src="../images/icons/floor-boss-96x96.webp" alt="Floor boss" width="28" height="28"> **FLOOR BOSS:** The four-ability gauntlet again, except every roll now crosses a process boundary. Watch the server terminal and count the DICE ROLL lines. The System already did.

Open a second terminal (the server keeps running in the first one), go to the same folder and run:

```bash
python narrator_mcp_client.py
```

Here is what happens. The client connects to `http://localhost:8002/mcp`, Strands asks the server for its tool list and receives the `roll_dice` specification, the same one you printed in Floor 3, built this time by FastMCP from your docstring. The client sends the same request as Floor 3: Lady Luck rolls four ability scores with 4d6 drop lowest. The difference is where they happen. Keep an eye on the server terminal: every call arrives there as a log line such as `DICE ROLL: 4d6 drop 1 = [5, 2, 6, 3] -> 14`, four of them, while the narration appears in the client terminal. Same agent, same tool, but the dice now live in another process.

Once the character is created, you can stop the client. If you plan to continue with Floor 5, keep the server terminal running: the Narrator will roll its dice through this same server.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **SYSTEM DESIGN, LAYER 4: ONE SOURCE OF LUCK.** A LitRPG audience has to trust the dice. If every agent rolled its own, nobody could audit a dance-off, and the System would be one prompt away from fudging a result. One MCP server that every agent shares, logging every roll with its notation, is the battle log readers check when a Final Beat comes down to a single point. See [The System](world/the-system.md#1-origin-and-interface).

## Floor Clear

Floor cleared, Crawler. You've built an MCP server and client, and connected your agent to a tool served over MCP.

Loot you're keeping:

- How to create an MCP server that exposes a tool (FastMCP)
- How to connect an MCP client to that server
- How to integrate MCP tools into a Strands agent

<img src="../images/icons/stairwell-96x96.webp" alt="Stairwell" width="24" height="24"> **Stairwell:** Head to [Floor 5](floor-5.md) where you'll discover Agent-to-Agent (A2A) communication and orchestrate teams of specialized agents.


> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[OUTSOURCED YOUR LUCK]**
>
> Reward: You received a [Silver Box]. Inside: a FastMCP server, a client that finds it, and four log lines proving the dice roll somewhere your agent is not.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Different process, same cruelty. [Floor 5](floor-5.md) is where your agents start talking to each other. It never ends well for the quiet one."
