# Side Passage: The Living Workbench (Floor 3 Sidequest)

[Back to Floor 3](../floor-3.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-3-living-workbench/living_workbench.py`](../../encounters/floor-3-living-workbench/living_workbench.py), [`encounters/floor-3-living-workbench/shelf/final_beat.py`](../../encounters/floor-3-living-workbench/shelf/final_beat.py), [`encounters/floor-3-living-workbench/tools/roll_d20.py`](../../encounters/floor-3-living-workbench/tools/roll_d20.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 3.** Past the last kelp holdfast there was a workbench bolted to the rock, with one tool hung on the pegboard: the dice. A tie came up on the table behind us, and the System said it could not settle the tie. No Final Beat on the bench. My first thought was the one I have in a motor pool: pull the aircraft, fit the part, spin it up again. Barnaby put an arm across the pegboard. "Sergeant, there is a folder. The System watches it. Put the part in the folder and the System takes the part, mid-sentence, without going down."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "A workbench. Hot-swappable. I want it on the record that I was not consulted, and that I have never once been caught without a tool. I am early for the tool."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 3](../floor-3.md), finished |
| build | an agent that watches a `tools/` folder, and a `final_beat` tool that joins it while the agent is running |
| teaches | [`strands.tools.watcher`](https://strandsagents.com/docs/api/python/strands.tools.watcher/), [`strands.tools.decorator`](https://strandsagents.com/docs/api/python/strands.tools.decorator/) |
| time | about 15 minutes |
| runs on | Amazon Nova 2 Lite, as on every floor |

On Floor 3 the code passed `tools=[...]` to the agent, and the agent had only the tools passed when it was built. A second way to give an agent tools is a folder. Build the agent with `load_tools_from_directory=True` and Strands loads every Python file in `./tools` at start, then starts a `ToolWatcher` on the folder. When a file in that folder is saved, the watcher reloads that tool, or registers the tool if the file is new. The agent does not restart and does not lose its conversation. See [Auto-loading and reloading tools](https://strandsagents.com/docs/user-guide/sdk/tools/using-tools/#auto-loading-and-reloading-tools).

The file added in this encounter is a tool, and a tool is made by the `@tool` decorator from `strands.tools.decorator`: the decorator reads the function's name, type hints and docstring and builds the specification Amazon Nova 2 Lite sees. Floor 3 used `from strands import tool`; `strands.tools.decorator` is the module behind that import. See [Loading function-based tools](https://strandsagents.com/docs/user-guide/sdk/tools/custom-tools/#loading-function-based-tools).

The tool is the Final Beat from the [Crawl Handbook](../world/crawl-handbook/04-final-beat.md): both sides roll, the total closest to 20 without going over wins, a total over 20 loses, and the drum goes again on a tie. The Final Beat function is written already, apart from the two lines that make it a tool, and waits on a shelf, in `shelf/final_beat.py`, outside the folder the agent watches. The script asks the agent to settle a tied round, copies the file into `tools/`, waits for the tool to appear, and asks again.

Signs the run worked: the first turn ends with the System saying the drum is not on the workbench, the tool list grows from `['roll_d20']` to include `final_beat` without the agent being rebuilt, and the second turn settles the tie with rolled totals.

Open the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-3-living-workbench
```

Run the script from the encounter folder. Strands looks for `./tools` in the current directory, and the script moves to the encounter folder before building the agent. The folder has to exist when the agent is built, or nothing watches it.

## Step 1: Watch the Folder

```python
# TODO: Step 1 - Load the tools in ./tools and watch the folder for changes: pass load_tools_from_directory=True
```

One argument on the `Agent`, in `make_workbench()`. Without the argument the agent ignores the folder, and `tools=` stays the only way in. With the argument, `roll_d20` loads at start, and the watcher is running before the first turn.

<details>
<summary>Show me the code for Step 1</summary>

```python
        # TODO: Step 1 - Load the tools in ./tools and watch the folder for changes: pass load_tools_from_directory=True
        load_tools_from_directory=True,
```

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** One flag, and a pegboard that had been decoration became inventory. The first turn came back with a list of one: the dice. I read the list twice. I always read the list twice before I change it.

## Step 2: Import the Decorator

```python
# TODO: Step 2 - Import tool from strands.tools.decorator
```

Open `shelf/final_beat.py`. The function is there, with its docstring, which is the part Amazon Nova 2 Lite reads. The function is not a tool yet. Import `tool` from `strands.tools.decorator` at the TODO.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Import tool from strands.tools.decorator
from strands.tools.decorator import tool
```

</details>

## Step 3: Mark It as a Tool

```python
# TODO: Step 3 - Mark final_beat as a tool with the @tool decorator
def final_beat(crawler: str = "Cordula") -> dict:
```

Put `@tool` on the line above `def final_beat`. That one line is the whole change. The decorator turns the function into a tool named `final_beat`, with an input called `crawler` and a description taken from the docstring. A file with no decorated function and no `TOOL_SPEC` is not a tool, and the watcher will refuse to register the file.

<details>
<summary>Show me the code for Steps 2 and 3</summary>

```python
# TODO: Step 2 - Import tool from strands.tools.decorator
from strands.tools.decorator import tool

FOOTWORK = {"Cordula": 1, "Barnaby": 4}  # the party's Dexterity modifiers


# TODO: Step 3 - Mark final_beat as a tool with the @tool decorator
@tool
def final_beat(crawler: str = "Cordula") -> dict:
```

The docstring tells Amazon Nova 2 Lite the rule and tells it not to roll or decide anything itself, the Floor 3 lesson. The drum can sound several times inside the tool; Amazon Nova 2 Lite sees one answer.

</details>

## Step 4: Put It on the Bench

```python
# TODO: Step 4 - Copy SHELF into the TOOLS folder with shutil.copyfile; the new file is TOOLS / SHELF.name
```

`SHELF` is the path of the file edited in Steps 2 and 3, and `TOOLS` is the watched folder. `shutil.copyfile(source, destination)` copies the file, and the destination is the whole new path, `TOOLS / SHELF.name`, not just the folder. The new file is the change the watcher sees. The script calls `put_on_the_bench()` after the first turn, with the agent still running, and then `wait_for_tool` checks `agent.tool_names` until `final_beat` appears, for up to ten seconds.

<details>
<summary>Show me the code for Step 4</summary>

```python
def put_on_the_bench() -> None:
    """Add final_beat to the folder while the agent is running."""
    # TODO: Step 4 - Copy SHELF into the TOOLS folder with shutil.copyfile; the new file is TOOLS / SHELF.name
    shutil.copyfile(SHELF, TOOLS / SHELF.name)
```

Replace the `pass`. The watcher reacts to a file that is modified, and a copy writes the new file, which counts. A copy the watcher catches half written fails to load and logs an error; the next write of the file loads the tool.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** I copied the file and counted. One second, two. The pegboard did not change, but the list did: dice, then dice and the Final Beat. The same agent, the same conversation, no restart. In the Reserve we called that a field repair. The tie came up again and the drum sounded, and that was the whole job.

## Work the Bench

```bash
python living_workbench.py
```

Check: two turns, with the tool list before each. The output below is an example; the words and the dice will differ:

```
ON THE BENCH: ['roll_d20']
  The drum is not on the workbench yet.

ON THE BENCH: ['roll_d20', 'final_beat']
  The drum sounded once: Cordula lands on 18, the banker on 12, and the party takes the tie.
```

The script removes `tools/final_beat.py` when it finishes, so the next run starts with a bare bench.

| you see | it means | fix |
|---|---|---|
| `ON THE BENCH: []` | the agent is not loading the folder | Step 1 |
| `final_beat never showed up on the bench` | the watcher could not load the file: a failed reload is logged and never raised | Steps 2 and 3; turn on debug logging as in [Floor 1, Step 1](../floor-1.md#step-1-enable-debug-logging) and read the error |
| `ON THE BENCH` lists `final_beat` but the second turn does not use it | Amazon Nova 2 Lite chose not to call `final_beat` | run the script again; the user message names the Final Beat on purpose |
| `AccessDeniedException` or `ExpiredToken` | the call to Amazon Nova 2 Lite failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Folder or Parameter?

`tools=[...]` is the right way to give an agent tools that ship with the code: the tools are checked when the program is written, and they cannot change while the agent runs. The folder is the right way during development, or when the tool set is meant to change while the agent lives. Edit a tool file in `tools/` and save the file, and the next turn uses the new version. Hot reload is also the risk. Anyone who can write to `tools/` can change what the agent can do, mid-conversation. Keep `load_tools_from_directory` for development, and list the tools in code for anything that faces the crowd.

## What It Costs

The folder and the watcher cost nothing; both run locally. The tool adds one specification to the input to Amazon Nova 2 Lite, about 150 tokens, and Amazon Nova 2 Lite bills those tokens on every call after the tool joins. A turn of about 1,000 input and 80 output tokens is 1,000 x $0.30 per million plus 80 x $2.50 per million, about $0.0005. The two turns are about a tenth of a cent in total. See the [Floor 1 cost table](../floor-1.md#what-a-turn-costs).

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Barnaby asked whether I would leave the bench open. I said no. A tool folder anyone can write to is a hangar door left up. He said that is the right instinct and also, regrettably, the same instinct that put a lock on the aquarium's snack cupboard. We shut the door and kept the key. The workbench stays for the shop. The crowd gets the finished kit.

## Encounter Clear

Loot to keep:

- `load_tools_from_directory=True` loads `./tools` at start and watches it
- A saved file in that folder is registered or reloaded without restarting the agent
- A tool file needs the `@tool` decorator from `strands.tools.decorator`, or a `TOOL_SPEC`
- A failed reload is logged and not raised, so a missing tool means a log to read
- Hot reload is for development; list the tools in code when the agent goes in front of the crowd

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[FIELD REPAIR, NO DOWNTIME]**
>
> Reward: You received a [Bronze Box]. Inside: a pegboard hook, a drum stick and a laminated card that reads "Pull the part, not the aircraft".

Back to [Floor 3](../floor-3.md#floor-clear), or on to [Floor 4](../floor-4.md).
