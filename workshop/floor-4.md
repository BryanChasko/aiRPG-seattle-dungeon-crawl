# Floor 4: The Portal Room (MCP)

[Previous: Floor 3](floor-3.md) | [Dungeon map](README.md) | [Next: Floor 5](floor-5.md) <!-- floor-nav -->

Files on this floor: [`4_mcp_integration/dice_roll_mcp_server.py`](../4_mcp_integration/dice_roll_mcp_server.py), [`4_mcp_integration/narrator_mcp_client.py`](../4_mcp_integration/narrator_mcp_client.py) <!-- floor-files -->

![Floor 4: The Portal Room (MCP)](../images/floors/floor-4-1200x675.webp)

<!-- cordula-log -->
> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, FLOOR 4.** At the Ship Canal the dungeon split in two. The Ballard Locks were glowing like portals, the dice were on the far side, and the party was on this one, with a swarm of developer advocates doing a live demo on the lock walls. You cannot carry dice through a portal. You can put them on a server and let anyone on any side roll them. Barnaby touched a machine he had never seen, asked it what it could do, and it told him. He went quiet for a long time after that. I think it was the first time he talked to something that was not alive.
<!-- /cordula-log -->

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 4. You will move your dice out of the agent's pocket and into a server. They are still my dice. They are just somewhere else now, being rolled in public, in front of everybody."

## Floor Objective

Serve `roll_dice` through the Model Context Protocol: build an MCP server that exposes the dice service, then connect the Narrator to it with Strands' MCP client.

