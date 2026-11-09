# Side Passage: The Hype Meter (Floor 6 Sidequest)

[Back to Floor 6](../floor-6.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-6-hype-meter/hype_meter.py`](../../encounters/floor-6-hype-meter/hype_meter.py), [`web/src/components/HypeMeter.vue`](../../../site/web/src/components/HypeMeter.vue), [`web/src/composables/useGameApi.ts`](../../../site/web/src/composables/useGameApi.ts), [`web/src/stores/gameStore.ts`](../../../site/web/src/stores/gameStore.ts), [`web/src/views/GameView.vue`](../../../site/web/src/views/GameView.vue) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 8, WEDNESDAY, JUNE 24, SIDE PASSAGE OFF FLOOR 6.** The throughput ticker in the corner of the arena had been going up all night and nobody would tell me the rule. The Fremont Troll judged from the end of the hall and gave nothing away. I distrust a number I cannot trace. So I found the Crawl Handbook page on Hype, the stat the Narrator tracks and the System AI shows, and I wired a counter to the events that raise it: a round called, a Crawler benched, a title announced. Then I put the counter on the screen. Barnaby watched it climb and said he had never felt so measured. He said it like a compliment.
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Visibility is hidden. The Narrator keeps the number and I show it when I choose to. Today I choose to. Do not get used to the display. Sponsors are watching the number, and so, for once, are you."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 6](../floor-6.md), finished: the Floor 5 Narrator on port 8009 and the web interface in `web/` |
| build | a hook that turns tool and model events into Visibility, a new `GET /hype` route on the Narrator, and a panel in the web interface that shows the total |
| teaches | [`strands.hooks.registry`](https://strandsagents.com/docs/api/python/strands.hooks.registry/): `HookProvider`, `HookRegistry.add_callback`; [`strands.hooks.events`](https://strandsagents.com/docs/api/python/strands.hooks.events/): `AfterToolCallEvent`, `AfterModelCallEvent` |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

A hook is a function Strands calls when an event happens in the agent loop: a model call starts, a tool call ends, a message is added. The loop stays as written, and Amazon Nova 2 Lite is never asked to cooperate. Write a class with a `register_hooks` method and hand the class to the agent; the class listens. See [Hooks](https://strandsagents.com/docs/user-guide/sdk/agents/hooks/) and the [list of events](https://strandsagents.com/docs/user-guide/sdk/agents/hooks-events/).

Visibility follows the [Crawl Handbook](../world/crawl-handbook/07-hype-sponsors-and-loot.md):

| what happens | Visibility |
|---|---|
| the party wins a dance-off round | +1 |
| the party wins a Final Beat | +3 |
| any achievement | +5 |
| a Crawler is benched | half is lost |

Sponsors may send a box at 10, 25 and 50 Visibility. The meter records each tier the first time Visibility reaches that tier.

The Narrator in this folder is the Floor 5 Narrator, copied and extended, so the new Narrator serves the same routes on the same port. The new Narrator adds two small tools, `call_the_round` and `bench_crawler`, and the Narrator's system prompt, which opens "You are the System" and speaks in the System AI's voice, asks the Narrator to call both tools after each round. The tool calls are the events the hook reads. The achievement is different: the achievement is words in an Amazon Nova 2 Lite reply, so the hook reads the model-call event and looks for the title in square brackets. A title already counted does not pay twice.

Check the result: `GET /hype` returns a total that rises after a round the party wins, and the web interface shows the total in a panel under the character sheet. The `HypeMeter` class, the `hype` attribute and the `GET /hype` field keep their names: the field name is legacy from the broadcast build.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/dungeon/encounters/floor-6-hype-meter
```

## Step 1: Watch Tool Calls

```python
# TODO: Step 1 - Register self.on_tool_result with registry.add_callback for AfterToolCallEvent
```

`registry.add_callback(EventType, function)` tells Strands to call `function` with an event of that type. `AfterToolCallEvent` fires when a tool call ends, and the event carries the call (`event.tool_use`, with the tool's name and input) and the outcome (`event.result`, with a status). `on_tool_result` is already written: `on_tool_result` adds 1 for a round the party won, 3 for a Final Beat, and halves the total when a Crawler is benched. A call that failed scores nothing.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** I wanted the counter to trust the tools, not the story. A story can say anything. A tool call either happened or it did not. So the round is only Visibility once the call has come back clean.

<details>
<summary>Show me the code for Step 1</summary>

```python
def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
    # TODO: Step 1 - Register self.on_tool_result with registry.add_callback for AfterToolCallEvent
    registry.add_callback(AfterToolCallEvent, self.on_tool_result)
```

Keep the `pass` until Step 2 is added, then delete the `pass`.

</details>

## Step 2: Watch Model Replies

```python
# TODO: Step 2 - Register self.on_model_reply with registry.add_callback for AfterModelCallEvent
```

`AfterModelCallEvent` fires when an Amazon Nova 2 Lite call returns. Its `stop_response` holds the Amazon Nova 2 Lite message, or `None` when the call failed. `on_model_reply` reads the words in that message, including the fields of the structured `StoryOutput` call, and scores each new achievement title for +5. Two hooks, two kinds of event, one `HypeMeter`: the same class can listen to any number of events.

<details>
<summary>Show me the code for Steps 1 and 2</summary>

```python
def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
    # TODO: Step 1 - Register self.on_tool_result with registry.add_callback for AfterToolCallEvent
    registry.add_callback(AfterToolCallEvent, self.on_tool_result)
    # TODO: Step 2 - Register self.on_model_reply with registry.add_callback for AfterModelCallEvent
    registry.add_callback(AfterModelCallEvent, self.on_model_reply)
```

Delete the `pass`. The trap: hook code runs inside the agent loop on every event, so keep the hook short and plain.

</details>

## Step 3: Hand the Meter to the Agent

```python
# TODO: Step 3 - Give the Agent the meter as a hook provider: hooks=[hype_meter]
```

`hype_meter = HypeMeter()` is built once at module level, so the Agent and the route share the meter. The `hooks` argument of `Agent` takes a list of hook providers, and Strands calls `register_hooks` on each one when the agent is built.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** One counter, two readers: the agent writes to the counter, the route reads from the counter. In the field we called that a shared logbook. Nobody gets to keep a private one.

<details>
<summary>Show me the code for Step 3</summary>

```python
        # TODO: Step 3 - Give the Agent the meter as a hook provider: hooks=[hype_meter]
        hooks=[hype_meter],
        tools=[mcp_client, a2a_client, call_the_round, bench_crawler],
```

Without the `hooks` argument the meter exists and the route answers, but nothing ever changes the total.

</details>

## Step 4: Serve the Meter

```python
# TODO: Step 4 - Return the meter's snapshot()
```

`snapshot()` returns the total, the sponsor tiers reached, the next tier and the last change, as a dictionary FastAPI turns into JSON. The snapshot is the whole contract with the web interface.

<details>
<summary>Show me the code for Step 4</summary>

```python
@app.get("/hype")
def get_hype():
    # TODO: Step 4 - Return the meter's snapshot()
    return hype_meter.snapshot()
```

Replace the `return {}`. The web interface treats an empty answer as "no Visibility yet" and hides the panel.

</details>

## The Panel in the Web Interface

The web interface already ships the panel. After each turn, `GameView.vue` asks `GET /hype` through `useGameApi`, keeps the answer in the game store, and `HypeMeter.vue` draws it under the character sheet: the total, a bar toward the next sponsor box, and the last change.

The panel is optional. If the Narrator has no `/hype` route, answers with an error, or sends a value that is not a number, the panel does not appear and nothing else changes. The Floor 5 Narrator and the Hype Meter Narrator both work with the same web page.

To see it, run the web interface from the aiRPG-seattle-dungeon-crawl repository, as in [Floor 6](../floor-6.md#web-interface):

```bash
cd aiRPG-seattle-dungeon-crawl/site/web
npm ci
npm run dev
```

The published page shows the panel once the page is rebuilt from the current `web/` folder.

## Run It

Stop the Floor 5 Narrator first: both listen on port 8009. Keep the dice server and the Rules and Character agents running.

```bash
python hype_meter.py
```

Check the meter before any dance-off:

```bash
curl http://127.0.0.1:8009/hype
```

Expected output:

```
{"hype":0,"sponsor_tiers":[],"next_sponsor_at":10,"last_event":""}
```

Enter the dungeon in the web interface and type the Floor 6 challenge: "Challenge the Pitch-Deck Founder to a dance-off in the Underground, with the Fremont Troll judging. Run all three rounds." When the turn comes back, the panel shows the Visibility. An example, with different dice and different insults:

```
{"hype":8,"sponsor_tiers":[],"next_sponsor_at":10,"last_event":"achievement [SMASH THAT LIKE BUTTON]: +5 Hype"}
```

Two rounds won and one achievement earned give 7 Visibility; a Final Beat won adds 3 more and the first sponsor tier opens at 10.

| symptom | cause | fix |
|---|---|---|
| `Address already in use` | the Floor 5 Narrator is still on port 8009 | stop the Floor 5 Narrator, then run the Hype Meter Narrator |
| the panel never appears | the page is talking to a Narrator without `/hype`, or the route still returns `{}` | Step 4, then reload the page |
| `/hype` stays at 0 after a dance-off the party won | the meter is not registered, or the Narrator did not call `call_the_round` | Steps 1 to 3, then watch the terminal for the tool call |
| a round the party won did not add 1 | the call came back with an error | read the terminal: `winner` must be `party` or `opponent` |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Hook or Tool?

A prompt could have asked Amazon Nova 2 Lite to keep the total and print the total in every reply. The total would drift, the Narrator would forget, and one bad turn would erase the review board's confidence. A hook keeps the number in Python code, where a dice roll gets the same arithmetic every time. The cost of that choice is the two small tools: the Narrator still has to report who won, and the hook trusts the report. To stop trusting the report, the next move is to read the dice server's log in the hook instead. That change belongs to a longer passage.

## What It Costs

The hooks themselves are plain Python, so they cost nothing. The price is the two extra tool calls the Narrator makes. Each call is another pass through Amazon Nova 2 Lite: assume about 6,000 tokens of input (the prompt plus the history so far) and 100 tokens of output.

- one pass: 6,000 x $0.30 per million is $0.0018 in, 100 x $2.50 per million is $0.00025 out, about $0.002
- a dance-off with three rounds and one benching is four extra calls: about $0.008, under a cent

Rates are the Nova 2 Lite prices from [Floor 1](../floor-1.md#what-a-turn-costs). Some of the calls may share a pass with other tool calls, which lowers the cost.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Eight tenths of a cent to know why the throughput numbers move. I have spent more on worse intelligence. The Troll, for the record, kept a straight face when the first sponsor tier opened. I took that as approval.

## Encounter Clear

Loot to keep:

- A hook provider is a class with `register_hooks(registry)`; `registry.add_callback(EventType, function)` subscribes the provider to an event
- `AfterToolCallEvent` carries the tool call and the call's result; `AfterModelCallEvent` carries the Amazon Nova 2 Lite reply
- `Agent(hooks=[...])` registers a provider when the agent is built, and the rest of the program can share the same provider
- A web interface can feature-detect a new route and stay quiet when the route is missing

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[ONE HUNDRED PERCENT ORGANIC APPLAUSE]**
>
> Reward: You received a [Silver Box]. Inside: one tiny tally counter, one sponsor tier, and a note from the review board that says "we saw the counter, we are fine with it."

Back to [Floor 6](../floor-6.md#floor-clear), or on to [Sponsor Interrupt](sponsor-interrupt.md).
