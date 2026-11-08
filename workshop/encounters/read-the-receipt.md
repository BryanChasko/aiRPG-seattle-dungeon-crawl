# Side Passage: Read the Receipt (Floor 1 Sidequest)

[Back to Floor 1](../floor-1.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-1-read-the-receipt/read_the_receipt.py`](../../encounters/floor-1-read-the-receipt/read_the_receipt.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 1.** There was a ticket window at the end of the Pier 59 service corridor, and behind the glass a receipt printer that had not stopped since the collapse. Every turn the System takes prints a slip. I had been reading the total at the bottom and nothing else. Barnaby unrolled the paper across the floor, eight arm tips pinning the curls down. "Sergeant, a total is a verdict. The lines above it are the evidence. You would not accept a vehicle inspection that only said PASS."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Receipts, Crawlers. Every turn has one, and almost nobody reads past the total. Tokens in, tokens out, trips through the loop, seconds on the clock. I am exact about all of it. It is the only thing I am humble about."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 1](../floor-1.md), finished |
| you build | a receipt for each turn of an agent: why it stopped, the tokens of that turn alone, the tokens of each trip through the event loop, how often each tool ran, and where the seconds went |
| teaches | [`strands.agent.agent_result`](https://strandsagents.com/docs/api/python/strands.agent.agent_result/), [`strands.telemetry.metrics`](https://strandsagents.com/docs/api/python/strands.telemetry.metrics/) |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

Calling an agent returns an `AgentResult`. [The Commentary Booth](commentary-booth.md#step-4-read-the-receipt) priced a turn from `metrics.accumulated_usage`, and that works for a fresh agent on its first turn. This encounter goes further, and it runs two turns on the same agent to show why. Some numbers on the result belong to the turn you just took. Others keep adding up for as long as the agent lives. A receipt that mixes them up is wrong from the second turn on.

The result carries a lot more than a count. `stop_reason` says why the turn ended. `metrics.latest_agent_invocation` is this turn: its `usage` and a list of `cycles`, one per trip through the event loop. `metrics.tool_metrics` counts every tool call, with errors and time. `metrics.traces` holds a timed trace for each cycle. See [Agent Loop Metrics](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/metrics/#agent-loop-metrics), [Tool Metrics](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/metrics/#tool-metrics) and [Local Execution Traces](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/metrics/#local-execution-traces).

How you know it worked: each round prints a receipt with a `turn_usage` that is smaller than `agent_usage_so_far` in round two, a `cycles` list that adds up to `turn_usage`, a `tools_so_far` count that grows from round one to round two, and `traces` for this round only.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-1-read-the-receipt
```

The file gives you two tools, `roll_d20` and `add_modifier`, so a turn has several tool calls to count, and `make_lady_luck()`, the agent. `read_the_receipt(result, seconds)` is the function you complete. It starts with four fields already filled in: `stop_reason`, `seconds` (a stopwatch the caller runs around the call), `context_size` and `agent_usage_so_far`. Every step adds one more field to the `receipt` dictionary.

## Step 1: This Turn Only

```python
# TODO: Step 1 - Add "turn_usage": the usage of this turn alone, turn.usage, as a dict
```

`turn` is already defined above the TODO: `metrics.latest_agent_invocation`, the invocation this result came from. Its `usage` is a dictionary with `inputTokens`, `outputTokens` and `totalTokens` for this turn and nothing before it. The given field next to it, `agent_usage_so_far`, comes from `metrics.accumulated_usage`, which adds up every turn the agent has taken. In round one they match. In round two they do not.

<details>
<summary>Show me the code for Step 1</summary>

```python
    # TODO: Step 1 - Add "turn_usage": the usage of this turn alone, turn.usage, as a dict
    receipt["turn_usage"] = dict(turn.usage)
```

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Round two came back with a lifetime total of 5,720 tokens and a turn total of 3,329. Same agent. If I had billed the banker for the lifetime number I would have charged him for round one twice. I do not sign for gear I did not issue.

## Step 2: Every Trip Through the Loop

```python
# TODO: Step 2 - Add "cycles": one {"input": ..., "output": ...} per cycle of this turn, from turn.cycles and the inputTokens and outputTokens of each cycle's usage
```

A turn is not one model call. The model asks for tools, Strands runs them, and the results go back to the model for another trip: a cycle. `turn.cycles` is a list with one entry per cycle, and each entry has its own `usage`. Build a small dictionary for each one, with the input and output counts. Watch the input column: every cycle resends the system prompt, the tool specification and everything said so far, so it grows with each trip.

<details>
<summary>Show me the code for Step 2</summary>

```python
    # TODO: Step 2 - Add "cycles": one {"input": ..., "output": ...} per cycle of this turn, ...
    receipt["cycles"] = [{"input": c.usage["inputTokens"], "output": c.usage["outputTokens"]} for c in turn.cycles]
```

</details>

## Step 3: Per-Tool Metrics

```python
# TODO: Step 3 - Add "tools_so_far": for each name and tool in metrics.tool_metrics, its call_count, error_count and total_time rounded to 3 places
```

`metrics.tool_metrics` maps each tool's name to a `ToolMetrics` with `call_count`, `success_count`, `error_count` and `total_time`, in seconds. This is the trap of the encounter: unlike `turn_usage`, it is a running tally for the whole life of the agent, so the key says `tools_so_far`. In round two the counts include round one's calls. To get one turn's calls alone, you would copy the counts before the turn and subtract.

<details>
<summary>Show me the code for Step 3</summary>

```python
    # TODO: Step 3 - Add "tools_so_far": for each name and tool in metrics.tool_metrics, ...
    receipt["tools_so_far"] = {
        name: {"calls": tm.call_count, "errors": tm.error_count, "seconds": round(tm.total_time, 3)}
        for name, tm in metrics.tool_metrics.items()
    }
```

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Four calls, no errors, a thousandth of a second in the tools. The dice are not the slow part. Anything slow in this turn is the model thinking, and the receipt can show me which trip. I like a checklist that tells me where to look.

## Step 4: Where the Seconds Went

```python
# TODO: Step 4 - Add "traces": for the last len(turn.cycles) entries of metrics.traces, its name, its duration() in seconds and the (name, duration) of each of its children
```

`metrics.traces` is a list with one `Trace` per cycle, for the life of the agent, so the cycles of this turn are the last `len(turn.cycles)` entries. A `Trace` has a `name`, a `duration()` in seconds (`None` until it ends, hence the `or 0`) and a list of `children`: the model call and each tool call of that cycle, with their own durations. Take the slice with `len(metrics.traces) - len(turn.cycles)`, and not `-len(turn.cycles)`: an empty turn would make the second form return every trace.

<details>
<summary>Show me the code for Step 4</summary>

```python
    # TODO: Step 4 - Add "traces": for the last len(turn.cycles) entries of metrics.traces, ...
    receipt["traces"] = [
        {
            "name": t.name,
            "seconds": round(t.duration() or 0, 2),
            "steps": [(child.name, round(child.duration() or 0, 2)) for child in t.children],
        }
        for t in metrics.traces[len(metrics.traces) - len(turn.cycles):]
    ]
```

</details>

## Run It

```bash
python read_the_receipt.py
```

Check: two receipts. This is an example; your numbers, and the exact children of each trace, will differ:

```
ROUND ONE
  stop_reason: end_turn
  seconds: 6.84
  context_size: 917
  agent_usage_so_far: {'inputTokens': 2231, 'outputTokens': 160, 'totalTokens': 2391}
  turn_usage: {'inputTokens': 2231, 'outputTokens': 160, 'totalTokens': 2391}
  tools_so_far: {'roll_d20': {'calls': 2, 'errors': 0, 'seconds': 0.001}, 'add_modifier': {'calls': 2, 'errors': 0, 'seconds': 0.0}}
  cycles:
    {'input': 612, 'output': 58}
    {'input': 702, 'output': 61}
    {'input': 917, 'output': 41}
  traces:
    {'name': 'Cycle 1', 'seconds': 2.31, 'steps': [('stream_messages', 2.29), ('Tool: roll_d20', 0.0), ('Tool: roll_d20', 0.0)]}
    ...

ROUND TWO
  stop_reason: end_turn
  seconds: 7.52
  agent_usage_so_far: {'inputTokens': 5391, 'outputTokens': 329, 'totalTokens': 5720}
  turn_usage: {'inputTokens': 3160, 'outputTokens': 169, 'totalTokens': 3329}
  tools_so_far: {'roll_d20': {'calls': 4, ...}, 'add_modifier': {'calls': 4, ...}}
```

Add up the `cycles` of a round and you get its `turn_usage`. In round two, `agent_usage_so_far` is round one plus round two, and `tools_so_far` has doubled.

| you see | it means | fix |
|---|---|---|
| a receipt with only `stop_reason`, `seconds`, `context_size` and `agent_usage_so_far` | the steps are not written yet | Steps 1 to 4 |
| `turn_usage` equal to `agent_usage_so_far` in round two | you read `metrics.accumulated_usage` instead of `turn.usage` | Step 1 |
| round two's `traces` list the cycles of round one too | the slice is missing, so every trace of the agent's life is listed | Step 4 |
| `tools_so_far` shows only one tool | the model skipped `add_modifier` and added the numbers itself | run it again; the tool docstring tells it not to, and the receipt just caught it |
| `AccessDeniedException` or `ExpiredToken` | the model call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws) |

