# Side Passage: Subcontract the Paperwork (Floor 5 Sidequest)

[Back to Floor 5](../floor-5.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-5-subcontract-the-paperwork/subcontract_the_paperwork.py`](../../encounters/floor-5-subcontract-the-paperwork/subcontract_the_paperwork.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 6, MONDAY, JUNE 22, SIDE PASSAGE OFF FLOOR 5.** The ferry run to Bainbridge Island left us with a stack of receipts and no one willing to staple them. On Floor 5 the Narrator would have phoned a Rules Agent or a Character Agent, each one living in its own terminal with its own port. Down here the Narrator did something smaller. The Narrator hired a clerk for the afternoon. One task in, one form out, and the clerk was gone before I finished my coffee. I have signed for contractors in a motor pool. I know the three questions: what may the contractor touch, what rules does the contractor work under, and who vouches for the contractor.
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Sidequest: Subcontract the Paperwork. The Narrator may hire one clerk per task. The clerk has a stamp, a calculator and strict instructions. The clerk does not have opinions, and the clerk may not hire another clerk. Shelly's siphon appears on the form as a line item. It is, as always, not finished."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 5](../floor-5.md), finished; this file runs on its own, so no server needs to be running |
| build | a `hire_clerk` tool that creates a one-off child agent with fixed rules, one calculator tool and a pinned model, and a Narrator that can call it |
| teaches | [`strands.vended_tools.subagent.subagent`](https://strandsagents.com/docs/api/python/strands.vended_tools.subagent.subagent/): `make_subagent`; [`strands.multiagent.spec`](https://strandsagents.com/docs/api/python/strands.multiagent.spec/): `Fixed`, `Preset` |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, on the Narrator and pinned on the clerk |

On Floor 5 the Narrator reaches other agents over the network, with the `a2a_client` tool. Each of those agents is a program started by hand and kept running. A subagent is the lighter alternative to a remote agent. The Narrator calls a tool, Strands builds a fresh child [`Agent`](https://strandsagents.com/docs/api/python/strands.agent.agent/) for that one tool call, the child runs its own turn in its own context, and its final text comes back to the Narrator as the tool result. Then the child is gone. Nothing is deployed and nothing is left running.

[`make_subagent`](https://strandsagents.com/docs/api/python/strands.vended_tools.subagent.subagent/) is the factory that decides what the Narrator is allowed to choose. The `hire_clerk` tool as the Narrator sees it has a `task` field and nothing else, unless an axis is opened. Each setting, called an axis in the module, is held by the code or handed to the Narrator: [`Fixed`](https://strandsagents.com/docs/api/python/strands.multiagent.spec/) pins a value and hides it from the Narrator, `Inherit` takes the parent's, `Open` lets the Narrator write the value, and `Choice` lets the Narrator pick from a list. A [`Preset`](https://strandsagents.com/docs/api/python/strands.multiagent.spec/) is a named role that sets instructions, tools and an Amazon Nova 2 Lite model id together.

There is a trap in the defaults that this side passage exists to close. A child agent given no model id takes the Narrator's model. Here the Narrator is on Amazon Nova 2 Lite, so the clerk would work today, but the clerk would change the day the Narrator's model changed. The crawl runs one model, so the clerk gets it by name.

Check the result: the run prints the Narrator's two-sentence report with a total of 9 tokens bought, and the last line reads `clerks hired: 1`.

Go to the encounter folder:

```bash
cd seattle-strands-dungeon-crawl/dungeon/encounters/floor-5-subcontract-the-paperwork
```

## Step 1: Import the Factory

```python
# TODO: Step 1 - Import make_subagent from strands.vended_tools.subagent.subagent, and Fixed and Preset from strands.multiagent.spec
```

The module path ends in `subagent.subagent`: the package is `subagent` and the file inside it is `subagent.py`. The package also exports a ready-made tool called `subagent`, so `from strands.vended_tools.subagent import subagent` returns that tool, not the module. Import `make_subagent` from the full path and the import returns the factory.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import make_subagent from strands.vended_tools.subagent.subagent, and Fixed and Preset from strands.multiagent.spec
from strands.multiagent.spec import Fixed, Preset
from strands.vended_tools.subagent.subagent import make_subagent
```

</details>

## Step 2: Write the Clerk's Job

```python
# TODO: Step 2 - Build the tool with make_subagent: name hire_clerk, one preset "clerk" with the CLERK_RULES instructions and only the add_up tool, and instructions=Fixed() so the model cannot rewrite them
```

`make_subagent` takes keyword arguments only. `name="hire_clerk"` is the name the Narrator calls and the name the child carries. `presets={"clerk": Preset(instructions=CLERK_RULES, tools=["add_up"])}` defines the role: the rules the clerk works under, and the one tool it may use, by name. `instructions=Fixed()` closes the axis, so the Narrator cannot slip new rules into the task. Without `instructions=Fixed()` the default is `Open()`, and the Narrator could write the clerk's whole job description.

The tool names in a preset are looked up in the parent's tools. The clerk can only borrow a tool the Narrator owns, which is why Step 4 gives the Narrator `add_up` too. A name the parent does not own is skipped with a log warning, and the clerk would be left to add by hand. See [`Preset`](https://strandsagents.com/docs/api/python/strands.multiagent.spec/).

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** A contractor gets a badge for the rooms the job needs and no others. This clerk got one room: the calculator. I liked that. Barnaby read the rules over my shoulder and asked why the clerk was forbidden to add numbers by hand. I said because a person who adds by hand will eventually add wrong. "Quite, Sergeant. It is the same reason one does not eyeball a fuel load."

## Step 3: Pin the Model

```python
# TODO: Step 3 - Pin the clerk's model in the same call with model=Fixed(...) set to Amazon Nova 2 Lite, so it never falls back to the parent's
```

This is the second axis in the same call. `model=Fixed("us.amazon.nova-2-lite-v1:0")` hands every clerk that exact model, by name, and the `model` field disappears from the `hire_clerk` tool the Narrator sees. The other settings are `Inherit()`, which applies when `model` is left out and takes the parent's model, and `Open()` or `Choice(...)`, which would let the Narrator pick the model. Neither setting belongs in a crawl that runs only Amazon Nova 2 Lite.

<details>
<summary>Show me the code for Steps 2 and 3</summary>

```python
def make_clerk_tool():
    """The tool the Narrator calls to hire a clerk for one task."""
    # TODO: Step 2 - Build the tool with make_subagent: name hire_clerk, one preset "clerk" with the CLERK_RULES instructions and only the add_up tool, and instructions=Fixed() so the model cannot rewrite them
    # TODO: Step 3 - Pin the clerk's model in the same call with model=Fixed(...) set to Amazon Nova 2 Lite, so it never falls back to the parent's
    return make_subagent(
        name="hire_clerk",
        description="Hire a one-off clerk to file the party's paperwork. Give it the whole task, with every number it needs.",
        presets={"clerk": Preset(instructions=CLERK_RULES, tools=["add_up"], description="a clerk who files forms and adds with add_up")},
        instructions=Fixed(),
        model=Fixed("us.amazon.nova-2-lite-v1:0"),  # Amazon Nova 2 Lite, US cross-Region inference profile
    )
```

Replace the `return None`. The trap: the Narrator reads the `description` when it decides whether to hire a clerk, and the clerk cannot ask questions, so the description tells the Narrator to pass the whole task with every number.

</details>

## Step 4: Equip the Narrator

```python
# TODO: Step 4 - Give the Narrator the add_up tool and the clerk_tool
```

The Narrator needs two things in its `tools` list: `clerk_tool`, so the Narrator can hire, and `add_up`, so the clerk has something to borrow. `add_up` is a plain `@tool` function, the kind written on Floor 3. The Narrator's system prompt tells the Narrator never to file anything itself, so `add_up` sits on its list for the clerk's sake. A clerk cannot hire a clerk either: the `strands.vended_tools.subagent` module limits delegation depth, and a child is built one level down.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The Narrator handed over the whole task in one paragraph: who bought how many tokens, Chonks's snack, the siphon line. The Narrator left nothing out, because the clerk could not call back. I have written that kind of order before. If the person reading the order cannot reach me, the order has to stand on its own.

<details>
<summary>Show me the code for Step 4</summary>

```python
        # TODO: Step 4 - Give the Narrator the add_up tool and the clerk_tool
        tools=[add_up, clerk_tool],
```

Replace the `tools=[]` line. Leave `add_up` off and the clerk's calculator is skipped, which the log reports only as a warning.

</details>

## Hire the Clerk

```bash
python subcontract_the_paperwork.py
```

Check: the Narrator reports the form in two sentences and names the total, 9. The wording comes from Amazon Nova 2 Lite, so this is an example:

```
The clerk filed the Bainbridge Island Ferry Token expense report: Cordula bought 4 tokens, Barnaby 3 and Chonks 2, and the siphon line remains unfinished. The total tokens bought is 9.

clerks hired: 1
```

| you see | meaning | fix |
|---|---|---|
| `ImportError: cannot import name 'make_subagent'` | the import comes from the package instead of the module | Step 1 |
| `AttributeError: 'NoneType' object has no attribute 'tool_name'` or the Narrator has no `hire_clerk` | `make_clerk_tool()` still returns `None` | Steps 2 and 3 |
| `clerks hired: 0` | the Narrator did the paperwork itself, or `clerk_tool` is not on the Narrator's tool list | Step 4 |
| a log line says the parent does not own `add_up` | the Narrator's tool list is missing `add_up` | Step 4 |
| `Subagent error:` in the tool result | the clerk's turn failed | read the text after `Subagent error:`; an Amazon Nova 2 Lite call failure is [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Clerk or Remote Agent?

The Rules Agent of Floor 5 is shared: many callers, one running service, one set of rules, and the Rules Agent needs a port and a terminal. The clerk is private. The clerk exists for one call, its context is separate from the Narrator's, and the Narrator never sees its reasoning, only its report. Use a remote agent when more than one program needs the same specialist. Use a subagent when one agent wants a short job done in a clean context, with the clerk's rules written in advance. The subagent tool can also pass the parent's conversation down, through a `context` setting; that setting stays closed here at its default, `none`, so the clerk starts fresh.

## What It Costs

Two Amazon Nova 2 Lite turns complete the run. The Narrator reads the task and hires the clerk (about 600 tokens in, 150 out). The clerk reads its rules and the task, calls `add_up`, and writes the form (about 700 in, 200 out, across two Amazon Nova 2 Lite calls). Then the Narrator writes its two sentences (about 900 in, 80 out). At about $0.30 per million input tokens and $2.50 per million output tokens, the total is roughly 3,000 tokens in and 700 out: about $0.003 for the whole run, a third of a cent. `add_up` runs in code and costs nothing. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Nine tokens, stamped and filed. The System AI said the clerk would like the log to note that the form was submitted on time. I asked whether the clerk got a name. The System AI said no, a clerk is a role. Barnaby said that is how most of the ferry system runs, and he meant it as praise.

## Encounter Clear

Loot to keep:

- A subagent tool builds a fresh child agent for one task, and the child is gone when it reports back
- `make_subagent` takes keyword arguments, and each axis (`instructions`, `tools`, `model`) is `Fixed`, `Inherit`, `Open` or `Choice`
- A `Preset` bundles a role's instructions and tools under a name
- Pin the model with `model=Fixed(...)`: the default inherits the Narrator's model
- A clerk borrows tools from the Narrator by name, so the Narrator has to own them

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[CONTRACTOR OF RECORD]**
>
> Reward: You received a [Bronze Box]. Inside: one rubber stamp, one calculator with a very good battery, and a Ferry Token receipt with a line item that never finishes.

Back to [Floor 5](../floor-5-3.md#floor-clear), or on to [Floor 6](../floor-6.md).
