# Side Passage: The Locks Turnstile (Floor 4 Sidequest)

[Back to Floor 4](../floor-4.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-4-locks-turnstile/locks_turnstile.py`](../../encounters/floor-4-locks-turnstile/locks_turnstile.py), [`encounters/floor-4-locks-turnstile/tide_server.py`](../../encounters/floor-4-locks-turnstile/tide_server.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 5, SUNDAY, JUNE 21, SIDE PASSAGE OFF FLOOR 4.** There was a gate in the lock wall that Floor 4 had not shown us: a turnstile, brass, with a placard of names. DICE. TIDE. Nothing else. The developer advocates were mid-demo on the far side, and one of them kept shouting new server names across the water, each one more exciting than the last. The turnstile did not care how exciting. It read the placard, found no match, and stayed shut. I have worked gates like that. I grew up three blocks from Salmon Bay and counted salmon at the fish ladder windows here every summer, so I know this gate list by heart. They are the only kind worth having. Barnaby read the placard twice. "Sergeant, a list that someone wrote down on purpose. How rare."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Sidequest: the Locks Turnstile. Two servers are on the list. A third would like to be. The review board has opinions about which one is more compliant, and the turnstile has a clipboard. The clipboard wins."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 4](../floor-4.md), finished; the dice server on port 8002 is on the list but this sidequest does not need the dice server running |
| build | a router tool with a two-server allowlist, and a gate keeper agent that can open, use and close connections to the servers on the allowlist |
| teaches | [`strands.vended_tools.mcp_router.mcp_router`](https://strandsagents.com/docs/api/python/strands.vended_tools.mcp_router.mcp_router/): `make_mcp_router`, the allowlist, the connection cap |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

On Floor 4 the developer picked the server: one `MCPClient`, one URL, wired in before the agent ever ran. The [MCP router](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/mcp-router/) is the other approach from [Integration Approaches](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#integration-approaches): the agent chooses the server at runtime. The MCP router is one tool with five commands, `connect`, `list_connections`, `list_tools`, `call_tool` and `disconnect`. The agent connects by a server name, gives the connection an id, lists the tools on the chosen server, and calls one of those tools.

Letting the agent choose a server is only safe when every allowed server is one you chose. `make_mcp_router` takes a `servers` dict, the allowlist, and the agent can only name a key from the allowlist. If the agent names any other server, the router raises an error before a connection is made. The values are the same config dicts `MCPClient` accepts, and `max_connections` also caps connections, so an agent that keeps opening doors cannot hold more than a few at once.

This encounter folder holds a second server: `tide_server.py`, a small FastMCP server on port 8003 with two tools, `tide_table` and `next_turn`. Its tide tables for Ballard Locks, Elliott Bay and the Tacoma Narrows are a fixed sample: no network, no clock, the same answer every run, and not for navigation.

Success looks like this: the first knock, for `ferry-wifi`, comes back as an error that names the servers that are allowed. The second, for `tide`, comes back as a success. Then the gate keeper connects to `tide` on its own, reports the next turn of the water at ballard-locks after 09:00 (14:40, a low of 2.1 feet), and reports that `ferry-wifi` was refused.

Change to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-4-locks-turnstile
```

## Step 1: Import the Router Factory

```python
# TODO: Step 1 - Import make_mcp_router from strands.vended_tools.mcp_router.mcp_router
```

The factory lives in the `mcp_router` module of the `mcp_router` package, which sits under `strands.vended_tools`. The package also re-exports `make_mcp_router`, but this encounter names the module so the import matches the API page.

<details>
<summary>Show me the code for Step 1</summary>

```python
from strands import Agent
# TODO: Step 1 - Import make_mcp_router from strands.vended_tools.mcp_router.mcp_router
from strands.vended_tools.mcp_router.mcp_router import make_mcp_router
```

</details>

## Step 2: Write the Allowlist

```python
# TODO: Step 2 - Write the allowlist: "dice" at http://localhost:8002/mcp and "tide" at TIDE_URL, each as {"url": ...}
ALLOWLIST: dict = {}
```

Each key is the name the agent will use in `server_name`. Each value is a config dict with the server's `url`, the same address passed to `MCPClient(url=...)` on Floor 4. Headers, a stdio `command` and OAuth credentials fit in the same dict when a server requires them. `make_mcp_router` raises `ValueError` if `ALLOWLIST` is empty: a turnstile with no names on the placard is a wall.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Two names. I wrote them myself, in my own hand, on my own clipboard. If a server is not on it, I do not need a reason to say no. That is the whole point of a list. Everybody who has ever approved something at the gate "just this once" has a story about it, and none of the stories are good.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Write the allowlist: "dice" at http://localhost:8002/mcp and "tide" at TIDE_URL, each as {"url": ...}
ALLOWLIST: dict = {
    "dice": {"url": "http://localhost:8002/mcp"},
    "tide": {"url": TIDE_URL},
}
```

</details>

## Step 3: Build the Turnstile

```python
# TODO: Step 3 - Build the router tool named "turnstile" from the allowlist, with at most 2 open connections
turnstile = None
```

`make_mcp_router(name=..., servers=..., max_connections=...)` returns a tool, the same kind of object a `@tool` function produces. `name` is what the agent calls the tool. Omit `description` and the router writes one that lists the permitted server names, so the agent knows the placard before knocking. `max_connections` defaults to 10; two covers both servers. Connections belong to the agent that opened them and stay open until the agent calls `disconnect` or is garbage collected.

<details>
<summary>Show me the code for Step 3</summary>

```python
# TODO: Step 3 - Build the router tool named "turnstile" from the allowlist, with at most 2 open connections
turnstile = make_mcp_router(name="turnstile", servers=ALLOWLIST, max_connections=2)
```

Replace the `turnstile = None`. The turnstile must exist before Step 4 can pass it to the agent.

</details>

## Step 4: Hand the Gate Keeper Its Only Tool

```python
        # TODO: Step 4 - Give the agent the turnstile as its only tool
```

Put `tools=[turnstile]` inside the `Agent(...)` call in `make_gate`. Pass the router as the only tool. The agent has no `MCPClient` and no URL. Whatever the agent learns about the dice or the tide, the agent learns by asking the turnstile.

<details>
<summary>Show me the code for Step 4</summary>

```python
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        # TODO: Step 4 - Give the agent the turnstile as its only tool
        tools=[turnstile],
        callback_handler=None,
    )
