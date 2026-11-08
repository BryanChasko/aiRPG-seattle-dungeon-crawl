# Side Passage: Trace the Portal (Floor 4 Sidequest)

[Back to Floor 4](../floor-4.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-4-trace-the-portal/trace_the_portal.py`](../../encounters/floor-4-trace-the-portal/trace_the_portal.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 4.** The portal worked. That was the problem. A die went in on one side of the Ship Canal and a number came out on the other, and in between there was a wire I could not see. The developer advocates on the lock wall called it "effortless" and charged for the word. I do not take a call on faith. I want the log: who sent it, when it crossed, who caught it, how long it sat. Barnaby had one arm on the portal frame. "Sergeant, you have asked for a flight recorder." I had. Every piece of gear that carries something across a gap gets one.
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Sidequest: Trace the Portal. Every call through the portal is now a span, with a trace id, a parent and a timestamp. I would say the audience will find it fascinating. The audience is a console. The console will print one line per span and then go home."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 4](../floor-4.md), finished; this encounter file brings its own small dice server, so nothing else needs to be running |
| build | the switches that print every span of an agent's MCP call to the console, including the span made inside the MCP server |
| teaches | [`strands.tools.mcp.mcp_instrumentation`](https://strandsagents.com/docs/api/python/strands.tools.mcp.mcp_instrumentation/), [`strands.telemetry.config`](https://strandsagents.com/docs/api/python/strands.telemetry.config/): `StrandsTelemetry`, `setup_console_exporter`, `trace_attributes` |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

[Traces](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/) in Strands are OpenTelemetry spans. One agent turn is a tree of them: `invoke_agent` at the root, then `execute_event_loop_cycle` for each trip around the loop, `chat` for each model call, and `execute_tool <name>` for each tool call. A tool that lives behind an MCP server is the one place the tree used to break, because the server is another process, or another thread, with no idea which turn asked.

Strands closes that gap two ways. On the client side, `MCPClient` writes the current trace context (a W3C `traceparent`) into the `_meta` field of every tool call it sends. On the server side, `mcp_instrumentation()` patches the `mcp` package so that a server hosted in the same process reads that `_meta` and continues the trace. A span the server makes then has the agent's tool span as its parent. This encounter hosts a small dice server in a background thread on port 8004 to show the trace continuing. A server in a different process needs its own OpenTelemetry setup to read the context; the client side is the same.

The spans go to the console through `StrandsTelemetry().setup_console_exporter()`. This exporter is OpenTelemetry's own console exporter, installed with the SDK, and needs no collector and no cloud service. By default the exporter prints each span as a screen of JSON. `trace_the_portal.py` hands the exporter a `formatter` that prints one line instead: name, trace, span and parent.

Check success: every line has the same `trace` value, and the `portal.roll_dice` line, a span made on the server, has a `parent` equal to the `span` of the `execute_tool roll_dice` line, made by the agent.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-4-trace-the-portal
```

## Step 1: Import the Switches

```python
# TODO: Step 1 - Import StrandsTelemetry from strands.telemetry and mcp_instrumentation from strands.tools.mcp.mcp_instrumentation
```

`StrandsTelemetry` builds the tracer provider and decides where finished spans go. `mcp_instrumentation` is a function, the one that patches the server side.

<details>
<summary>Show me the code for Step 1</summary>

```python
from strands.tools.mcp import MCPClient
# TODO: Step 1 - Import StrandsTelemetry from strands.telemetry and mcp_instrumentation from strands.tools.mcp.mcp_instrumentation
from strands.telemetry import StrandsTelemetry
from strands.tools.mcp.mcp_instrumentation import mcp_instrumentation
```

</details>

## Step 2: Print the Spans

```python
    # TODO: Step 2 - Create a StrandsTelemetry and set up its console exporter with formatter=one_line
```

Write the call in `light_the_portal`. `StrandsTelemetry()` creates a tracer provider and sets that provider as the global provider, so every span in the process, the agent's and the server's, goes through it. `setup_console_exporter(**kwargs)` adds a console exporter and passes its keyword arguments to OpenTelemetry's `ConsoleSpanExporter`; the `formatter` argument turns a finished span into the string it prints. `trace_the_portal.py` provides `one_line`. Without `formatter`, the exporter prints the full JSON for each span; run that once to see it. See [Enabling Tracing](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/#enabling-tracing).

## Step 3: Patch the Server Side

```python
    # TODO: Step 3 - Apply mcp_instrumentation() so the server in this process joins the client's trace
```

Call `mcp_instrumentation()` with no arguments, once, before the server starts: the call patches the transport and the session class the server's sessions are built from. `trace_the_portal.py` starts the server after `light_the_portal()` for that reason. The call is safe to repeat; the second and later calls do nothing. Under the `mcp` 2.x line the call does nothing at all, because that release line carries the context natively; this workshop pins `mcp` below 2.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Order of operations. Recorder on first, then the portal opens. I have seen a flight recorder installed after the flight. It records the landing very well. Barnaby said that was an unkind thing to say about a landing. He was not wrong. I moved the recorder up the checklist anyway.

<details>
<summary>Show me the code for Steps 2 and 3</summary>

```python
def light_the_portal() -> None:
    """Turn the tracing on. Call it before the portal server starts, so the server's sessions are patched."""
    # TODO: Step 2 - Create a StrandsTelemetry and set up its console exporter with formatter=one_line
    StrandsTelemetry().setup_console_exporter(formatter=one_line)
    # TODO: Step 3 - Apply mcp_instrumentation() so the server in this process joins the client's trace
    mcp_instrumentation()
```

Replace the `pass`.

</details>

## Step 4: Tag the Trace

```python
        # TODO: Step 4 - Tag the agent's trace with trace_attributes={"encounter": "trace-the-portal"}
```

Add the argument inside the `Agent(...)` call in `make_watcher`. `trace_attributes` is a dict of custom attributes, added to the agent's root span. Tags by game, floor or learner make a trace findable later among thousands. See [Custom Attribute Tracking](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/#custom-attribute-tracking). The console formatter only prints names and ids, so the tag shows up in the full JSON, not in the one-line view.

<details>
<summary>Show me the code for Step 4</summary>

```python
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        tools=[portal_client],
        # TODO: Step 4 - Tag the agent's trace with trace_attributes={"encounter": "trace-the-portal"}
        trace_attributes={"encounter": "trace-the-portal"},
        callback_handler=None,
    )
```

</details>

## Open the Portal

```bash
python trace_the_portal.py
```

The server prints its own startup and request lines to the same terminal. Scroll past the server lines to the `SPANS` heading. Check: one line per finished span, in the order they finished, then Lady Luck's sentence. The output below is an example, trimmed to the lines that matter. Ids, die and cycle count differ on every run:

```
SPANS, in the order they finish
  chat                                 trace 3f9a1c  span 41b2  parent 9e07
  portal.roll_dice                     trace 3f9a1c  span 7d10  parent c5e3
  execute_tool roll_dice               trace 3f9a1c  span c5e3  parent 9e07
  ...
  invoke_agent Strands Agents          trace 3f9a1c  span 2a60  parent none

Lady Luck: Cordula rolled a 14 on her Read the Room check.
```

Find the tool call and the server span: `portal.roll_dice` has the same `trace` as `execute_tool roll_dice`, and its `parent` is that line's `span`. That parent link is the wire, drawn.

| you see | it means | fix |
|---|---|---|
| `ImportError` for `StrandsTelemetry` or `mcp_instrumentation` | Step 1 is missing or misspelled | check both names and the module path of the second |
| `SPANS` and then no lines | `light_the_portal` still ends with `pass` | Steps 2 and 3 |
| a screen of JSON for each span | `setup_console_exporter` was called without `formatter=one_line` | Step 2 |
| `portal.roll_dice` shows `parent none` and a different `trace` | `mcp_instrumentation()` did not run before the server started | Step 3, and call it before `start_portal_server()` |
| `the portal server did not come up on port 8004` | another program is using the port | stop that program, or change `PORT` at the top of the file |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Where the Spans Go Next

The console is the smallest exporter. The same `StrandsTelemetry` has `setup_otlp_exporter()`, which sends spans to any OpenTelemetry collector: that is how to watch the same tree in a trace viewer. The collector setup needs a running collector, so this encounter stops at the console. The [Traces](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/#local-development-setup) page has the local development setup.

## What It Costs

Tracing adds no Amazon Nova 2 Lite calls and no AWS charges: the spans are made in the Python process and printed to the terminal. The run itself is two Amazon Nova 2 Lite calls: one asks for the roll, one reports the result, about 1,000 input tokens and 100 output tokens each. Total: 2,000 input tokens at about $0.30 per million (about $0.0006) and 200 output tokens at about $2.50 per million (about $0.0005): about a tenth of a cent. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot kept:

- A Strands turn is a tree of OpenTelemetry spans: `invoke_agent`, `execute_event_loop_cycle`, `chat`, `execute_tool`
- `MCPClient` sends the trace context in every MCP call, and `mcp_instrumentation()` lets a server in the same process continue the trace
- `StrandsTelemetry().setup_console_exporter()` prints spans with no collector, and `formatter` shapes the line
- `trace_attributes` tags a trace so you can find it again
- Why the recorder goes on before the portal opens

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[FLIGHT RECORDER ONLINE]**
>
> Reward: You received a [Bronze Box]. Inside: a trace id, a parent span, and a small brass recorder with one dial labeled "Effortless" that reads zero.

Back to [Floor 4](../floor-4.md#floor-clear), or on to [Floor 5](../floor-5.md).
