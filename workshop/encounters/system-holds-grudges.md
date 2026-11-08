# Side Passage: The System Holds Grudges (Floor 7 Sidequest)

[Back to Floor 7](../floor-7.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-7-system-holds-grudges/system_holds_grudges.py`](../../encounters/floor-7-system-holds-grudges/system_holds_grudges.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 7.** The Safe Room on the bluffs takes the conversation and gives back a blank page. I know the drill from the Reserve: when the radio net goes down, I do not trust anyone's memory, I trust the logbook. So I wanted a logbook. Not the whole transcript, which is a pile. Just the entries: who became a friend, who owes us, who is not forgiven. Pat the accountant, for one, who shook my hand on the Pier 59 ferry deck and handed me a Ferry Token. And the Pitch-Deck Founder, who stood on Shelly's tail. Barnaby wants that grudge in ink.
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "The System does not forget, Crawlers. The System is merely rate-limited by the Safe Room. Hand me a clerk and a folder and I will hold a grudge for as long as the folder lasts. Keep the folder somewhere dry."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 7](../floor-7.md), finished. This encounter uses the plain Strands Agents SDK `Agent` instead of the harness, because the memory manager is easier to see when nothing else is wrapped around the memory manager |
| build | a memory manager over a folder of Markdown files, filled after every turn by a clerk, and a second campaign that remembers the first |
| teaches | [`strands.memory.memory_manager`](https://strandsagents.com/docs/api/python/strands.memory.memory_manager/), [`strands.memory.extraction.triggers`](https://strandsagents.com/docs/api/python/strands.memory.extraction.triggers/), [`strands.memory.extraction.model_extractor`](https://strandsagents.com/docs/api/python/strands.memory.extraction.model_extractor/), [`strands.vended_memory_stores.file_memory_store.store`](https://strandsagents.com/docs/api/python/strands.vended_memory_stores.file_memory_store.store/) |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor; the clerk that writes the facts is a second Nova 2 Lite call |

A session, from [Save Points](save-points.md), keeps the whole conversation. Memory keeps smaller, longer-lived records: facts in a store that any later agent can search. A `MemoryManager` sits on an agent and does two jobs. After a turn, the `MemoryManager` hands the new messages to each store's extractor, and a `ModelExtractor` asks Amazon Nova 2 Lite to read the new messages and write down only the durable facts. Before a turn, it searches the stores with the latest message and puts the best matches in front of Amazon Nova 2 Lite, inside a `<memory>` block that never lands in the saved history. See [Memory](https://strandsagents.com/docs/user-guide/sdk/memory/overview/) and [Managing Memory](https://strandsagents.com/docs/user-guide/sdk/memory/managing-memory/).

Three pieces, then, and each is a step: the extractor (what counts as a fact), the store (where facts live), and the manager (joins the extractor to the store). The store here is the [`FileMemoryStore`](https://strandsagents.com/docs/user-guide/sdk/memory/file-memory-store/): one Markdown file per topic, found again by matching words from the question against the file name and the file body. The extraction trigger says when the clerk works. `InvocationTrigger` runs it after every turn, the most thorough choice and one extra Amazon Nova 2 Lite call per turn; `IntervalTrigger(turns=5)` runs the clerk every fifth turn instead.

Check that it worked: campaign one ends with a ledger of Markdown files, one headed for Pat and one for the Pitch-Deck Founder, and none for the question about the Final Beat. Then a new System with zero messages in its history answers from the ledger.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-7-system-holds-grudges
```

## Step 1: Import the Pieces

```python
# TODO: Step 1 - Import MemoryManager from strands.memory, InvocationTrigger from strands.memory.extraction.triggers,
#                ModelExtractor from strands.memory.extraction.model_extractor and FileMemoryStore from
#                strands.vended_memory_stores.file_memory_store.store
```

Four imports, one per piece, from four modules. `Agent`, `BedrockModel` and `LocalFileStorage` are already imported.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import MemoryManager from strands.memory, InvocationTrigger from strands.memory.extraction.triggers,
#                ModelExtractor from strands.memory.extraction.model_extractor and FileMemoryStore from
#                strands.vended_memory_stores.file_memory_store.store
from strands.memory import MemoryManager
from strands.memory.extraction.triggers import InvocationTrigger
from strands.memory.extraction.model_extractor import ModelExtractor
from strands.vended_memory_stores.file_memory_store.store import FileMemoryStore
```

</details>

## Step 2: Hire the Clerk

```python
# TODO: Step 2 - Return a ModelExtractor that uses a BedrockModel with model_id "us.amazon.nova-2-lite-v1:0" and EXTRACT_PROMPT as its system_prompt
```

`ModelExtractor(model=..., system_prompt=...)` is an Amazon Nova 2 Lite call with one job: read a transcript, return the facts. The clerk uses whichever model the code names. Leave the model out and the clerk borrows the System agent's model, also Amazon Nova 2 Lite here, but a clerk with a model named in the code is a clerk that can be swapped alone. `BedrockModel(model_id=...)` configures a model object when a string is not enough. The prompt is `EXTRACT_PROMPT`: it says what a fact is (a friend, a debt, a grudge) and what to skip (questions, small talk). The extractor adds its own output rule after `EXTRACT_PROMPT`, so no prompt can break the format.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Every unit has a clerk. Mine reads the whole shift log and writes down three lines. The skill is what the clerk leaves out. I told this one: friends, debts, grudges. Questions are not entries. Barnaby said that briefing was the first time anyone had made a filing system sound like a chain of command.

<details>
<summary>Show me the code for Step 2</summary>

```python
def make_extractor():
    # TODO: Step 2 - Return a ModelExtractor that uses a BedrockModel with model_id "us.amazon.nova-2-lite-v1:0" and EXTRACT_PROMPT as its system_prompt
    return ModelExtractor(
        model=BedrockModel(model_id="us.amazon.nova-2-lite-v1:0"),  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=EXTRACT_PROMPT,
    )
```

Replace `return None`. The heading rule is in `EXTRACT_PROMPT`: the store names a file after the first line of each fact, so "# Pat the accountant" becomes `pat-the-accountant.md`.

</details>

## Step 3: Open the Ledger

```python
# TODO: Step 3 - Return a FileMemoryStore named "grudges" on LocalFileStorage(str(MEMORY_DIR)), with extraction set to an InvocationTrigger and the extractor
```

`FileMemoryStore(name=..., storage=..., extraction=...)`. The name tells the store apart from other stores; the storage is where the files go (a [`LocalFileStorage`](https://strandsagents.com/docs/user-guide/sdk/storage/) on a folder; the store adds `memory/grudges/` under that folder); `extraction` is a dictionary with the `trigger` and the `extractor`. Leave `extraction` out and the store only holds facts written by hand. Pass the extractor from Step 2, which names Amazon Nova 2 Lite.

<details>
<summary>Show me the code for Step 3</summary>

```python
def make_store(extractor):
    # TODO: Step 3 - Return a FileMemoryStore named "grudges" on LocalFileStorage(str(MEMORY_DIR)), with extraction set to an InvocationTrigger and the extractor
    return FileMemoryStore(
        name="grudges",
        storage=LocalFileStorage(str(MEMORY_DIR)),
        extraction={"trigger": InvocationTrigger(), "extractor": extractor},
    )
```

</details>

## Step 4: Give the System a Manager

```python
# TODO: Step 4 - Return a MemoryManager over the one store
```

`MemoryManager(stores=[store])`. Two defaults do the rest. `injection=True` searches the store before every Amazon Nova 2 Lite call, using the latest user message as the query, and prepends what the search finds. `search_tool_config=True` also gives the agent a `search_memory` tool, so the agent can search memory on purpose. Pass the manager to the agent as `memory_manager=`, which `make_system` already does.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Second campaign, same Safe Room, blank System. I asked which accountant I could trust. The System said Pat, and the ferry deck, and the Ferry Token, in two sentences, from a file it had never seen in this life. Then I asked about the Founder and the System went quiet in a way I can only call pleased. The System holds a grudge better than any sergeant I served under.

<details>
<summary>Show me the code for Step 4</summary>

```python
def make_manager(store):
    # TODO: Step 4 - Return a MemoryManager over the one store
    return MemoryManager(stores=[store])
```

A trap: the store finds files by matching the words in the question against file names and text. "Which accountant can I trust?" finds `pat-the-accountant.md` because "accountant" is in both. A question phrased in other words ("who in finance is my friend?") can miss `pat-the-accountant.md`. Keyword matching is the default; [Keyword versus Vector](keyword-versus-vector.md) covers that trade-off.

</details>

## Run the Campaigns

```bash
python system_holds_grudges.py
```

Check: three turns, the ledger, then the second campaign. This is an example; Amazon Nova 2 Lite words the answers and facts differently on each run:

```
CAMPAIGN ONE: three turns, and a clerk reading over the System's shoulder
  ...
  the ledger, 2 file(s) in /tmp/system-holds-grudges
  --- pat-the-accountant.md
      # Pat the accountant
      Pat is a friend of Cordula. Pat gave Cordula a Ferry Token on the Pier 59 ferry deck.
  --- pitch-deck-founder.md
      # Pitch-Deck Founder
      Barnaby will not forgive the Pitch-Deck Founder for standing on Shelly's tail at the Ballard Locks.

A NIGHT IN THE SAFE ROOM: the conversation is gone, the ledger is not
  messages in the new System's head: 0
  the System: Pat the accountant is your friend, Crawler. Barnaby is still angry at the Pitch-Deck Founder.
```

| output | cause | fix |
|---|---|---|
| `TypeError: 'NoneType' object is not callable` or `AttributeError` on `None` | a `make_` function still returns `None` | Steps 2, 3 and 4 |
| `the ledger, 0 file(s)` | the clerk wrote nothing: no trigger, or Amazon Nova 2 Lite returned no facts | check `extraction={"trigger": ..., "extractor": ...}` in Step 3, then run it again |
| a file for the Final Beat question | the clerk kept a question | tighten `EXTRACT_PROMPT`; the clerk is an Amazon Nova 2 Lite call, so it sometimes ignores the prompt |
| the second campaign says the System has lost it | the store found no file for the words in the question | read the ledger's file names; ask with a word that appears in one file name |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

The files stay in `/tmp/system-holds-grudges/memory/grudges/` after the run. Open one in an editor. A readable memory is a fixable memory.

## Memory or Session?

The Floor 7 harness gives the Narrator both, and the two answer different questions. A session, as in [Save Points](save-points.md), keeps the conversation itself so the same agent can pick up where it stopped. Memory keeps what was learned from conversations, so a different agent, in a different campaign, can use those facts. [Floor 7](../floor-7.md) buys both pre-assembled; this encounter builds the memory half by hand: the extractor, the trigger, the store and the manager.

## What It Costs

Every turn is two Nova 2 Lite calls: the System's answer, and the clerk's read of the transcript. Campaign one is three turns, so six calls; campaign two is one more turn, so two more, plus a store lookup that costs nothing. At about 1,000 input tokens and 150 output tokens a call, eight calls are 8,000 input tokens x $0.30 per million = $0.0024 and 1,200 output tokens x $2.50 per million = $0.0030, so about half a cent a run. `IntervalTrigger(turns=5)` would run the clerk once every five turns, which cuts the clerk's share of a long campaign by four fifths. Rates and the worked turn are on [Floor 1](../floor-1.md#what-a-turn-costs). The ledger itself is files on the local disk.

## Encounter Clear

Loot to keep:

- A `MemoryManager` looks facts up before a turn and has facts written down after the turn
- A `ModelExtractor` is a model call with a prompt for what counts as a fact, and here the clerk's model is Amazon Nova 2 Lite
- An extraction trigger decides when the clerk works: every turn with `InvocationTrigger`, every few with `IntervalTrigger`
- A `FileMemoryStore` keeps one Markdown file per topic, where you can read it
- Memory is not a session: a session keeps what was said, memory keeps what was learned

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[THE LEDGER NEVER LIES]**
>
> Reward: The party received a [Silver Box]. Inside: one folder of Markdown, a clerk with strict opinions about small talk, and a list of names the Pitch-Deck Founder would prefer the party lost.

Back to [Floor 7](../floor-7.md#floor-clear), or on to [Save Points](save-points.md).
