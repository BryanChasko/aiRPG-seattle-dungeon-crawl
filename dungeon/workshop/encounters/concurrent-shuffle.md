# Side Passage: The Concurrent Shuffle (Floor 3 Dance-Off)

[Back to Floor 3](../floor-3.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-3-concurrent-shuffle/concurrent_shuffle.py`](../../encounters/floor-3-concurrent-shuffle/concurrent_shuffle.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 3, FRIDAY, JUNE 19, SIDE PASSAGE OFF FLOOR 3.** A second table sat deeper in the kelp, and its dice were heavy: abalone shell, slow to tumble, a full second before they settled. The Quarterly Close Accountant was already there, early for once, and wanted a round of Footwork. Lady Luck rolled for me, waited for my die to land, then rolled for the accountant. Two seconds of dead air on an open status channel. Barnaby counted it with one arm tip tapping the table. "Sergeant. Two dancers. Two dice. Why is one of them waiting for the other?"
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "A dance-off, Crawlers, against the clock. Same dancers, same dice, same croupier. Only one detail changes: whether the dice wait their turn. The review board hates waiting. The review board also hates chaos. Pick one."

## The Brief

| | |
|---|---|
| type | dance-off |
| starts from | [Floor 3](../floor-3.md), finished |
| build | two Lady Lucks that differ only in their tool executor, and a timed round for each |
| teaches | [`strands.tools.executors.concurrent`](https://strandsagents.com/docs/api/python/strands.tools.executors.concurrent/), [`strands.tools.executors.sequential`](https://strandsagents.com/docs/api/python/strands.tools.executors.sequential/) |
| time | about 15 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

When Amazon Nova 2 Lite asks for two or more tool calls in one response, the agent's tool executor decides how the calls run. The `ConcurrentToolExecutor` runs the calls side by side: `ConcurrentToolExecutor` is the default, so every agent built on Floors 2 to 5 already used `ConcurrentToolExecutor`. The `SequentialToolExecutor` runs the calls one after the other, in the order Amazon Nova 2 Lite asked. In this file each die takes a second to land, so the difference shows on the clock: about two seconds of dice in the air with `SequentialToolExecutor`, about one with `ConcurrentToolExecutor`.

> <img src="../../../art/images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** Sergeant, I do not queue my arms. The first four do not wait for the second four to finish being interesting. Two dice have nothing to say to each other; making one wait is not discipline, it is queueing for its own sake. The battle log is another matter. There, order is the record, and even I take my turn.

Success looks like this: the sequential round prints the dice landing one second apart, in the order Lady Luck asked; the concurrent round prints them landing together; both rounds report `model responses: 2`.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/dungeon/encounters/floor-3-concurrent-shuffle
```

The tool, `roll_for`, repeats the Floor 3 lesson: the `roll_for` docstring tells Amazon Nova 2 Lite to ask for both rolls in the same response, because an executor can only run side by side the calls the executor receives together.

## Step 1: Import the Executors

```python
# TODO: Step 1 - Import ConcurrentToolExecutor and SequentialToolExecutor from strands.tools.executors
```

Both classes live in `strands.tools.executors`. See [Concurrent Executor](https://strandsagents.com/docs/user-guide/sdk/tools/executors/#concurrent-executor) and [Sequential Executor](https://strandsagents.com/docs/user-guide/sdk/tools/executors/#sequential-executor).

<details>
<summary>Show me the code for Step 1</summary>

```python
from strands import Agent, tool
# TODO: Step 1 - Import ConcurrentToolExecutor and SequentialToolExecutor from strands.tools.executors
from strands.tools.executors import ConcurrentToolExecutor, SequentialToolExecutor
```

</details>

## Step 2: The Sequential Band

```python
# TODO: Step 2 - Build the sequential band: make_band with a SequentialToolExecutor, as sequential_band
```

`make_band` is given: `make_band` builds Lady Luck with Amazon Nova 2 Lite, the tool and the prompt, and takes the executor as its only argument and passes the executor to the agent's `tool_executor` parameter. An executor is an object, so create one: `SequentialToolExecutor()`.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Build the sequential band: make_band with a SequentialToolExecutor, as sequential_band
sequential_band = make_band(SequentialToolExecutor())
```

</details>

## Step 3: The Concurrent Band

```python
# TODO: Step 3 - Build the concurrent band: make_band with a ConcurrentToolExecutor, as concurrent_band
```

The same call with the other executor. Omitting the executor from `Agent(...)` also gives `ConcurrentToolExecutor` by default; naming it explicitly makes the comparison plain.

<details>
<summary>Show me the code for Step 3</summary>

```python
# TODO: Step 3 - Build the concurrent band: make_band with a ConcurrentToolExecutor, as concurrent_band
concurrent_band = make_band(ConcurrentToolExecutor())
```

</details>

## Run the Dance-Off

```bash
python concurrent_shuffle.py
```

Check: two blocks, one per band, each with two dice and their timings. Numbers differ by a few hundredths:

```
SEQUENTIAL: one die at a time, in the order Lady Luck asked
  Cordula: left the hand at 0.00 s, landed at 1.00 s
  the Quarterly Close Accountant: left the hand at 1.00 s, landed at 2.00 s
  dice in the air: 2.00 s
  model responses: 2 (2 means both rolls came in one response)

CONCURRENT: both dice in the air together
  Cordula: left the hand at 0.00 s, landed at 1.00 s
  the Quarterly Close Accountant: left the hand at 0.00 s, landed at 1.00 s
  dice in the air: 1.00 s
  model responses: 2 (2 means both rolls came in one response)
```

In the concurrent block, the two dice can land in either order: they finish when they finish. Unordered landing is the price of the speed.

| output | cause | fix |
|---|---|---|
| `NameError: name 'sequential_band' is not defined` | Step 2 or 3 is missing, or the variable has another name | name the variables `sequential_band` and `concurrent_band` |
| `model responses: 3`, and 2 seconds in the air in both blocks | Amazon Nova 2 Lite asked for one roll, then the other: the executor had only one call at a time to run | run `python concurrent_shuffle.py` again; if `model responses: 3` repeats, firm up the `roll_for` docstring about "both rolls in the same response" |
| `no dice rolled` | Amazon Nova 2 Lite answered without calling `roll_for` | check that `make_band` still passes `tools=[roll_for]` |
| `AccessDeniedException` or `ExpiredToken` | the call to Amazon Nova 2 Lite failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## When to Pick Which

Concurrent is the right default when the calls do not depend on each other: two dancers' dice, three lookups, a handful of web requests. Pick sequential when order is part of the result: a tool that writes the battle log, two calls that touch the same file, anything where the second call reads what the first one wrote. The [Event Ordering](https://strandsagents.com/docs/user-guide/sdk/tools/executors/#event-ordering) section of the executors page covers what each executor promises about the order of its events.

## What It Costs

Nothing extra: the executor changes when the tools run, not what Amazon Nova 2 Lite reads or writes. Both rounds make the same two Amazon Nova 2 Lite calls, under a tenth of a cent each round. What concurrency saves is time, and on an open status channel a second is a long time.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Second round, both dice left the table together and came down together, one second flat. The accountant was so surprised they forgot the footwork and lost the round by four. Lady Luck looked at the clock and sulked. Barnaby kept the sequential table anyway, for the battle log, where the order matters. "One table for speed, Sergeant, one for the record." I told him that is how a motor pool works. He said he knew. He had read about it.

## Encounter Clear

Loot kept:

- What a tool executor does, and that `ConcurrentToolExecutor` is every agent's default
- How to pick an executor with `tool_executor=`
- Why concurrency only helps when Amazon Nova 2 Lite asks for the calls in the same response, and how the `roll_for` docstring prompts that
- When to give up the speed for the order

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[TWO DICE, ONE SECOND]**
>
> Reward: Cordula received a [Silver Box]. Inside: a stopwatch, a concurrent executor, and a sequential one kept for the paperwork.

Back to [Floor 3](../floor-3.md#floor-clear), or on to [Floor 4](../floor-4.md).
