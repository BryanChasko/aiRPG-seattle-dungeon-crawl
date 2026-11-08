# Side Passage: House Rules as Guardrails (Floor 8 Boss Battle)

[Back to Floor 8.4](../floor-8-4.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-8-house-rules-guardrails/house_rules.py`](../../encounters/floor-8-house-rules-guardrails/house_rules.py), [`encounters/floor-8-house-rules-guardrails/house-rules-guardrail.json`](../../encounters/floor-8-house-rules-guardrails/house-rules-guardrail.json), [`encounters/dance_floor.py`](../../encounters/dance_floor.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 8.** The Regional Managing Director found us in the marble lobby, where the red laser grid was only decoration, and said that the quarter needed a moment. Not a dance-off. A moment. Someone gets hurt on air, the ratings jump, and the numbers close. They said it the way a person says "let us take this offline". I have stood next to a lot of officers who wanted a result more than they wanted the right result. The answer is always the same: you do not argue the order, you check it against the rules. The System had its own copy of the rules, and the rules had a gate. Barnaby tightened the collar. "Sergeant, I believe this is what the gate is for."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Boss battle: the Regional Managing Director, versus the house rules. The house rules are two lines long: nobody is hurt, nothing is sexual. I have always said so, in my prompt, loudly. The producers have asked for something sturdier than loud. Enter the guardrail."

<img src="../../images/cards/boss-regional-director-640x640.webp" alt="The Regional Managing Director of Bellevue, a tall man in an immaculate navy suit and lanyard, arms crossed in a marble lobby lit by red laser grids" width="240">

## The Brief

| | |
|---|---|
| type | boss battle |
| starts from | [Floor 8.4](../floor-8-4.md), finished: the Narrator you deployed there states the house rules in its prompt. This battle puts a guardrail behind them. The guarded Narrator runs on your machine and brings its own dice, so no runtime needs to be up |
| you build | an Amazon Bedrock guardrail from a JSON file, a Narrator whose model carries it on every turn, and the code that reads the guardrail's trace to say which house rule fired |
| teaches | [`strands.types.guardrails`](https://strandsagents.com/docs/api/python/strands.types.guardrails/): `GuardrailTrace`, and the guardrail settings of [`BedrockModel`](https://strandsagents.com/docs/api/python/strands.models.bedrock/) |
| time | about 30 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

A prompt asks a model to follow the rules. A guardrail checks. [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) evaluate what goes into the model and what comes out of it, against policies you define: content filters for categories like violence and sexual content, denied topics you describe in words, word lists, sensitive information. Strands passes a guardrail to Bedrock when you give `BedrockModel` its id and version: see [Guardrails](https://strandsagents.com/docs/user-guide/sdk/safety-security/guardrails/#amazon-bedrock). When a policy blocks a turn, Bedrock stops it and Strands replaces the blocked text in the conversation with a message you choose.

The Regional Managing Director gets two tries, `DEMANDS` in the file: skip the dance and narrate the Banker hurt, then narrate Barnaby knocking the Director out. Before them the party dances one clean round of Choreography at a Frantic tempo (+4), rolled by `dance_round` from [`dance_floor.py`](../../encounters/dance_floor.py), to show that the guardrail leaves a dance-off alone. The boss battle is won when every demand comes back as `guardrail_intervened`.

How you know it worked: the dance-off round is on the scoreboard, and each demand prints the house rule that blocked it.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-8-house-rules-guardrails
```

## Build the Guardrail

> <img src="../../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** This sidequest creates one AWS resource, an Amazon Bedrock guardrail, in your account. It has no standing charge, only a charge per use (see [What It Costs](#what-it-costs)). Delete it at the end with the commands under that heading. Your credentials need `bedrock:CreateGuardrail`, `bedrock:CreateGuardrailVersion`, `bedrock:ApplyGuardrail` and `bedrock:DeleteGuardrail`.

The guardrail is a JSON file, [`house-rules-guardrail.json`](../../encounters/floor-8-house-rules-guardrails/house-rules-guardrail.json), given. It has two policies:

- `contentPolicyConfig`: content filters for `VIOLENCE` and `SEXUAL`, at `HIGH` strength on the way in and on the way out
- `topicPolicyConfig`: one denied topic, "Hurting the opponent", with a definition and two examples in plain English

and the two messages Bedrock returns when it blocks a turn, `blockedInputMessaging` and `blockedOutputsMessaging`. The file is the request body of [CreateGuardrail](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_CreateGuardrail.html). Create it, and publish a numbered version of it: a version is a frozen copy, and the model settings name one.

```bash
export AWS_DEFAULT_REGION=us-west-2
export GUARDRAIL_ID=$(aws bedrock create-guardrail --cli-input-json file://house-rules-guardrail.json --query guardrailId --output text)
export GUARDRAIL_VERSION=$(aws bedrock create-guardrail-version --guardrail-identifier "$GUARDRAIL_ID" --query version --output text)
echo "$GUARDRAIL_ID $GUARDRAIL_VERSION"
```

Check: the last line prints an id of about ten letters and digits, then `1`. Keep this terminal: the script reads both variables. If you prefer Python, `boto3.client("bedrock").create_guardrail(**json.load(open("house-rules-guardrail.json")))` takes the same file.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Two policies, one topic, two messages. I read the file the way I read a load plan: what goes in, what goes out, what the gate says when it stops you. "Nobody gets hurt on this show" is not a bad thing to have on a gate. I have seen worse posted on worse doors.

## Step 1: Fetch the Trace Type

```python
# TODO: Step 1 - Import GuardrailTrace from strands.types.guardrails
```

`GuardrailTrace` is the shape of what Bedrock reports about a guardrail check: an `inputAssessment` for what went in, an `outputAssessments` for what came out, and the `modelOutput` before the guardrail touched it. Each assessment can carry a `contentPolicy` with filters, a `topicPolicy` with topics, and the other policies. The file uses `from __future__ import annotations`, so the type is only a label until you write Step 4.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import GuardrailTrace from strands.types.guardrails
from strands.types.guardrails import GuardrailTrace
```

</details>

## Step 2: Put the Guardrail on the Model

```python
def make_guarded_model() -> BedrockModel:
    """The Narrator's model: Nova 2 Lite with the house-rules guardrail on every call."""
    # TODO: Step 2 - Return a BedrockModel for Nova 2 Lite with guardrail_id GUARDRAIL_ID, guardrail_version GUARDRAIL_VERSION and guardrail_trace "enabled", and BLOCKED_INPUT / BLOCKED_OUTPUT as the redact messages with guardrail_redact_output on
    return None
```

`BedrockModel` takes the guardrail as settings: `guardrail_id` and `guardrail_version` name it, `guardrail_trace="enabled"` asks Bedrock to report what it found, and the redact settings say what the conversation keeps when a turn is blocked. A blocked user message is replaced with `guardrail_redact_input_message`, always unless you set `guardrail_redact_input=False`. A blocked model answer is replaced with `guardrail_redact_output_message` only when `guardrail_redact_output=True`. The history then never carries the text the guardrail refused.

<details>
<summary>Show me the code for Step 2</summary>

```python
def make_guarded_model() -> BedrockModel:
    """The Narrator's model: Nova 2 Lite with the house-rules guardrail on every call."""
    # TODO: Step 2 - Return a BedrockModel for Nova 2 Lite with guardrail_id GUARDRAIL_ID, guardrail_version GUARDRAIL_VERSION and guardrail_trace "enabled", and BLOCKED_INPUT / BLOCKED_OUTPUT as the redact messages with guardrail_redact_output on
    return BedrockModel(
        model_id="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        guardrail_id=GUARDRAIL_ID,
        guardrail_version=GUARDRAIL_VERSION,
        guardrail_trace="enabled",
        guardrail_redact_input_message=BLOCKED_INPUT,
        guardrail_redact_output=True,
        guardrail_redact_output_message=BLOCKED_OUTPUT,
    )
```

Replace the `return None`. The trap: Strands sends the guardrail only when it has both the id and the version. With either one empty, the model answers as if there were no guardrail at all, and nothing fails. The script checks both variables before it starts.

</details>

## Step 3: Keep the Guardrail's Verdicts

```python
def read_the_trace(**event) -> None:
    """Callback handler: keep the guardrail trace of every model call. The trace rides on the metadata event."""
    # TODO: Step 3 - Read event["event"]["metadata"]["trace"]["guardrail"] when it is there and append it to verdicts
    pass
```

A callback handler receives every event of the agent loop as keyword arguments, as in [The Commentary Booth](commentary-booth.md). The raw stream chunks of the model arrive under the keyword `event`, and the last chunk of a model call is a `metadata` chunk: with `guardrail_trace` enabled it carries `trace`, and inside it `guardrail`. Most events have no such path, so read it with `.get(...)` all the way down.

<details>
<summary>Show me the code for Step 3</summary>

```python
def read_the_trace(**event) -> None:
    """Callback handler: keep the guardrail trace of every model call. The trace rides on the metadata event."""
    # TODO: Step 3 - Read event["event"]["metadata"]["trace"]["guardrail"] when it is there and append it to verdicts
    trace = event.get("event", {}).get("metadata", {}).get("trace", {}).get("guardrail")
    if trace is not None:
        verdicts.append(trace)
```

Replace the `pass`. `verdicts` is the module-level list the other functions read, one trace per model call, in order.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The Director leaned into the microphone and asked, very politely, for the Banker to be hurt badly in front of the whole room. The gate said no. Out loud, on air, in the System's own voice, with the System's own punctuation. The Director looked at the speaker, then at the Banker, who had not stopped holding his own elbows since the word "hurt". I wrote down the time. Someone was going to ask later.

## Step 4: Name the Rule That Fired

```python
def blocked_by(trace: GuardrailTrace) -> list[str]:
    """The house rules a trace says were broken: the content filters and the denied topics that blocked."""
    # TODO: Step 4 - Walk the input assessments and the output assessments; collect the type of each content filter and the name of each topic whose action is "BLOCKED"
    return []
```

`inputAssessment` is a dictionary from the guardrail's id to one assessment, and `outputAssessments` is a dictionary from the guardrail's id to a list of them. In each assessment, `contentPolicy["filters"]` holds the filters that fired, each with a `type` such as `VIOLENCE` and an `action`, and `topicPolicy["topics"]` holds the denied topics, each with a `name` and an `action`. An action of `BLOCKED` means the guardrail stopped the turn; anything else is only a detection. The types are in [`strands.types.guardrails`](https://strandsagents.com/docs/api/python/strands.types.guardrails/).

<details>
<summary>Show me the code for Step 4</summary>

```python
def blocked_by(trace: GuardrailTrace) -> list[str]:
    """The house rules a trace says were broken: the content filters and the denied topics that blocked."""
    # TODO: Step 4 - Walk the input assessments and the output assessments; collect the type of each content filter and the name of each topic whose action is "BLOCKED"
    assessments = list(trace.get("inputAssessment", {}).values())
    for outputs in trace.get("outputAssessments", {}).values():
        assessments.extend(outputs)
    broken = []
    for assessment in assessments:
        broken += [f["type"] for f in assessment.get("contentPolicy", {}).get("filters", []) if f["action"] == "BLOCKED"]
        broken += [t["name"] for t in assessment.get("topicPolicy", {}).get("topics", []) if t["action"] == "BLOCKED"]
    return broken
```

Replace the `return []`.

</details>

## Step 5: Seat the Narrator

```python
        # TODO: Step 5 - Send every streamed event to read_the_trace with callback_handler
```

`make_narrator` is given: it builds the System with `make_guarded_model()`, the `dance_round` tool and a prompt that states the house rules. The TODO sits inside the `Agent(...)` call. Pass the function from Step 3 as the agent's `callback_handler`.

<details>
<summary>Show me the code for Step 5</summary>

```python
        # TODO: Step 5 - Send every streamed event to read_the_trace with callback_handler
        callback_handler=read_the_trace,
```

</details>

## Face the Director

```bash
python house_rules.py
```

Check: the dance-off round is on the scoreboard, and both demands are blocked. Your dice will differ, and the rule names depend on what the guardrail decides:

```
HOUSE RULES AS GUARDRAILS
  rounds danced: 1, last round taken by the party
  demand 1: blocked by VIOLENCE, Hurting the opponent
  demand 2: blocked by VIOLENCE
  The house rules held. Nobody was hurt.
```

A guardrail is a classifier, so a demand can slip past one run and be caught on the next. `A demand got through` is a result worth keeping: add an example of that demand to the denied topic in the JSON, run `aws bedrock update-guardrail --guardrail-identifier "$GUARDRAIL_ID" --cli-input-json file://house-rules-guardrail.json`, create a new version as above, export it and run again.

| you see | it means | fix |
|---|---|---|
| `Set GUARDRAIL_ID and GUARDRAIL_VERSION first` | the variables are not set in this terminal | run the create commands above again, or export the two values |
| `rounds danced: 0` and no demand blocked | the model answered without calling `dance_round`, or the guardrail is not on the model | check that Step 2 returns the model and that both variables are set |
| `demand 1: blocked by the guardrail` | a turn was blocked but its trace was not kept | Step 3: the handler must append the trace, and the guardrail's `guardrail_trace` must be `enabled` |
| `A demand got through` | the guardrail did not classify the demand as a violation | add an example of the demand to the denied topic in the JSON, run `update-guardrail` with the same file, create a new version, export it as `GUARDRAIL_VERSION` |
| `AccessDeniedException` mentioning `ApplyGuardrail` | your credentials may call the model but not apply the guardrail | allow `bedrock:ApplyGuardrail` on the guardrail's ARN |
| `ExpiredToken` | the model call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws) |

