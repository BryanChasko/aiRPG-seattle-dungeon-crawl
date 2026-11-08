"""Floor 8 encounter, Mid-Song Save: stop a dance-off in the middle of a round and pick it up after a restart.

An agent created with checkpointing=True pauses at the boundaries of its loop: after the model asks for a tool and
before the tool runs, and after the tool runs and before the model reads the result. The pause comes back as a
checkpoint, a small marker you can write to disk. A checkpoint holds no conversation: a session manager keeps that.
Run this file three times and the song survives every restart: the round is announced, the dice are thrown, the
round is called.

Run it from this folder, with the workshop environment active, once per beat:
    python mid_song_save.py
    python mid_song_save.py
    python mid_song_save.py
"""

import json
import shutil
import sys
from pathlib import Path

from strands import Agent
from strands.session.file_session_manager import FileSessionManager
# TODO: Step 1 - Import Checkpoint from strands.experimental.checkpoint.checkpoint
from strands.experimental.checkpoint.checkpoint import Checkpoint

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # the shared dance floor lives in encounters/
from dance_floor import dance_round, scoreboard

STATE_DIR = Path(__file__).resolve().parent / ".mid-song-save"  # the session and the checkpoint live here
CHECKPOINT_FILE = STATE_DIR / "checkpoint.json"
OPENING = "Round one against the Bonus-Season Investment Banker: Presence, Driving tempo. Call the round."


def make_band() -> Agent:
    """A fresh Lady Luck. A restarted runtime builds this again; the session and the checkpoint carry the song."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[dance_round],
        system_prompt="""You are Lady Luck, the System's croupier subroutine, calling one round of a dance-off against the
Bonus-Season Investment Banker. Call dance_round once with opponent="the Bonus-Season Investment Banker", move_call="Presence",
crawler="Barnaby", opponent_modifier=2, tempo="Driving". Then report each side as die + modifier = total and name who took
the round, in two sentences. Never roll or decide anything yourself. Plain text only, no emoji.""",
        session_manager=FileSessionManager(session_id="mid-song-save", storage_dir=str(STATE_DIR)),
        # TODO: Step 2 - Turn on checkpointing so the loop pauses at its cycle boundaries and returns a checkpoint
        checkpointing=True,
        callback_handler=None,
    )


def save_checkpoint(result) -> None:
    """Write the checkpoint of a paused result where the next run will find it."""
    # TODO: Step 3 - Write result.checkpoint.to_dict() to CHECKPOINT_FILE as JSON
    CHECKPOINT_FILE.write_text(json.dumps(result.checkpoint.to_dict()))


def resume(band: Agent):
    """Pick the song up where the last run left it."""
    # TODO: Step 4 - Read CHECKPOINT_FILE, check it with Checkpoint.from_dict, and call the band with a {"checkpointResume": {"checkpoint": ...}} block
    checkpoint = Checkpoint.from_dict(json.loads(CHECKPOINT_FILE.read_text()))
    return band({"checkpointResume": {"checkpoint": checkpoint.to_dict()}})


def play_next_beat() -> str:
    """One run of the script: start the round, or resume it. Return a line saying where the song stands."""
    band = make_band()
    result = resume(band) if CHECKPOINT_FILE.exists() else band(OPENING)
    if result.stop_reason == "checkpoint":
        save_checkpoint(result)
        return f"paused {result.checkpoint.position}, cycle {result.checkpoint.cycle_index}"
    shutil.rmtree(STATE_DIR, ignore_errors=True)
    return f"round called: {str(result).strip()}"


if __name__ == "__main__":
    if "--reset" in sys.argv:
        shutil.rmtree(STATE_DIR, ignore_errors=True)
        sys.exit("The save is gone. The next run starts a new round.")
    print(f"MID-SONG SAVE: {play_next_beat()}")
    print(f"  dice thrown in this run: {len(scoreboard)}")
