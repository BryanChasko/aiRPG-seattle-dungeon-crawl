"""Floor 8 encounter, The Broadcast Booth: stamp each dance-off round with span attributes and read them back in Amazon CloudWatch.

The System AI broadcasts every round, and a broadcast keeps a log. Here each round is danced through the shared
dance floor and traced: the agent's spans carry the round number and the Move Call, one span wraps the whole
round and records who won, and the agent's metrics become a small receipt. Run under the AWS Distro for
OpenTelemetry, the spans reach CloudWatch, where --read-back finds them again by those attributes.

Run it from this folder, with the workshop environment active (the page sets the OpenTelemetry variables first):
    opentelemetry-instrument python broadcast_booth.py
    python broadcast_booth.py --read-back
"""

import sys
import time
from pathlib import Path

import boto3
from strands import Agent
# TODO: Step 1 - Import get_tracer from strands.telemetry.tracer and metrics_to_string from strands.telemetry.metrics
from strands.telemetry.tracer import get_tracer
from strands.telemetry.metrics import metrics_to_string

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # the shared dance floor lives in encounters/
from dance_floor import dance_round, scoreboard

OPPONENT = "the Bonus-Season Investment Banker"
ROUNDS = [(1, "Presence", "Barnaby"), (2, "Footwork", "Cordula")]  # round number, Move Call, who dances for the party

# Logs Insights query over the shared span log group: the rounds, found again by the attributes this file sets
SPAN_QUERY = (
    "fields @timestamp, `attributes.dance.round` as round, `attributes.dance.move_call` as move_call, "
    "`attributes.dance.winner` as winner "
    "| filter name = 'broadcast.round' "
    "| sort @timestamp asc"
)


def make_booth(round_number: int, move_call: str, crawler: str) -> Agent:
    """One Lady Luck for one round: the same model, tool and prompt every time; only the round changes."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        name="broadcast-booth",
        tools=[dance_round],
        system_prompt=f"""You are Lady Luck, the System AI's croupier subroutine, calling round {round_number} of a dance-off against
{OPPONENT}. Call dance_round once with opponent="{OPPONENT}", move_call="{move_call}", crawler="{crawler}",
opponent_modifier=2, tempo="Driving". Then report each side as die + modifier = total and name who took the round,
in two sentences. Never roll or decide anything yourself. Plain text only, no emoji.""",
        # TODO: Step 2 - Stamp every span of this agent with trace_attributes: dance.round, dance.move_call and dance.opponent
        trace_attributes={"dance.round": round_number, "dance.move_call": move_call, "dance.opponent": OPPONENT},
        callback_handler=None,
    )


def run_round(round_number: int, move_call: str, crawler: str):
    """Dance one round and return the agent's result."""
    return make_booth(round_number, move_call, crawler)(f"Round {round_number}: {move_call} against {OPPONENT}. Call it.")


def broadcast_round(round_number: int, move_call: str, crawler: str):
    """Dance one round inside a span of its own, so the whole round shows up as one line in CloudWatch."""
    # TODO: Step 3 - Run run_round inside a span named "broadcast.round" opened with get_tracer().tracer.start_as_current_span; set dance.round and dance.move_call on it first, and dance.winner from the scoreboard after the round
    with get_tracer().tracer.start_as_current_span("broadcast.round") as span:
        span.set_attribute("dance.round", round_number)
        span.set_attribute("dance.move_call", move_call)
        result = run_round(round_number, move_call, crawler)
        span.set_attribute("dance.winner", scoreboard[-1]["winner"] if scoreboard else "none")
    return result


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


def read_back(minutes: int = 30) -> list[dict]:
    """Ask CloudWatch Logs Insights for the broadcast.round spans of the last few minutes."""
    logs = boto3.client("logs")
    now = int(time.time())
    query_id = logs.start_query(
        logGroupName="aws/spans", startTime=now - minutes * 60, endTime=now, queryString=SPAN_QUERY, limit=20,
    )["queryId"]
    while True:
        answer = logs.get_query_results(queryId=query_id)
        if answer["status"] in ("Complete", "Failed", "Cancelled", "Timeout"):
            break
        time.sleep(1)
    return [{cell["field"]: cell["value"] for cell in row if not cell["field"].startswith("@ptr")} for row in answer["results"]]


if __name__ == "__main__":
    if "--read-back" in sys.argv:
        rows = read_back()
        print(f"{len(rows)} broadcast.round spans in the last 30 minutes")
        for row in rows:
            print(f"  round {row.get('round')}: {row.get('move_call')} -> {row.get('winner')}")
        sys.exit(0)
    for round_number, move_call, crawler in ROUNDS:
        result = broadcast_round(round_number, move_call, crawler)
        danced = scoreboard[-1] if scoreboard else None
        print(f"\nROUND {round_number}, {move_call}: {danced['crawler'] if danced else 'no roll'} against "
              f"{danced['opponent_roll'] if danced else 'no roll'} -> {danced['winner'] if danced else 'none'}")
        print(f"  receipt: {round_receipt(result)}")
        print(f"  {metrics_to_string(result.metrics)}")
    print("\nGive the spans a minute or two to land, then: python broadcast_booth.py --read-back")
