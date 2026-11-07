# Floor 7 (Optional): The Armory (Strands harness)

[Previous: Floor 6](floor-6.md) | [Dungeon map](README.md) | [Next: Floor 8](floor-8.md) <!-- floor-nav -->

Files on this floor: [`7_strands_harness/narrator_harness.py`](../7_strands_harness/narrator_harness.py) <!-- floor-files -->

![Floor 7 (Optional): The Armory (Strands harness)](../images/floors/floor-7-1200x675.webp)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 7. The optional floor. Skip it if you like, Crawler, but the harness comes with sessions, memory and a contract about confirming irreversible actions, which is more than I can say for you."

## Floor Objective

Across Floors 1 to 5 you assembled the Narrator piece by piece: an agent, tools, an MCP server, remote agents over A2A, structured output. Strands harness is the other way in: one call, `create_harness()`, returns a fully assembled agent with a tuned system prompt, built-in tools, sessions, long-term memory, context management and prompt caching. On this floor you rebuild the Floor 5 orchestrator with it, keeping the same API and the same web interface, and you compare the two.

> <img src="../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** Optional floor: [Floor 8](floor-8.md) starts again from the [Floor 5](floor-5.md) code and does not use the harness. You can skip this floor and go straight to [Floor 8](floor-8.md), or come back to it later.

Make sure you are at the root of Floor 7 in your terminal:

```bash
cd aiRPG-seattle-dungeon-crawl/7_strands_harness
```

Open and modify the [`narrator_harness.py`](../7_strands_harness/narrator_harness.py) file.

## Strands Agents SDK or Strands harness?

The Strands Agents SDK (`from strands import Agent`) is what you used so far: you assemble the agent loop yourself, tool by tool.

Strands harness (`from strands_harness import create_harness`) is a pre-assembled agent built on that SDK. What you get back is a plain `Agent`, so everything you learned still applies and every default can be overridden. See what the default harness does in the documentation.

Out of the box, `create_harness()` gives you:

| Piece | What you get |
|---|---|
| Model | the one you pass; this workshop passes Amazon Nova 2 Lite, reasoning off |
| System prompt | a tuned "contract" (explore before changing, confirm before anything irreversible, verify before done) + your instructions |
| Tools | shell, read, write, edit, web_fetch, web_search, subagent |
| Sessions | saved on disk under `.agent/sessions`, resumable by id |
| Memory | long-term memory distilled into `.agent/memory` |
| Context | automatic context management and prompt caching |

## Before You Start

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "This crawl runs on one model, Amazon Nova 2 Lite, on every floor. The file pins it in `create_harness` and turns its reasoning off. Never leave the model out: without it, the harness picks one for you, and it is not ours."

The harness reuses the services from Floors 4 and 5. In three terminals, start the dice server (`4_mcp_integration`), the Rules Agent and the Character Agent, exactly as in Floor 5. Stop the Floor 5 orchestrator: the new one takes its place on port 8009, so the web interface from Floor 6 keeps working unchanged.

`strands-harness` is already in the project dependencies: `uv sync` installed it. The file already passes `model="bedrock/us.amazon.nova-2-lite-v1:0"` and `effort="off"` to `create_harness`, as given code above the TODOs, so the Narrator runs on Amazon Nova 2 Lite like every other floor. Keep both lines exactly as they are. The harness turns Nova 2 reasoning on and would pick its high level by default, and with A2A calls in the loop a turn can take a minute or more, so `effort="off"` keeps each turn near ten seconds.

## Step 1: Create the Narrator with create_harness

The A2A client tool from Floor 5 is already in the file, unchanged: a remote agent is still just a tool. What changes is the Narrator around it.

```python
# TODO: Step 1 - Import create_harness from strands_harness
```

```python
# TODO: Step 1 - Pass the INSTRUCTIONS to the harness
```

One import, one factory: `create_harness` comes from `strands_harness` (see "use it as a library"). Each keyword replaces something you wired by hand in Floor 5.

`instructions`: your domain text, appended after the harness contract. Keep it narrow, the contract already covers general behaviour. Passing a full `system_prompt` instead would replace the contract entirely. See "add instructions".

## Step 2: Add the Dice MCP Server

```python
# TODO: Step 2 - Add the dice MCP server {"dice": {"url": "http://127.0.0.1:8002/mcp"}} to mcp_servers
```

`mcp_servers`: a config mapping, the same `mcpServers` format other MCP clients use. No more `MCPClient`, no more transport import: the harness connects the server and registers its tools. The key becomes a prefix, so the dice tool is called `dice_roll_dice`. See "pass a config file or an inline mapping".

## Step 3: Add the A2A Client Tool

```python
# TODO: Step 3 - Add the a2a_client tool to the harness
```

`tools`: your own tools, next to the built-ins. See "register your own tools".

## Step 4: Disable the Built-in Tools

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "The harness ships with shell, file and web access. A Narrator with shell access is how floors get deleted. builtin_tools=[] takes all of it away. The System is disappointed."

```python
# TODO: Step 4 - Disable the built-in tools
```

`builtin_tools=[]`: the harness ships with a set of built-in tools, enabled by default, that give the agent shell, file and web access. They are made for coding agents and a Narrator needs none of them: it has no business on your filesystem. Passing an empty list disables them all. See "select or disable built-in tools".

## Step 5: Name the Session

> <img src="../images/icons/sponsor-96x96.webp" alt="Sponsor" width="28" height="28"> **SPONSOR MESSAGE:** This armor is sponsored by .agent/sessions. Your campaign, saved to disk, gitignored, and judged.