What is MCP? The [Model Context Protocol](https://modelcontextprotocol.io/) is an open standard that defines how an AI application talks to external tools and data sources. An MCP server exposes tools (functions with a name, a description and a JSON schema, exactly what you saw in `tool_spec`) over a standard transport: stdio for a local process, streamable HTTP for a remote one. An MCP client, your agent, connects to the server, lists its tools and calls them, without any custom code for that particular server. In Floor 3 the `roll_dice` tool lived inside the agent's process; with MCP it runs in its own server, possibly on another machine or written in another language, and any number of agents can share it. Think of it as a universal plug between agents and tools.

Make sure you are at the root of Floor 4 in your terminal:

```bash
cd aiRPG-seattle-dungeon-crawl/4_mcp_integration
```

Create an MCP system with two components:

- An MCP Server ([`4_mcp_integration/dice_roll_mcp_server.py`](../4_mcp_integration/dice_roll_mcp_server.py)) - exposes the dice rolling service
- An MCP Client ([`4_mcp_integration/narrator_mcp_client.py`](../4_mcp_integration/narrator_mcp_client.py)) - connects to the server and uses its tools

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

Import the `FastMCP` class (the `random` and `logging` modules are already imported), then create a `FastMCP` instance on port 8002. The server needs no name: the model only ever sees the tools it serves, never the server itself. See [Implementing an MCP Server](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#implementing-an-mcp-server) for an example.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import FastMCP from mcp.server
from mcp.server import FastMCP
```

```python
# TODO: Step 1 - Create an MCP server on port 8002
mcp = FastMCP(port=8002)
```

The file already holds `mcp = FastMCP(` with a commented-out `# port=` inside: fill in the port, or replace the three lines with the one above. Keep the name `mcp`: the decorator and `mcp.run(...)` below use it.

</details>

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The Locks hum when a portal is open, a low note you feel in your fillings. Nothing physical crosses. A die thrown at the glow came back as a puddle. So the dice stay on one side, in a box with an address, and anyone who knows the address can ask for a roll. Barnaby liked that: one set of dice, rolled in the open, no pockets.

### Step 2: Expose roll_dice as an MCP Tool

```python
# TODO: Step 2 - Add the decorator to expose roll_dice as an MCP tool
```

Decorate `roll_dice` with `@mcp.tool()`. This is the Floor 3 move again: there `@tool` turned the function into a tool for one agent, here `@mcp.tool()` (note the parentheses, it is called) registers it on the server for any MCP client. The function and its docstring are unchanged, so FastMCP builds the specification from the same name, the same parameters and the same docstring, and sends it over the network to whoever connects. One difference shows up when you compare: Strands moved the `Args:` lines into each parameter's description, while FastMCP keeps the whole docstring, `Args:` included, as the tool description. The model gets the same facts either way. The `@mcp.tool()` decorator appears in the same [Implementing an MCP Server](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#implementing-an-mcp-server) example.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Add the decorator to expose roll_dice as an MCP tool
@mcp.tool()
def roll_dice(faces: int = 6, count: int = 1, drop_lowest: int = 0) -> dict:
```

</details>

### Step 3: Choose the Transport

> <img src="../images/icons/item-96x96.webp" alt="Item" width="28" height="28"> **ITEM ACQUIRED: [streamable-http]**
>
> Turns your server into its own process with its own URL. Rarity: Uncommon. Pairs well with a second terminal and mild paranoia.

```python
# TODO: Step 3 - Run the MCP server with the streamable-http transport
```

In the main section, start the MCP server with the `streamable-http` transport, as in the [Streamable HTTP](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-transports/#streamable-http) section of MCP Transports. MCP defines two standard transports. With stdio, the client launches the server as a child process and talks to it through stdin/stdout: simple, but the server lives and dies with that one client. With streamable HTTP, the server is an independent process listening on a URL, here `http://localhost:8002/mcp`, and any number of clients can connect over the network, from another terminal, another machine or the cloud. That is what we need: the Narrator runs in a second terminal, and in Floor 5 several agents share the same dice server.

<details>
<summary>Show me the code for Step 3</summary>

```python
if __name__ == "__main__":
    print("Starting Dice Roll MCP Server...")
    # TODO: Step 3 - Run the MCP server with the streamable-http transport
    mcp.run(transport="streamable-http")
```

</details>

### Step 4: Launch the Server

> <img src="../images/icons/sponsor-96x96.webp" alt="Sponsor" width="28" height="28"> **SPONSOR MESSAGE:** This portal is brought to you by port 8002. Port 8002: it was free.

```bash
python dice_roll_mcp_server.py
```

You should see "Starting Dice Roll MCP Server..." followed by Uvicorn running on `http://127.0.0.1:8002`. Leave this terminal open: the server has to stay up while the client talks to it.

| you see | it means | fix |
|---|---|---|
| `ImportError: cannot import name 'FastMCP' from 'mcp.server'` | mcp 2.x is installed, which renamed the class | `uv sync` puts back the version this crawl pins (`mcp<2`) |
| `address already in use` | something else holds port 8002, often a server from an earlier run | stop it with Ctrl+C in its terminal; on macOS and Linux, `lsof -i :8002` shows who has the port |
| the script ends at once, with no Uvicorn line | `mcp.run(...)` is missing, or sits outside `if __name__ == "__main__":` | Step 3 |

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The box with the dice in it lit up on the far wall of the lock chamber and stayed lit. A developer advocate on the lock wall pointed at it and told her livestream it was a "reference architecture." I let her have that one.

## Part 2: Creating the MCP Client (narrator_mcp_client.py)

### Step 1: Create the MCP Client

```python
# TODO: Step 1 - Import MCPClient from strands.tools.mcp
```

```python
# TODO: Step 1 - Create an MCPClient with the url "http://localhost:8002/mcp"
```

Import `MCPClient` (`Agent` is already imported), then create an `MCPClient` that connects to the dice server: give it the server address with `url="http://localhost:8002/mcp"`. From a `url`, Strands builds the streamable HTTP transport itself, the one your server runs (Part 1, Step 3). See [Client Configuration](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#client-configuration) on the MCP tools page.

<details>
<summary>Show me the code for Step 1</summary>

```python
from strands import Agent
# TODO: Step 1 - Import MCPClient from strands.tools.mcp
from strands.tools.mcp import MCPClient

# TODO: Step 1 - Create an MCPClient with the url "http://localhost:8002/mcp"
mcp_dice_client = MCPClient(url="http://localhost:8002/mcp")
```

Name it `mcp_dice_client`: Step 2 uses that name.

</details>

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Barnaby put one arm tip against the glow, which I would not have done, and asked the box what it could do. It answered: a name, a description, a list of arguments, the same promises he wrote into the docstring on the floor above. He held still for a long time. Everything he had ever talked to was alive. This was not, and it understood him anyway.

### Step 2: Add MCP Tools to Your Agent

```python
# TODO: Step 2 - Add the MCP tool to the narrator agent
```

Pass `mcp_dice_client` itself in `tools=[...]`. No `with` block is needed: `MCPClient` is a tool provider, so when the agent receives it this way Strands manages the connection, opening it as soon as the agent is created to list the tools and closing it when the agent shuts down. That is why the server must already be running when you start the client: without it, creating the agent fails with `MCPClientInitializationError`. This is the managed integration that [Integration Approaches](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#integration-approaches) recommends. The `with mcp_client:` form shown on the [MCP Transports](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-transports/) page is the manual variant, only required when you call `list_tools_sync()` or `call_tool_sync()` yourself.

<details>
<summary>Show me the code for Step 2</summary>

```python
narrator = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    system_prompt="""...Plain text only, no emoji.""",
    # TODO: Step 2 - Add the MCP tool to the narrator agent
    tools=[mcp_dice_client],
)
```

Watch the comma: in the file, the closing `"""` of the system prompt has no comma after it, because it was the last argument. Add one before your new line, or Python stops with `SyntaxError: invalid syntax. Perhaps you forgot a comma?`

</details>

### Step 3: Launch the Client

> <img src="../images/icons/floor-boss-96x96.webp" alt="Floor boss" width="28" height="28"> **FLOOR BOSS:** The four-ability gauntlet again, except every roll now crosses a process boundary. Watch the server terminal and count the DICE ROLL lines. The System already did.

Open a second terminal (the server keeps running in the first one), go to the same folder and run:

```bash
python narrator_mcp_client.py
```

Here is what happens. The client connects to `http://localhost:8002/mcp`, Strands asks the server for its tool list and receives the `roll_dice` specification, the same one you printed in Floor 3, built this time by FastMCP from your docstring. The client sends the same request as Floor 3: Lady Luck rolls four ability scores with 4d6 drop lowest. The difference is where they happen. Keep an eye on the server terminal: every call arrives there as a log line such as `DICE ROLL: 4d6 drop 1 = [5, 2, 6, 3] -> 14`, four of them, while the narration appears in the client terminal. Same agent, same tool, but the dice now live in another process.

Once the character is created, you can stop the client. If you plan to continue with Floor 5, keep the server terminal running: the Narrator will roll its dice through this same server.

Check: four `DICE ROLL: 4d6 drop 1 = ...` lines in the server terminal, and four totals in the client terminal that match them one for one.

| you see | it means | fix |
|---|---|---|
| `MCPClientInitializationError` | the client could not reach the server when the agent was created | start the server first (Part 1, Step 4) and keep its terminal open; see [MCPClientInitializationError](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#mcpclientinitializationerror-python) |
| `SyntaxError ... Perhaps you forgot a comma?` | the comma after the system prompt | Step 2 |
| the client answers, but no `DICE ROLL` line appears in the server terminal | the agent has no MCP tool and is inventing rolls | check `tools=[mcp_dice_client]` |
| `404 Not Found` in the server terminal | the client URL lacks `/mcp` | `url="http://localhost:8002/mcp"` |

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The developer advocates were mid-demo when the first roll crossed the portal, and every one of them stopped to film it. Four rolls went over, four came back, and the log on the far wall printed each one where everybody could read it. Somebody in the swarm asked if we had a QR code. We did not. The swarm dispersed to find better lighting, and the Locks let us through.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **SYSTEM DESIGN, LAYER 4: ONE SOURCE OF LUCK.** A LitRPG audience has to trust the dice. If every agent rolled its own, nobody could audit a dance-off, and the System would be one prompt away from fudging a result. One MCP server that every agent shares, logging every roll with its notation, is the battle log readers check when a Final Beat comes down to a single point. See [The System](world/the-system.md#1-origin-and-interface).

## Side Passages (optional)

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The lock walls have a turnstile Floor 4 never showed us, and a wire under the portal nobody can see.

- [The Locks Turnstile](encounters/locks-turnstile.md), sidequest: an MCP router with an allowlist, the dice server and a tide server you write, that refuses every other server
- [Trace the Portal](encounters/trace-the-portal.md), sidequest: every MCP call as a span on the console, the one inside the server included

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
