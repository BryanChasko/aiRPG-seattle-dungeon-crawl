"""Floor 2 sidequest, The Sandbox Tide Pool: let Kiro the Doomsday Scripter detonate scrolls somewhere that is not your machine.

It starts from bonus_quest.py. There, Kiro's shell and file_editor ran on your own computer, behind a
human's yes. Here the agent gets a sandbox: a Docker container, standing in the pool, where every command
and every file lands. The tools are the same shape; only the place changes.

Needs Docker running on your machine. Start the pool once, before the run:
    docker run -d --name tide-pool python:3.13-slim sleep infinity
and clear it afterwards:
    docker rm -f tide-pool

Run it from this folder, with the workshop environment active:
    python tide_pool.py
"""

import asyncio
from pathlib import Path

from strands import Agent
# TODO: Step 1 - Import DockerSandbox from strands.sandbox.docker and PosixShellSandbox from strands.sandbox.posix_shell
from strands.sandbox.docker import DockerSandbox
from strands.sandbox.posix_shell import PosixShellSandbox

CONTAINER = "tide-pool"  # the name given to docker run above
SCROLL = "/tmp/scroll.py"  # a path inside the container, not on your machine


def check_pool(pool) -> None:
    """DockerSandbox is a PosixShellSandbox: it only says how to run one command, and files and code follow from that."""
    if not isinstance(pool, PosixShellSandbox):
        raise TypeError(f"expected a PosixShellSandbox, got {type(pool).__name__}")


# TODO: Step 2 - Build a DockerSandbox for the CONTAINER, with working_dir "/tmp" and user "nobody", as pool
pool = DockerSandbox(CONTAINER, working_dir="/tmp", user="nobody")


def make_kiro() -> Agent:
    """Kiro the Doomsday Scripter, with no tools listed: the sandbox brings its own shell and file editor."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        # TODO: Step 3 - Give the agent the pool as its sandbox
        sandbox=pool,
        callback_handler=None,
        system_prompt=f"""You are Kiro the Doomsday Scripter, a crawler whose class treats code as demolition magic.
You work inside a sandbox, a tide pool in a container: use sandbox_file_editor to inscribe scrolls (files) and
sandbox_shell to cast them, narrating every step as if the scroll might detonate. It will not, and if it did, only the
pool would feel it. Plain text only, no emoji.""",
    )


JOBS = (f"Inscribe {SCROLL} with sandbox_file_editor: a scroll that prints the first 10 numbers of the Fibonacci sequence. "
        f"Cast it with sandbox_shell. Then run `whoami` in the pool and tell me who you are in there.")

if __name__ == "__main__":
    check_pool(pool)
    result = make_kiro()(JOBS)
    print(f"\nKiro: {str(result).strip()}")
    # TODO: Step 4 - Read the scroll back from inside the pool with pool.read_text (an async method: run it with asyncio.run) and print it
    print(f"\nThe scroll, read from inside the pool:\n{asyncio.run(pool.read_text(SCROLL))}")
    print(f"\nA scroll.py in this folder on your machine? {Path('scroll.py').exists()}")
