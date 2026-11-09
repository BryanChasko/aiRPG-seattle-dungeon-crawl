"""Floor 4 encounter, The Locks Turnstile: the tide server, given.

A small FastMCP server on port 8003 that knows the tide tables for three Puget Sound stations.
The numbers are a fixed sample for the workshop: no network, no clock, the same answer every
time. They are not for navigation. The turnstile in locks_turnstile.py lets an agent connect to
this server by name.

Run it on its own, with the workshop environment active, if you want to poke at it:
    python tide_server.py
"""

import logging

from mcp.server import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PORT = 8003

# station -> the day's turns of the tide: (clock time, height in feet, "high" or "low")
TIDES: dict[str, list[tuple[str, float, str]]] = {
    "ballard-locks": [("02:10", 0.8, "low"), ("08:25", 11.6, "high"), ("14:40", 2.1, "low"), ("20:55", 10.9, "high")],
    "elliott-bay": [("02:30", 0.5, "low"), ("08:45", 11.9, "high"), ("15:00", 1.8, "low"), ("21:15", 11.2, "high")],
    "tacoma-narrows": [("01:50", 0.2, "low"), ("08:05", 12.3, "high"), ("14:20", 1.4, "low"), ("20:35", 11.7, "high")],
}

mcp = FastMCP(name="tide", port=PORT)


@mcp.tool()
def tide_table(station: str) -> dict:
    """Look up the day's tide table for one Puget Sound station.

    Use it when someone asks how high or low the water is, or when it turns.

    Args:
        station: One of "ballard-locks", "elliott-bay" or "tacoma-narrows".

    Returns:
        A dict with the station and a list of turns, each with the clock time (24 hour),
        the height in feet and whether it is a high or a low.
    """
    key = station.strip().lower()
    if key not in TIDES:
        raise ValueError(f"Unknown station {station!r}. Stations: {', '.join(sorted(TIDES))}")
    turns = [{"time": t, "feet": feet, "kind": kind} for t, feet, kind in TIDES[key]]
    logging.info(f"[TIDE] table for {key}: {len(turns)} turns")
    return {"station": key, "turns": turns}


@mcp.tool()
def next_turn(station: str, after: str = "00:00") -> dict:
    """Find the next turn of the tide at one station after a given clock time.

    Use it for "when does the water turn next" questions, for example before a boat
    goes through the Ballard Locks.

    Args:
        station: One of "ballard-locks", "elliott-bay" or "tacoma-narrows".
        after: A 24 hour clock time as HH:MM. Defaults to the start of the day.

    Returns:
        A dict with the station, the clock time of the next turn, its height in feet and
        whether it is a high or a low. If no turn is left today, "time" is "none".
    """
    table = tide_table(station)
    for turn in table["turns"]:
        if turn["time"] > after:
            return {"station": table["station"], **turn}
    return {"station": table["station"], "time": "none", "feet": 0.0, "kind": "none"}


if __name__ == "__main__":
    print(f"Starting Tide MCP Server on port {PORT}...")
    mcp.run(transport="streamable-http")
