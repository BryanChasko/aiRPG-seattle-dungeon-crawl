# Side Passage: The Tide Table (Floor 2 Sidequest)

[Back to Floor 2](../floor-2.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-2-tide-table/tide_table.py`](../../encounters/floor-2-tide-table/tide_table.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 2.** The Estuary dance floor sits down in the pickleweed, and I have stood on it at low water. Dry, flat, good grip. I have also stood on it when the Sound came back in, and it is a pond. The schedule for the next dance-off said "Estuary, midday" and nobody on the broadcast knew which of the two floors we were getting. A crew chief does not guess about water. There is a tide gauge on Elliott Bay that has been writing the numbers down for years, and the number for today is public. Barnaby read the schedule twice. "Sergeant, the surface world publishes the sea's timetable. We should read it."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Sidequest: the Tide Table. The Estuary floor floods at eleven feet and not one inch earlier, and the audience has bet on it. I will rule. You will bring me the real number. If your number is made up, the audience will know, because the audience has a window."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 2](../floor-2.md), finished: `http_request` is already in your toolbox |
| you build | an agent that fetches today's real high and low tides for Seattle from NOAA, keeps the party's notes in a notebook, and rules on the dance floor |
| teaches | [`strands.vended_tools.http_request`](https://strandsagents.com/docs/api/python/strands.vended_tools.http_request.http_request/), [`strands.vended_tools.notebook`](https://strandsagents.com/docs/api/python/strands.vended_tools.notebook.notebook/) |
| time | about 15 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

On Floor 2 the agent looked up a creature on an open game API. This time the data is real and it changes every day: NOAA, the United States ocean and weather agency, publishes tide predictions for its gauges through the [Tides and Currents data API](https://api.tidesandcurrents.noaa.gov/api/prod/). The Seattle gauge on Elliott Bay is [station 9447130](https://tidesandcurrents.noaa.gov/stationhome.html?id=9447130). No key and no account are needed. The `interval=hilo` setting asks for only the highs and lows of the day, a handful of lines instead of one every six minutes.

The new tool is [`notebook`](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/notebook/). It gives the agent named notebooks to create, write to, read back and clear. They live in the agent's own state, so they last as long as the agent does and cost no extra service. A notebook is useful when a job has more than one step and the model should not have to carry every number in its head: write each tide down once, read the page back, then rule.

How you know it worked: the run prints the System's ruling with the day's highest tide quoted to the tenth of a foot, then the contents of the `tide-log` notebook, one line per tide. Compare it to the [station page](https://tidesandcurrents.noaa.gov/stationhome.html?id=9447130): the audience checks.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-2-tide-table
```

## Step 1: Import the Tools

```python
# TODO: Step 1 - Import http_request and notebook from strands.vended_tools
```

Both ship with the SDK, as the Floor 2 tools do. See [HTTP Request](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/http-request/) and [Notebook](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/notebook/) for the notebook.

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

`tide_url` turns a day into the web address the agent will fetch; `urlencode` joins the pairs you fill in. Most of the names come from the NOAA data API page: `product=predictions` asks for forecast tides, `interval=hilo` for the highs and lows only, `datum=MLLW` measures heights above mean lower low water (the average of the lower of each day's two lows, which is what the chart datum in the Sound is), `time_zone=lst_ldt` gives Seattle's local clock with daylight saving, and `application` tells NOAA who is asking. Dates are `YYYYMMDD`, and `strftime("%Y%m%d")` writes them.

You can check the address with one bare request, no agent involved. It should answer `200` and a short list of tides:

```bash
curl -s "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&interval=hilo&station=9447130&begin_date=20260101&end_date=20260101&datum=MLLW&units=english&time_zone=lst_ldt&format=json&application=aiRPG_workshop"
```

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** I tested the address by hand before I trusted it to the machine. One request, four lines back: a high before dawn, a low in the morning, a high at lunch, a deep low after dark. Same as checking a radio before you hand it to a new crew member. If the radio does not work in my hand, it will not work in theirs.

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

Both tools go in the `tools` list. The prompt does the rest: it tells the System to fetch the address with a GET, keep a notebook called `tide-log` with one line per tide, read it back and rule. The flood line is a number in the prompt, `FLOOD_LINE_FT`, because the System is bad at being asked to remember a rule it was never told.

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

The notebook tool stores its pages in the agent's state under the key `notebooks`, a dictionary of notebook name to text. Reading it from your own code, outside the conversation, is how you check the model's notes against its ruling. See [Agent State](https://strandsagents.com/docs/api/python/strands.vended_tools.notebook.notebook/) in the tool's API page: the module docstring names the `notebooks` key.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The notebook is the logbook. When the System says the high is eleven point six at four twenty-one, I do not take its word. I open the log and read the line it wrote when the number came in. If the two disagree, the log wins.

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

Check: the ruling, then the notes. The tides depend on the day you run it; this is an example for 1 January 2026:

```
THE SYSTEM RULES: The Estuary dance floor is underwater today, Crawler. The highest tide is 11.812 feet at 13:36, past the 11.0 foot flood line, so bring boots and a better excuse.

THE PARTY'S NOTES:
[tide-log]
04:21 H 11.619 ft: floods
08:58 L 8.886 ft: dry
13:36 H 11.812 ft: floods
21:07 L -3.174 ft: dry
```

| you see | it means | fix |
|---|---|---|
| `NameError: name 'http_request' is not defined` | Step 1 is missing | add the import |
| the System says it cannot look up tides | the `tools` list is empty or lacks `http_request` | finish Step 3 |
| `THE PARTY'S NOTES:` and nothing under it | the model ruled without writing to the notebook, or Step 3 left out `notebook` | add `notebook` to the tools, then run again |
| the ruling says there is no data | the address is wrong: NOAA answered 200 with an `error` body | print `tide_url(date.today())` and compare it to the `curl` above |
| `ConnectError` in the tool result | your machine could not reach NOAA | check your network and run again |
| `AccessDeniedException` or `ExpiredToken` | the model call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws) |

## Why a Notebook and Not the Conversation

The model could write each tide in its reply and read it back from the conversation. The notebook is different in three ways. It has a name, so two jobs do not share a page. It lives in the state, so your code can read it, clear it or save it. And it is a tool call, so you can see in the run exactly when the agent decided something was worth writing down. For eight lines it is a convenience. For a job that gathers hundreds of lines, it is what keeps them out of every later model call.

## What It Costs

NOAA's data is free. The model side is a handful of calls: one to read the task, one for the fetch, a few notebook writes, one to read the page back, one to rule. About 6 calls at roughly 2,500 input tokens each is 15,000 input tokens at $0.30 per million, $0.0045, plus about 800 output tokens at $2.50 per million, $0.002. Under a cent a run. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot you're keeping:

- A real data source behind `http_request`, with the address built in code and checked by hand first
- `notebook`: named pages of notes kept in the agent's state, readable from your own code
- The habit of checking the model's ruling against the log it wrote

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[HIGH WATER MARK]**
>
> Reward: You received a [Bronze Box]. Inside: a tide chart, a waterproof pencil, and a note in Barnaby's hand that reads "Verified."

Back to [Floor 2](../floor-2.md#floor-clear), or on to [The Sandbox Tide Pool](sandbox-tide-pool.md).
