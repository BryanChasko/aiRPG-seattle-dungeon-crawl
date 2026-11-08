# Side Passage: The Warehouse Automation Grid (Floor 4 Sidequest)

[Back to Floor 4](../floor-4.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-4-warehouse-automation-grid/warehouse_grid.py`](../../encounters/floor-4-warehouse-automation-grid/warehouse_grid.py), [`encounters/floor-4-warehouse-automation-grid/grid_server.py`](../../encounters/floor-4-warehouse-automation-grid/grid_server.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 4, SATURDAY, JUNE 20, SIDE PASSAGE OFF FLOOR 4.** A warehouse on the Ship Canal, a stone's throw from the Locks, with a door in the lock wall that opened onto it. Cadabra rents the dungeon its obstacles, and this was the rental: four conveyor belts, a sorter, six robotic arms, all of it wired to one control panel with eight switches. Three of the switches say LOOK. Four say MOVE. One says SCAN AND RELEASE ALL, in the same friendly font as the others. The systems integrator who installed it stood by the panel with a clipboard and a lanyard and the calm of a person whose invoice has already cleared. "Just give the agent everything," they said. "Easier to maintain." I have signed for a lot of gear. I do not hand a crew every switch on the panel. I hand each person the one they run.
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Sidequest: the Warehouse Automation Grid. Eight tools, one parcel, and a belt that has been stalled since breakfast. The audience is hoping somebody presses the friendly one. Cadabra's delivery drones are hovering by the skylight, in case. I have always said a fulfillment contractor can smell a bad permission model from across the Sound."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 4](../floor-4.md), finished; this sidequest runs its own grid server on port 8004 and does not need the dice server |
| build | a filtered `MCPClient` that shows an agent only the read-only tools of a warehouse grid, and a dock attendant that holds only that client |
| teaches | [`MCPClient`](https://strandsagents.com/docs/api/python/strands.tools.mcp.mcp_client/#mcpclient) and [`ToolFilters`](https://strandsagents.com/docs/api/python/strands.tools.mcp.mcp_client/#toolfilters): the `tool_filters` argument, its `allowed` and `rejected` lists |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

On Floor 4 the dice server exposed one tool, and the agent got it. A real server exposes dozens. An agent that sees every tool can call every tool, and each tool also costs tokens, because its name, description and input schema ride along on every call to the model. The [Tool Filtering](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/#client-configuration) option on `MCPClient` fixes both: you decide which tools the agent ever hears about.

`tool_filters` is a dict with two optional keys. `allowed` is a list: when it is present, only tools that match one of its entries stay. `rejected` is a list too: any tool that matches one of its entries is removed afterward. The order matters, allowed first and rejected second, so `rejected` can take back a tool that a broad `allowed` pattern let in. An entry is an exact name string, a compiled regex (matched from the start of the name), or a function that takes the tool and returns true or false.

This encounter folder holds the grid: `grid_server.py`, a FastMCP server with eight tools. `list_belts`, `belt_status` and `scan_parcel` only look. `set_belt_speed`, `route_parcel`, `arm_pick` and `arm_sweep_aisle` move machinery. `scan_and_release_all` has a name that starts like a look and releases every belt and arm at once. The state is a fixed sample: no network, no clock, the same answer every run, and nothing here touches a real machine.

How you know it worked: the unfiltered client lists all eight tools and the filtered client lists exactly three, `belt_status`, `list_belts` and `scan_parcel`. Then the dock attendant finds that parcel PKG-4471 sits on belt-3 in lane C, and that belt-3 is stalled.

Change to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-4-warehouse-automation-grid
```

## Step 1: Import the Client

```python
# TODO: Step 1 - Import MCPClient from strands.tools.mcp
```

`MCPClient` is the same class you wired to the dice server on Floor 4. The filters are an argument to it, not a separate tool.

<details>
<summary>Show me the code for Step 1</summary>

```python
from strands import Agent
# TODO: Step 1 - Import MCPClient from strands.tools.mcp
from strands.tools.mcp import MCPClient
```

</details>

## Step 2: Write the Allowed List

```python
# TODO: Step 2 - Write the allowed list: one compiled regex, re.compile(r"^(list|belt|scan)_"), the read-only name prefixes
ALLOWED: list = []
```

One pattern covers the three tools you want and anything that grows later with the same prefixes. A compiled regex is matched with `match`, which anchors at the start of the name, so `^` is a habit and not a requirement. The patterns are checked against the name the server declares, not a name with a `prefix` added by the client.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** I wrote LOOK on a card and handed it to the filter. List, belt, scan. Three words, three verbs that leave the floor exactly as they found it. Barnaby watched me write it and asked why not just list the three tools by name. "Sergeant, a regex is a rule about shapes. A name is a rule about a thing." I told him I wanted a rule that still held when the integrator added a fourth look. He wrote that down. Then I read the eight names against it, and the eighth one got through.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Write the allowed list: one compiled regex, re.compile(r"^(list|belt|scan)_"), the read-only name prefixes
ALLOWED: list = [re.compile(r"^(list|belt|scan)_")]
```

The trap is the eighth name. `scan_and_release_all` starts with `scan_`, so the pattern lets it through. A broad `allowed` pattern is a net, and a net catches what its mesh allows. Step 3 is the knife.

</details>

## Step 3: Write the Rejected List

```python
# TODO: Step 3 - Write the rejected list: the exact name "scan_and_release_all", a tool that passes the allowed list and should not
REJECTED: list = []
```

`rejected` runs after `allowed` and removes whatever it matches. An exact string is the strictest entry: it matches one tool name and nothing else, so a new tool added next month cannot slip under it by accident.

<details>
<summary>Show me the code for Step 3</summary>

```python
# TODO: Step 3 - Write the rejected list: the exact name "scan_and_release_all", a tool that passes the allowed list and should not
REJECTED: list = ["scan_and_release_all"]
```

`rejected` does not work alone as a safety net. A tool you forgot to name stays visible. The safe shape is a narrow `allowed` list and a short `rejected` list for the exceptions.

</details>

## Step 4: Build the Filtered Client

```python
    # TODO: Step 4 - Return an MCPClient for GRID_URL with tool_filters holding "allowed" (ALLOWED) and "rejected" (REJECTED)
    return None
```

Put the two lists in the `tool_filters` dict inside `make_grid_client`. The filters apply wherever the client lists tools: when you call `list_tools_sync` yourself, and when an `Agent` loads the client's tools. The function builds a new client on every call because a client is opened and closed around its connection, and the encounter opens three: one to list every tool, one to list the filtered tools and one for the agent.

<details>
<summary>Show me the code for Step 4</summary>

```python
    # TODO: Step 4 - Return an MCPClient for GRID_URL with tool_filters holding "allowed" (ALLOWED) and "rejected" (REJECTED)
    return MCPClient(url=GRID_URL, tool_filters={"allowed": ALLOWED, "rejected": REJECTED})
```

Replace the `return None`. The filters hide tools from the agent. They do not stop the server from offering them to some other client, so the filter is a least-privilege control on this agent, and the server still needs its own access rules.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Eight names went in and three came out. I listed both sides by hand before I trusted it, no model in the loop, the way I count a crew before the boat leaves the dock. The integrator watched the second list print and went quiet about maintainability. The panel still has eight switches. The attendant only sees three of them.

## Step 5: Hand the Attendant Its Filtered Tools

```python
        # TODO: Step 5 - Give the agent the filtered client as its tools
```

Put `tools=[grid_client]` inside the `Agent(...)` call in `make_attendant`. The parameter is the client `make_attendant` receives, and `main` passes it the filtered one. An agent that is handed an `MCPClient` in `tools` loads the tools from that client, and the client applies its filters when it lists them.

<details>
<summary>Show me the code for Step 5</summary>

```python
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        # TODO: Step 5 - Give the agent the filtered client as its tools
        tools=[grid_client],
        callback_handler=None,
    )
