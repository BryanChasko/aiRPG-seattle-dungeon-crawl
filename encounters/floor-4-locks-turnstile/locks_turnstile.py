"""Floor 4 encounter, The Locks Turnstile: let an agent pick its MCP server, from a list you wrote.

On Floor 4 you wired one MCPClient to one server. The mcp_router tool is the other way round: the
agent opens connections at runtime, by name. Every name it can ask for comes from an allowlist
you write, so a server that is not on the list is refused before anything connects.

Run it from this folder, with the workshop environment active:
    python locks_turnstile.py
"""

import socket
import threading
import time

from strands import Agent
# TODO: Step 1 - Import make_mcp_router from strands.vended_tools.mcp_router.mcp_router

import tide_server

TIDE_URL = f"http://localhost:{tide_server.PORT}/mcp"

# TODO: Step 2 - Write the allowlist: "dice" at http://localhost:8002/mcp and "tide" at TIDE_URL, each as {"url": ...}
ALLOWLIST: dict = {}

# TODO: Step 3 - Build the router tool named "turnstile" from the allowlist, with at most 2 open connections
turnstile = None

SYSTEM_PROMPT = """You are the gate keeper at the Ballard Locks turnstile, a router for the System's MCP servers.
Open a connection with the turnstile tool (command connect, a short connection_id, and a server_name),
list the server's tools, call the one you need, then disconnect. Report what each step returned.
If the turnstile refuses a server, say so in one sentence and do not try again. Plain text only, no emoji."""

ASK = ("The water level decides which lane the boats take. Connect to the tide server and tell me when the water "
       "next turns at ballard-locks after 09:00. Then try to connect to a server called ferry-wifi and tell me what happened.")


def make_gate() -> Agent:
    """One gate keeper: the same model and prompt every time; the turnstile is the only tool it holds."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        # TODO: Step 4 - Give the agent the turnstile as its only tool
        callback_handler=None,
    )


def start_tide_server() -> None:
    """Run the tide server in a background thread and wait until its port answers."""
    threading.Thread(target=lambda: tide_server.mcp.run(transport="streamable-http"), daemon=True).start()
    for _ in range(50):
        try:
            socket.create_connection(("localhost", tide_server.PORT), timeout=0.2).close()
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"the tide server did not come up on port {tide_server.PORT}")


def knock(gate: Agent, server_name: str) -> str:
    """Ask the turnstile to connect to one server by hand, with no model involved, and return what it said."""
    result = gate.tool.turnstile(
        command="connect", connection_id="probe", server_name=server_name, record_direct_tool_call=False
    )
    return f"{result['status']}: {result['content'][0]['text']}"


if __name__ == "__main__":
    start_tide_server()
    gate = make_gate()
    print("KNOCK, no model involved")
    print(f"  ferry-wifi -> {knock(gate, 'ferry-wifi')}")
    print(f"  tide -> {knock(gate, 'tide')}")
    gate.tool.turnstile(command="disconnect", connection_id="probe", record_direct_tool_call=False)
    print("\nTHE GATE KEEPER, with the model")
    print(f"  {str(gate(ASK)).strip()}")
