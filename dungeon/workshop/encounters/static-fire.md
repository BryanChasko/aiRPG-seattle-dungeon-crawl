# Side Passage: Static Fire on the Pad (Floor 7 Sidequest)

[Back to Floor 7](../floor-7.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-7-static-fire/static_fire.py`](../../encounters/floor-7-static-fire/static_fire.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 9, THURSDAY, JUNE 25, SIDE PASSAGE OFF FLOOR 7.** Low water at 0855, minus 0.3 feet, and the tidal flat below the bluffs lay bare to the madrone roots. A rocket stood on it. Forty-five metric tons of payload rating, a Cadabra logo the size of a ferry, and a gantry with a lanyard-wearing Range Safety Officer on top who had a 214-line checklist and had read every line out loud to the gulls. Static fire at 0858. Three minutes on the clock and three jobs on the table: read the clock, sweep the beach, make the call. I can do one job at a time. The System AI had already started the broadcast. Barnaby had a view. "Sergeant. Three duties, and only one of you."
<!-- /cordula-log -->

> <img src="../../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Crawlers, a heavy-lift rocket, a tidal flat and a beach full of people who did not read the signage. Cadabra's engine test is scheduled, funded and, I am told, fully insured. Your range desk needs a countdown reader, a debris check and a hold call. I will be watching the third one closely. The viewers have money on it."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 7](../floor-7.md), finished |
| build | a range desk agent from one plugin you write (two tools and a hook) and one plugin you configure (two skills) |
| teaches | [`strands.plugins.plugin`](https://strandsagents.com/docs/api/python/strands.plugins.plugin/), [`strands.plugins.decorator`](https://strandsagents.com/docs/api/python/strands.plugins.decorator/), [`strands.vended_plugins.skills.agent_skills`](https://strandsagents.com/docs/api/python/strands.vended_plugins.skills.agent_skills/), [`strands.vended_plugins.skills.skill`](https://strandsagents.com/docs/api/python/strands.vended_plugins.skills.skill/) |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

A plugin is a package of behavior that snaps onto an agent. A Strands `Plugin` subclass can bring tools (methods marked `@tool`), hooks (methods marked `@hook`) and its own set-up code, and the agent registers all of them when you pass the plugin in `plugins=[...]`. One object, three kinds of change. The countdown reader and the debris check are tools; a hook that logs each tool call rides along in the same class. See [Plugins](https://strandsagents.com/docs/user-guide/sdk/plugins/) and [Building plugins](https://strandsagents.com/docs/user-guide/sdk/plugins/custom-plugins/#basic-plugin-structure).

A skill is a different kind of capability: instructions, not code. The `AgentSkills` plugin puts only each skill's name and one-line description into the system prompt, and gives the agent a tool called `skills`. When the agent decides a skill fits, it calls `skills` with the skill's name and gets the full instructions back. That is progressive disclosure: the hold-call rules cost nothing until the agent needs them. See [Skills](https://strandsagents.com/docs/user-guide/sdk/plugins/skills/#how-skills-work). Both plugins go into the same `plugins=[...]` list, which is the composing.

How you know it worked: the range desk calls `read_countdown` and `debris_check`, activates `hold-call`, and calls HOLD because the kayak tour sits 400 meters from the pad. The script prints the tools called in order and the skills activated.

Adapted from the plugins and skills sample in the Strands Agents Course ([`samples/06-plugins-skills`](https://github.com/aws-samples/sample-building-with-strands-course/tree/main/samples/06-plugins-skills), MIT-0), with the APIs checked against the installed Strands Agents SDK.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/dungeon/encounters/floor-7-static-fire
```

Given code: the pad clock (`pad_clock`), the beach (`beach_scan`), the exclusion radius of 500 meters, the `range_log` list, two `Skill` objects (`HOLD_CALL` and `PAD_CALLOUT`), the range desk prompt and the `make_director` function. A `Skill` is a name, a description and instructions; nothing in it calls a model.

> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Pre-launch is a checklist, and a checklist is a division of labor. One person reads the clock. One person walks the perimeter. One person holds the authority to stop it. I have never seen one person do all three on a live range, and I have seen what happens when one tries. The agent needs the same split. Tools for the reading and the walking, a written rule for the call.

## Step 1: Import the Pieces

```python
# TODO: Step 1 - Import AgentSkills and tool from strands, Plugin and hook from strands.plugins, and BeforeToolCallEvent from strands.hooks
```

Five names from three modules. `Plugin` is the base class and `hook` is the decorator that marks a method as an event callback, both from `strands.plugins`. `BeforeToolCallEvent` is the event the hook will listen for, from `strands.hooks`. `AgentSkills` and `tool` come from the top-level `strands` package, next to `Agent` and `Skill`.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import AgentSkills and tool from strands, Plugin and hook from strands.plugins, and BeforeToolCallEvent from strands.hooks
from strands import AgentSkills, tool
from strands.hooks import BeforeToolCallEvent
from strands.plugins import Plugin, hook
```

</details>

## Step 2: Write the Range Crew

```python
# TODO: Step 2 - Write class RangeCrew(Plugin): name "range-crew", a @tool method read_countdown that returns pad_clock(), a @tool method debris_check(radius_m: int = EXCLUSION_RADIUS_M) that returns beach_scan(radius_m), and a @hook method note_call(self, event: BeforeToolCallEvent) that appends event.tool_use["name"] to range_log
```

Three rules for a plugin class. It needs a `name`: a stable string, set as a class attribute, and the agent refuses two plugins with the same name. Methods marked `@tool` become tools the agent can call, built from the method's signature and docstring exactly as on Floor 3, with `self` left out of the tool's schema. Methods marked `@hook` become event callbacks, and the event type comes from the type hint on the `event` parameter, so the hint is required. See [Registering hooks in plugins](https://strandsagents.com/docs/user-guide/sdk/plugins/custom-plugins/#registering-hooks-in-plugins) and the [hook decorator](https://strandsagents.com/docs/api/python/strands.plugins.decorator/).

Write careful docstrings. Amazon Nova 2 Lite chooses between `read_countdown` and `debris_check` by reading them.

> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The hook is the range log. Before any tool runs, the hook writes its name on the list. It does not decide anything and it does not touch the tool. It watches. Every range has one person doing only that, and after an incident, that list is the first thing anyone asks for.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Write class RangeCrew(Plugin): name "range-crew", a @tool method read_countdown that returns pad_clock(), a @tool method debris_check(radius_m: int = EXCLUSION_RADIUS_M) that returns beach_scan(radius_m), and a @hook method note_call(self, event: BeforeToolCallEvent) that appends event.tool_use["name"] to range_log
class RangeCrew(Plugin):
    name = "range-crew"

    @tool
    def read_countdown(self) -> dict:
        """Read the pad clock: seconds to launch, chamber pressure and propellant load.

        Returns:
            t_minus_seconds, chamber_pressure_pct (the safe band is 90 to 105) and propellant_load_pct.
        """
        return pad_clock()

    @tool
    def debris_check(self, radius_m: int = EXCLUSION_RADIUS_M) -> list:
        """List everything on the beach and the water within radius_m meters of the pad.

        Args:
            radius_m: How far from the pad to look, in meters. The default is the exclusion radius.

        Returns:
            One entry per thing found, with its item and distance_m. An empty list means the radius is clear.
        """
        return beach_scan(radius_m)

    @hook
    def note_call(self, event: BeforeToolCallEvent):
        range_log.append(event.tool_use["name"])
```

The trap: a `@hook` method with no type hint on `event` fails when the class is defined, with a `ValueError` that says the event type cannot be inferred. Write `event: BeforeToolCallEvent`, not `event`.

</details>

## Step 3: Hand the Desk Its Skills

```python
# TODO: Step 3 - Build the skills plugin: AgentSkills with skills=[HOLD_CALL, PAD_CALLOUT], as skills_plugin
```

`AgentSkills` is itself a `Plugin`, built into the SDK. Its `skills` argument takes a list, and each entry can be a `Skill` object (as here), a path to a folder holding a `SKILL.md`, or a path to a folder of such folders. This encounter keeps both skills as `Skill` objects in the file so the whole lesson sits on one page. A folder of `SKILL.md` files is the same idea on disk; see [Usage](https://strandsagents.com/docs/user-guide/sdk/plugins/skills/#usage) and [Programmatic skill creation](https://strandsagents.com/docs/user-guide/sdk/plugins/skills/#programmatic-skill-creation).

Creating `AgentSkills` calls nothing remote. The skills reach the agent when the plugin attaches in Step 4.

<details>
<summary>Show me the code for Step 3</summary>

```python
# TODO: Step 3 - Build the skills plugin: AgentSkills with skills=[HOLD_CALL, PAD_CALLOUT], as skills_plugin
skills_plugin = AgentSkills(skills=[HOLD_CALL, PAD_CALLOUT])
```

</details>

## Step 4: Compose the Range Desk

```python
        # TODO: Step 4 - Give the agent both plugins: plugins=[crew, skills_plugin]
```

This line is inside the `Agent(...)` call in `make_director`. `plugins=` takes a list of `Plugin` instances. When the agent is built, each plugin is initialized with the agent, and the agent registers the plugin's tools and hooks. The crew adds `read_countdown` and `debris_check`; `AgentSkills` adds the `skills` tool and, before each run, appends the list of skill names and descriptions to the system prompt. The plugins do not know about each other, and they do not need to.

> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Barnaby read the Agent call over my shoulder. "Two plugins, Sergeant. A squad and a field manual." I told him the squad is the crew and the manual is the skills. He said the manual is the better idea: nobody carries every page into the field, only the table of contents, and you open to the page when the situation arrives. He then asked what T-minus meant. He knew. He wanted to hear a Marine say it.

<details>
<summary>Show me the code for Step 4</summary>

```python
def make_director(crew: "RangeCrew") -> Agent:
    """The range desk: Amazon Nova 2 Lite with the crew plugin and the skills plugin."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None,
        # TODO: Step 4 - Give the agent both plugins: plugins=[crew, skills_plugin]
        plugins=[crew, skills_plugin],
    )
```

The trap: plugin names must be unique on one agent. Passing two `RangeCrew()` instances in the same list fails with `plugin already registered`, because both are named `range-crew`.

</details>

## Run It

```bash
python static_fire.py
```

Check: the range desk's callout, then the two logs. Wording varies by run; the HOLD does not, because the kayak tour is 400 meters out and the exclusion radius is 500:

```
Range desk: T-minus 3:00 HOLD. A team-building kayak tour from Bellevue, six people in matching vests and one clipboard, is 400 meters from the pad, inside the 500 meter exclusion radius.

tools called, in order: ['read_countdown', 'debris_check', 'skills', 'skills']
skills activated: ['hold-call', 'pad-callout']
```

The order of the first two tools can swap, and they can arrive in the same response. The `skills` entries show up once per skill the desk activated. `range_log` records every tool call, including the call to `skills`, because the hook fires for every tool on the agent, not only for the crew's own.

| you see | it means | fix |
|---|---|---|
| `NameError: name 'RangeCrew' is not defined` | Step 2 is missing, or the class has another name | name the class `RangeCrew` |
| `NameError: name 'skills_plugin' is not defined` | Step 3 is missing, or the variable has another name | name the variable `skills_plugin` |
| `ValueError` about inferring the event type, when the file loads | the `@hook` method has no type hint on `event` | write `event: BeforeToolCallEvent` |
| `TypeError: Can't instantiate abstract class RangeCrew` | the class has no `name` | add `name = "range-crew"` as a class attribute |
| `tools called, in order: []` | the agent never called a tool: `plugins=[...]` is missing from `Agent(...)`, or the model answered without tools | check Step 4, then run again |
| `skills activated: []` with the right tools called | Amazon Nova 2 Lite made the call without loading a skill | run again; the system prompt tells the desk to activate the skills that fit |
| `AccessDeniedException` or `ExpiredToken` | the call to Amazon Nova 2 Lite failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Skills Versus One Long Prompt

The same rules could sit in `SYSTEM_PROMPT`: the 500 meters, the pressure band, the callout format. For two small skills that would be fine. The skills version pays off as the list grows. Ten skills in the prompt means ten sets of rules read on every model call; ten skills behind the `skills` tool means ten names and descriptions on every call, and only the instructions the desk loads. The price is one extra tool call per skill used, and the chance that the model skips a skill it should have loaded. The hold-call rules are exactly the kind of text where you want the desk to load them on purpose, which is why the system prompt says to.

## What It Costs

A run makes three or four Amazon Nova 2 Lite calls: the two readings, the skill activations, the callout. Each call carries the system prompt, the skill list and three tool definitions, roughly 500 to 1,100 input tokens. About 3,400 input tokens at $0.30 per million is $0.0010, and about 350 output tokens at $2.50 per million is $0.0009: about two tenths of a cent a run. The tools, the hook and the plugins cost nothing. Rates and the math behind a turn are on [What a Turn Costs](../floor-1.md#what-a-turn-costs).

> <img src="../../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** HOLD at T-minus 3:00. The Range Safety Officer on the gantry looked at the kayak tour, then at the clipboard, then at their own clipboard, and found a line 143 that said "confirm beach is empty". They had not confirmed it. They sat down on the gantry. The tour paddled off, one vest at a time, with the clipboard held high like a flag. The rocket stayed on the pad, humming. The System AI called it a scrub and sold the replay. Barnaby asked for the range log. I handed it over. Four lines. He read all four.

## Encounter Clear

Loot kept:

- A `Plugin` subclass packages tools and hooks into one object that an agent takes with `plugins=[...]`
- `@tool` and `@hook` on methods, and why a `@hook` method needs a type hint on its event
- `AgentSkills` and `Skill`: progressive disclosure, with names in the prompt and instructions behind the `skills` tool
- Two plugins on one agent, with unique names

> <img src="../../../images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[HOLD AT T-MINUS THREE]**
>
> Reward: Cordula received a [Bronze Box]. Inside: a pad clock, a laminated range log with four lines on it, and a field manual that is mostly table of contents.

Back to [Floor 7](../floor-7.md#floor-clear), or on to [Floor 8](../floor-8.md).
