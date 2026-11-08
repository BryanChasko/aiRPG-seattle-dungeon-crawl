# Side Passage: Save Points (Floor 7 Sidequest)

[Back to Floor 7](../floor-7.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-7-save-points/save_points.py`](../../encounters/floor-7-save-points/save_points.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 7.** Under the madrones on the bluffs there were three lockers, bolted to the rock, each with a different lock. A steel one with a folder inside, a glass one that held a single sealed jar, and a third that Barnaby said was not on the bluffs at all, only its key was. I asked what they were for. The System said save points, and for once it did not make a joke. I put one fact in each: the code word for the ferry gate. Then I walked away, came back as a new agent with no memory, and opened every locker. I check every exit before I need one.
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Three lockers, Crawlers. The folder, the jar and the one in the cloud. Each keeps your progress until the lights go out. One of them charges rent. I will let you work out which."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 7](../floor-7.md), finished. This encounter uses the plain Strands Agents SDK `Agent` instead of the harness, so the session manager is the only thing between you and the model |
| you build | the same save point three ways, and a player that comes back from each of them |
| teaches | [`strands.session.file_session_manager`](https://strandsagents.com/docs/api/python/strands.session.file_session_manager/), [`strands.session.snapshot_session_manager`](https://strandsagents.com/docs/api/python/strands.session.snapshot_session_manager/), [`strands.session.s3_session_manager`](https://strandsagents.com/docs/api/python/strands.session.s3_session_manager/) |
| time | about 20 minutes; the S3 part is optional and adds about 10 |
| model | Amazon Nova 2 Lite, as on every floor |

A session manager saves an agent as it talks and loads it again when a new agent starts with the same session id and the same agent id. You give the agent a `session_manager=`; the agent does the rest. All three managers here do that job. They differ in where the bytes go and in what else they give you. See [Session Management](https://strandsagents.com/docs/user-guide/sdk/agents/session-management/).

| manager | where it saves | shape | extra |
|---|---|---|---|
| `FileSessionManager` | a folder on your disk | one JSON file per message | nothing to set up |
| `SnapshotSessionManager` | any Strands `Storage`, here a local folder | the whole agent as one blob | numbered checkpoints you can travel back to |
| `S3SessionManager` | an Amazon S3 bucket | one object per message, the file layout | survives the machine; needs a bucket |

The flow for each is the same, and `play` is given: tell the System a secret, build a second agent on the same save point, and ask for the secret back. The second agent is restored while it is built, with no model call, and the script prints how many messages it already holds.

How you know it worked: for each manager, the second agent holds a few messages before you ask it anything, and answers `Heron`. The snapshot run then pins a checkpoint, adds a turn, and goes back.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-7-save-points
```

## Step 1: Import the Three Managers

```python
# TODO: Step 1 - Import FileSessionManager from strands.session.file_session_manager, SnapshotSessionManager from
#                strands.session.snapshot_session_manager and S3SessionManager from strands.session.s3_session_manager
```

One module per manager, named for the manager.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import FileSessionManager from strands.session.file_session_manager, SnapshotSessionManager from
#                strands.session.snapshot_session_manager and S3SessionManager from strands.session.s3_session_manager
from strands.session.file_session_manager import FileSessionManager
from strands.session.snapshot_session_manager import SnapshotSessionManager
from strands.session.s3_session_manager import S3SessionManager
```

</details>

## Step 2: The Folder

```python
# TODO: Step 2 - Return a FileSessionManager with session_id "bluffs-file" and storage_dir str(SAVE_DIR / "file")
```

`FileSessionManager(session_id=..., storage_dir=...)`. The session id names the save point; the folder is where the JSON files land. Leave `storage_dir` out and it uses a private folder under your home directory, which is the right choice for a project and the wrong one for a workshop you want to clean up.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The steel locker. I opened it and the whole shift was in there, one sheet per message, in order. You can read a folder. You can copy it, diff it, hand it to somebody. I kept it as the baseline.

<details>
<summary>Show me the code for Step 2</summary>

```python
def file_save():
    # TODO: Step 2 - Return a FileSessionManager with session_id "bluffs-file" and storage_dir str(SAVE_DIR / "file")
    return FileSessionManager(session_id="bluffs-file", storage_dir=str(SAVE_DIR / "file"))
```

Replace the `return None`. The trap: the session id and the agent id together find the save point. `make_player` gives the agent a fixed `agent_id="cordula"`, so a second agent finds the first one's messages. Without a fixed agent id, each run would create a new one and restore nothing.

</details>

## Step 3: The Jar

```python
# TODO: Step 3 - Return a SnapshotSessionManager with session_id "bluffs-snapshot" and storage LocalFileStorage(str(SAVE_DIR / "snapshot"))
```

`SnapshotSessionManager(session_id=..., storage=...)`. It saves the whole agent in one blob after every turn, as `snapshot_latest`, and it writes through a Strands `Storage`, the same `LocalFileStorage` used by [Keyword versus Vector](keyword-versus-vector.md). Swap the storage and the same manager saves somewhere else.

The extra is checkpoints. `await manager.save_snapshot(agent, is_latest=False)` writes a numbered snapshot that never gets overwritten and returns its id; `await manager.restore_snapshot(agent, snapshot_id=...)` puts the agent back the way it was; `await manager.list_snapshot_ids(agent)` lists them. `time_travel` in the file is given and does exactly this, around one extra turn. Where the file manager saves a history, the snapshot manager saves moments.

<details>
<summary>Show me the code for Step 3</summary>

```python
def snapshot_save():
    # TODO: Step 3 - Return a SnapshotSessionManager with session_id "bluffs-snapshot" and storage LocalFileStorage(str(SAVE_DIR / "snapshot"))
    return SnapshotSessionManager(session_id="bluffs-snapshot", storage=LocalFileStorage(str(SAVE_DIR / "snapshot")))
```

Replace the `return None`. These calls are coroutines, which is why `time_travel` runs them with `asyncio.run`.

</details>

## Step 4: The Locker in the Cloud (Optional)

```python
# TODO: Step 4 - Return an S3SessionManager with session_id "bluffs-s3", the bucket, prefix "save-points/" and region_name REGION
```

`S3SessionManager(session_id=..., bucket=..., prefix=..., region_name=...)`. It saves the same layout as the folder, one object per message, under the prefix in your bucket. It reads your normal credentials the way every other call in this workshop does ([Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws)).

The script only runs this part when the environment variable `SAVE_POINTS_BUCKET` is set. Without it the script prints that the S3 part was skipped and you lose nothing: Steps 2 and 3 do not need a bucket, and Step 4 is a single call that you can write and leave. If you want to run it, create the bucket first.

Create the bucket. The name must be unique across all accounts, so put your account number in it:

```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws s3api create-bucket --bucket "save-points-$ACCOUNT" --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
export SAVE_POINTS_BUCKET="save-points-$ACCOUNT"
```

When you are done, delete the objects and then the bucket:

```bash
aws s3 rm "s3://save-points-$ACCOUNT" --recursive
aws s3api delete-bucket --bucket "save-points-$ACCOUNT" --region us-west-2
```

A bucket must be empty before it can be deleted, which is why the objects go first. The [Cleanup](../cleanup.md) page covers the Floor 8 resources; this bucket is yours alone, so remove it here.

<details>
<summary>Show me the code for Step 4</summary>

```python
def s3_save(bucket: str):
    # TODO: Step 4 - Return an S3SessionManager with session_id "bluffs-s3", the bucket, prefix "save-points/" and region_name REGION
    return S3SessionManager(session_id="bluffs-s3", bucket=bucket, prefix="save-points/", region_name=REGION)
```

Replace the `return None`. A trap: unlike the folder, the bucket keeps the save point between runs, because the script clears only the local folder. Run it twice and the second run's agent wakes up already holding the first run's conversation. Delete the objects between runs if you want a clean slate.

</details>

## Run the Lockers

```bash
python save_points.py
```

Check: three blocks, or two and a skip. This is an example; the model words its answers its own way, and the message counts depend on the turns:

```
FILE SESSION MANAGER: a folder of JSON files
  Cordula: Safe Room on the bluffs, under the madrones. The code word for the ferry gate is Heron. Remember it.
  the System: Noted: the code word for the ferry gate is Heron.
  a new agent, built on the same save point, already holds 2 messages
  Cordula: The lights came back on. What is the code word for the ferry gate?
  the System: The code word for the ferry gate is Heron.

SNAPSHOT SESSION MANAGER: one blob, and checkpoints
  ...
  checkpoint 0190c7e4-... saved at 4 messages
  after one more turn: 6 messages
  restored the checkpoint: 4 messages

S3 SESSION MANAGER: skipped. Set SAVE_POINTS_BUCKET to a bucket you created to try it.
```

| you see | it means | fix |
|---|---|---|
| `AttributeError: 'NoneType' object has no attribute ...` | a `_save` function still returns `None` | Steps 2, 3 and 4 |
| `holds 0 messages` and the System has lost the word | the second agent did not find the first one's save point | check that both use the same session id (the manager function) and the same `agent_id` (`make_player`) |
| `SessionException` mentioning the bucket, or `NoSuchBucket` | the bucket name in `SAVE_POINTS_BUCKET` does not exist | create it with the commands above |
| `AccessDenied` on the bucket | your credentials cannot read or write that bucket | use the same account that made it |
| `AccessDeniedException` or `ExpiredToken` on the model call | the model call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws) |

## Which Locker?

Start with the folder: it is the simplest, and you can read it. Move to snapshots when you want to go back to a moment, as in a game with save slots, and to restore in one read. Move to S3 when the agent runs somewhere that disappears, such as a container, and the save point has to be somewhere else. Each of them keeps the conversation and nothing more; what the agent learned from it is the job of memory, in [The System Holds Grudges](system-holds-grudges.md). The Floor 8 build puts the Narrator's conversation in AgentCore Memory for the same reason S3 is here: the machine will go.

## What It Costs

Model: the folder run is two turns, the snapshot run is two turns and the extra checkpoint turn, and the optional S3 run is two more. Seven calls at about 1,000 input tokens and 100 output tokens is 7,000 input tokens x $0.30 per million = $0.0021 and 700 output tokens x $2.50 per million = $0.0018, so under half a cent. See [what a turn costs](../floor-1.md#what-a-turn-costs).

S3, if you run Step 4: storage is billed per GB-month and requests per thousand, both listed on the [Amazon S3 pricing page](https://aws.amazon.com/s3/pricing/). A save point of a few turns is a few kilobytes and a few dozen requests, a tiny fraction of a cent. The bucket keeps costing a little for as long as it exists, so run the delete commands in Step 4 when you finish.

## Encounter Clear

Loot you're keeping:

- A session manager is one argument, `session_manager=`, and a new agent with the same session id and agent id wakes up with the old conversation
- The file manager is a folder you can read; the snapshot manager saves the whole agent and keeps checkpoints you can travel back to; the S3 manager moves the folder to a bucket
- A fixed `agent_id` is what lets a new agent find an old one
- A save point holds what was said, not what was learned

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[AUTOSAVE, THREE WAYS]**
>
> Reward: You received a [Silver Box]. Inside: a steel key, a sealed jar, and a receipt for one bucket you promised to delete.

Back to [Floor 7](../floor-7.md#floor-clear), or on to [Floor 8](../floor-8.md).
