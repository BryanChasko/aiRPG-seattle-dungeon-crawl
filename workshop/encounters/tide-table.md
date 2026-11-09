# Side Passage: The Tide Table (Floor 2 Sidequest)

[Back to Floor 2](../floor-2.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-2-tide-table/tide_table.py`](../../encounters/floor-2-tide-table/tide_table.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 2, THURSDAY, JUNE 18, SIDE PASSAGE OFF FLOOR 2.** The schedule names an Estuary dance floor, down in the pickleweed. I have stood on flats like it at low water: dry, flat, good grip. I have also stood on one when the Sound came back in, and the floor is a pond. The schedule for the next dance-off said "Estuary, midday" and nobody on the broadcast knew which of the two floors we were getting. A crew chief does not guess about water. There is a tide gauge on Elliott Bay that has been writing the numbers down for years, and the number for today is public: low water at 1400 is minus 2.7 feet, and the high at 2135 is 12.4, 1.4 feet past the eleven-foot line. Barnaby read the schedule twice. Shelly dug in at my heel and puffed a cloud of sea mist at the schedule. "Sergeant, the surface world publishes the sea's timetable. We should read the timetable."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Sidequest: the Tide Table. The Estuary floor floods at eleven feet and not one inch earlier, and the audience has bet on it. I will rule. Crawler, bring me the real number. If the number is made up, the audience will know, because the audience has a window."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 2](../floor-2.md), finished: `http_request` is already in the Floor 2 toolbox |
| you build | an agent that fetches today's real high and low tides for Seattle from NOAA, keeps the party's notes in a notebook, and rules on the dance floor |
| teaches | [`strands.vended_tools.http_request`](https://strandsagents.com/docs/api/python/strands.vended_tools.http_request.http_request/), [`strands.vended_tools.notebook`](https://strandsagents.com/docs/api/python/strands.vended_tools.notebook.notebook/) |
| time | about 15 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

On Floor 2 the agent looked up a creature on an open game API. This time the data is real and changes every day: NOAA, the United States ocean and weather agency, publishes tide predictions for NOAA's gauges through the [Tides and Currents data API](https://api.tidesandcurrents.noaa.gov/api/prod/). The Seattle gauge on Elliott Bay is [station 9447130](https://tidesandcurrents.noaa.gov/stationhome.html?id=9447130). No key and no account are needed. The `interval=hilo` setting asks for only the highs and lows of the day, a handful of lines instead of one every six minutes.

The new tool is [`notebook`](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/notebook/). The `notebook` tool gives the agent named notebooks to create, write to, read back and clear. Notebooks live in the agent's state and last as long as the agent, with no extra service to pay for. A notebook is useful when a job has more than one step and Amazon Nova 2 Lite should not carry every number between calls: write each tide down once, read the page back, then rule.

Success check: the run prints the System's ruling with the day's highest tide quoted to the tenth of a foot, then the contents of the `tide-log` notebook, one line per tide. Compare the ruling to the [station page](https://tidesandcurrents.noaa.gov/stationhome.html?id=9447130): the audience checks. The ruling is the Narrator's, spoken in the System AI's voice: the agent's prompt opens "You are the System".

Open the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-2-tide-table
```

## Step 1: Import the Tools

```python
# TODO: Step 1 - Import http_request and notebook from strands.vended_tools
```

`http_request` and `notebook` ship with the SDK, as the Floor 2 tools do. See [HTTP Request](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/http-request/) and [Notebook](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/notebook/).

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import http_request and notebook from strands.vended_tools
from strands.vended_tools import http_request, notebook
```

</details>

## Step 2: Build the Address

```python
# TODO: Step 2 - Fill params for NOAA: product predictions, interval hilo, station SEATTLE_STATION, begin_date and end_date both day as YYYYMMDD, datum MLLW, units english, time_zone lst_ldt, format json, application aiRPG_workshop
```

`tide_url` turns a day into the web address the agent will fetch; `urlencode` joins the pairs filled in at Step 2. Most of the names come from the NOAA data API page: `product=predictions` asks for forecast tides, `interval=hilo` for the highs and lows only, `datum=MLLW` measures heights above mean lower low water (the average of the lower of each day's two lows, the chart datum for Puget Sound), `time_zone=lst_ldt` gives Seattle's local clock with daylight saving, and `application` tells NOAA who is asking. Dates are `YYYYMMDD`, and `strftime("%Y%m%d")` writes them.

Check the address with one bare request, no agent involved. The request should answer `200` and a short list of tides:

```bash
curl -s "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&interval=hilo&station=9447130&begin_date=20260101&end_date=20260101&datum=MLLW&units=english&time_zone=lst_ldt&format=json&application=aiRPG_workshop"
```

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** I tested the address by hand before I trusted the address to the machine. One request, four lines back, two highs and two lows. Same as checking a radio before you hand it to a new crew member. If the radio does not work in my hand, it will not work in theirs.

<details>
<summary>Show me the code for Step 2</summary>

```python
    # TODO: Step 2 - Fill params for NOAA: product predictions, interval hilo, station SEATTLE_STATION, begin_date and end_date both day as YYYYMMDD, datum MLLW, units english, time_zone lst_ldt, format json, application aiRPG_workshop
    params = {
        "product": "predictions",
        "interval": "hilo",
        "station": SEATTLE_STATION,
        "begin_date": day.strftime("%Y%m%d"),
        "end_date": day.strftime("%Y%m%d"),
        "datum": "MLLW",
        "units": "english",
        "time_zone": "lst_ldt",
        "format": "json",
        "application": "aiRPG_workshop",
    }
```

Trap: NOAA answers a bad request with status 200 and a JSON body that starts with `"error"`. A typo in a parameter name does not fail loudly; the agent just reports that there is no data.

</details>

## Step 3: Add the Tools to the Agent

```python
# TODO: Step 3 - Add the http_request and notebook tools to the agent
```

Add `http_request` and `notebook` to the `tools` list. The prompt does the rest: the prompt tells the System to fetch the address with a GET, keep a notebook called `tide-log` with one line per tide, read the notebook back and rule. The flood line is a number in the prompt, `FLOOD_LINE_FT`, because the System cannot follow a rule the prompt never states.

<details>
<summary>Show me the code for Step 3</summary>

```python
    tools=[
        # TODO: Step 3 - Add the http_request and notebook tools to the agent
        http_request,
        notebook,
    ],
```

</details>

## Step 4: Read the Party's Notes

```python
# TODO: Step 4 - Read the party's notes: print the "notebooks" entry of the system agent's state
```

The notebook tool stores pages in the agent's state under the key `notebooks`, a dictionary of notebook name to text. Reading `notebooks` from the script, outside the conversation, checks the System AI's notes against the System AI's ruling. The module docstring on the tool's [API page](https://strandsagents.com/docs/api/python/strands.vended_tools.notebook.notebook/) names the `notebooks` key.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The notebook is the logbook. When the System AI says the high is twelve point four at nine thirty-five tonight, I do not take the System AI's word. I open the log and read the line the System AI wrote when the number came in. If the ruling and the log disagree, the log wins.

<details>
<summary>Show me the code for Step 4</summary>

```python
    # TODO: Step 4 - Read the party's notes: print the "notebooks" entry of the system agent's state
    print("\nTHE PARTY'S NOTES:")
    for name, text in (system.state.get("notebooks") or {}).items():
        print(f"[{name}]\n{text}")
```

</details>

## Run It

```bash
python tide_table.py
```

Check: the ruling, then the notes. The tides depend on the run date; this example shows 1 January 2026:

```
THE SYSTEM RULES: The Estuary dance floor is underwater today, Crawler. The highest tide is 11.812 feet at 13:36, past the 11.0 foot flood line, so bring boots and a better excuse.

THE PARTY'S NOTES:
[tide-log]
04:21 H 11.619 ft: floods
08:58 L 8.886 ft: dry
13:36 H 11.812 ft: floods
21:07 L -3.174 ft: dry
```

| you see | cause | fix |
|---|---|---|
| `NameError: name 'http_request' is not defined` | Step 1 is missing | add the Step 1 import |
| the System says it cannot look up tides | the `tools` list is empty or lacks `http_request` | finish Step 3 |
| `THE PARTY'S NOTES:` and nothing under it | the System ruled without writing to the notebook, or Step 3 left out `notebook` | add `notebook` to the tools, then rerun |
| the ruling says there is no data | the address is wrong: NOAA answered 200 with an `error` body | print `tide_url(date.today())` and compare it to the `curl` above |
| `ConnectError` in the tool result | this computer could not reach NOAA | check the network connection, then rerun |
| `AccessDeniedException` or `ExpiredToken` | the call to Amazon Nova 2 Lite failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Why a Notebook and Not the Conversation

Amazon Nova 2 Lite could write each tide in the reply and read the tides back from the conversation. The notebook differs in three ways. A notebook has a name, so two jobs do not share a page. A notebook lives in the state, so the script can read, clear or save a notebook. And a notebook write is a tool call, so the run shows exactly when the agent decided a line was worth writing down. For eight lines a notebook is a convenience. For a job that gathers hundreds of lines, a notebook is what keeps those lines out of every later Amazon Nova 2 Lite call.

## What It Costs

NOAA's data is free. The Amazon Nova 2 Lite side is about 6 calls: one to read the task, one for the fetch, a few notebook writes, one to read the page back, one to rule. About 6 calls at roughly 2,500 input tokens each is 15,000 input tokens at $0.30 per million, $0.0045, plus about 800 output tokens at $2.50 per million, $0.002. Under a cent a run. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot kept:

- A real data source behind `http_request`, with the address built in code and checked by hand first
- `notebook`: named pages of notes kept in the agent's state, readable from the script
- The habit of checking the System AI's ruling against the log it wrote

> <img src="../../images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[HIGH WATER MARK]**
>
> Reward: You received a [Bronze Box]. Inside: a tide chart, a waterproof pencil, and a note in Barnaby's hand that reads "Verified."

Back to [Floor 2](../floor-2.md#floor-clear), or on to [The Sandbox Tide Pool](sandbox-tide-pool.md).
