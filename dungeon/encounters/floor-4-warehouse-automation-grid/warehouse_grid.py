"""Floor 4 encounter, The Warehouse Automation Grid: show an agent only the MCP tools it needs.

A warehouse grid exposes eight tools over MCP: three look, four move machinery, and one releases
the whole grid. An agent handed every tool can trip all of it. MCPClient takes tool_filters, an
allowed list and a rejected list, so the agent only ever sees the tools you leave in.

Run it from this folder, with the workshop environment active:
    python warehouse_grid.py
"""

import re
import socket
import threading
import time

from strands import Agent
# TODO: Step 1 - Import MCPClient from strands.tools.mcp

import grid_server

GRID_URL = f"http://localhost:{grid_server.PORT}/mcp"

# TODO: Step 2 - Write the allowed list: one compiled regex, re.compile(r"^(list|belt|scan)_"), the read-only name prefixes
ALLOWED: list = []

# TODO: Step 3 - Write the rejected list: the exact name "scan_and_release_all", a tool that passes the allowed list and should not
REJECTED: list = []

SYSTEM_PROMPT = """You are the dock attendant at a warehouse on the Ship Canal beside the Ballard Locks.
You answer questions about parcels and belts using only the tools you hold. You look; you never move a belt,
a sorter or an arm. Report the belt, the lane and the state in two short sentences. Plain text only, no emoji."""

ASK = "Parcel PKG-4471 for the Locks is late. Which belt is it on, and what state is that belt in? Look only."


def make_grid_client() -> "MCPClient":
    """One client for the grid server, with the filters that decide which tools the agent can see."""
    # TODO: Step 4 - Return an MCPClient for GRID_URL with tool_filters holding "allowed" (ALLOWED) and "rejected" (REJECTED)
    return None


def make_attendant(grid_client: "MCPClient") -> Agent:
    """One dock attendant: the same model and prompt every time; the filtered client is the only tool source."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        # TODO: Step 5 - Give the agent the filtered client as its tools
        callback_handler=None,
    )


def tool_names(client: "MCPClient") -> list[str]:
    """Open the client, list the tools it exposes, and return their names. No model involved."""
    with client:
        return sorted(tool.tool_name for tool in client.list_tools_sync())


def start_grid_server() -> None:
    """Run the grid server in a background thread and wait until its port answers."""
    threading.Thread(target=lambda: grid_server.mcp.run(transport="streamable-http"), daemon=True).start()
    for _ in range(50):
        try:
            socket.create_connection(("localhost", grid_server.PORT), timeout=0.2).close()
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"the grid server did not come up on port {grid_server.PORT}")


if __name__ == "__main__":
    start_grid_server()
    print("EVERY TOOL ON THE GRID, no filters")
    print(f"  {tool_names(MCPClient(url=GRID_URL))}")
    print("\nWHAT THE ATTENDANT SEES, with the filters")
    print(f"  {tool_names(make_grid_client())}")
    attendant = make_attendant(make_grid_client())
    print("\nTHE DOCK ATTENDANT, with the model")
    print(f"  {str(attendant(ASK)).strip()}")
