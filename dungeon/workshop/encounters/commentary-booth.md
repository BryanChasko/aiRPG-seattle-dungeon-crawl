# Side Passage: The Commentary Booth (Floor 1 Sidequest)

[Back to Floor 1](../floor-1.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-1-commentary-booth/commentary_booth.py`](../../encounters/floor-1-commentary-booth/commentary_booth.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 1, WEDNESDAY, JUNE 17, SIDE PASSAGE OFF FLOOR 1.** Behind the aquarium's old gift shop there was a door marked STATUS, and behind it a glass booth with two chairs, a dead microphone and a window onto the tide pools. The System AI had a voice again, but it spoke in finished paragraphs, minutes late, like an audit memo. A stress-test needs a play-by-play: every word as it happens, every roll the moment it is called. Barnaby sat in the second chair with three arms on the mixing board. "If we are going to be on the record, Sergeant, we will at least know what the record costs."
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "The commentary booth. Here you decide what the review board hears while the Narrator thinks. Every word, every tool call, every token on the bill. I recommend you do not read the bill out loud."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 1](../floor-1.md), finished |
| build | a callback handler that streams the narration and announces each tool call, and a receipt for the turn |
| teaches | [`strands.handlers.callback_handler`](https://strandsagents.com/docs/api/python/strands.handlers.callback_handler/), [`strands.event_loop.streaming`](https://strandsagents.com/docs/api/python/strands.event_loop.streaming/), [`strands.agent.agent_result`](https://strandsagents.com/docs/api/python/strands.agent.agent_result/) |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

On Floor 1 the answer appeared in the terminal without a prompt: Strands gave the Floor 1 agent a default callback handler, `PrintingCallbackHandler`, that prints text as it streams and a `Tool #N` line for each tool call. A callback handler is any callable the agent calls with keyword arguments for every event of a turn. Replace the default with a custom handler to decide what the review board sees. Then read the `AgentResult` the call returns and price the turn with the Floor 1 cost table.

Success check: the narration streams word by word, one `PLAY-BY-PLAY: roll_d20` line appears per roll, and the run ends with a `RECEIPT:` line holding the stop reason, the tokens and the dollars.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/dungeon/encounters/floor-1-commentary-booth
```

The file defines a dice tool, `roll_d20`, so the turn has tool calls to announce, and Lady Luck, the Narrator's croupier, to call the round.

## Step 1: Stream the Narration

```python
# TODO: Step 1 - Print each chunk of text as it arrives: kwargs.get("data"), on the same line, flushed
```

While Amazon Nova 2 Lite writes, Strands calls the handler with `data=`, the newest chunk of text, a few characters at a time. Print each chunk with `end=""`, so the chunks join into one line, and `flush=True`, so they appear now and not when Python's buffer fills. Most calls carry no `data`, so test it before printing. See [Custom Callback Handlers](https://strandsagents.com/docs/user-guide/sdk/streaming/callback-handlers/#custom-callback-handlers) and the [stream event types](https://strandsagents.com/docs/user-guide/sdk/streaming/events/#model-stream-events).

<details>
<summary>Show me the code for Step 1</summary>

```python
    def __call__(self, **kwargs):
        # TODO: Step 1 - Print each chunk of text as it arrives: kwargs.get("data"), on the same line, flushed
        # TODO: Step 2 - Announce each tool call once: ...
        data = kwargs.get("data")
        if data:
            print(data, end="", flush=True)
```

Replace the `pass` under the two TODOs. Both steps live in the same method, one after the other.

</details>

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The first time the words came through live, the tide pool crowd turned toward the booth like a flock of gulls. Same words as before. They arrived while they were still true.

## Step 2: Call the Play-by-Play

```python
# TODO: Step 2 - Announce each tool call once: the first time kwargs.get("current_tool_use") carries a new toolUseId, print "PLAY-BY-PLAY: " and its name on a new line
```

When Amazon Nova 2 Lite asks for a tool, the request streams in too: the handler gets `current_tool_use=`, a dictionary with the call's `toolUseId`, `name` and `input` so far. The event arrives many times per call, once per new piece of input, so announce a call only on the first event with that `toolUseId`. The class already keeps a set for that, `self.calls_announced`.

<details>
<summary>Show me the code for Step 2</summary>

```python
        tool_use = kwargs.get("current_tool_use")
        if tool_use and tool_use.get("toolUseId") and tool_use["toolUseId"] not in self.calls_announced:
            self.calls_announced.add(tool_use["toolUseId"])
            print(f"\nPLAY-BY-PLAY: {tool_use['name']}", flush=True)
```

</details>

## Step 3: Hand Over the Microphone

```python
# TODO: Step 3 - Hand a CommentaryBooth to the agent as its callback_handler
```

Pass an instance, `CommentaryBooth()`, in the agent's `callback_handler` parameter. The instance replaces the default handler entirely: from now on, nothing reaches the terminal unless `CommentaryBooth` prints it. To silence an agent completely, pass `callback_handler=None`, as Floor 8 does for its runtimes.

<details>
<summary>Show me the code for Step 3</summary>

```python
    lady_luck = Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[roll_d20],
        # TODO: Step 3 - Hand a CommentaryBooth to the agent as its callback_handler
        callback_handler=CommentaryBooth(),
        system_prompt="""...""",
    )
