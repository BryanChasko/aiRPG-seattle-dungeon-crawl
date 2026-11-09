# Side Passage: The Ferry Manifest (Floor 8 Sidequest)

[Back to Floor 8.3](../floor-8-3.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-8-ferry-manifest/ferry_manifest.py`](../../encounters/floor-8-ferry-manifest/ferry_manifest.py), [`encounters/floor-8-ferry-manifest/rules-agent-manifest.json`](../../encounters/floor-8-ferry-manifest/rules-agent-manifest.json), [`encounters/floor-8-ferry-manifest/rules_tool.py`](../../encounters/floor-8-ferry-manifest/rules_tool.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 13, MONDAY, JUNE 29, SIDE PASSAGE OFF FLOOR 8.** The last ferry across the Narrows leaves at 2140, and the ferry does not leave until the deck officer has a manifest in hand. Who is aboard, how many, what they carry. Anything not on the list stays on the dock, however loudly the passenger argues. A clerk in a hi-vis vest took my name, Barnaby's, Shelly's and Chonks's, checked each against a clipboard, and looked at the Rules Agent standing in the queue. "And this one?" <img src="../../../art/images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** "The Rules Agent is assembled from parts, on the spot, by whoever builds it."
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Sidequest: the Ferry Manifest. The Rules Agent will be assembled from a JSON file: a name, a model, a prompt, a list of tools. Four lines. I did not think a rules lawyer could fit on a form. I stand corrected, and I have the form."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 8.3](../floor-8-3.md), finished: the `rules` knowledge base is deployed and the `rules` ingestion shows `COMPLETE`. The agent built here runs on the local machine and does not touch the runtime |
| builds | the Rules Agent of 8.3 from a configuration file, and a check that refuses a manifest that pins any model id but Amazon Nova 2 Lite |
| teaches | [`strands.experimental.agent_config`](https://strandsagents.com/docs/api/python/strands.experimental.agent_config/): `config_to_agent` |
| time | about 15 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

In 8.3 the Rules Agent is Python: a `create_agent` function with a model, a name, a prompt and a tool. `config_to_agent` builds the same kind of agent from a configuration, which is the path of a JSON file, or a dictionary. The file has four keys and no others: `name`, `model`, `prompt` and `tools`. A key the file schema does not know is an error, not a shrug. The `tools` are loaded by what the strings say: a path to a Python file, or a module name. See [Agent Configuration](https://strandsagents.com/docs/user-guide/sdk/experimental/agent-config/#file-configuration), [Supported Keys](https://strandsagents.com/docs/user-guide/sdk/experimental/agent-config/#supported-keys) and [Tool Loading](https://strandsagents.com/docs/user-guide/sdk/experimental/agent-config/#tool-loading). `config_to_agent` is experimental.

The encounter folder holds the manifest: [`rules-agent-manifest.json`](../../encounters/floor-8-ferry-manifest/rules-agent-manifest.json). It names the agent `Rules Agent`, pins `us.amazon.nova-2-lite-v1:0`, carries the prompt of 8.3 and lists one tool, `rules_tool.py`. The tool is [`rules_tool.py`](../../encounters/floor-8-ferry-manifest/rules_tool.py), provided: the `query_rules` of 8.3 in a file of its own, so the manifest can point at it. `query_rules` searches the managed knowledge base, reading the id from `KNOWLEDGE_BASE_RULES_ID` when it runs.

Success check: the script prints the manifest, then the Rules Agent built from the manifest, with `query_rules` as its only tool, then the answer to a rules question with the section name.

Open a terminal in the encounter folder and stay there: the manifest names its tool by a path relative to the folder where `ferry_manifest.py` runs.

```bash
cd aiRPG-seattle-dungeon-crawl/dungeon/encounters/floor-8-ferry-manifest
```

Find the knowledge base id the way 8.3, Part 1 did (the ten characters after `knowledge-base/` in `agentcore status`, run from `gameprod`) and export the id and the region:

```bash
export AWS_DEFAULT_REGION=us-west-2
export KNOWLEDGE_BASE_RULES_ID=<your-knowledge-base-id>
```

The AWS credentials need `bedrock:Retrieve` on the knowledge base.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Four lines on a form. Name, model, prompt, tools. I held the file up to the deck officer's lamp and read it the way I read a manifest: line by line, nothing implied. It said the model and it said which one. Nobody was going to wake up on the Narrows with a different crew than the one on the list. That is the entire reason you write a manifest.

## Step 1: Fetch the Builder

```python
# TODO: Step 1 - Import config_to_agent from strands.experimental.agent_config
```

`config_to_agent` lives in `strands.experimental.agent_config`.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import config_to_agent from strands.experimental.agent_config
from strands.experimental.agent_config import config_to_agent
```

</details>

## Step 2: Check the Manifest

```python
def check_manifest(path: Path) -> dict:
    """Read the manifest and refuse to sail unless it pins Nova 2 Lite."""
    # TODO: Step 2 - Load the JSON from path and raise ValueError unless its "model" is NOVA; return the manifest
    return {}
```

`config_to_agent` validates the shape of the file, but not the choice of Amazon Nova 2 Lite: any model id is a valid string. This crawl runs one model, so the check is code to write. Read the file with `json.loads`, compare the manifest `"model"` with `NOVA` (already defined in the file) and raise a `ValueError` that names the model id found.

<details>
<summary>Show me the code for Step 2</summary>

```python
def check_manifest(path: Path) -> dict:
    """Read the manifest and refuse to sail unless it pins Nova 2 Lite."""
    # TODO: Step 2 - Load the JSON from path and raise ValueError unless its "model" is NOVA; return the manifest
    manifest = json.loads(path.read_text())
    if manifest.get("model") != NOVA:
        raise ValueError(f"{path.name} pins {manifest.get('model')!r}; this crawl runs {NOVA}")
    return manifest
```

Replace the `return {}`. `check_manifest` refuses a manifest with no `model` key at all too: without one, the agent would fall back on the SDK default, and a manifest that leaves out the model id does not pin it.

</details>

## Step 3: Build the Agent from the File

```python
def build_rules_agent(path: Path = MANIFEST):
    """The Rules Agent, built from the manifest. The manifest names its tool by a relative path: run from this folder."""
    check_manifest(path)
    # TODO: Step 3 - Return config_to_agent(str(path)) with callback_handler=None passed as a keyword argument
    return None
```

`config_to_agent(path)` takes the file path as a string and returns an `Agent`. Each key in the file becomes an `Agent(...)` parameter: `name`, `model`, `prompt` as `system_prompt`, and `tools`. Extra keyword arguments go straight to the `Agent` constructor and win over the file, which is how the code adds what a file cannot hold. Step 3 passes `callback_handler=None`, the same setting `create_agent` has in 8.3, so the Rules Agent does not stream the answer to the terminal.

<details>
<summary>Show me the code for Step 3</summary>

```python
def build_rules_agent(path: Path = MANIFEST):
    """The Rules Agent, built from the manifest. The manifest names its tool by a relative path: run from this folder."""
    check_manifest(path)
    # TODO: Step 3 - Return config_to_agent(str(path)) with callback_handler=None passed as a keyword argument
    return config_to_agent(str(path), callback_handler=None)
```

Replace the `return None`.

</details>

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The second deck officer ran a finger down the form, stopped at the model line and read it aloud, as deck officers do. Then the second deck officer tried to add a fifth line. A description, for the passenger card. The form would not take it. Unknown field, rejected at the gate. I admired the form. <img src="../../../art/images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** "The price of a short form. The A2A agent card of 8.3 is why the Rules Agent still has a code version."

## Sail

```bash
python ferry_manifest.py
```

Check: the manifest, the agent that boarded, and an answer that names a handbook section. The wording of the answer will differ:

```
FERRY MANIFEST: Rules Agent aboard, model us.amazon.nova-2-lite-v1:0, tools ['rules_tool.py']
  boarded as Rules Agent with tools ['query_rules']
  How does the Final Beat work?
  Both sides roll 1d20 plus their Dexterity modifier, and the total closest to 20 without going over wins. Final Beat section, as I have said four thousand times.
```

| you see | cause | fix |
|---|---|---|
| `ImportError` or `NameError: name 'config_to_agent' is not defined` | Step 1 is missing | add the import |
| `AttributeError: 'NoneType' object has no attribute 'name'` | `build_rules_agent` still returns `None` | Step 3 |
| `ValueError: rules-agent-manifest.json pins ...` | the manifest pins another model id | put `us.amazon.nova-2-lite-v1:0` back in the `model` key |
| `ValueError: Configuration validation error at root: Additional properties are not allowed` | the manifest has a key the schema does not know, for example `system_prompt` instead of `prompt` | use only `name`, `model`, `prompt` and `tools` |
| the tool is not found or `tools []` | the script ran from another folder | `cd` to the folder; the manifest's `rules_tool.py` is relative to the folder where the script runs |
| `KeyError: 'KNOWLEDGE_BASE_RULES_ID'` | `KNOWLEDGE_BASE_RULES_ID` is not set in this terminal | export `KNOWLEDGE_BASE_RULES_ID`, as above |
| `ResourceNotFoundException` or an answer with no section name | the id is not the `rules` knowledge base id, or the `rules` ingestion is not complete | `agentcore status` in `gameprod`: copy the ten characters after `knowledge-base/`, and wait for `Ingestion: COMPLETE` |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call or the knowledge base search failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Manifest or Code?

A file is easy to read, review and change without touching Python, and a manifest fits a fleet of agents that differ in a prompt and a tool list. A manifest holds four keys and no more: it has no place for a session manager, a callback handler, a description or a tool that needs a constructor argument. Add those in code after the call, or as keyword arguments, as Step 3 does. The deployed Rules Agent of 8.3 stays Python because it serves an A2A agent card with a name and a description, and a `create_agent` factory that builds one agent per conversation. The manifest is the right shape for an agent run locally, not an agent served over A2A.

## What It Costs

No new AWS resource. Each question is two Amazon Nova 2 Lite calls of a short prompt (about 1,000 input tokens and 150 output tokens in all, an estimate): 1,000 x $0.30 / 1,000,000 + 150 x $2.50 / 1,000,000 = $0.0003 + $0.000375, under a tenth of a cent ([Floor 1](../floor-1.md#what-a-turn-costs)), and one Retrieve call on the managed knowledge base at $1.00 per 1,000 calls, a tenth of a cent ([Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/), Knowledge Bases; the same rate as [What Floor 8 Costs](../floor-8.md#what-floor-8-costs)). The `rules` knowledge base and its bucket are the ones 8.3 created, and the [Cleanup](../cleanup.md) page removes them. This page creates nothing to delete. Clear the variable:

```bash
unset KNOWLEDGE_BASE_RULES_ID
```

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The Rules Agent sailed on the 2140, name on the list, model on the list, one tool in its hand. At the Narrows the clerk waved the Rules Agent through without a second look. Shelly dug in on the car deck. Chonks stuck himself to the manifest. <img src="../../../art/images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** "The form has not changed. That is the best part of it."

## Encounter Clear

Loot kept:

- `config_to_agent` builds an `Agent` from a JSON file or a dictionary with four keys: `name`, `model`, `prompt`, `tools`
- Keyword arguments to `config_to_agent` reach the `Agent` constructor and win over the file
- A manifest is validated for its shape, and the model id a manifest pins is checked in code
- A manifest suits an agent run locally, and code suits an agent served over A2A

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[IT'S ON THE LIST]**
>
> Reward: You received a [Bronze Box]. Inside: a clipboard, a hi-vis vest two sizes too big for a geoduck, and a boarding pass for a ferry that leaves on time.

Back to [Floor 8.3](../floor-8-3.md#floor-clear), or on to [The Grudge Ledger in the Cloud](grudge-ledger.md).
