"""Floor 4 encounter, Trace the Portal: see every MCP call as a span.

A call from an agent to an MCP server crosses a wire, and a wire hides things. OpenTelemetry
draws the call as spans: one for the agent's turn, one for the tool, one on the server side.
Strands carries the trace across the wire inside each MCP request, and mcp_instrumentation lets
a server that lives in the same process join the same trace. The spans print to the console, one
line each: no collector, no cloud service.

Run it from this folder, with the workshop environment active:
    python trace_the_portal.py
"""

import random
import socket
import threading
import time

from mcp.server import FastMCP
from opentelemetry import trace
from strands import Agent
from strands.tools.mcp import MCPClient
# TODO: Step 1 - Import StrandsTelemetry from strands.telemetry and mcp_instrumentation from strands.tools.mcp.mcp_instrumentation

PORT = 8004
PORTAL_URL = f"http://localhost:{PORT}/mcp"

tracer = trace.get_tracer("the-portal")
portal = FastMCP(name="portal", port=PORT)


@portal.tool()
def roll_dice(faces: int = 20) -> dict:
    """Roll one die with the given number of faces.

    Use it every time a roll is needed. Report the result this tool returns; never invent a roll.

    Args:
        faces: Number of faces on the die, 1 or more. Defaults to 20.

    Returns:
        A dict with the faces and the die rolled.
    """
    if faces < 1:
        raise ValueError("Dice must have at least 1 face")
    with tracer.start_as_current_span("portal.roll_dice") as span:  # a span made on the server side of the wire
        die = random.randint(1, faces)
        span.set_attribute("dice.faces", faces)
        span.set_attribute("dice.result", die)
    return {"faces": faces, "die": die}


def one_line(span) -> str:
    """Print a finished span as one line: its name, the trace it belongs to, its own id and its parent's id."""
    ctx = span.get_span_context()
    parent = "none" if span.parent is None else format(span.parent.span_id, "016x")[-4:]
    return f"  {span.name:<36} trace {format(ctx.trace_id, '032x')[-6:]}  span {format(ctx.span_id, '016x')[-4:]}  parent {parent}\n"


def light_the_portal() -> None:
    """Turn the tracing on. Call it before the portal server starts, so the server's sessions are patched."""
    # TODO: Step 2 - Create a StrandsTelemetry and set up its console exporter with formatter=one_line
    # TODO: Step 3 - Apply mcp_instrumentation() so the server in this process joins the client's trace
    pass


SYSTEM_PROMPT = """You are Lady Luck, the System's croupier subroutine. Always use the roll_dice tool for every roll
and report the number it returns, in one sentence. Plain text only, no emoji."""

ASK = "Roll one d20 for Cordula's Read the Room check."


def make_watcher(portal_client: MCPClient) -> Agent:
    """One Lady Luck with the portal's dice; the tracing is the only thing that is new."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        tools=[portal_client],
        # TODO: Step 4 - Tag the agent's trace with trace_attributes={"encounter": "trace-the-portal"}
        callback_handler=None,
    )


def start_portal_server() -> None:
    """Run the portal server in a background thread and wait until its port answers."""
    threading.Thread(target=lambda: portal.run(transport="streamable-http"), daemon=True).start()
    for _ in range(50):
        try:
            socket.create_connection(("localhost", PORT), timeout=0.2).close()
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"the portal server did not come up on port {PORT}")


if __name__ == "__main__":
    light_the_portal()
    start_portal_server()
    print("SPANS, in the order they finish")
    watcher = make_watcher(MCPClient(url=PORTAL_URL))
    result = watcher(ASK)
    print(f"\nLady Luck: {str(result).strip()}")