```

The `knock` helper in `locks_turnstile.py` calls the turnstile without calling Amazon Nova 2 Lite, through `gate.tool.turnstile(...)`, with `record_direct_tool_call=False` so the knocks stay out of the agent's conversation. Calling a tool this way is [Direct Tool Invocation](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#direct-tool-invocation) applied to a router.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** I knocked first, by hand, with Amazon Nova 2 Lite out of the loop. Ferry-wifi: refused, with the list read back to me. Tide: open. Then I let Lady Luck's cousin run the gate and watched her repeat the run in her own words. She connected, listed the tools, called one, and shut the door behind her. Barnaby said it was the first time he had watched an agent tidy up after itself. He wrote it down.

## Run the Turnstile

```bash
python locks_turnstile.py
```

The tide server runs inside this process, in a background thread, and the tide server prints its own request lines to the same terminal. Scroll past the request lines. Check the two knock lines first, then the gate keeper's report. The gate keeper's words will differ:

```
KNOCK, no model involved
  ferry-wifi -> error: Error: MCPRouterToolError - Server 'ferry-wifi' is not on the MCP server allowlist: dice, tide
  tide -> success: Successfully connected to tide as 'probe'

THE GATE KEEPER, with the model
  The tide at ballard-locks turns next at 14:40, a low of 2.1 feet. The turnstile refused ferry-wifi because it is not on the allowlist.
```

| you see | it means | fix |
|---|---|---|
| `NameError: name 'make_mcp_router' is not defined` | Step 1 is missing | add the import |
| `AttributeError: Tool 'turnstile' not found` | the gate keeper has no `turnstile` tool: Step 3 or Step 4 is missing | Steps 3 and 4 |
| `ValueError: ... servers must not be empty` | `ALLOWLIST` is still `{}` | Step 2 |
| the knock for `tide` is an error about connecting | the tide server did not start, or another program holds port 8003 | stop the other program; running `python tide_server.py` on its own shows the same error |
| the knock for `ferry-wifi` says success | the allowlist has a name that does not belong there | read `ALLOWLIST` again |
| the gate keeper tries `dice` and fails | the Floor 4 dice server is on the list but not running | start it with `python dice_roll_mcp_server.py` in `4_mcp_integration`, or leave the dice server stopped: the question never needs the dice server |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Wired In or Chosen at Runtime?

Floor 4's `MCPClient` is the right default when you know the servers at build time: the agent starts with the tools already loaded, and the tools appear in the agent's tool list. The router is the right call when the set of servers is large, or changes between runs, or when every tool of every server should stay out of the prompt on every turn. The price is more calls to Amazon Nova 2 Lite, one each to connect, list, call and disconnect, and an agent that has to read the tool list before using the tools. The allowlist is what keeps that freedom from turning into "any server the agent finds". See the [Using Multiple MCP Servers](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#using-multiple-mcp-servers) section for wiring multiple servers in at build time instead.

## What It Costs

The knocks are free: no Amazon Nova 2 Lite call. The gate keeper's run is about six Amazon Nova 2 Lite calls: connect, list the tools, call one, disconnect, then the refused connect and the final answer. Each call carries the conversation so far, including the tool list, so assume 2,500 input tokens on average and 100 output tokens. Six calls is 15,000 input tokens at about $0.30 per million (about $0.0045) and 600 output tokens at about $2.50 per million (about $0.0015): six-tenths of a cent a run. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot kept:

- The MCP router is one tool with five commands that lets an agent open MCP connections at runtime
- The allowlist passed to `make_mcp_router` is the only set of server names the agent can reach, and every other name is refused before a connection opens
- `max_connections` caps how many doors an agent can hold open
- `agent.tool.<name>(...)` calls any tool, router included, without calling Amazon Nova 2 Lite
- Wire a server in at build time or let the agent choose: the trade-off

> <img src="../../images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[THE CLIPBOARD WINS]**
>
> Reward: You received a [Silver Box]. Inside: a brass turnstile token, a tide table for Ballard Locks, and a clipboard with exactly two names on it.

Back to [Floor 4](../floor-4.md#floor-clear), or on to [Trace the Portal](trace-the-portal.md).
