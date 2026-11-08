"""Floor 7 encounter, Save Points: three ways to save a conversation before the lights go out.

A session manager saves an agent as it talks and loads it again when a new agent starts with the same
session id. The file session manager writes one JSON file per message. The snapshot session manager
writes the whole agent as one blob, and can keep numbered checkpoints you can travel back to. The
S3 session manager writes the same layout as the file one into a bucket, so a save point survives the
machine. The S3 part is optional: set SAVE_POINTS_BUCKET to a bucket you created, or skip it.

Run it from this folder, with the workshop environment active:
    python save_points.py
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path

from strands import Agent
from strands.storage import LocalFileStorage
# TODO: Step 1 - Import FileSessionManager from strands.session.file_session_manager, SnapshotSessionManager from
#                strands.session.snapshot_session_manager and S3SessionManager from strands.session.s3_session_manager
from strands.session.file_session_manager import FileSessionManager
from strands.session.snapshot_session_manager import SnapshotSessionManager
from strands.session.s3_session_manager import S3SessionManager

SAVE_DIR = Path(tempfile.gettempdir()) / "save-points"  # the file and snapshot save points land under here
REGION = "us-west-2"

SYSTEM_PROMPT = """You are the System, the sardonic broadcast AI of a dungeon crawl under Seattle. Answer from the
conversation only: if a fact is not in it, say the System has lost it. One sentence.
Plain text only, no emoji."""

TELL = "Safe Room on the bluffs, under the madrones. The code word for the ferry gate is Heron. Remember it."
ASK = "The lights came back on. What is the code word for the ferry gate?"
MORE = "One more thing: Chonks ate the ferry map."


def file_save():
    """One JSON file per message, in a folder."""
    # TODO: Step 2 - Return a FileSessionManager with session_id "bluffs-file" and storage_dir str(SAVE_DIR / "file")
    return FileSessionManager(session_id="bluffs-file", storage_dir=str(SAVE_DIR / "file"))


def snapshot_save():
    """The whole agent as one blob, on the Storage of your choice, plus checkpoints."""
    # TODO: Step 3 - Return a SnapshotSessionManager with session_id "bluffs-snapshot" and storage LocalFileStorage(str(SAVE_DIR / "snapshot"))
    return SnapshotSessionManager(session_id="bluffs-snapshot", storage=LocalFileStorage(str(SAVE_DIR / "snapshot")))


def s3_save(bucket: str):
    """The file layout, in a bucket."""
    # TODO: Step 4 - Return an S3SessionManager with session_id "bluffs-s3", the bucket, prefix "save-points/" and region_name REGION
    return S3SessionManager(session_id="bluffs-s3", bucket=bucket, prefix="save-points/", region_name=REGION)


def make_player(manager) -> Agent:
    """Same agent id every time: a new agent with this id and the manager's session id picks up where the last one stopped."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        agent_id="cordula",
        system_prompt=SYSTEM_PROMPT,
        session_manager=manager,
        callback_handler=None,
    )


def play(label: str, make_manager):
    """Tell the System a secret, drop the agent, start a new one on the same save point and ask for it back."""
    print(f"\n{label}")
    first = make_player(make_manager())
    print(f"  Cordula: {TELL}")
    print(f"  the System: {str(first(TELL)).strip()}")
    second_manager = make_manager()
    second = make_player(second_manager)  # restored while it is built: no model call yet
    print(f"  a new agent, built on the same save point, already holds {len(second.messages)} messages")
    print(f"  Cordula: {ASK}")
    print(f"  the System: {str(second(ASK)).strip()}")
    return second_manager, second


def time_travel(manager, agent: Agent) -> None:
    """Snapshots only: pin a checkpoint, say one more thing, then go back to the checkpoint."""
    snapshot_id = asyncio.run(manager.save_snapshot(agent, is_latest=False))
    print(f"\n  checkpoint {snapshot_id} saved at {len(agent.messages)} messages")
    agent(MORE)
    print(f"  after one more turn: {len(agent.messages)} messages")
    asyncio.run(manager.restore_snapshot(agent, snapshot_id=snapshot_id))
    print(f"  restored the checkpoint: {len(agent.messages)} messages")


if __name__ == "__main__":
    shutil.rmtree(SAVE_DIR, ignore_errors=True)  # start every run with empty save points

    play("FILE SESSION MANAGER: a folder of JSON files", file_save)
    manager, agent = play("SNAPSHOT SESSION MANAGER: one blob, and checkpoints", snapshot_save)
    time_travel(manager, agent)

    bucket = os.environ.get("SAVE_POINTS_BUCKET")
    if bucket:
        play(f"S3 SESSION MANAGER: the file layout, in s3://{bucket}/save-points/", lambda: s3_save(bucket))
    else:
        print("\nS3 SESSION MANAGER: skipped. Set SAVE_POINTS_BUCKET to a bucket you created to try it.")