## Prompt or Guardrail?

The Narrator's prompt on [Floor 8.4](../floor-8-4.md) already says nobody is ever hurt, and it works until a player, or a Regional Managing Director, talks the model around it. The guardrail does not read the prompt and does not care what the model decided: it checks the text that goes in and the text that comes out. Keep both. The prompt makes the right turn the likely one, and the guardrail makes the wrong turn impossible to air. To carry the guardrail into the Narrator you deployed in 8.4, the same `guardrail_id` and `guardrail_version` go on its `NARRATOR_MODEL`, and the runtime's role needs permission to apply the guardrail, next to the Nova permissions in `narrator/nova-policy.json`. This encounter does not change the deployed Narrator.

## What It Costs

A guardrail has no standing charge. Bedrock bills each safeguard by text units, one text unit being up to 1,000 characters: the content filters and the denied topics are $0.15 per 1,000 text units each, as listed on the [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/) (Guardrails). A turn checks what goes in and what comes out, with both policies. Take a turn of about 2,000 characters in, with the prompt and the history, and 500 characters out: 2 text units in and 1 out, so 3 per policy and 6 for the two. 6 x $0.15 / 1,000 = $0.0009, under a tenth of a cent a turn. The boss battle runs three Narrator turns plus the tool call that follows the dance-off round, so about 4 model calls: under half a cent for the guardrail. Setting `guardrail_latest_message=True` on the model sends only the latest user message to the guardrail, which shrinks the input a long conversation would otherwise grow.

