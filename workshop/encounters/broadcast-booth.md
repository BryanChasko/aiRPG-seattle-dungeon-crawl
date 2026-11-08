# Side Passage: The Broadcast Booth (Floor 8 Sidequest)

[Back to Floor 8.4](../floor-8-4.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-8-broadcast-booth/broadcast_booth.py`](../../encounters/floor-8-broadcast-booth/broadcast_booth.py), [`encounters/dance_floor.py`](../../encounters/dance_floor.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 8.** Behind the glass wall of the Bellevue conference room there was a second room, smaller, dark, full of blinking gear. A broadcast booth. Somebody had labeled every dial with masking tape and a marker, which I respect. The System keeps a log of every round it airs, it told us, and a log is only worth something if you can find the line you want in it. I asked how it files a round. By number, by move, by who won, it said. I asked who reads the log. The producers, it said, and a very small number of accountants. Barnaby was already looking at the dials. "Sergeant. We are being recorded. I should like to be recorded correctly."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Sidequest: the Broadcast Booth. Every round of every dance-off is stamped with its number and its Move Call, wrapped in a span of its own, and filed in Amazon CloudWatch. The producers will be searching it by Friday. Label things properly. The System hates a bad label."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 8.4](../floor-8-4.md), finished: the deployment turned on Transaction Search for the account, which CloudWatch needs to keep spans. The booth runs on the learner's machine and brings its own dice |
| build | a dance-off round that carries its round number and Move Call on every span, one span of its own that records the winner, a receipt read from the agent's metrics, and a query that finds the rounds again in CloudWatch |
| teaches | [`strands.telemetry.tracer`](https://strandsagents.com/docs/api/python/strands.telemetry.tracer/): `get_tracer`, and [`strands.telemetry.metrics`](https://strandsagents.com/docs/api/python/strands.telemetry.metrics/): `EventLoopMetrics`, `metrics_to_string` |
| time | about 25 minutes, plus a few minutes for the spans to land |
| model | Amazon Nova 2 Lite, as on every floor |

Every Strands agent already emits [traces](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/): OpenTelemetry spans for the turn, for each trip around the agent loop, for each model call and for each tool call. What the SDK cannot know is what a round means in the game. Two tools put the round's meaning on the spans. The `trace_attributes` parameter of `Agent` stamps attributes on every span the agent makes, and the SDK's tracer accepts spans from the booth code, so one span can wrap a whole round and carry facts only the booth code has, like the winner. See [Custom Attribute Tracking](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/#custom-attribute-tracking) and [Custom Spans](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/#custom-spans).

The same agent also keeps [metrics](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/metrics/): cycles, tool calls, tokens, latency. The metrics sit on the result of every turn, in `result.metrics`, and `get_summary()` turns them into a dictionary Python code can read.

The booth runs on the learner's machine, under the AWS Distro for OpenTelemetry, which sends the spans to CloudWatch. On [Floor 8.4, Part 4](../floor-8-4.md#part-4-see-what-your-agents-do) the deployed runtimes did that automatically; here, switch the exporter on by hand, in six environment variables. Reading the rounds back is a CloudWatch Logs Insights query, run from Python.

How to check it worked: each round prints one line and a receipt, and a minute or two later `--read-back` lists the same rounds from CloudWatch, found by the `dance.winner` attribute the `broadcast.round` span carried.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-8-broadcast-booth
```

## Wire the Booth to CloudWatch

> <img src="../../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** This sidequest creates one AWS resource, a CloudWatch log group, and sends spans to the account's shared span log group, `aws/spans`. The log group and the span ingestion both bill by the byte. Delete the log group at the end, with the commands in [What It Costs](#what-it-costs).

The AWS Distro for OpenTelemetry is not in the workshop environment: the deployed runtimes install the distro from their own `pyproject.toml`, and this booth runs on the learner's machine. Add the distro to the active environment, the same version the runtimes use (a uv environment has no `pip`, so use `uv pip`):

```bash
uv pip install "aws-opentelemetry-distro~=0.21.0"
```

Create a log group and a log stream for the booth, then set the OpenTelemetry variables in the terminal that will run the booth. These six variables come from the AgentCore guide for agents hosted outside AgentCore Runtime: see [Get started with AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-get-started.html).

```bash
export AWS_DEFAULT_REGION=us-west-2
aws logs create-log-group --log-group-name /aws/gameprod/broadcast-booth
aws logs create-log-stream --log-group-name /aws/gameprod/broadcast-booth --log-stream-name booth
export AGENT_OBSERVABILITY_ENABLED=true
export OTEL_PYTHON_DISTRO=aws_distro
export OTEL_PYTHON_CONFIGURATOR=aws_configurator
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=/aws/gameprod/broadcast-booth,x-aws-log-stream=booth,x-aws-metric-namespace=gameprod
export OTEL_RESOURCE_ATTRIBUTES=service.name=broadcast-booth
```

`service.name` is the name the CloudWatch GenAI Observability dashboard lists the booth under. The spans themselves go to the `aws/spans` log group, where Transaction Search keeps them.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Six exports and a log group. I wrote them on the back of my hand, under the version number from Floor 8. A booth with no cable run to the truck is a very expensive closet. So I ran the cable first, and checked the other end of it before we went on air.

## Step 1: Fetch the Tracer and the Metrics Printer

```python
# TODO: Step 1 - Import get_tracer from strands.telemetry.tracer and metrics_to_string from strands.telemetry.metrics
```

`get_tracer()` returns the tracer the Strands SDK itself uses, the same one that makes the `invoke_agent` and `chat` spans. Its `tracer` attribute is the OpenTelemetry tracer underneath, and spans opened on it join the agent's trace. `metrics_to_string` turns the metrics of a result into a printable summary. The module pages are [`strands.telemetry.tracer`](https://strandsagents.com/docs/api/python/strands.telemetry.tracer/) and [`strands.telemetry.metrics`](https://strandsagents.com/docs/api/python/strands.telemetry.metrics/).

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import get_tracer from strands.telemetry.tracer and metrics_to_string from strands.telemetry.metrics
from strands.telemetry.tracer import get_tracer
from strands.telemetry.metrics import metrics_to_string
```

</details>

## Step 2: Stamp the Agent's Spans

```python
        # TODO: Step 2 - Stamp every span of this agent with trace_attributes: dance.round, dance.move_call and dance.opponent
```

`make_booth` is given: it builds one Lady Luck for one round, with `dance_round` as her tool and a prompt that tells her to call it once. The TODO sits inside the `Agent(...)` call. `trace_attributes` takes a dictionary of names and values and adds them to every span the agent makes: the turn, the cycles, the model calls and the tool call. Values must be strings, numbers or booleans.

<details>
<summary>Show me the code for Step 2</summary>

```python
        # TODO: Step 2 - Stamp every span of this agent with trace_attributes: dance.round, dance.move_call and dance.opponent
        trace_attributes={"dance.round": round_number, "dance.move_call": move_call, "dance.opponent": OPPONENT},
```

The dots in the names are plain characters; the names only look like a hierarchy. Keep the dots: CloudWatch shows them as `attributes.dance.round`, and so does the query.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Round one went to the Bonus-Season Investment Banker's Presence. Barnaby took the mic, +3 against their +4, and the dial labeled ROUND went to one. The dial labeled MOVE went to Presence. Every wire off that board carried both labels. That is how you find a particular wire at two in the morning.

## Step 3: Wrap the Round in a Span

```python
    # TODO: Step 3 - Run run_round inside a span named "broadcast.round" opened with get_tracer().tracer.start_as_current_span; set dance.round and dance.move_call on it first, and dance.winner from the scoreboard after the round
    return run_round(round_number, move_call, crawler)
```

The attributes of Step 2 ride on the agent's spans, but the agent does not know who won: `dance_round` rolls the dice, and the winner lands on the shared `scoreboard` after the tool ran. So each round gets a span of its own. `start_as_current_span` opens a span and makes it the current one, so the agent's spans become its children, and closes it when the `with` block ends. `span.set_attribute` adds a fact. That span now holds the round, the Move Call and the winner, and the query looks for that span.

<details>
<summary>Show me the code for Step 3</summary>

```python
def broadcast_round(round_number: int, move_call: str, crawler: str):
    """Dance one round inside a span of its own, so the whole round shows up as one line in CloudWatch."""
    # TODO: Step 3 - Run run_round inside a span named "broadcast.round" opened with get_tracer().tracer.start_as_current_span; set dance.round and dance.move_call on it first, and dance.winner from the scoreboard after the round
    with get_tracer().tracer.start_as_current_span("broadcast.round") as span:
        span.set_attribute("dance.round", round_number)
        span.set_attribute("dance.move_call", move_call)
        result = run_round(round_number, move_call, crawler)
        span.set_attribute("dance.winner", scoreboard[-1]["winner"] if scoreboard else "none")
    return result
```

Replace the `return run_round(...)` line. The `"none"` covers a round where Lady Luck answered without calling the tool: the span still gets filed, and the query shows the gap.

</details>

## Step 4: Read the Receipt

```python
    # TODO: Step 4 - Read result.metrics.get_summary() and return model_cycles, dance_round_calls, input_tokens and output_tokens
    return {}
```

`result.metrics` is an `EventLoopMetrics`. `EventLoopMetrics.get_summary()` returns a dictionary: `total_cycles`, the `tool_usage` of each tool with the `execution_stats` of that tool, and the `accumulated_usage` with `inputTokens` and `outputTokens`. See [Agent Loop Metrics](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/metrics/#agent-loop-metrics) and [Tool Metrics](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/metrics/#tool-metrics). A round that works prints two cycles, one `dance_round` call, and the tokens of both model calls.

<details>
<summary>Show me the code for Step 4</summary>

```python
def round_receipt(result) -> dict:
    """What the round did and cost, read from the agent's metrics."""
    # TODO: Step 4 - Read result.metrics.get_summary() and return model_cycles, dance_round_calls, input_tokens and output_tokens
    summary = result.metrics.get_summary()
    usage = summary["accumulated_usage"]
    calls = summary["tool_usage"].get("dance_round", {}).get("execution_stats", {}).get("call_count", 0)
    return {
        "model_cycles": summary["total_cycles"],
        "dance_round_calls": calls,
        "input_tokens": usage["inputTokens"],
        "output_tokens": usage["outputTokens"],
    }
```

Replace the `return {}`. `tool_usage` has no entry for a tool that never ran, so the lookup uses `.get` and a round without a roll reports zero calls instead of failing.

</details>

## Run the Booth

Run it under `opentelemetry-instrument`, so the distro wires the exporters before `broadcast_booth.py` starts:

```bash
opentelemetry-instrument python broadcast_booth.py
```

Check: two rounds, each with a line, a receipt and the metrics summary. Dice and totals will differ:

```
ROUND 1, Presence: Barnaby: 12 + 3 = 15 against the Bonus-Season Investment Banker: 8 + 4 = 12 -> party
  receipt: {'model_cycles': 2, 'dance_round_calls': 1, 'input_tokens': 1480, 'output_tokens': 96}
  Event Loop Metrics Summary:
  ...

ROUND 2, Footwork: Cordula: 6 + 1 = 7 against the Bonus-Season Investment Banker: 13 + 4 = 17 -> opponent
  receipt: {'model_cycles': 2, 'dance_round_calls': 1, 'input_tokens': 1495, 'output_tokens': 88}
  ...
Give the spans a minute or two to land, then: python broadcast_booth.py --read-back
```

Wait a couple of minutes, then read the rounds back from CloudWatch:

```bash
python broadcast_booth.py --read-back
```

Check: the same rounds, found by their attributes (example output):

```
2 broadcast.round spans in the last 30 minutes
  round 1: Presence -> party
  round 2: Footwork -> opponent
```

`--read-back` runs a Logs Insights query over `aws/spans`: it filters on the span name `broadcast.round` and lists `attributes.dance.round`, `attributes.dance.move_call` and `attributes.dance.winner`. Change the filter and the same attributes answer other questions about the rounds: the rounds one Move Call lost, the rounds that never rolled. See [Analyzing log data with CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html). Open the CloudWatch console, Transaction Search, and filter on `service.name` `broadcast-booth` to see the whole tree of a round, with the `broadcast.round` span at the top and the agent's spans under it.

| you see | it means | fix |
|---|---|---|
| `0 broadcast.round spans` | the spans have not landed, or never left | wait two more minutes and run `--read-back` again; then check that the booth ran under `opentelemetry-instrument` with the six variables set in that same terminal |
| `opentelemetry-instrument: command not found` | the distro is not installed in the active environment | `uv pip install "aws-opentelemetry-distro~=0.21.0"` |
| `ResourceNotFoundException` from `--read-back` | `aws/spans` does not exist: Transaction Search was never turned on in this account and region | finish [Floor 8.4](../floor-8-4.md), or see Enable Transaction Search under the warnings of [8.4, Part 4](../floor-8-4.md#part-4-see-what-your-agents-do) |
| `receipt: {'model_cycles': 1, 'dance_round_calls': 0 ...}` and `no roll` | Lady Luck answered without calling the tool | run the booth again; the prompt tells her to call `dance_round` once |
| `NameError: name 'get_tracer' is not defined` | Step 1 is missing | add the two imports |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call or a CloudWatch call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Booth or Portal?

[Trace the Portal](trace-the-portal.md) on Floor 4 prints spans to the console with `StrandsTelemetry`, to see how a trace is built. The booth keeps the spans, and adds meaning to each one: attributes on the agent's own spans, one span of your own, and a query on the far end. Use the console when you are learning what the SDK emits. Use the booth when someone else has to find a round in a week.

## What It Costs

Nova 2 Lite: each round is two Amazon Nova 2 Lite calls of a short prompt, about 1,500 input tokens and 100 output tokens in all (an estimate). At about $0.30 per million input tokens and $2.50 per million output tokens ([Floor 1](../floor-1.md#what-a-turn-costs)) that is 1,500 x $0.30 / 1,000,000 + 100 x $2.50 / 1,000,000 = $0.00045 + $0.00025, under a tenth of a cent a round.

CloudWatch bills the telemetry at the rates on the [CloudWatch pricing page](https://aws.amazon.com/cloudwatch/pricing/), the same ones as [What Floor 8 Costs](../floor-8.md#what-floor-8-costs): about $0.35 per GB of spans ingested, $0.50 per GB of logs ingested, $0.03 per GB-month stored. A round makes about seven spans of a couple of kilobytes each, so about 15 KB (an estimate): 2 rounds x 15 KB = 30 KB, or $0.00001 of spans. A Logs Insights query is billed at $0.005 per GB scanned beyond a monthly allowance of five times your ingestion; `--read-back` scans a few kilobytes. AgentCore Observability has no charge of its own: it bills the CloudWatch usage ([AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/), Observability).

The log group never expires and the spans stay in `aws/spans`. Delete the log group and the environment variables, from the terminal where the variables were set:

```bash
aws logs delete-log-group --log-group-name /aws/gameprod/broadcast-booth
unset AGENT_OBSERVABILITY_ENABLED OTEL_PYTHON_DISTRO OTEL_PYTHON_CONFIGURATOR OTEL_EXPORTER_OTLP_PROTOCOL OTEL_EXPORTER_OTLP_LOGS_HEADERS OTEL_RESOURCE_ATTRIBUTES
uv pip uninstall aws-opentelemetry-distro
```

Check: the command prints nothing.

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/gameprod/broadcast-booth --query 'logGroups[].logGroupName' --output text
```

`aws/spans` belongs to Transaction Search for the whole account, and the deployed runtimes of Floor 8 write spans to `aws/spans` too. If nothing else in the account needs those spans, shorten how long `aws/spans` keeps the spans: `aws logs put-retention-policy --log-group-name aws/spans --retention-in-days 1`. Otherwise leave the retention unchanged. The [Cleanup](../cleanup.md) page removes the runtimes.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The producers searched the log on Friday, as promised. They asked for every round Barnaby lost on Footwork. One query, zero rows. Barnaby read the empty result twice, pleased, and then asked me to check that the query was right. It was. He asked me to check the query again.

## Encounter Clear

Loot to keep:

- `trace_attributes` stamps what the booth code knows on every span an agent makes
- `get_tracer().tracer.start_as_current_span` puts a span of your own around a unit of work, with facts only the booth code has
- `result.metrics.get_summary()` is the receipt of a turn, as a dictionary
- Spans from outside AgentCore Runtime reach CloudWatch through the AWS Distro for OpenTelemetry, and a Logs Insights query finds them by attribute

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[LABELED, FILED AND FINDABLE]**
>
> Reward: You received a [Silver Box]. Inside: a roll of masking tape, a permanent marker, and a log group with your name on it that you will remember to delete.

Back to [Floor 8.4](../floor-8-4.md#floor-clear), or on to [House Rules as Guardrails](house-rules-guardrails.md).
