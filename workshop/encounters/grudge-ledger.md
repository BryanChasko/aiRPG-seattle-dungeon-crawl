# Side Passage: The Grudge Ledger in the Cloud (Floor 8 Sidequest)

[Back to Floor 8.3](../floor-8-3.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-8-grudge-ledger/grudge_ledger.py`](../../encounters/floor-8-grudge-ledger/grudge_ledger.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 8.** On the bluffs the System kept its grudges in a folder on a laptop, and a laptop is a thing that gets closed. In Bellevue everything the System owns lives somewhere with an address, so I asked where the grudges had gone. The System said it had moved them to a records office on the twelfth floor, in a room with a lock and a very patient clerk. I asked to see the room. It was a knowledge base with one door and a shelf of small sentences: who stood on whose tail, who lost by how many points, who is rehearsing a reply. Barnaby read the shelf from the doorway. "Sergeant," he said. "That is the most terrifying filing system I have ever seen."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Sidequest: the Grudge Ledger in the Cloud. Every grudge is filed in an Amazon Bedrock knowledge base, indexed, scoped to the party and searchable. When the Accountant walks back onto the floor, I will already know what they have not forgiven. I will not be showing my work."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 8.3](../floor-8-3.md), finished: you know the managed knowledge base commands from its Part 1 and from the Floor 8 page. This sidequest adds a second knowledge base, `grudges`, to the `gameprod` project. The agent runs on your machine |
| you build | a Bedrock knowledge base as a writable memory store, two functions that file a grudge and search the ledger, and a System whose memory manager brings the right grudge up before each model call |
| teaches | [`strands.vended_memory_stores.bedrock_knowledge_base.store`](https://strandsagents.com/docs/api/python/strands.vended_memory_stores.bedrock_knowledge_base.store/): `BedrockKnowledgeBaseStore`, and [`strands.memory.memory_manager`](https://strandsagents.com/docs/api/python/strands.memory.memory_manager/): `MemoryManager` |
| time | about 30 minutes, most of it waiting for a deploy |
| model | Amazon Nova 2 Lite, as on every floor |

The Floor 7 sidequest, The System Holds Grudges, keeps the System's grudges as Markdown files in a folder on your machine, and a memory manager brings the right ones up before a turn. It does not need to be built for this one, and this one shares none of its code. What this one asks is where the grudges should live once the System runs in production, and the answer is the same place as the rules: a managed Amazon Bedrock knowledge base, which survives any laptop, any microVM and any redeploy.

Strands wraps a knowledge base as a memory store, `BedrockKnowledgeBaseStore`. A store can be searched, and when it is writable it can be added to: the store uploads the text to an S3 bucket, ingests that one document into the knowledge base, and attaches metadata to it. A `scope` keeps one party's grudges apart from another's by stamping a `namespace` attribute on every write and filtering on it in every search. A `MemoryManager` then puts the store behind an agent: before each model call it searches the store with the player's latest message and slips the best hits in front of the model, and it registers a `search_memory` and an `add_memory` tool so the model can look things up and file new facts itself. See [Memory](https://strandsagents.com/docs/user-guide/sdk/memory/overview/), [Amazon Bedrock Knowledge Base](https://strandsagents.com/docs/user-guide/sdk/memory/bedrock-knowledge-base/) and [Scope and Namespaces](https://strandsagents.com/docs/user-guide/sdk/memory/bedrock-knowledge-base/#scope-and-namespaces).

How you know it worked: `write` files three grudges and prints their S3 locations; a minute later `ask`, in a new process, prints the grudge that matches the question about Footwork, and the System greets the Accountant with it.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-8-grudge-ledger
```

## Build the Records Office

> <img src="../../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** This sidequest creates AWS resources in your account: an S3 bucket and a managed knowledge base, deployed by the same `gameprod` project as the rest of Floor 8. Both bill by the month, a few cents at most. Delete them at the end, with the commands in [What It Costs](#what-it-costs).

From the project folder, as on the Floor 8 page:

```bash
cd ../../8_agentcore_production/gameprod
export AWS_DEFAULT_REGION=us-west-2
export GRUDGE_BUCKET=gameprod-grudges-$(aws sts get-caller-identity --query Account --output text)
aws s3 mb s3://$GRUDGE_BUCKET
echo "The ledger is open. No grudges are filed yet." | aws s3 cp - s3://$GRUDGE_BUCKET/grudges/00-ledger-open.txt
agentcore add knowledge-base --name grudges --description "Grudges between the party and the opponents" --source s3://$GRUDGE_BUCKET/
agentcore deploy -y
```

The small seed file gives the first ingestion a document to read. `agentcore deploy` creates the knowledge base in a few minutes. Check the knowledge base the way 8.3 did, and copy its id (the ten characters after `knowledge-base/`) when `grudges` shows `Ingestion: COMPLETE`:

```bash
agentcore status
```

Then look up the id of its data source, and export all three:

```bash
export GRUDGE_KB_ID=<the-ten-characters>
export GRUDGE_DATA_SOURCE_ID=$(aws bedrock-agent list-data-sources --knowledge-base-id $GRUDGE_KB_ID --query 'dataSourceSummaries[0].dataSourceId' --output text)
echo $GRUDGE_KB_ID $GRUDGE_DATA_SOURCE_ID $GRUDGE_BUCKET
```

Check: the last line prints a knowledge base id, a data source id and the bucket name. Your credentials need the permissions listed under [Required IAM Permissions](https://strandsagents.com/docs/user-guide/sdk/memory/bedrock-knowledge-base/#required-iam-permissions): `bedrock:Retrieve`, `bedrock:IngestKnowledgeBaseDocuments` and `s3:PutObject` on the bucket. The file gives the store the knowledge base type, so `bedrock:GetKnowledgeBase` is not needed.

If `aws s3 mb` fails with `BucketAlreadyExists`, add a suffix to `GRUDGE_BUCKET` and keep it for the delete commands.

Back to the encounter folder:

```bash
cd ../../encounters/floor-8-grudge-ledger
```

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** One more bucket, one more shelf. I labeled the bucket the way I label gear: what is in it, whose it is, when it gets turned in. Barnaby asked how many grudges the System would keep. I said as many as there were opponents. He said that was not a comfort. I said I knew.

## Step 1: Fetch the Manager and the Store

```python
# TODO: Step 1 - Import MemoryManager from strands.memory and BedrockKnowledgeBaseStore from strands.vended_memory_stores.bedrock_knowledge_base
```

`MemoryManager` sits on an agent and runs its memory stores. `BedrockKnowledgeBaseStore` is the store that talks to a Bedrock knowledge base.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import MemoryManager from strands.memory and BedrockKnowledgeBaseStore from strands.vended_memory_stores.bedrock_knowledge_base
from strands.memory import MemoryManager
from strands.vended_memory_stores.bedrock_knowledge_base import BedrockKnowledgeBaseStore
```

</details>

## Step 2: Open the Ledger

```python
def make_store() -> BedrockKnowledgeBaseStore:
    """The grudges knowledge base as a memory store, writable, with every grudge filed under the party."""
    # TODO: Step 2 - Return a BedrockKnowledgeBaseStore named "grudges", scope "party", writable=True; its config names the MANAGED knowledge base GRUDGE_KB_ID, an S3 data source GRUDGE_DATA_SOURCE_ID and the s3 bucket GRUDGE_BUCKET with prefix "grudges/"
    return None
```

The store takes keyword arguments. `config` says which knowledge base to reach: `knowledge_base_id`, `knowledge_base_type` (`"MANAGED"`, the kind you deployed: saying so skips a `GetKnowledgeBase` call at startup), `data_source_type` (`"S3"`, the kind the CLI created), `data_source_id`, and `s3` with the `bucket` and the `prefix` where writes land. Then the store's own fields: `name`, a `description` the search tool shows the model, `scope`, and `writable=True`. Without `writable=True` the store can be searched but `add` raises an error. See [Data Source Types and Writability](https://strandsagents.com/docs/user-guide/sdk/memory/bedrock-knowledge-base/#data-source-types-and-writability).

<details>
<summary>Show me the code for Step 2</summary>

```python
def make_store() -> BedrockKnowledgeBaseStore:
    """The grudges knowledge base as a memory store, writable, with every grudge filed under the party."""
    # TODO: Step 2 - Return a BedrockKnowledgeBaseStore named "grudges", scope "party", writable=True; its config names the MANAGED knowledge base GRUDGE_KB_ID, an S3 data source GRUDGE_DATA_SOURCE_ID and the s3 bucket GRUDGE_BUCKET with prefix "grudges/"
    return BedrockKnowledgeBaseStore(
        config={
            "knowledge_base_id": os.environ["GRUDGE_KB_ID"],
            "knowledge_base_type": "MANAGED",
            "data_source_type": "S3",
            "data_source_id": os.environ["GRUDGE_DATA_SOURCE_ID"],
            "s3": {"bucket": os.environ["GRUDGE_BUCKET"], "prefix": "grudges/"},
        },
        name="grudges",
        description="Grudges between the party and the opponents they have met",
        scope="party",
        writable=True,
    )
```

Replace the `return None`. The ids come from the environment, as the knowledge base id does in 8.3, and never from the code.

</details>

## Step 3: File a Grudge

```python
def remember(store: BedrockKnowledgeBaseStore, opponent: str, grudge: str):
    """File one grudge in the ledger, with the opponent as metadata."""
    # TODO: Step 3 - Run store.add(...) with asyncio.run: the text is the opponent and the grudge, the metadata is {"opponent": opponent}
    return None
```

`store.add(content, metadata=...)` is a coroutine, so `asyncio.run` runs it. It uploads the text as an object under `grudges/`, writes a small `.metadata.json` file beside it carrying the scope and the metadata, and asks Bedrock to ingest that document. It returns an object whose `document_id` is the S3 location. The `opponent` metadata lets you filter on a name later.

<details>
<summary>Show me the code for Step 3</summary>

```python
def remember(store: BedrockKnowledgeBaseStore, opponent: str, grudge: str):
    """File one grudge in the ledger, with the opponent as metadata."""
    # TODO: Step 3 - Run store.add(...) with asyncio.run: the text is the opponent and the grudge, the metadata is {"opponent": opponent}
    return asyncio.run(store.add(f"{opponent} {grudge}", metadata={"opponent": opponent}))
```

Replace the `return None`.

</details>

## Step 4: Search the Ledger

```python
def recall(store: BedrockKnowledgeBaseStore, question: str):
    """Search the ledger. Each entry has .content and .metadata."""
    # TODO: Step 4 - Run store.search(question) with asyncio.run and return the entries
    return []
```

`store.search(query)` is a coroutine too. It calls the Retrieve API with a managed search configuration and the filter for the store's scope, and returns `MemoryEntry` objects: the text in `.content`, and in `.metadata` the attributes you filed plus `_relevance_score` and `_source_location`.

<details>
<summary>Show me the code for Step 4</summary>

```python
def recall(store: BedrockKnowledgeBaseStore, question: str):
    """Search the ledger. Each entry has .content and .metadata."""
    # TODO: Step 4 - Run store.search(question) with asyncio.run and return the entries
    return asyncio.run(store.search(question))
```

Replace the `return []`.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** I filed the first one myself, standing at the shelf: the Pitch-Deck Founder, Shelly's tail, the Ship Canal locks. The file came back with a location and nothing else. No receipt, no stamp. Barnaby said that was how records offices work. You do not get a receipt. You get a shelf.

## Step 5: Give the System a Memory

```python
        # TODO: Step 5 - Give the agent memory_manager=MemoryManager(stores=[store], add_tool_config=True)
```

`make_system` is given: it builds the System with a prompt that tells it to work a matching grudge into its line. The TODO sits inside the `Agent(...)` call. The agent's `memory_manager` parameter takes a `MemoryManager` built on a list of stores. `add_tool_config=True` registers the `add_memory` tool next to the `search_memory` tool that every manager has: the model can then file a new grudge during a turn, when it decides one has been earned. Without it the memory is read-only for the model, and you stay in charge of every write.

<details>
<summary>Show me the code for Step 5</summary>

```python
        # TODO: Step 5 - Give the agent memory_manager=MemoryManager(stores=[store], add_tool_config=True)
        memory_manager=MemoryManager(stores=[store], add_tool_config=True),
```

</details>

## Open the Ledger and Come Back

File the grudges. This is the first process:

```bash
python grudge_ledger.py write
```

Check: one line per grudge with an S3 location (example):

```
filed: the Pitch-Deck Founder: s3://gameprod-grudges-123456789012/grudges/5c1e0b0e-0000-0000-0000-000000000000.txt
filed: the Quarterly Close Accountant: s3://gameprod-grudges-123456789012/grudges/...
filed: the Bonus-Season Investment Banker: s3://gameprod-grudges-123456789012/grudges/...
Give the knowledge base a minute, then: python grudge_ledger.py ask
```

Wait a minute, then run a second, separate process:

```bash
python grudge_ledger.py ask
```

Check: the search finds the Accountant's grudge, and the System uses it. The wording and the score will differ:

```
remembered: the Quarterly Close Accountant lost a Footwork round to Cordula by four and has not forgotten the margin (score 0.71)

SYSTEM: The Quarterly Close Accountant returns to the floor, and I see a certain margin of four is still on the books. Do be careful with the footwork, Crawlers.
```

The second process has nothing from the first except the knowledge base: that is the point.

| you see | it means | fix |
|---|---|---|
| `KeyError: 'GRUDGE_KB_ID'` (or `GRUDGE_DATA_SOURCE_ID`, `GRUDGE_BUCKET`) | the variable is not set in this terminal | export all three, as above |
| `AttributeError: 'NoneType' object has no attribute 'document_id'` | `remember` returns `None` | Step 3 |
| `ValueError: ... store is not writable` | the store was built without `writable=True` | Step 2 |
| `ValidationException` about `vectorSearchConfiguration` | the store thinks the knowledge base is self-managed | give the config `"knowledge_base_type": "MANAGED"` |
| `ask` prints nothing under `remembered:` | the document is not indexed yet, or `write` did not finish | wait another minute and run `ask` again; if it stays empty, `agentcore run ingest` from `gameprod` indexes the bucket again |
| the System answers with no grudge | the memory manager is not on the agent | Step 5 |
| `AccessDeniedException` on `IngestKnowledgeBaseDocuments`, `Retrieve` or `PutObject` | your credentials lack one of the permissions listed above | add it and run again |
| `ExpiredToken` | the model call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws) |

## Ledger or Folder?

A folder of Markdown files is the right ledger on your machine: nothing to deploy, nothing to pay for, and you can open every grudge in an editor. The knowledge base is the right ledger when the System runs in AgentCore: it outlives any microVM, any runtime session and any redeploy, every session reads the same one, and a search finds a grudge by meaning, not by matching words. The price is a deploy, an IAM policy and a bill by the gigabyte. The memory manager does not change either way: swap the store and the agent code stays as it is.

## What It Costs

The same rates as the `rules` knowledge base ([What Floor 8 Costs](../floor-8.md#what-floor-8-costs), from the [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/), Knowledge Bases): $5.00 per GB of raw data a month and $1.00 per 1,000 Retrieve calls, with parsing and embeddings included. Three grudges are about 300 bytes: 0.0000003 GB x $5.00 = $0.0000015 a month. Each `ask` makes one Retrieve call for `recall` and one before the System's model call, so two: $0.002. The S3 bucket holds a handful of tiny objects, under a cent ([Amazon S3 pricing](https://aws.amazon.com/s3/pricing/)).

Nova 2 Lite for the System's turn is one model call of about 600 input tokens and 60 output tokens (an estimate): 600 x $0.30 / 1,000,000 + 60 x $2.50 / 1,000,000 = $0.00018 + $0.00015, about a thirtieth of a cent ([Floor 1](../floor-1.md#what-a-turn-costs)). A model that uses `add_memory` adds one ingest per grudge and nothing else.

Delete what you built, from the `gameprod` folder. The knowledge base is part of the project, so remove it from the project and deploy, then delete the bucket by hand, as the [Cleanup](../cleanup.md#step-3-delete-the-rules-bucket) page does for the rules bucket:

```bash
cd ../../8_agentcore_production/gameprod
agentcore remove knowledge-base --name grudges -y
agentcore deploy -y
aws s3 rb s3://$GRUDGE_BUCKET --force
unset GRUDGE_KB_ID GRUDGE_DATA_SOURCE_ID GRUDGE_BUCKET
```

Check: `agentcore status` no longer lists `grudges`, and the bucket is gone:

```bash
agentcore status
aws s3 ls s3://gameprod-grudges-$(aws sts get-caller-identity --query Account --output text)
```

The second command should end with `NoSuchBucket`. If you skip this and later follow the Cleanup page, its `agentcore remove all -y` takes the `grudges` knowledge base too, but only the bucket step above removes the grudges bucket.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The Accountant walked back onto the floor and the System said, before anyone had asked, that a margin of four is still on the books. The Accountant went pale in a way that suggested they had been losing sleep over exactly that number. Barnaby leaned over. "It never forgets a point, Sergeant." I said I knew a few people like that. He asked if I meant the System. I said no. I meant me.

## Encounter Clear

Loot you're keeping:

- `BedrockKnowledgeBaseStore` makes a Bedrock knowledge base a memory store, searchable and, with `writable=True`, writable through S3 and direct ingestion
- A `scope` keeps one party's memories apart, and metadata files each one under a name
- A `MemoryManager` searches the store before each model call and gives the model `search_memory` and `add_memory` tools
- The memory manager stays the same whether the store is a folder or a knowledge base

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[THE CLOUD NEVER FORGETS]**
>
> Reward: You received a [Gold Box]. Inside: a records office with one door, a shelf of small sentences, and a standing invitation from the Accountant to discuss the margin.

Back to [Floor 8.3](../floor-8-3.md#floor-clear), or on to [Floor 8.4](../floor-8-4.md).
