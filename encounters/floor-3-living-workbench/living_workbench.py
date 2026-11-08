"""Floor 3 encounter, The Living Workbench: add a tool to a running agent by dropping a file in a folder.

An agent built with load_tools_from_directory=True loads every tool file in ./tools and keeps a
watcher on the folder. Save a new file there, or change one, and the tool is registered or reloaded
without restarting the agent. Here the agent is asked to settle a tied round before it has a
final_beat tool, then the tool is copied onto the bench, and the same agent is asked again.

Run it from this folder, with the workshop environment active:
    python living_workbench.py
"""

import os
import shutil
import time
from pathlib import Path

from strands import Agent

HERE = Path(__file__).resolve().parent
TOOLS = HERE / "tools"  # the folder Strands watches: it looks for ./tools in the current directory
SHELF = HERE / "shelf" / "final_beat.py"  # the tool waiting to be added

ASK = "Cordula and the Bonus-Season Investment Banker finished the round level. Settle it with the Final Beat for Cordula and report both totals."


def make_workbench() -> Agent:
    """The System at the workbench. Its tools are whatever is in ./tools right now."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        callback_handler=None,
        system_prompt="""You are the System, the game-show host of Dungeon Crawl: Seattle, settling a tied round. Every roll comes
from a tool; never roll, add or decide anything yourself. If the tool you need is not on the workbench, say "The drum is not on the
workbench yet." and stop. Otherwise report what the tool returned. Two sentences. Plain text only, no emoji.""",
        # TODO: Step 1 - Load the tools in ./tools and watch the folder for changes: pass load_tools_from_directory=True
    )


def put_on_the_bench() -> None:
    """Add final_beat to the folder while the agent is running."""
    # TODO: Step 4 - Copy SHELF into the TOOLS folder with shutil.copyfile; the new file is TOOLS / SHELF.name
    pass


def wait_for_tool(agent: Agent, name: str, seconds: float = 10.0) -> bool:
    """Wait for the watcher to register a tool on the agent; True when it shows up."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if name in agent.tool_names:
            return True
        time.sleep(0.2)
    return False


if __name__ == "__main__":
    os.chdir(HERE)  # Strands looks for ./tools relative to the current directory
    (TOOLS / SHELF.name).unlink(missing_ok=True)  # start every run with a bare bench
    system = make_workbench()
    try:
        print(f"\nON THE BENCH: {system.tool_names}")
        print(f"  {str(system(ASK)).strip()}")

        put_on_the_bench()
        if wait_for_tool(system, "final_beat"):
            print(f"\nON THE BENCH: {system.tool_names}")
            print(f"  {str(system(ASK)).strip()}")
        else:
            print("\nfinal_beat never showed up on the bench: check the shelf file for Steps 2 and 3.")
    finally:
        (TOOLS / SHELF.name).unlink(missing_ok=True)  # leave the bench bare for the next run
