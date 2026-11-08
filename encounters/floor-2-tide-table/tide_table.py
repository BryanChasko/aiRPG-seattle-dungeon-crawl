"""Floor 2 sidequest, The Tide Table: ask the real Elliott Bay tide gauge whether the Estuary dance floor is underwater.

It starts from agent_with_vended_tools.py. There, http_request read a monster manual. Here it reads
today's high and low tides from NOAA, the United States ocean and weather agency, for the Seattle
gauge (station 9447130). The notebook tool gives the party a place to keep notes between tool calls,
and the System rules on the dance floor from those notes. No key or account is needed.

Run it from this folder, with the workshop environment active:
    python tide_table.py
"""

from datetime import date
from urllib.parse import urlencode

from strands import Agent
# TODO: Step 1 - Import http_request and notebook from strands.vended_tools

NOAA_API = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
SEATTLE_STATION = "9447130"  # the Elliott Bay tide gauge
FLOOD_LINE_FT = 11.0  # the Estuary dance floor floods when a high tide reaches this height, in feet above the lowest tides


def tide_url(day: date) -> str:
    """The NOAA address for the high and low tides of one day at the Seattle gauge."""
    # TODO: Step 2 - Fill params for NOAA: product predictions, interval hilo, station SEATTLE_STATION, begin_date and end_date both day as YYYYMMDD, datum MLLW, units english, time_zone lst_ldt, format json, application aiRPG_workshop
    params = {}
    return f"{NOAA_API}?{urlencode(params)}"


system = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    tools=[
        # TODO: Step 3 - Add the http_request and notebook tools to the agent
    ],
    callback_handler=None,
    system_prompt=f"""You are the System, the sardonic AI that runs a dungeon crawl under Seattle as a show for alien viewers.
Today you rule on whether the Estuary dance floor, down in the pickleweed, is underwater. The floor floods when a high tide
reaches {FLOOD_LINE_FT} feet. You will be given an address: fetch it with http_request (GET). It returns NOAA tide
predictions: each entry has t (the time), v (the height in feet) and type (H for high, L for low).
Keep the party's notes in a notebook called "tide-log": create it, then write one line per tide with its time, height and
whether it passes the flood line. Then read the notebook back and rule, in three sentences, with the highest tide's exact
height and time. Get every number right: the audience checks. Plain text only, no emoji.""",
)

if __name__ == "__main__":
    today = date.today()
    result = system(f"Is the Estuary dance floor underwater today? The tide table for {today.isoformat()} is at {tide_url(today)}")
    print(f"\nTHE SYSTEM RULES: {str(result).strip()}")
    # TODO: Step 4 - Read the party's notes: print the "notebooks" entry of the system agent's state
