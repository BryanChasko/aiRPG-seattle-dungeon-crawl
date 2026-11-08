# Side Passage: Barnaby Takes the Call (Floor 5 Sidequest)

[Back to Floor 5](../floor-5.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-5-barnaby-takes-the-call/barnaby_takes_the_call.py`](../../encounters/floor-5-barnaby-takes-the-call/barnaby_takes_the_call.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 7, TUESDAY, JUNE 23, SIDE PASSAGE OFF FLOOR 5.** On Floor 5 the Narrator did all the phoning. It decided when to ring the Rules Agent, what to say, and when to hang up, and I only heard the result. Down here Barnaby pulled the handset off the wall. He dialed the rules desk himself, with the line open and the speaker on, and every word that came back crackled out of it as it was said: connected, working, here is a piece of the answer, done. I have run a radio net. I know what it is to hear a call as it happens instead of in the after-action report.
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Sidequest: Barnaby Takes the Call. No more middleman tool. The octopus dials, the octopus listens, and the octopus gets his own number, extension 8003. Calls are not recorded. Calls are, however, streamed."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 5](../floor-5.md), finished: the Rules Agent running on port 8000 and the Character Agent on port 8001 |
| build | a caller that reaches both agents with an `A2AAgent` and prints every A2A event as it streams in, then Barnaby's own A2A server on port 8003 |
| teaches | [`strands.agent.a2a_agent`](https://strandsagents.com/docs/api/python/strands.agent.a2a_agent/): `A2AAgent`, `get_agent_card`, `stream_async`; [`strands.multiagent.a2a.server`](https://strandsagents.com/docs/api/python/strands.multiagent.a2a.server/): `A2AServer` |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

On Floor 5 the Narrator reaches the other agents through the `a2a_client` tool, from [Step 2 of the Narrator](../floor-5.md#step-2-create-the-a2a-client-tool). That tool is the Narrator's choice to call: Amazon Nova 2 Lite picks the moment, the endpoint and the words. An [`A2AAgent`](https://strandsagents.com/docs/api/python/strands.agent.a2a_agent/) is the same conversation held by Python code. Pass the base URL of a remote agent; the `A2AAgent` reads the agent card, sends the message and returns the answer as an `AgentResult`, the type from [The Commentary Booth](commentary-booth.md). No Amazon Nova 2 Lite call happens on the calling side.

This side passage covers `stream_async`. Instead of one answer at the end, `stream_async` yields every A2A event as the remote agent produces it: the task being accepted, status updates while the remote agent works, chunks of the answer, the final state. Each event arrives wrapped in a dictionary with `"type": "a2a_stream"`, and the last item is a dictionary holding the finished `"result"`. The provided `describe` function turns an event into one readable line, to show a call as it happens.

The other half is the server side. Floor 5 turned two agents into servers with `A2AServer`; here Barnaby gets a server of his own, so the next agent that wants to ask the party leader a question can dial him with the same `A2AAgent`.

Success looks like this: each of the two calls prints the remote agent's name and description from its card, a few event lines as the answer streams in, and then the final answer; and `python barnaby_takes_the_call.py serve` starts Uvicorn on `http://127.0.0.1:8003` with an agent card named `Barnaby`.

Start the Rules Agent and the Character Agent from Floor 5 first, each in its own terminal (`python rules_agent.py` from `5_a2a_integration/agents/rules_agent`, `python character_agent.py` from `5_a2a_integration/agents/character_agent`). Then open a third terminal in the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-5-barnaby-takes-the-call
```

## Step 1: Import the Client and the Server

```python
# TODO: Step 1 - Import A2AAgent from strands.agent.a2a_agent and A2AServer from strands.multiagent.a2a.server
```

Both classes live in the Strands package already installed for Floor 5. The Narrator imported the server class as `from strands.multiagent.a2a import A2AServer`; the module path `strands.multiagent.a2a.server` names the file the class comes from, and the API page for that file is the one linked above.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import A2AAgent from strands.agent.a2a_agent and A2AServer from strands.multiagent.a2a.server
from strands.agent.a2a_agent import A2AAgent
from strands.multiagent.a2a.server import A2AServer
```

</details>

## Step 2: Pick Up the Phone

```python
# TODO: Step 2 - Return an A2AAgent for the endpoint, with a timeout of 60 seconds
```

`A2AAgent(endpoint, timeout=60)` is the whole call setup. The first argument is the base URL of the remote agent, the same string Floor 5 puts in `allowed_endpoints`. The timeout is in seconds and covers each HTTP operation, the card fetch and the message; the default is 300, which is a long time to hold a line on a broadcast. The name and description stay empty until the card is fetched: `await line.get_agent_card()` fetches the card, and `main` already calls it, so the printout can say who picked up. See [`A2AAgent`](https://strandsagents.com/docs/api/python/strands.agent.a2a_agent/).

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** One line of code and the Rules Agent was on the other end of it. No dispatcher, no relay. Barnaby read the card off the wire the way I would read a unit patch off a stranger's sleeve: who are you, what do you do, and are you allowed to be here. "Sixty seconds, Sergeant. Beyond that, one is not waiting. One is hoping."

<details>
<summary>Show me the code for Step 2</summary>

```python
def phone(endpoint: str) -> A2AAgent:
    """An A2AAgent for one remote endpoint, with a 60 second limit on each HTTP operation."""
    # TODO: Step 2 - Return an A2AAgent for the endpoint, with a timeout of 60 seconds
    return A2AAgent(endpoint, timeout=60)
```

Replace the `return None`.

</details>

## Step 3: Hear Every Event

```python
# TODO: Step 3 - Loop over line.stream_async(question): print describe(event["event"]) for each "a2a_stream" event, and keep event["result"] when it arrives
```

`stream_async` is an async generator, so the loop is `async for event in line.stream_async(question):`. Each `event` is a dictionary. When `event.get("type") == "a2a_stream"`, the A2A object is in `event["event"]`: print `describe(...)` of that event. When `"result"` is in the event, that value is the finished `AgentResult`: keep it in `result`; the function returns `result` and `main` prints it. The result is always the last item. To get only the answer, `await line.invoke_async(question)` runs the same stream and returns only that result; use the loop to see the call as it happens. See the example in the [`stream_async`](https://strandsagents.com/docs/api/python/strands.agent.a2a_agent/) docstring.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Status working. Status working. A chunk of the answer. Status completed. I counted the events the way I count a convoy: how many came in, in what order, and whether the last one was the one that says we are done. Barnaby tapped the table at each one. He says a streamed answer is a conversation, and a returned answer is a verdict.

<details>
<summary>Show me the code for Step 3</summary>

```python
async def take_the_call(line: A2AAgent, question: str):
    """Send one question down the line and print each A2A event as it arrives. Returns the final AgentResult."""
    result = None
    # TODO: Step 3 - Loop over line.stream_async(question): print describe(event["event"]) for each "a2a_stream" event, and keep event["result"] when it arrives
    async for event in line.stream_async(question):
        if event.get("type") == "a2a_stream":
            print(f"    {describe(event['event'])}")
        elif "result" in event:
            result = event["result"]
    return result
```

The trap: the A2A event is nested under `event["event"]`, not the event itself. The outer dictionary is only the wrapper that says what kind of event the wrapper holds.

</details>

## Step 4: Give Barnaby a Number

```python
# TODO: Step 4 - Return an A2AServer with the create_barnaby factory on port 8003 (BARNABY_PORT)
```

`A2AServer(agent_factory=create_barnaby, port=8003)` is the same call as the Rules Agent's, with a different factory. The factory takes a context id and returns a fresh agent, so every caller gets its own Barnaby who has never heard of the previous caller. `create_barnaby` is provided and runs on Amazon Nova 2 Lite. Ports 8000, 8001, 8002 and 8009 are Floor 5's, so Barnaby takes 8003. See [A2A Server configuration](https://strandsagents.com/docs/user-guide/sdk/multi-agent/a2a-server-configuration/#server-configuration-options) and [`A2AServer`](https://strandsagents.com/docs/api/python/strands.multiagent.a2a.server/).

<details>
<summary>Show me the code for Step 4</summary>

```python
def build_barnaby_line() -> A2AServer:
    """Barnaby's own line: an A2A server on port 8003 that builds a Barnaby for every caller."""
    # TODO: Step 4 - Return an A2AServer with the create_barnaby factory on port 8003 (BARNABY_PORT)
    return A2AServer(agent_factory=create_barnaby, port=BARNABY_PORT)
```

Replace the `return None`. This function only builds the server; `serve()` starts the server, and the script calls `serve()` when run with the `serve` argument.

</details>

## Take the Calls

With the Rules Agent and the Character Agent running:

```bash
python barnaby_takes_the_call.py
```

Check: two calls, each with the card line, the question, a few event lines and the answer. The event lines vary with how the remote agent streams, so the output below is an example:

```
Barnaby dials Rules Agent at http://127.0.0.1:8000: Rules lookup for the dungeon: fast answers from the Crawl Handbook, with the section they come from.
  Barnaby: What happens when a dance-off round ends level? Name the handbook section.
    task submitted
    status working:
    status completed: The round goes to the Final Beat ... [Final Beat]
  Rules Agent: The round goes to the Final Beat ...

Barnaby dials Character Agent at http://127.0.0.1:8001: Crawler registration for the dungeon: ...
  Barnaby: Find Barnaby's sheet and report his Dexterity, Groove and Mana.
    ...
  Character Agent: Barnaby, Uplifted Giant Pacific Octopus Benthic Dragoon, Dexterity 18, Groove 11, Mana 11.
```

Then pick up Barnaby's own line in one terminal:

```bash
python barnaby_takes_the_call.py serve
```

Uvicorn runs on `http://127.0.0.1:8003`, and `curl -s http://127.0.0.1:8003/.well-known/agent-card.json` prints a card that starts with `{"name":"Barnaby"` (the fields may come in another order). To call him, point `phone` at `http://127.0.0.1:8003` from another script.

| output | cause | fix |
|---|---|---|
| `AttributeError: 'NoneType' object has no attribute 'get_agent_card'` | `phone()` still returns `None` | Step 2 |
| `NameError: name 'A2AAgent' is not defined` | Step 1 is missing | Step 1 |
| the call dies with a connection error | the Rules Agent or the Character Agent is not running | start that agent as in [Floor 5, Part 1](../floor-5.md#part-1-setting-up-the-rules-agent) or Part 2 |
| the Character Agent answers that Barnaby is not found | the party was never registered | run the registration curl from [Floor 5, Part 4](../floor-5.md#part-4-test-the-system) once |
| no event lines print, only the answer | the loop in Step 3 is not printing `a2a_stream` events | check `event.get("type") == "a2a_stream"` |
| `address already in use` on `serve` | another process holds port 8003 | stop that process, or change `BARNABY_PORT` |
| `AccessDeniedException` or `ExpiredToken` | the remote agent's Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Tool or Agent Object?

The `a2a_client` tool and `A2AAgent` reach the same agents over the same protocol. The tool puts the call inside the Narrator's turn: Amazon Nova 2 Lite decides to discover an agent, decides what to send, and reads the reply as a tool result, which suits a Narrator. The `A2AAgent` puts the call in script code: the script sets the order and the wording and sees the events, which suits a script, a web page or a test. Use the tool when the Narrator should choose who to ask; use the object when the endpoint is already known. The module that defines `A2AAgent` says it can be used standalone or as part of the multi-agent patterns, the swarms and graphs of the other side passages.

## What It Costs

The calling side costs nothing: `A2AAgent` is HTTP, with no Amazon Nova 2 Lite call behind the request. The Rules Agent and the Character Agent each spend a couple of short Amazon Nova 2 Lite calls on one question, about a thousand tokens in and a couple of hundred out. At about $0.30 per million input tokens and $2.50 per million output tokens, that costs roughly a tenth of a cent a call, and under a cent for the whole script. Barnaby's server costs a call only when someone dials him. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Barnaby's line is up on 8003. I put a sticker over the port number so nobody takes it for the Narrator's. He asked for a ring tone. The System AI offered the Final Beat drum. He accepted before the offer was finished. Shelly has already tried to call it from the mudflat, and I have decided that is a problem for the next shift.

## Encounter Clear

Loot kept:

- An `A2AAgent` is Python code calling a remote agent, with no Amazon Nova 2 Lite call on the calling side
- `get_agent_card` reports who answered, and `stream_async` shows every A2A event as it happens
- The final `AgentResult` is the last item of the stream, and `invoke_async` returns only that
- `A2AServer` with an `agent_factory` gives any agent a number of its own

> <img src="../../images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[CALL WAITING, OCTOPUS EDITION]**
>
> Reward: You received a [Silver Box]. Inside: one handset, eight arms of long-distance minutes, and a sticker that says "port 8003, not the Narrator."

Back to [Floor 5](../floor-5.md#floor-clear), or on to [Floor 6](../floor-6.md).