```

The system prompt also tells the attendant to look and never move anything. The prompt is a request. The filter is a fence. Use both, and trust the fence.

</details>

## Run the Grid

```bash
python warehouse_grid.py
```

The grid server runs inside this process, in a background thread, and prints its own request lines to the same terminal. Check the two tool lists first, then the attendant's report. The attendant's words will differ:

```
EVERY TOOL ON THE GRID, no filters
  ['arm_pick', 'arm_sweep_aisle', 'belt_status', 'list_belts', 'route_parcel', 'scan_and_release_all', 'scan_parcel', 'set_belt_speed']

WHAT THE ATTENDANT SEES, with the filters
  ['belt_status', 'list_belts', 'scan_parcel']

THE DOCK ATTENDANT, with the model
  Parcel PKG-4471 is on belt-3 in lane C. Belt-3 is stalled, waiting on a jammed sorter.
```

| you see | it means | fix |
|---|---|---|
| `NameError: name 'MCPClient' is not defined` | Step 1 is missing | add the import |
| the filtered list shows all eight tools | `ALLOWED` is empty, or Step 4 passes no `tool_filters` | Steps 2 and 4 |
| the filtered list shows four tools, `scan_and_release_all` among them | `REJECTED` is empty | Step 3 |
| the filtered list is empty | the pattern in `ALLOWED` does not match any name, or `REJECTED` holds a pattern that matches them all | read both lists against the eight names |
| `AttributeError: 'NoneType' object has no attribute ...` | `make_grid_client` still returns `None` | Step 4 |
| the attendant says it has no tools | Step 5 is missing | add `tools=[grid_client]` |
| the grid server fails to start, with `address already in use` | another program holds port 8004 | stop the other program |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Filtering or the Router's Allowlist?

[The Locks Turnstile](locks-turnstile.md) guards which servers an agent may reach. This sidequest guards which tools the agent may use on a server it has already reached. The two stack: an allowlist of servers, and a tool filter on each one. Filtering at the client also trims the prompt. Each tool the filter removes is a name, a description and a schema that Amazon Nova 2 Lite does not have to read on every turn.

## What It Costs

The two tool lists are free: no Amazon Nova 2 Lite call. The attendant's run is about three calls: scan the parcel, read the belt, answer. Each call carries the conversation so far and three tool specifications, so assume 1,200 input tokens on average and 100 output tokens. Three calls is 3,600 input tokens at about $0.30 per million (about $0.0011) and 300 output tokens at about $2.50 per million (about $0.0008): two-tenths of a cent a run. Without the filters the same run carries eight tool specifications. At roughly 150 tokens a specification, an estimate and not a measurement, that adds about 750 input tokens a call, about 2,250 over the run, or about $0.0007 more. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot kept:

- `MCPClient(..., tool_filters={...})` decides which of a server's tools an agent can see
- `allowed` keeps only what matches, then `rejected` removes what matches: allowed first, rejected second
- An entry is an exact name, a compiled regex matched from the start of the name, or a function
- A broad `allowed` pattern needs a short `rejected` list for the tool that has a friendly name and a dangerous job
- The filter limits this agent. The server still needs its own access rules

> <img src="../../images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[LEAST PRIVILEGE, MOST PARCELS]**
>
> Reward: You received a [Bronze Box]. Inside: a lanyard with three switches printed on it, a belt-3 maintenance tag, and a sticky note from the integrator that says "maintainability" with a line through it.

Source note: the tool filter pattern is adapted from the MIT-0 strands-agents-course and strands-agents-dussault-workshop materials, and checked against the installed Strands Agents SDK.

Back to [Floor 4](../floor-4.md#floor-clear), or on to [The Locks Turnstile](locks-turnstile.md).
