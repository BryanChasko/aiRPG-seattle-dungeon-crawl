# Side Passage: The Reasoning Dial (Floor 1 Boss Battle)

[Back to Floor 1](../floor-1.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-1-reasoning-dial/reasoning_dial.py`](../../encounters/floor-1-reasoning-dial/reasoning_dial.py), [`encounters/dance_floor.py`](../../encounters/dance_floor.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, DAY 1, WEDNESDAY, JUNE 17, SIDE PASSAGE OFF FLOOR 1.** The Bonus-Season Investment Banker was waiting under the Pier 59 clock, fleece vest zipped to the chin, and the System AI's voice was doing something I had not heard before. It was fast for the heckling and slow for the rulings. Barnaby found the cause on the collar's service panel: a brass dial with two marks, QUICK and CAREFUL. "One mind, Sergeant, two settings. The Narrator turns the knob itself, and for most of a bout it leaves the dial on QUICK. A good crew chief does not torque every bolt to spec, only the ones that hold a wing on."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Boss battle: the Bonus-Season Investment Banker. They have synergies. The party has a dial. The Narrator will think hard about exactly one thing today, and it will be whether the party tied. Do not make me think hard about anything else."

<img src="../../images/cards/opponent-banker-640x640.webp" alt="The Bonus-Season Investment Banker, a young man in a fleece vest over a dress shirt, slipping mid-spin on a wet floor as his sunglasses fly off" width="240">

## The Brief

| | |
|---|---|
| type | boss battle |
| starts from | [Floor 1](../floor-1.md), finished; this page brings its own dice, so no server needs to be running |
| build | a router over two settings of Amazon Nova 2 Lite: reasoning off for banter and plain rounds, reasoning on for a close Final Beat, a classifier that picks, and a fallback that drops back to reasoning off when the deeper turn times out |
| teaches | [`strands.models.routing.router`](https://strandsagents.com/docs/api/python/strands.models.routing.router/), [`strands.models.routing.classifier_strategy`](https://strandsagents.com/docs/api/python/strands.models.routing.classifier_strategy/), [`strands.models.routing.fallback_strategy`](https://strandsagents.com/docs/api/python/strands.models.routing.fallback_strategy/) |
| time | about 25 minutes |
| model | Amazon Nova 2 Lite, as on every floor, in both settings and in the classifier |

Amazon Nova 2 Lite can answer straight away or think first. Thinking is a setting on the request, not a different model: the Narrator on Floor 5 turns reasoning on with `additional_request_fields={"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}}` on the Narrator's `BedrockModel`, as the [code comment in the Floor 5 Narrator](../../5_a2a_integration/agents/narrator_orchestrator/narrator_orchestrator.py) explains. Thinking costs time and output tokens, and most of a dance-off needs no thinking. A heckle needs no thinking. A Final Beat that decides the whole bout might need it.

A `ModelRouter` holds several candidates and lets a strategy choose one candidate for each turn. A candidate is a `RoutingCandidate`: a model with a name and a description. The strategy reads the candidate descriptions. The `ClassifierStrategy` asks a model to read the latest request and pick a candidate. The `FallbackStrategy` picks the healthiest candidate that has not failed yet, and the router asks the strategy again after a failed call. A router takes one strategy, and the banker fight needs both: the classifier to open each turn, the fallback to rescue it. The file supplies `DialStrategy`, a short class that hands the opening choice to the classifier and every choice after a failure to the fallback, and logs which candidate was picked. See [How Model Routing Works](https://strandsagents.com/docs/user-guide/sdk/model-providers/model-routing/#how-model-routing-works), [Route Each Request by Content](https://strandsagents.com/docs/user-guide/sdk/model-providers/model-routing/#route-each-request-by-content), [Route Failures to a Backup Model](https://strandsagents.com/docs/user-guide/sdk/model-providers/model-routing/#route-failures-to-a-backup-model) and [Build a Custom Routing Strategy](https://strandsagents.com/docs/user-guide/sdk/model-providers/model-routing/#build-a-custom-routing-strategy).

The bout is three turns, and the dial should move on the third:

| turn | request | the dial should pick |
|---|---|---|
| banter | the banker asks Cordula about synergy; heckle back | quick |
| a round | Footwork against the banker, rolled with `dance_round` | quick |
| the Final Beat | the last round finished level; call the drum and rule on the winner | deep |

The dice come from [`dance_floor.py`](../../encounters/dance_floor.py), and the Final Beat is the one in the [Crawl Handbook](../world/crawl-handbook/04-final-beat.md): both sides roll, the total closest to 20 without going over wins. The party wins the bout by taking the Final Beat.

Success check: each turn prints which candidate the dial chose, quick for the first two and deep for the third, and the Final Beat turn is the slowest.

Change to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-1-reasoning-dial
```

## Step 1: Import the Router

```python
# TODO: Step 1 - Import ModelRouter and RoutingCandidate from strands.models.routing.router, ClassifierStrategy from strands.models.routing.classifier_strategy and FallbackStrategy from strands.models.routing.fallback_strategy
```

Three modules, four names. The package `strands.models.routing` also re-exports all four names, but the modules are where the SDK documents each name.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import ModelRouter and RoutingCandidate from strands.models.routing.router, ClassifierStrategy from ...
from strands.models.routing.router import ModelRouter, RoutingCandidate
from strands.models.routing.classifier_strategy import ClassifierStrategy
from strands.models.routing.fallback_strategy import FallbackStrategy
```

</details>

## Step 2: The Quick Candidate

```python
# TODO: Step 2 - Build the quick candidate: a RoutingCandidate around a BedrockModel with model_id "us.amazon.nova-2-lite-v1:0" and reasoning off, named "quick", described by QUICK_DESCRIPTION
quick = None
```

`RoutingCandidate(model, name=..., description=...)` wraps a `BedrockModel`. The name shows up in logs and in `dial.log`. The description is what the classifier reads, so the description says when to use this candidate: the file supplies `QUICK_DESCRIPTION` and `DEEP_DESCRIPTION`. Reasoning off is the default, so the quick candidate's model is the plain `BedrockModel(model_id="us.amazon.nova-2-lite-v1:0")`. Candidates are listed in order, and the first is the router's default: when the classifier cannot decide, the turn runs on quick.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Build the quick candidate: a RoutingCandidate around a BedrockModel with model_id ...
quick = RoutingCandidate(
    BedrockModel(model_id="us.amazon.nova-2-lite-v1:0"),  # Amazon Nova 2 Lite, US cross-Region inference profile
    name="quick",
    description=QUICK_DESCRIPTION,
)
```

Replace `quick = None`.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The banker opened with a sentence about monetizing the dance floor as an asset class. The collar answered before they finished it. One line, no pause, a heckle about the vest. The crowd on the pier laughed at the speed as much as the joke.

## Step 3: The Deep Candidate

```python
# TODO: Step 3 - Build the deep candidate: the same model with additional_request_fields={"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}} and a boto_client_config of Config(read_timeout=DEEP_PATIENCE_SECONDS, retries={"total_max_attempts": 1, "mode": "standard"}), named "deep", described by DEEP_DESCRIPTION
deep = None
```

The same model id, a second `BedrockModel` object, and two extra arguments. `additional_request_fields` carries the reasoning setting to Amazon Bedrock. `boto_client_config` is a botocore `Config`: `read_timeout` is how many seconds the connection may stay silent before the call fails, and `retries` with `total_max_attempts` of 1 stops botocore from trying the slow call again before the router can step in. A timed-out call is a failed call, and a failed call is what wakes the fallback.

Why build a second `BedrockModel` instead of reusing the one in `quick`? The router keeps a health record for each candidate, so the router refuses one `BedrockModel` behind two candidates and raises a `ValueError`. Build two `BedrockModel` objects.

<details>
<summary>Show me the code for Step 3</summary>

```python
# TODO: Step 3 - Build the deep candidate: the same model with additional_request_fields=... and a boto_client_config of ...
deep = RoutingCandidate(
    BedrockModel(
        model_id="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        additional_request_fields={"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}},
        boto_client_config=Config(read_timeout=DEEP_PATIENCE_SECONDS, retries={"total_max_attempts": 1, "mode": "standard"}),
    ),
    name="deep",
    description=DEEP_DESCRIPTION,
)
```

Replace `deep = None`. The timeout is a read timeout, so the timer measures silence, not the length of the whole turn. A deep turn that keeps streaming for a minute is not timed out.

</details>

## Step 4: The Dial

```python
# TODO: Step 4 - Build the dial: a DialStrategy of a ClassifierStrategy and a FallbackStrategy, as dial. The classifier runs on its own BedrockModel with model_id "us.amazon.nova-2-lite-v1:0", system_prompt=DIAL_POLICY and timeout=15
dial = None
```

`DialStrategy(classifier, fallback)` comes with the file. Build the two strategies that go inside it. `ClassifierStrategy(model, system_prompt=..., timeout=...)` needs its own `BedrockModel` to classify, and the crawl runs one model, so the classifier uses Amazon Nova 2 Lite too, with reasoning off: a third `BedrockModel`, not one of the two candidates. `DIAL_POLICY` is the routing policy in plain words: pick deep only for a close call. The `timeout` is in seconds. If the classifier fails or runs out of time, the classifier declines, and the turn runs on the first candidate, so a broken classifier leaves the dial on quick and the bout continues. `FallbackStrategy()` takes no arguments.

<details>
<summary>Show me the code for Step 4</summary>

```python
# TODO: Step 4 - Build the dial: a DialStrategy of a ClassifierStrategy and a FallbackStrategy, as dial. ...
dial = DialStrategy(
    ClassifierStrategy(
        BedrockModel(model_id="us.amazon.nova-2-lite-v1:0"),  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=DIAL_POLICY,
        timeout=15,
    ),
    FallbackStrategy(),
)
```

Replace `dial = None`.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Barnaby read the dial's policy out loud, because Barnaby cannot resist a posted rule. Choose the deep setting only for a close call. Everything else goes to quick. He said it was the first rule posted about how the Narrator thinks that I would have signed. Then he asked who decides what counts as close, and I pointed at the descriptions. The classifier reads them. I wrote them. I took the job seriously.

## Step 5: The Router

```python
# TODO: Step 5 - Build the router: a ModelRouter over quick and deep with dial as its strategy, as router
router = None
```

`ModelRouter([quick, deep], strategy=dial)`. A router is not a model, but an `Agent` accepts a router wherever it accepts a model: `make_system()` passes `model=router` to the `Agent`. From there the router drives each turn: it asks the strategy once per turn, and again after any failed call. See [Configure Model Routing](https://strandsagents.com/docs/user-guide/sdk/model-providers/model-routing/#configure-model-routing).

<details>
<summary>Show me the code for Step 5</summary>

```python
# TODO: Step 5 - Build the router: a ModelRouter over quick and deep with dial as its strategy, as router
router = ModelRouter([quick, deep], strategy=dial)
```

Replace `router = None`. The router makes the choice at the start of each turn and keeps it for the whole turn, tool calls included, unless a call fails. Read [Understand Retries and Switches](https://strandsagents.com/docs/user-guide/sdk/model-providers/model-routing/#understand-retries-and-switches) for what happens after a failed call.

</details>

## Face the Banker

```bash
python reasoning_dial.py
```

Check: three turns, each with the dial's choice and the clock, then the scoreboard. This output is an example; the words, the dice and the seconds will differ:

```
BANTER: the dial chose quick (3.4 s)
  Synergy, sir, is what you call two people standing near a spreadsheet. Cordula calls it a Tuesday.

A ROUND: the dial chose quick (6.2 s)
  Cordula rolls 14 + 1 = 15 against the banker's 9 + 1 = 10. The party takes the round.

THE FINAL BEAT: the dial chose deep (21.7 s)
  Cordula lands on 19 and the banker overshoots to 23, so the drum is hers. The party wins the bout.

  Footwork: Cordula: 14 + 1 = 15 against the Bonus-Season Investment Banker: 9 + 1 = 10 -> party
  Final Beat: Cordula: 19 against the Bonus-Season Investment Banker: 23 -> party
  The party took the Final Beat. The banker has gone to restructure.
```

The Final Beat is a coin flip weighted by Footwork. If the banker takes the Final Beat, the last line says so, and the dial still did its job: run `reasoning_dial.py` again.

To watch the fallback, set `DEEP_PATIENCE_SECONDS = 1` at the top of `reasoning_dial.py` and run the script again. A deep turn that stays silent for a second fails, and the third line becomes `THE FINAL BEAT: the dial chose deep then quick`: the router asked the fallback after the failure, and the fallback named the one candidate not yet tried. Set `DEEP_PATIENCE_SECONDS` back to 30.

| you see | it means | fix |
|---|---|---|
| `AttributeError: 'NoneType' object has no attribute 'log'` | `dial` is still `None` | Step 4 |
| `AttributeError: 'NoneType' object has no attribute ...` from `Agent` or `ModelRouter` | one of `quick`, `deep` or `router` is still `None` | Steps 2, 3 and 5 |
| `ValueError: ... repeats a model already routed to` | one `BedrockModel` object sits behind both candidates | build a separate `BedrockModel` for each |
| `the dial chose declined, so the first candidate` | the classifier failed or timed out, so the turn ran on quick | run the script again; if the decline repeats, check [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |
| `the dial chose quick` on the Final Beat, every time | the classifier did not read the request as a close call | make `DEEP_DESCRIPTION` firmer about a tied round and a Final Beat |
| `the dial chose deep` on the banter | the classifier misread the banter as a close call | make `QUICK_DESCRIPTION` firmer about heckles |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Dial or Always On?

Reasoning could stay on for the whole agent, as the Floor 5 Narrator comment suggests, with every turn paying for it. Or leave reasoning off everywhere and hope the Final Beat is easy. The router is the middle road: two settings, one agent, and a rule for when each is worth it. The router costs one extra short Amazon Nova 2 Lite call per turn, the classifier. The router earns that back the first time it keeps a heckle off the slow path. The router has limits too. The classifier sees the latest request, not the whole fight, and `Agent.structured_output()` skips the router and calls the first candidate directly, as the [limits](https://strandsagents.com/docs/user-guide/sdk/model-providers/model-routing/#work-within-current-limits) section says. The routing API is marked provisional in the SDK, so the API may change.

## What It Costs

Time is the real price. On Floor 5 a Narrator turn measured about 9 s with reasoning off, and 24 to 91 s with reasoning at medium. The deep candidate uses low effort, which should land between; time each turn with [Read the Receipt](read-the-receipt.md). If all three turns of this bout ran with reasoning at medium, the bout would take from about 72 s to over four minutes. With the dial, only the Final Beat turn takes that long.

Money follows the output tokens, because thinking is billed as output, at $2.50 per million against $0.30 per million for input ([Floor 1 cost table](../floor-1.md#what-a-turn-costs)). A worked estimate, with round numbers:

| turn | input tokens | output tokens | about |
|---|---|---|---|
| classifier call, each turn | 700 | 10 | $0.00023 |
| banter, quick | 1,900 | 60 | $0.00072 |
| a round, quick | 2,400 | 150 | $0.00110 |
| the Final Beat, deep, with 1,800 tokens of thinking | 2,000 | 1,900 | $0.00535 |

Three turns and three classifier calls come to under a cent, about $0.0079. The same bout all on deep, with no classifier, is about $0.016. The Final Beat turn is two thirds of the dial's bill, and that turn is the one that earned the spend.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The drum sped up. The banker rolled a 23 and kept dancing past the final strike, the way they keep going past the end of every meeting. I rolled a 19 and stopped on the beat. The collar took long enough on the ruling that I counted the seconds: twenty-one seconds. Barnaby said he had been waiting since 0551 for the System AI to pause before it spoke. He sounded nearly moved.

## Encounter Clear

Loot kept:

- Reasoning is a setting on Amazon Nova 2 Lite; each setting can be a `RoutingCandidate` with a name and a description
- A `ModelRouter` takes a strategy that chooses the candidate for each turn, and an agent takes the router as its `model`
- `ClassifierStrategy` reads the descriptions and the latest request, and needs its own `BedrockModel`
- `FallbackStrategy` answers the router's question after a failed call, and a read timeout turns a slow call into one
- A custom strategy can hand different questions to different strategies, as `DialStrategy` does

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[TURNS THE KNOB ONLY WHEN IT MATTERS]**
>
> Reward: You received a [Gold Box]. Inside: a brass dial with two marks, a stopwatch, and a fleece vest the banker left behind. The vest is a size small. Barnaby is wearing the vest.

Back to [Floor 1](../floor-1.md#floor-clear), or on to [Floor 2](../floor-2.md).
