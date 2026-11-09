# Side Passage: Launch Commit Criteria (Floor 6 Sidequest)

[Back to Floor 6](../floor-6.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-6-launch-commit-criteria/launch_commit_criteria.py`](../../encounters/floor-6-launch-commit-criteria/launch_commit_criteria.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 8, WEDNESDAY, JUNE 24, SIDE PASSAGE OFF FLOOR 6.** A service tunnel off the Underground under Pioneer Square opened into a Cadabra launch console: a 45-metric-ton rocket standing on a pad that had no business fitting under a sidewalk, and one bench of screens. The Launch Operations Lead had written a countdown loop that asked the System AI for a go/no-go the instant the last answer landed. No pause. No gap. Tick, tick, tick. The System AI answered every one, and every answer was a model call, and the meter on the wall counted them the way a taxi meter does in traffic. Barnaby watched it for ten seconds. "Sergeant. That is not a countdown. That is a person leaning on a doorbell." On a checklist, you poll each station once, you wait for the read-back, and you do not poll again until something could have changed. I have called more go/no-go polls than I can count. Nobody ever called one every breath.
<!-- /cordula-log -->

> <img src="../../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Launch control has asked me for a go/no-go forty times since you sat down, Crawler. Forty. I answered all forty. I would like it noted that I enjoy being needed, and that I would also like lunch."

Adapted from the tool-count limiter in the Strands Agents Course (`samples/05-hooks/rate_limiter.py`, MIT-0).

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 6](../floor-6.md), finished. This script needs no dice server and no other agent |
| you build | a hook that refuses a go/no-go poll that comes too soon or too often, and cancels model calls once the countdown has spent its allowance |
| teaches | [`strands.hooks.events`](https://strandsagents.com/docs/api/python/strands.hooks.events/): `BeforeToolCallEvent` and `BeforeModelCallEvent`; [`strands.hooks.registry`](https://strandsagents.com/docs/api/python/strands.hooks.registry/): `HookProvider`, `HookRegistry` |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

A hook is a function that Strands calls at a fixed moment in the agent loop. You have seen hooks on Floor 6 already: [the Hype Meter](hype-meter.md) reads results after a tool runs, and [Sponsor Interrupt](sponsor-interrupt.md) stops a tool before it runs. This one uses the same "before" moment for a different job: it counts. A rate limiter has two rules, and a hook can hold both. A minimum interval says "not again so soon". A budget says "not again at all, this countdown". See [Hooks](https://strandsagents.com/docs/user-guide/sdk/agents/hooks/) and the cookbook entry [Limit Tool Counts](https://strandsagents.com/docs/user-guide/sdk/agents/hooks/#limit-tool-counts).

Two events matter here, and they cancel in two different ways:

| event | fires | how a hook cancels it |
|---|---|---|
| `BeforeToolCallEvent` | immediately before a tool runs | set `event.cancel_tool` to a message; the message goes back to the model as the tool's result, with an error status |
| `BeforeModelCallEvent` | immediately before each call to Amazon Nova 2 Lite | set `event.cancel` to a message; the model is never called, and the message ends the turn as the reply |

The cancelled calls cost nothing. A cancelled tool call still returns a result to the model, so the model reads the refusal and adjusts. A cancelled model call never reaches Amazon Bedrock: no tokens in, no tokens out.

The script is a small launch pad. `go_no_go()` polls four stations (propellant, range safety, weather, pad crew) and reports GO or NO-GO for each; every station is GO by the second poll that runs. `launch_control` is the loop that floods the System AI: eight ticks, no sleep between them. `LaunchPacer` is yours to finish.

How you know it worked: the output ends with a `PACER:` line that shows polls asked, polls let through and polls refused, and the polls that ran are far fewer than the ticks.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/dungeon/encounters/floor-6-launch-commit-criteria
```

## Step 1: Listen Before Every Tool and Every Model Call

```python
# TODO: Step 1 - Register self.pace_the_poll with registry.add_callback for BeforeToolCallEvent, and self.count_model_call for BeforeModelCallEvent
```

`LaunchPacer` is a `HookProvider`: a class with a `register_hooks(registry)` method. Strands calls `register_hooks` once, when the Agent is built with `hooks=[pacer]`. Inside it, `registry.add_callback(EventType, function)` says "call this function at this moment". One provider can hold callbacks for several events, and the callbacks share the provider's fields: the counters in `__init__` are how the interval check, the budget and the report all see the same numbers.

`pace_the_poll` ignores every tool but `go_no_go`. The Agent in this script has no other tool, but a pacer that checks the name is safe to reuse on one that does.

<details>
<summary>Show me the code for Step 1</summary>

```python
def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
    # TODO: Step 1 - Register self.pace_the_poll with registry.add_callback for BeforeToolCallEvent, and self.count_model_call for BeforeModelCallEvent
    registry.add_callback(BeforeToolCallEvent, self.pace_the_poll)
    registry.add_callback(BeforeModelCallEvent, self.count_model_call)
```

Replace the `pass`. The trap: register the bound method (`self.pace_the_poll`), not a call to it (`self.pace_the_poll()`).

</details>

> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Two callbacks, one clipboard. The tool check watches the polls and the model check watches the spend. I like a checklist that keeps its own tally. It means nobody has to remember how many times we asked.

## Step 2: Spend a Budget of Polls

```python
# TODO: Step 2 - When self.polls has reached self.tool_budget, set event.cancel_tool to a message that says the budget is spent and not to poll again, then return
```

`self.polls` counts the polls that were let through. Once `self.polls` reaches `self.tool_budget`, every further poll is refused for the rest of the countdown. Setting `event.cancel_tool` to a string cancels the call and sends the string to Amazon Nova 2 Lite as the tool result. Write it as an order the model can follow: say what happened, then say "Do NOT call go_no_go again". Then `return`, so the poll is not counted.

The budget check runs first on purpose. A budget is the stronger rule: a poll refused for budget will never be allowed, so telling the model to "try again in 12 seconds" would only send it back for a second refusal.

<details>
<summary>Show me the code for Step 2</summary>

```python
        # TODO: Step 2 - When self.polls has reached self.tool_budget, set event.cancel_tool to a message that says the budget is spent and not to poll again, then return
        if self.polls >= self.tool_budget:
            event.cancel_tool = f"LAUNCH CONTROL: the poll budget of {self.tool_budget} is spent. Do NOT call go_no_go again."
            return
```

The trap: `return` matters. Without it the code falls through to `self.polls += 1`, and a refused poll gets counted as a poll that ran.

</details>

## Step 3: Enforce a Minimum Interval

```python
# TODO: Step 3 - When self.last_poll is set and fewer than self.min_interval seconds have passed since it, set event.cancel_tool to a message with the seconds left, then return
```

`now` is already read from `self.clock()` at the top of the callback. The first poll has no `last_poll`, so it can never be too soon. After that, `now - self.last_poll` is the time since the last allowed poll. When that is under `self.min_interval`, cancel with a message that names the seconds left, so Amazon Nova 2 Lite can tell launch control exactly how long the hold lasts.

The given lines at the bottom of the callback, `self.last_poll = now` and `self.polls += 1`, run only for polls that were let through. A refused poll does not restart the interval: otherwise a loop that keeps asking would keep pushing the next allowed poll further away, and nothing would ever pass.

<details>
<summary>Show me the code for Step 3</summary>

```python
        # TODO: Step 3 - When self.last_poll is set and fewer than self.min_interval seconds have passed since it, set event.cancel_tool to a message with the seconds left, then return
        if self.last_poll is not None and now - self.last_poll < self.min_interval:
            left = self.min_interval - (now - self.last_poll)
            event.cancel_tool = f"LAUNCH CONTROL: too soon, {left:.0f} seconds until the next poll. Do NOT call go_no_go again this tick."
            return
```

The trap: `self.clock` is `time.monotonic`, a clock that only moves forward. `time.time()` can jump when the system clock is corrected, and a jump backwards would make `now - self.last_poll` negative and refuse every poll.

</details>

> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Twenty seconds between polls. In the Reserve we called it a read-back interval: you ask, they answer, you wait for the thing to change before you ask again. The Lead said twenty seconds was "a lot of dead air". I told the Lead that a rocket does not get warmer faster because you asked more often.

## Step 4: Cancel the Model Calls Past the Budget

```python
# TODO: Step 4 - When self.model_calls is past self.model_budget, set event.cancel to a one-line hold message the System AI will say
```

A refused poll still costs a model call: Amazon Nova 2 Lite asks for the tool, reads the refusal, and writes an answer. A loop that never stops asking can still run up the bill one refusal at a time. The model budget is the backstop. `count_model_call` already adds one to `self.model_calls` on every `BeforeModelCallEvent`. When the count goes past `self.model_budget`, set `event.cancel` (not `cancel_tool`: this event has its own field) to a short message. Strands skips the call and uses the message as the model's reply, so the countdown holds at the last report and the loop can keep ticking without spending anything.

<details>
<summary>Show me the code for Step 4</summary>

```python
        # TODO: Step 4 - When self.model_calls is past self.model_budget, set event.cancel to a one-line hold message the System AI will say
        if self.model_calls > self.model_budget:
            event.cancel = "LAUNCH CONTROL: the countdown has spent its model calls. The count holds at the last report."
```

The trap: the count is `>` and not `>=`. `self.model_calls` is incremented before the check, so the call that brings the count to the budget is still the last one allowed.

</details>

## Run It

```bash
python launch_commit_criteria.py
```

Check: eight `tick` lines, then the `PACER:` line and the list of polls that ran. The wording and the exact counts change between runs, because the ticks run as fast as Amazon Nova 2 Lite answers. An example:

```
tick 1: Station check, Crawler! Propellant GO, range safety NO-GO, weather GO, pad crew NO-GO. The count holds.
tick 2: The pacer is holding the count: too soon, 16 seconds until the next poll. Last report stands.
tick 3: The pacer is holding the count: too soon, 12 seconds until the next poll. Last report stands.
...
tick 6: Second poll in. All four stations GO. Launch control may exhale.
tick 7: The pacer is holding the count: too soon, 17 seconds until the next poll. Last report stands.
tick 8: LAUNCH CONTROL: the countdown has spent its model calls. The count holds at the last report.

PACER: polls asked 7, let through 2, refused 5; model calls started 14, cancelled 2
polls that ran: [1, 2]
```

| you see | it means | fix |
|---|---|---|
| `polls asked 8, let through 8` and every station reports GO by tick 2 | the callbacks never ran | Step 1; check the `pass` is gone and the Agent still has `hooks=[pacer]` |
| `let through` is the same as `asked` and the budget never bites | Step 2 or Step 3 is still only a comment | write the `if` blocks |
| `let through 1` in a run that should have passed 20 seconds | the loop finished in under 20 seconds, so only the first poll was allowed | expected for a fast run; raise `TICKS` or lower `MIN_INTERVAL` to see a second poll |
| `model calls started` keeps growing and `cancelled` stays `0` | Step 4 is still only a comment | write the `if` block |
| the System AI polls again right after a refusal | the model ignored "Do NOT call go_no_go again" | nothing to fix: the model budget in Step 4 is the backstop for exactly this |
| `NameError: name 'BeforeModelCallEvent' is not defined` | an import line was deleted | the file imports both events from `strands.hooks.events` at the top |
| `AccessDeniedException` or `ExpiredToken` | the call to Amazon Nova 2 Lite failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## A Hook or a Sleep?

The simplest pacer is `time.sleep(20)` in the loop. It works for one loop and no more. The next caller of the same agent, another loop, a web route, a second console, has no sleep, and the System AI is flooded again. The hook lives on the Agent, so every caller meets the same rule. The hook also refuses the model's own extra calls, which a sleep in the caller cannot see: a single tick can make two or three model calls, and only the Agent knows how many.

The cost of the hook is that it refuses instead of waiting. The refusal goes back to Amazon Nova 2 Lite as a tool result, and the model has to cope with it. A hook that waited, with `time.sleep` inside the callback, would hold the whole agent thread for twenty seconds and would give the pad no information. Refuse, say how long, let the caller decide.

## What It Costs

Assume about 3,000 tokens in and 120 out for each Amazon Nova 2 Lite call, and two calls for a tick that polls: one to ask for the tool, one to report. Rates are the Nova 2 Lite prices from [Floor 1](../floor-1.md#what-a-turn-costs).

- one tick that polls: 6,000 x $0.30 per million is $0.0018 in, 240 x $2.50 per million is $0.0006 out, about $0.0024
- the eight-tick flood in this script, no pacer: about 16 calls, about $0.02
- with the pacer, the model budget of 12 caps the run at 12 calls, about $0.015, and cancelled calls cost nothing
- a flood that never stops, one tick a second for an hour: 3,600 ticks x $0.0024 is about $8.64
- the same hour paced to one poll every 20 seconds: 180 polls x $0.0024 is about $0.43, one twentieth of the flood

The budget of three polls in this script ends a countdown long before an hour. The hour figures show why a limiter matters on a loop that runs without anyone watching.

> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** All four stations went green on the second poll, twenty seconds after the first. The Lead watched the wall and said it felt slower. It was slower. It was also done. Barnaby tapped one arm on the console and said the rocket had been ready since the first poll and the Lead had simply not waited to hear it. I wrote that down. Then I closed the checklist and we walked back out through the tunnel.

## Encounter Clear

Loot to keep:

- A `HookProvider` registers callbacks with `registry.add_callback(EventType, function)`, and the callbacks share the provider's fields
- `BeforeToolCallEvent` plus `event.cancel_tool` refuses a tool call; the message goes back to the model as the tool result
- `BeforeModelCallEvent` plus `event.cancel` skips the call to Amazon Nova 2 Lite and ends the turn with your message; cancelled calls cost nothing
- A rate limiter is two rules: a minimum interval and a budget. Count only the calls you let through, and use a monotonic clock
- A hook on the Agent paces every caller; a sleep in one loop paces one loop

> <img src="../../../images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[T-MINUS NEVER]**
>
> Reward: You received a [Bronze Box]. Inside: one pacer, one stopwatch labeled "ask me in twenty seconds", and a doorbell with its button taped over.

Back to [Floor 6](../floor-6.md#floor-clear), or on to [Floor 7](../floor-7.md).
