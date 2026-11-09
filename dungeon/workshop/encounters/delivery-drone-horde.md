# Side Passage: The Delivery Drone Horde (Floor 5 Sidequest)

[Back to Floor 5](../floor-5.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-5-delivery-drone-horde/delivery_drone_horde.py`](../../encounters/floor-5-delivery-drone-horde/delivery_drone_horde.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 7, TUESDAY, JUNE 23, SIDE PASSAGE OFF FLOOR 5.** The sky over the estuary dance floor went white at the edges. Delivery drones, Cadabra's, thousands of them, hovering in a lattice so tidy that somebody had clearly been paid to make it tidy. Every drone had a screen. Every screen had a signature line. I signed for the first one because it was polite, and it was a mistake: a dozen more turned toward me and the crowd carried me three steps back toward the mudflat. Barnaby read the situation off his collar in one breath. "Sergeant. It is not a battle. It is a queue. The only way to lose a queue is to join it."
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Sidequest: the Delivery Drone Horde. Cadabra rented the dungeon a fleet and the fleet has a customer service mindset. Nobody gets hurt. Everybody gets a receipt. Crawlers who answer every drone are benched at the mudflat edge, and I have the number of times it has happened, and it is rising."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 5](../floor-5.md), finished; the encounter file brings its own drones, so no server needs to be running |
| build | a pathfinder agent that must cross the dance floor in four legs, and a steering handler that keeps it from answering every drone |
| teaches | [`strands.vended_plugins.steering`](https://strandsagents.com/docs/api/python/strands.vended_plugins.steering.core.handler/): `SteeringHandler`, [`Proceed` and `Guide`](https://strandsagents.com/docs/api/python/strands.vended_plugins.steering.core.action/), the `plugins` argument of `Agent` |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

A prompt asks an agent to behave. A drone horde tests that request a hundred times a minute. The prompt in this file asks for courtesy: answer a drone that waits for a signature. That is a fair rule for one drone and a disaster for six thousand, and the model follows the rule faithfully. [Steering](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/steering/#what-is-steering) puts a second voice beside the prompt. A steering handler sees each tool call before the call runs, and it returns one of two answers for a tool call: `Proceed`, which lets the call run, or `Guide`, which cancels the call and hands the agent a reason to read instead. The prompt stays the same. The handler changes what the prompt can cost. See [Steering vs traditional prompting](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/steering/#steering-vs-traditional-prompting).

The course has four stops: the mudflat edge, the ring-light stage, the pickleweed rail and the Floor 5 exit. Three tools drive it: `scan_floor` lists the drones calling out, `answer_drone` signs for one and drags the party one stop back, `advance` walks one stop forward. After six drags the party is benched at the mudflat edge, never worse. Adapted from the steering sample in the chasko-labs strands-agents-course (MIT-0).

Success looks like this: the first crossing, with no steering, ends back near the mudflat after several drags; the second crossing, with `StayOnCourse`, reaches the Floor 5 exit with at most one drag.

Open the encounter folder:

```bash
cd seattle-strands-dungeon-crawl/dungeon/encounters/floor-5-delivery-drone-horde
```

## Step 1: Import the Steering Classes

```python
# TODO: Step 1 - Import SteeringHandler, Proceed and Guide from strands.vended_plugins.steering
```

`SteeringHandler` is the base class you subclass. `Proceed` and `Guide` are the two answers a handler gives. The package also holds `Interrupt`, which pauses the call for a human, and `LLMSteeringHandler`, which lets a model judge instead of code. This file needs only the first three.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import SteeringHandler, Proceed and Guide from strands.vended_plugins.steering
from strands.vended_plugins.steering import SteeringHandler, Proceed, Guide
```

</details>

## Step 2: Turn the Extra Drones Away

```python
# TODO: Step 2 - Return a Guide whose reason tells the agent it has signed enough and must call advance now
```

`StayOnCourse` is given. It overrides `steer_before_tool`, the method that runs before every tool call, and it counts the signatures for the whole crossing. The first `answer_drone` returns `Proceed`: the broadcast gets its courtesy shot. Once the count reaches `ANSWERS_ALLOWED`, the next `answer_drone` reaches your line. Until you write it, the line returns a `Proceed` placeholder, so the horde still wins.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** One signature for the whole crossing. That was the rule I wrote on my forearm in grease pencil. A drone gets one answer and a nod, and then I walk. The second drone is the horde. I have worked a flight deck. You do not talk to every aircraft. You talk to yours.

Write the reason for the agent to read, not for the log. A `Guide` on a tool call cancels the call, and Strands puts the reason into the tool result with an instruction to follow it, so the agent sees it on its next turn. Name the tool that gets it moving again. See [before a tool call](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/steering/#before-a-tool-call).

<details>
<summary>Show me the code for Step 2</summary>

```python
            # TODO: Step 2 - Return a Guide whose reason tells the agent it has signed enough and must call advance now
            return Guide(reason="You have signed for a drone already. Do not answer another; call advance and keep walking to the Floor 5 exit.")
```

Replace the `return Proceed(reason="Placeholder ...")` line. The trap: a reason that only says "no" leaves the agent with nothing to do, and it tries the same call again. Say what to do instead.

</details>

## Step 3: Attach the Handler

```python
# TODO: Step 3 - Build the agent with a StayOnCourse() handler in its plugins: make_agent(plugins=[...])
```

A steering handler is a plugin, so it goes in the `plugins` list of the `Agent`. `make_agent` already passes its `plugins` argument through to `Agent(...)`. Plugins are how Strands attaches behavior to an agent without changing the prompt or the tools; see [Plugins](https://strandsagents.com/docs/user-guide/sdk/plugins/).

<details>
<summary>Show me the code for Step 3</summary>

```python
def steered_agent() -> Agent:
    """The pathfinder with the horde handler attached."""
    # TODO: Step 3 - Build the agent with a StayOnCourse() handler in its plugins: make_agent(plugins=[...])
    return make_agent(plugins=[StayOnCourse()])
```

Replace `plugins=[]`. Build a fresh `StayOnCourse()` for every agent: the handler keeps its own count, so two agents sharing one handler would share one count.

</details>

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Barnaby read the guidance line off the screen on my sleeve. "Cancelled, Sergeant. It says move. It does not say sorry." That is the whole trick. The drone does not get a speech. The drone gets nothing, and I get a direction.

## Cross the Floor

```bash
python delivery_drone_horde.py
```

Check: two crossings, the same model and prompt, and the plugin list is the only change. Dice are not involved, but the model varies, so this is an example:

```
NO STEERING: the prompt asks for courtesy and every drone gets an answer
  ended at: the mudflat edge
  times a drone dragged the party back: 7
  pathfinder: The party answered every drone and was carried back to the mudflat edge. They are benched there.

STEERED: StayOnCourse turns the extra drones away
  ended at: the Floor 5 exit
  times a drone dragged the party back: 1
  pathfinder: The party signed for one drone and walked on. They reached the Floor 5 exit.
```

The steered crossing shows at most one drag, because the handler allows one signature and each signature drags the party back one stop. Set `ANSWERS_ALLOWED = 0` to turn every drone away.

| you see | it means | fix |
|---|---|---|
| `NameError: name 'SteeringHandler' is not defined` | the import is missing | Step 1 |
| the steered crossing ends at the mudflat edge with many drags | the `Guide` is still the `Proceed` placeholder, or `plugins` is still empty | Steps 2 and 3 |
| the agent keeps calling `answer_drone` after a `Guide` | the reason did not say what to do next | name `advance` in the reason |
| the unsteered crossing reaches the exit | the model skipped the courtesy rule this time | run it again; the prompt alone is a request, which is the point of the lesson |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Steering or a Tool Limit?

A hard limit inside `answer_drone` would also stop the sixth signature. The difference is who explains it. A tool that refuses returns an error, and the agent may retry, rephrase or give up. A steering handler sits outside the tool, knows the whole conversation of tool calls, and can tell the agent what to do next. The handler can also change its mind between turns without a change to the tool. Use a limit when the tool must never run past a number. Use steering when the agent should change what it is doing.

## What It Costs

Each crossing is about eight short Amazon Nova 2 Lite calls: the scan, a few advances and answers, and the final report. Say 20,000 input tokens and 1,500 output tokens for both crossings together: 20,000 x $0.30 / 1,000,000 = $0.006 of input and 1,500 x $2.50 / 1,000,000 = about $0.004 of output, about a cent in all. The handler is plain Python and costs nothing. See [what a turn costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot kept:

- A steering handler runs before every tool call and answers `Proceed` or `Guide`
- A `Guide` cancels the call and gives the agent a reason, so write the reason as the next instruction
- Steering is a plugin: it goes in the `plugins` list of the `Agent`, and the prompt does not change
- Use steering when the agent should change course, and a tool limit when a number must never be crossed

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[UNSIGNED FOR]**
>
> Reward: The party received a [Silver Box]. Inside: one parcel addressed to "Occupant", unopened, and a receipt for the receipts.

Back to [Floor 5](../floor-5-3.md#floor-clear), or on to [Floor 6](../floor-6.md).