```

</details>

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Lady Luck took the microphone as if she had been waiting for it her whole subroutine. Two calls, two rolls, two lines on the board, each one the instant she reached for the dice. The guide of the tourist pod watched the number come up before she finished saying the name.

## Step 4: Read the Receipt

```python
# TODO: Step 4 - Return result.stop_reason, the inputTokens and outputTokens of result.metrics.accumulated_usage, and their cost in dollars at the prices above
```

Calling an agent returns an `AgentResult`. `AgentResult.stop_reason` says why the turn ended (`end_turn` when Amazon Nova 2 Lite finished its answer), and `AgentResult.metrics` holds the numbers of the event loop: `accumulated_usage` is a dictionary with `inputTokens`, `outputTokens` and `totalTokens` across every model call of the turn. Multiply each token count by its price, the two constants at the top of the file, and add the two products. See [Agent Loop Metrics](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/metrics/#agent-loop-metrics).

<details>
<summary>Show me the code for Step 4</summary>

```python
def read_the_receipt(result) -> dict:
    """What the turn cost: why it stopped, the tokens it used, and their price."""
    # TODO: Step 4 - Return result.stop_reason, ...
    usage = result.metrics.accumulated_usage
    return {
        "stop_reason": result.stop_reason,
        "input_tokens": usage["inputTokens"],
        "output_tokens": usage["outputTokens"],
        "dollars": round(usage["inputTokens"] * PRICE_PER_INPUT_TOKEN + usage["outputTokens"] * PRICE_PER_OUTPUT_TOKEN, 6),
    }
```

</details>

## Run It

```bash
python commentary_booth.py
```

Check: the narration builds up word by word, two `PLAY-BY-PLAY: roll_d20` lines appear while it does, one per dancer, and the last line looks like this, with the numbers from the run:

```
RECEIPT: {'stop_reason': 'end_turn', 'input_tokens': 1834, 'output_tokens': 212, 'dollars': 0.00108}
```

| you see | it means | fix |
|---|---|---|
| nothing at all until `RECEIPT:` | the handler prints nothing | Step 1 |
| the answer appears all at once at the end | `flush=True` is missing, or the handler prints `kwargs.get("message")` instead of `data` | Step 1 |
| dozens of `PLAY-BY-PLAY` lines | the handler announces every `current_tool_use` event, not every new `toolUseId` | Step 2 |
| `Tool #1: roll_d20` instead of `PLAY-BY-PLAY` | the agent still has the default handler | Step 3 |
| `RECEIPT: {}` | Step 4 is missing | Step 4 |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## What It Costs

The receipt is the cost: this turn makes two or three Amazon Nova 2 Lite calls and comes to about a tenth of a cent. Two figures in the receipt deserve a second look. The input count is several times the prompt length, because every Amazon Nova 2 Lite call of the turn resends the system prompt, the tool specification and the conversation so far. And output tokens cost about eight times input tokens, so a chatty Lady Luck costs more than a long prompt. Change the system prompt to "Keep it to one sentence" and run it again: the output count, and the dollars, drop.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Barnaby read the receipt out loud anyway, to the decimal. A tenth of a cent for a dance-off. He said that if the System AI ever tried to charge us more than that for one round, we would have the paperwork to prove it. Then he asked if the booth had a second microphone. It did. He has not given it back.

## Encounter Clear

Loot kept:

- A callback handler is any callable; Strands calls the handler with every event of the turn as keyword arguments
- `data` streams the text, `current_tool_use` streams each tool call, and the default handler is one way to print `data` and `current_tool_use`
- `AgentResult.stop_reason` and `AgentResult.metrics.accumulated_usage`, and how to turn tokens into dollars

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[LIVE FROM THE TIDE POOLS]**
>
> Reward: You received a [Bronze Box]. Inside: a microphone, a play-by-play, and an itemized receipt for a dance-off that cost less than the paper it would be printed on.

Back to [Floor 1](../floor-1.md#floor-clear), or on to [Floor 2](../floor-2.md).