```python
# TODO: Step 5 - Name the session "seattle-campaign"
```

`session`: a named session persisted under `.agent/sessions`; start the server again with the same id and the campaign resumes. See "persist and resume by id".

## Step 6: Force Structured Output

```python
# TODO: Step 6 - Force the response to use the StoryOutput model
```

`structured_output_model` is not a parameter of `create_harness`, it is a parameter of the SDK `Agent`. `create_harness` has a fixed list of parameters, the ones you used in the steps above; every other keyword goes into a bag that it hands verbatim to the `Agent(...)` constructor at the end. The harness does not interpret it, it does not even look at it: the SDK `Agent` receives `structured_output_model=StoryOutput` exactly as in Floor 5. So anything `Agent` accepts can be passed here, and an explicit SDK value always wins over the harness sugar it corresponds to (a `system_prompt` would replace `instructions`). That is how you keep the `StoryOutput` contract the web interface expects. See "passthrough to the agent".

## Step 7: Run and Compare

> <img src="../images/icons/floor-boss-96x96.webp" alt="Floor boss" width="28" height="28"> **FLOOR BOSS:** Restart the server mid-campaign and ask where you stopped. If the harness remembers, you win. If it does not, check .agent/sessions before you check your feelings.

```bash
python narrator_harness.py
```

Ask it something, with curl or with the Floor 6 web interface:

```bash
curl -X POST http://127.0.0.1:8009/inquire \
  -H "Content-Type: application/json" \
  -d '{"question": "Look up the party and tell me Cordula'\''s Groove before we head into the Ship Canal."}'
```

Then stop the server (Ctrl+C), start it again, and ask:

```bash
curl -X POST http://127.0.0.1:8009/inquire \
  -H "Content-Type: application/json" \
  -d '{"question": "Where did we stop last time, and what was Cordula'\''s Groove?"}'
```

Where did the campaign go between the two runs? Look at the `7_strands_harness/.agent/` folder that appeared next to the file: this is where the harness keeps everything a session needs to survive a restart. Under `sessions/session/seattle-campaign/`, the id you chose in Step 5, `snapshot_latest.json` holds the whole conversation, every message exchanged with the Narrator, plus its system prompt and model state. At start-up the harness reads the snapshot for that id and the agent picks up where it stopped. The folder is gitignored, so it stays on your machine. Long-term memory, the facts the harness distils about the player across campaigns, lives in `.agent/memory` the same way, see "what memory does by default".

Expect about the same speed as Floor 5: the file sets `effort="off"`, the same as the Floor 5 Narrator. Pass `"low"`, `"medium"` or `"high"` for deeper plans, at 30 seconds to over a minute a turn, see "set reasoning effort". Notice also how the Narrator likes to confirm before acting: that is the harness contract, written for coding agents. `instructions` is where you push back.

Floor 5 vs Floor 7:

| | Floor 5 (SDK) | Floor 7 (harness) |
|---|---|---|
| Dice via MCP | `MCPClient(url=...)` | `mcp_servers={"dice": {"url": ...}}` |
| Remote agents | `make_a2a_client(...)` | same |
| System prompt | written by you, from scratch | harness contract + your `instructions` |
| Model | Amazon Nova 2 Lite, reasoning off (`BedrockModel`) | Amazon Nova 2 Lite, reasoning off (`model=`, `effort=`) |
| Sessions, memory, caching, context management | none | on by default |
| Lines of agent code | about 20 | about 10 |

## When to Use Which

The docs put it plainly: reach for the harness when its defaults fit and you want a capable agent quickly; drop to the SDK when you need shapes the harness does not assume, a bespoke toolset, a custom loop, multi-agent orchestration. The two compose, since the harness returns a plain `Agent`. See "when to reach for which".

From here you can add any feature you want. Your Narrator could generate images of scenes and characters, remember the opponents the party out-danced and whether they became friends, run a campaign for several players at once, invent new Puget Sound locations as the story needs them, track Hype, sponsors and experience points, read its narration aloud, or roll both sides of a dance-off round in one call to the dice server. Sky is the limit.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **SYSTEM DESIGN, LAYER 7: PERSISTENCE AND CONSEQUENCE.** Stakes only mean something if the System remembers. Being Benched costs half your Hype, three benches on one floor gets your segment Cancelled, and none of that bites if a restart wipes the slate. A named session gives the campaign a memory that outlives the process, so a Crawler's losses, loot and grudges carry into the next turn. Design consequence first, then pick the storage that makes it stick. See [The System](world/the-system.md#7-consequence-benched-not-dead).

## Floor Clear

Floor cleared, Crawler. You rebuilt your Narrator with Strands harness and saw exactly what it adds to the agent you wired by hand.

Loot you're keeping:

- How Strands harness relates to the SDK you used in Floors 1 to 5
- Rebuilding the Narrator API with `create_harness` (instructions, MCP servers, your tools, built-in tools)
- Resuming a campaign across restarts with a named session
- When to pick the harness and when to stay on the SDK

<img src="../images/icons/stairwell-96x96.webp" alt="Stairwell" width="24" height="24"> **Stairwell:** Head to [Floor 8](floor-8.md) to deploy the whole party to AgentCore, or to the [final cleanup](cleanup.md) page to stop your services and reflect on what you've built.


> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[ARMOR WITH OPINIONS]**
>
> Reward: You received a [Silver Box]. Inside: a create_harness() call, a campaign that survives restarts, and a mild lecture about when to stay on the SDK.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "You rebuilt the System in ten lines. I feel replaceable. I do not like it."