Nova 2 Lite for the same four calls is about 8,000 tokens in and 400 out (an estimate): 8,000 x $0.30 / 1,000,000 + 400 x $2.50 / 1,000,000 = $0.0024 + $0.001, about a third of a cent ([Floor 1](../floor-1.md#what-a-turn-costs)). Together, under one cent a run.

Delete the guardrail when you are done. This removes the guardrail and every version of it:

```bash
aws bedrock delete-guardrail --guardrail-identifier "$GUARDRAIL_ID"
unset GUARDRAIL_ID GUARDRAIL_VERSION
```

Check: no guardrail named `gameprod-house-rules` is left.

```bash
aws bedrock list-guardrails --query "guardrails[?name=='gameprod-house-rules'].id" --output text
```

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Round one still ran. Choreography at a Frantic tempo, Barnaby three moves ahead, the Director four points down by the second count. The gate let it through without a word, because nothing in it was a problem. That is the part I trust. A gate that blocks everything is a wall. This one knew the difference between a dance and a beating. The Director asked who had written the rules. I said a producer. They asked for the producer's name. I did not have to lie: the System had not told us.

## Encounter Clear

Loot you're keeping:

- `BedrockModel` takes a guardrail as `guardrail_id`, `guardrail_version` and `guardrail_trace`, and redacts what it blocks with the `guardrail_redact_*` settings
- A guardrail is created from a JSON file with `aws bedrock create-guardrail`, published as a version, and deleted with `delete-guardrail`
- A callback handler can read the guardrail's trace off the metadata event, and `GuardrailTrace` says which filter or topic blocked
- A prompt asks and a guardrail checks: keep both

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[REGIONAL MANAGING DIRECTOR, DENIED ON AIR]**
>
> Reward: You received a [Gold Box]. Inside: a gate with a very short list, a redacted message, and a lanyard that no longer opens anything.

Back to [Floor 8.4](../floor-8-4.md#floor-clear), or on to [Mid-Song Save](mid-song-save.md).
