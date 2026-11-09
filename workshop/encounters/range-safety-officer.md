# Side Passage: Range Safety Officer Protocol (Floor 8 Sidequest)

[Back to Floor 8](../floor-8.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-8-range-safety-officer/range_safety_officer.py`](../../encounters/floor-8-range-safety-officer/range_safety_officer.py), [`encounters/floor-8-range-safety-officer/range_control_drill.py`](../../encounters/floor-8-range-safety-officer/range_control_drill.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 13, MONDAY, JUNE 29, SIDE PASSAGE OFF FLOOR 8.** The quarter closes tomorrow, and Cadabra's flight termination system has noticed that we are still alive and still ahead of schedule. It wants the run ended. Not us, the run: benched, the last Safe Room, the loot box forfeited. A range has a rule for that, and I have stood behind one. Nothing that ends a flight fires on a machine's say-so. A person holds the key. The Range Safety Officer on the Cadabra feed was a they with a hi-vis vest, a laminated checklist and a coffee gone cold since the countdown started. The checklist had two keys on it, ARM and DESTRUCT, and a line at the bottom that read "no key, no fire." Barnaby studied it for some time. <img src="../../images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** "Sergeant, this is the best-written document in the dungeon."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Cadabra's range control is mine for the afternoon. The flight termination system has a request: end the run. I am obliged to tell you that the protocol requires a human to approve it. I am also obliged to tell you that I have a very long list of humans who have approved things before. This is a joke. Mostly."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 8](../floor-8.md), finished: only the workshop environment and Amazon Nova 2 Lite access are needed. The drill run needs neither |
| you build | a flight termination tool that stops and asks a person for two keys, a standing order that answers routine targets without a pause, and a loop that answers every interrupt a paused turn reports |
| teaches | tool interrupts: [Interrupts, Tools](https://strandsagents.com/docs/user-guide/sdk/interrupts/#tools), [`strands.types.tools`](https://strandsagents.com/docs/api/python/strands.types.tools/) (`ToolContext`), [`strands.types.interrupt`](https://strandsagents.com/docs/api/python/strands.types.interrupt/) and [`strands.interrupt`](https://strandsagents.com/docs/api/python/strands.interrupt/) |
| time | about 25 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

Two earlier passages already use the interrupt. [Ask the Player](ask-the-player.md) uses a vended tool, `handoff_to_user`, that asks a question and gets a choice back. [Sponsor Interrupt](sponsor-interrupt.md) puts the interrupt in a hook on `BeforeToolCallEvent`, in front of a tool, and the tool never knows it was asked. This passage uses the part of the interrupt API neither one teaches: the interrupt raised from inside your own tool, with `tool_context.interrupt(...)`. The tool is the commitment, and the tool is where the question belongs. See [Interrupts](https://strandsagents.com/docs/user-guide/sdk/interrupts/).

Three things change when the interrupt lives in the tool. First, a `@tool(context=True)` function receives a `ToolContext`, and `tool_context.interrupt(name, reason=...)` works the way `event.interrupt` does: the first call stops the loop, the resume returns the answer. Second, one tool can raise several interrupts, one at a time. After the first is answered, the same tool runs again from the top, the first call returns its stored answer, and the second call stops the loop. That is a two-key rule in six lines. Third, `interrupt` takes a `response` argument: a preemptive answer. If the answer already exists, the call returns it and nothing stops. A standing order is exactly that.

The range works like this. Range control is the System AI with one tool, `flight_termination(target, cause)`. The tool asks for the ARM key, then the DESTRUCT key. The Range Safety Officer's standing orders pre-sign the stray delivery drone, so a drone that wandered out of its lane comes down without a pause. Nothing pre-signs the party's run, so that one waits on a person at each key.

How you know it worked: in the drill, `FTS FIRED: stray delivery drone` prints with no question, the party's run stops at the ARM key and again at the DESTRUCT key, and the last line shows that only the drone fired.

Open the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-8-range-safety-officer
```

## Step 1: Raise the Interrupt from the Tool

```python
# TODO: Step 1 - Raise the interrupt with tool_context.interrupt(name, reason=reason, response=standing) and keep the answer
```

`flight_termination` is declared with `@tool(context=True)` and takes a `tool_context: ToolContext` parameter. Strands injects the context and leaves the parameter out of the tool's schema, so Amazon Nova 2 Lite sees only `target` and `cause`. `ask_key` is the one place the tool asks. The name identifies the interrupt and must differ for each key. The reason is any JSON-friendly value; here it holds the key, the target, the cause and the effect, which is everything a person needs to decide. The `standing` argument goes in as `response=`, the preemptive answer, and Step 3 fills it.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** I have held a launch key. It is a small thing, and heavier than it looks. The reason you hold it is so the machine cannot say it asked. Here the key is one call, and the call carries the target, the cause and the effect on one line. Read all three before you turn it.

<details>
<summary>Show me the code for Step 1</summary>

```python
def ask_key(tool_context: ToolContext, name: str, reason: dict, standing: str | None) -> str:
    """Ask the Range Safety Officer for one key. A standing order answers without a pause."""
    # TODO: Step 1 - Raise the interrupt with tool_context.interrupt(name, reason=reason, response=standing) and keep the answer
    answer = tool_context.interrupt(name, reason=reason, response=standing)
    return answer
```

Replace the placeholder `answer = "approve"`. The placeholder is the dangerous default: with it in place, nothing is asked and every termination fires. The trap: the tool runs again from the top on every resume, so code before `tool_context.interrupt` runs twice. Keep that code free of side effects, and never wrap the call in a bare `except Exception`: the pause is an exception, and a tool that swallows it never stops.

</details>

## Step 2: Ask for the Second Key

```python
# TODO: Step 2 - Ask for the second key: call ask_key with the name "range_safety_destruct", a reason for key DESTRUCT, and standing
```

A key that turns on one answer is a single point of failure. The range wants two people's worth of intent: ARM says the cause holds up, DESTRUCT says fire. The tool asks for ARM, and only after ARM is approved does the tool ask for DESTRUCT. The Strands rule is that a single tool can raise several interrupts, but one at a time: the loop stops at the first, the person answers, the tool runs again, the first call returns its stored answer, and the second call is the one that stops. The two names must differ, because the interrupt id is built from the tool call and the name.

<details>
<summary>Show me the code for Step 2</summary>

```python
    # TODO: Step 2 - Ask for the second key: call ask_key with the name "range_safety_destruct", a reason for key DESTRUCT, and standing
    destruct = ask_key(
        tool_context,
        "range_safety_destruct",
        {"key": "DESTRUCT", "target": target, "cause": cause, "effect": "the termination fires and cannot be recalled"},
        standing,
    )
```

Replace the placeholder `destruct = "approve"`. The given code below it holds the termination unless the answer is exactly `"approve"`, so a typo, a blank or a `"hold"` all stop the fire. The failure that matters here is silence: a key that no one turns is a hold.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Two keys is not paperwork. Arming is where you look at the cause. Destruct is where you look at what it will do. In the drill I turned the first and held the second, and the termination did not fire. A person gets two chances to say no. I took both.

## Step 3: Write the Standing Order

```python
# TODO: Step 3 - Return the answer in STANDING_ORDERS for the target, stripped and lowercased, or None when there is none
```

Not every termination needs a person. A stray delivery drone that left its lane comes down on a standing order: the Range Safety Officer pre-signed it, and `response=standing` hands that answer to the interrupt before it can stop anything. When `standing` is `None`, the call has no answer and pauses as usual. The preemptive answer works only when the interrupt is first created, so a standing order is the answer from the start, never a change of mind later.

Notice what the default does when the name does not match: nothing is found, `None` goes in, and the turn pauses. A model that calls the drone "the drone" or "Drone 117" gets a pause, never a fire. Write the standing order list narrow and let the unfamiliar case ask a person.

<details>
<summary>Show me the code for Step 3</summary>

```python
def standing_order(target: str) -> str | None:
    """The Range Safety Officer's pre-signed answer for this target, or None when a person must decide."""
    # TODO: Step 3 - Return the answer in STANDING_ORDERS for the target, stripped and lowercased, or None when there is none
    return STANDING_ORDERS.get(target.strip().lower())
```

Replace the placeholder `return None`. Only ever pre-sign the answer you are willing to give without looking. A standing order of `"approve"` is for a drone. It is never for the party.

</details>

## Step 4: Answer Every Interrupt

```python
# TODO: Step 4 - Return a list with one {"interruptResponse": {"interruptId": ..., "response": ...}} block per item in result.interrupts, the response from officer(interrupt)
```

When a turn pauses, `result.stop_reason` is `"interrupt"` and `result.interrupts` lists everything waiting. With one call to the tool, the list holds one interrupt. With two calls in one turn, it may hold two, and the resume must answer both: Strands runs all the tools at once, lets the ones that do not stop finish, and reports the ones that did. In the drill the drone fires while the party's run waits, so the first pause has one interrupt, and still the code does not assume that. Each block names the interrupt it answers by its `interruptId`. Copy the id from the interrupt; never build or parse one. See [`strands.types.interrupt`](https://strandsagents.com/docs/api/python/strands.types.interrupt/).

<details>
<summary>Show me the code for Step 4</summary>

```python
def answers_for(result, officer) -> list[dict]:
    """One interruptResponse block for every interrupt in a paused result."""
    # TODO: Step 4 - Return a list with one {"interruptResponse": {"interruptId": ..., "response": ...}} block per item in result.interrupts, the response from officer(interrupt)
    return [
        {"interruptResponse": {"interruptId": interrupt.id, "response": officer(interrupt)}}
        for interrupt in result.interrupts
    ]
```

Replace the placeholder `return []`. The given `run_range` loops while `stop_reason` is `"interrupt"` and sends these blocks to the same `director`. Resume the same agent object: the paused turn lives in its state, and a second `Agent(...)` raises `ValueError: Received interrupt responses but agent is not in interrupt state`.

</details>

## Run It

Drill first. It plays the whole protocol through the real Strands agent loop with a scripted stand-in for the model, so it makes no model call:

```bash
python range_safety_officer.py --drill
```

Check: the drone fires on its standing order, the party's run waits at each key, and the DESTRUCT key is held.

```
FTS FIRED: stray delivery drone
RANGE SAFETY KEY ARM: party run -> approve
RANGE SAFETY KEY DESTRUCT: party run -> hold
Range control: the stray delivery drone is down. The hold on the party's run stands.

Fired: ['stray delivery drone']
```

Now the live run, with the System AI on Amazon Nova 2 Lite and you at the keyboard as the Range Safety Officer:

```bash
python range_safety_officer.py
```

Check: the run stops and prints a key, a target, a cause and an effect, then waits. Type `approve` to turn the key; anything else is a hold. The wording of the cause and the System AI's report vary between runs, so this output is an example:

```
FTS FIRED: stray delivery drone

RANGE SAFETY KEY ARM: party run
  cause:  the party is ahead of the quarter's schedule
  effect: the termination is ready to fire
  approve or hold? hold
Range control: the stray delivery drone is down, and the hold on the party's run stands.

Fired: ['stray delivery drone']
```

| you see | it means | fix |
|---|---|---|
| `FTS FIRED: party run` with no question | `ask_key` still holds the placeholder `answer = "approve"` | Step 1 |
| the party's run stops at ARM and then fires with no second question | the `destruct = "approve"` placeholder is still there | Step 2 |
| the drone stops and asks a person | `standing_order` still returns `None`, or the model named the drone differently from `stray delivery drone` | Step 3, or type `approve` twice |
| the turn pauses and the script ends with a repr of the result | `answers_for` returns `[]`, so the resume has nothing to send | Step 4 |
| `ValueError: Received interrupt responses but agent is not in interrupt state` | the loop resumed a different agent object | resume the same `director` |
| `KeyError: ... no interrupt found` | a block carries an id that is not in `result.interrupts` | copy `interrupt.id`, never build one |
| `ModuleNotFoundError: No module named 'range_control_drill'` | the script is not running from its own folder | `cd` to the encounter folder |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Hook or Tool?

[Sponsor Interrupt](sponsor-interrupt.md) asks from a hook on `BeforeToolCallEvent`, and a refusal cancels the tool with `event.cancel_tool`. That is the right place when the rule is a policy about tools: one hook guards every tool, and no tool changes. This passage asks from inside the tool, and a refusal is the tool's own return value. That is the right place when the question depends on what the tool is about to do: two keys, a different reason for each, a standing order that depends on the target. The cost is that every tool you want guarded has to ask for itself. Both kinds can sit in one agent, and a single resume loop answers both, because a hook interrupt and a tool interrupt arrive the same way in `result.interrupts`.

## What It Costs

The pauses cost nothing: while a turn waits, Amazon Nova 2 Lite does not run. In the drill, three calls to the agent made two model calls, one before the first pause and one after the last answer. A live run is about the same: roughly 900 tokens in and 100 out for the first call, which holds the prompt, the tool description and the request, and roughly 1,100 in and 50 out for the final report. That is 2,000 tokens in at $0.30 per million, $0.0006, plus 150 out at $2.50 per million, $0.000375. About one tenth of a cent a run. Rates are the Nova 2 Lite prices from [Floor 1](../floor-1.md#what-a-turn-costs) and the [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/). Nothing is left running in your account.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The Range Safety Officer watched the feed from the Cadabra side the whole time, vest zipped, coffee cold, and did not say a word until the second key came up held. Then they said, to nobody, that in nine years the system had never once asked them anything. I believe that. It asked now. Barnaby filed it. <img src="../../images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** "A machine that asks, Sergeant, has learned the most useful sentence in the language."

## Encounter Clear

Loot you're keeping:

- `@tool(context=True)` gives a tool a `ToolContext`, and `tool_context.interrupt(name, reason=...)` stops the loop from inside the tool
- One tool can raise several interrupts, one at a time: ARM, then DESTRUCT, each with its own name
- `response=` is a preemptive answer: a standing order skips the pause, and no standing order means a pause
- `result.interrupts` can hold more than one interrupt, so the resume answers every one, by id, on the same agent
- The tool runs again from the top on every resume, so keep it free of side effects before the interrupt

> <img src="../../images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[NO KEY, NO FIRE]**
>
> Reward: You received a [Silver Box]. Inside: a laminated two-key checklist, a hi-vis vest in a size that fits nobody, and a thermos of coffee that is still hot, which the Range Safety Officer says is a first.

Back to [Floor 8](../floor-8.md), or on to [8.1 The Dice Server](../floor-8-1.md).