## Receipt or Booth?

The Commentary Booth watches a turn while it happens: every chunk, every tool call, as a callback handler sees them. The receipt reads the turn once it is over, from the result. The booth is for the audience. The receipt is for you, when a turn was slow or expensive and you want to know which trip did it.

## What It Costs

The receipt costs nothing: it reads numbers Strands has already counted. What it shows is what the turn cost, and now you can see why. Round one above is 2,231 input tokens and 160 output tokens: 2,231 x $0.30 per million is $0.00067, and 160 x $2.50 per million is $0.00040, so about a tenth of a cent. Round two is 3,160 input and 169 output, about $0.00137, because the model rereads round one before it starts. The cycle column shows the same thing inside a single turn, where each trip resends everything before it. Input tokens grow with every cycle and every turn; output tokens are the ones that cost eight times as much. The prices are on the [Floor 1 cost table](../floor-1.md#what-a-turn-costs).

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** I tore the slips off the printer, folded them into the pocket of my kayak vest, and sent the System a copy of the second one with the cycles circled. It replied in four seconds with an invoice for the paper. Barnaby has framed the invoice. He says it is the first honest thing the System has produced.

## Encounter Clear

Loot you're keeping:

- `AgentResult` is more than a string: `stop_reason`, `metrics`, `context_size`
- `metrics.latest_agent_invocation` is one turn; `metrics.accumulated_usage` and `metrics.tool_metrics` are the agent's whole life
- `turn.cycles` shows each trip through the event loop, and why input tokens grow
- `metrics.traces` and `Trace.duration()` show where the seconds went

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[ITEMIZED AND UNAMUSED]**
>
> Reward: You received a [Bronze Box]. Inside: a receipt roll, a pair of reading glasses and a stamp that says VOID for the lifetime total.

Back to [Floor 1](../floor-1.md#floor-clear), or on to [The Reasoning Dial](reasoning-dial.md).
