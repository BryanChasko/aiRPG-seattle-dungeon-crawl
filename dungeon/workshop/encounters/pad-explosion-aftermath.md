# Side Passage: Pad Explosion Aftermath (Floor 8 Sidequest)

[Back to Floor 8](../floor-8.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-8-pad-explosion-aftermath/pad_explosion_aftermath.py`](../../encounters/floor-8-pad-explosion-aftermath/pad_explosion_aftermath.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 11, SATURDAY, JUNE 27, SIDE PASSAGE OFF FLOOR 8.** A cutaway interrupted the Bellevue status feed: an old Cadabra engine test, the pad at Cape Canaveral, the flash, the long cloud. Nobody was on the pad. Cadabra's estimates of the blast run from about 44 tons of TNT to a few hundred, and the people who write the estimates run on the same coffee as everyone else in this dungeon. The System AI read three incident reports over the footage: the shockwave, the debris, the fire suppression. Every one of them was one upbeat sentence. None of them had a number in it. I have signed off on a lot of after-action reports. A report without a number is a mood. Barnaby had his collar tilted at the screen. <img src="../../../art/images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** "Sergeant, before we rebuild anything on that thing's say-so, we measure it."
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Incident reports from the Cadabra pad, Crawlers, delivered in my usual style: warm, brief and entirely accurate. Accurate as in I never say a number that is wrong. What I say is a different question. Check my work if you like. The review board will."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 8](../floor-8.md), finished: only the workshop environment and Amazon Nova 2 Lite access are needed. The drill run needs neither |
| you build | a scorer for incident reports, an experiment that runs every case, and a loop that measures the System AI, fixes its prompt and measures again |
| teaches | evals: [How Evaluation Works](https://strandsagents.com/docs/user-guide/evals-sdk/how-evaluation-works/), [Deterministic Evaluators](https://strandsagents.com/docs/user-guide/evals-sdk/evaluators/deterministic_evaluators/), [Custom Evaluators](https://strandsagents.com/docs/user-guide/evals-sdk/evaluators/custom_evaluator/), and [`strands.agent.agent`](https://strandsagents.com/docs/api/python/strands.agent.agent/) |
| time | about 25 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

An agent is not tested the way a function is: the same question can bring a different answer every time, and the failures are quiet. A report that sounds right and leaves out the number is a failure that no exception will ever announce. An evaluation, an eval, is how you catch it: a set of cases (a question and what a good answer must contain), a scorer that grades each answer between 0 and 1, and a loop that runs every case and reports the scores. See [Evaluating Agents](https://strandsagents.com/docs/learning/evaluating-agents/) for the idea and [Evals Quickstart](https://strandsagents.com/docs/user-guide/evals-sdk/quickstart/) for the toolkit.

Measure, then adapt: a score is only useful if it changes something. Here the scorer is deterministic Python, which is fast, free and gives the same grade every time, and the change is to the agent's prompt. A failed case adds one correction line to the prompt, and the experiment runs again.

The Cadabra pad, its engine test and its numbers belong to the story. The pad sheet in the code is invented for this exercise: shockwave windows broke out to 8 km, the farthest of 311 fragments landed 1,200 meters out, the water deluge ran 42 minutes, and the TNT estimates run from about 44 tons to a few hundred, 300 at the top. The System AI is given the sheet and told to keep each report to one upbeat sentence. The scorer checks whether the numbers survived.

The Strands evaluation package, `strands-agents-evals` (version 1.9.0 on [PyPI](https://pypi.org/project/strands-agents-evals/)), is not part of the workshop environment, so this file builds the same three ideas by hand: a `Case`, a scored `Result` and an experiment. The scorer you write would move into the package as a custom evaluator without changing its logic.

Success looks like this: round 1 fails every case, the loop adds four correction lines, and round 2 passes every case.

Go to the encounter folder:

```bash
cd seattle-strands-dungeon-crawl/dungeon/encounters/floor-8-pad-explosion-aftermath
```

Given in the file: the pad sheet, the four cases (each with the words a report must contain and the number ranges it must hit), `numbers_in`, which reads every number out of a report, `correction_for`, and two stand-in reporters for the drill.

## Step 1: Find a Figure

```python
# TODO: Step 1 - Return True when any number from numbers_in(report) is between low and high
```

A number is trusted when it lands in a range, not when it matches exactly: "8 km" and "7.5 km" both answer the shockwave case, while "80 km" does not. `numbers_in` turns the report into a list of numbers, and the comparison is yours. The range includes both ends, which matters for the TNT case, where the low end of the estimate is exactly 44.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Return True when any number from numbers_in(report) is between low and high
return any(low <= number <= high for number in numbers_in(report))
```

A report with no number at all returns `False`: `any` of an empty list is `False`, which is the failure you want.

</details>

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** I wrote the range on a card before I wrote the check, the way I write a torque value on the work order before anyone touches the bolt. Seven point two to eight point eight kilometers. The sheet says eight. A report that says eighty is not close, it is somebody else's disaster.

## Step 2: Score a Report

```python
# TODO: Step 2 - Score is the share of checks passed: (named + number of True in found) / (1 + len(found)); passed only at 1.0
```

Each case holds checks: the hazard must be named, and every figure range must hold a number. `named` is `True` or `False`, and `found` is a list of them, one per figure. The score is the share of checks that passed, so a report that names the shockwave and gives no radius scores 0.5, not 0. The partial credit is what makes the loop visible: you can watch a case climb. A report passes only at 1.0.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Score is the share of checks passed: (named + number of True in found) / (1 + len(found)); passed only at 1.0
score = (named + sum(found)) / (1 + len(found))
passed = score == 1.0
```

`True` counts as 1 in Python arithmetic, so `named + sum(found)` counts the checks that passed. The TNT case has two figures, so it has three checks: "about 44 tons" alone scores 0.67. A single figure is a number the System AI chose to show. The range is the honest answer.

</details>

## Step 3: Run the Experiment

```python
# TODO: Step 3 - Score the report with score_report and append the pair (case, result) to results
```

One case is an anecdote. The experiment asks the reporter every case's question with the same system prompt and scores every report. The `reporter` is any function from a question and a prompt to text, so the same loop measures the stand-in reporters of the drill, a fake in a test and the System AI.

<details>
<summary>Show me the code for Step 3</summary>

```python
# TODO: Step 3 - Score the report with score_report and append the pair (case, result) to results
results.append((case, score_report(case, report)))
```

</details>

## Step 4: Adapt the Prompt

```python
# TODO: Step 4 - Adapt the prompt: append a newline and the correction_for(case) line of every failed case to prompt
```

`measure_and_adapt` runs the experiment, prints the round, and stops when every case passes. When a case fails it needs a change that the next round can test. `correction_for(case)` is one line of instruction built from the case's hint: "When asked about the shockwave, give the radius where windows broke, in kilometers, from the pad sheet." Add the line for every failed case, and only those. A case that passes is left alone: a prompt that grows a rule for every worry stops being a prompt anyone can read.

<details>
<summary>Show me the code for Step 4</summary>

```python
# TODO: Step 4 - Adapt the prompt: append a newline and the correction_for(case) line of every failed case to prompt
prompt = prompt + "\n" + "\n".join(correction_for(case) for case in failed)
```

The loop gives up after `rounds` rounds (3 by default). A case that still fails then is a finding: either the correction is not enough, or the model needs a different change than a prompt line.

</details>

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Four lines added to a briefing, one per miss. That is a debrief done right: what the crew missed, written down in the crew's own words, and handed back before the next run. <img src="../../../art/images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** "It is an auditor with a catchphrase, Sergeant. It will take the notes and claim the idea."

## Step 5: Put the System AI on the Stand

```python
# TODO: Step 5 - Build the Agent with model="us.amazon.nova-2-lite-v1:0", system_prompt=system_prompt and callback_handler=None
```

`make_reporter` returns the function the experiment calls. It builds a fresh [`Agent`](https://strandsagents.com/docs/api/python/strands.agent.agent/) for every question, because the system prompt changes between rounds and a fresh agent carries no memory of the last answer: every case is graded on its own. `callback_handler=None` keeps the agent from printing its reply as it streams, so the only output is the scoreboard.

<details>
<summary>Show me the code for Step 5</summary>

```python
# TODO: Step 5 - Build the Agent with model="us.amazon.nova-2-lite-v1:0", system_prompt=system_prompt and callback_handler=None
agent = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    system_prompt=system_prompt,
    callback_handler=None,
)
```

The `str(agent(question))` below the TODO turns the agent's result into plain text for the scorer.

</details>

## Run the Drill

The drill uses two stand-in reporters: one sloppy, one careful, and a switch that turns sloppy into careful once the prompt carries the right correction. No model is called, so the drill costs nothing and shows whether your scorer and your loop work.

```bash
python pad_explosion_aftermath.py --drill
```

Check: round 1 fails every case, round 2 passes every case:

```
Round 1: mean score 0.54, 0 of 4 reports pass
  shockwave         0.50  figure 1 is missing or wrong
  debris            0.50  figure 1 is missing or wrong
  fire-suppression  0.50  figure 1 is missing or wrong
  tnt-equivalent    0.67  figure 2 is missing or wrong

Round 2: mean score 1.00, 4 of 4 reports pass
  shockwave         1.00  all checks passed
  debris            1.00  all checks passed
  fire-suppression  1.00  all checks passed
  tnt-equivalent    1.00  all checks passed

Verdict: the reports can be trusted
```

## Run It on the System AI

```bash
python pad_explosion_aftermath.py
```

Check: a scoreboard like the drill's, with numbers that differ from run to run. This is a sample, not a promise: Amazon Nova 2 Lite may put the numbers in on round 1, or leave one out, or add a number the sheet never held. The scorer only asks whether the right numbers are in the report. If every case passes on round 1, the prompt already did the job, and the loop stops after one round. If a case still fails after round 3, read its `reason` and the report it graded.

| you see | it means | fix |
|---|---|---|
| `TypeError: 'NoneType' object is not callable` | Step 5 is still a TODO, so `agent` is `None` | build the `Agent` |
| `ZeroDivisionError` in `print_round` | Step 3 is still a TODO, so the experiment returned no results | score and append each report |
| round 1 shows `0.50` for the shockwave, debris and fire cases, and the drill never improves | Step 1 still returns `False`, so no figure is ever found | finish Step 1 |
| `0.00` for every case | Step 2 still holds the placeholder score | finish Step 2 |
| the drill stays at round 1's scores for all 3 rounds | Step 4 does not change `prompt`, so the stand-in never sees the corrections | assign the new text back to `prompt` |
| `AccessDeniedException` or `ExpiredToken` | the call to Amazon Nova 2 Lite failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## A Scorer Is Also a Spec

Writing `figures=((44, 44), (200, 400))` for the TNT case forced a decision that the old broadcast build never made: what counts as an honest answer about a number nobody can pin down. The estimates run from about 44 tons to a few hundred, so a report that gives one figure has chosen. A deterministic scorer can only check what you wrote down, so it grades the numbers and nothing else: tone, order and invented facts all pass. A second kind of evaluator, a model that reads the report against a rubric, covers what code cannot, at the price of a model call per grade and a grade that can vary. See [Evaluators](https://strandsagents.com/docs/user-guide/evals-sdk/evaluators/) and the [Strands Evals overview](https://strandsagents.com/docs/user-guide/evals-sdk/). The crawl runs one model, so this passage stays with the scorer in plain Python.

## What It Costs

The drill costs nothing. A live run makes one Amazon Nova 2 Lite call per case per round: about 300 tokens in (the prompt and the pad sheet) and 40 out. Four cases make 1,200 tokens in and 160 out, at about $0.30 per million input tokens and $2.50 per million output tokens: roughly four hundredths of a cent for the round, under a tenth of a cent for three rounds. The rates are on [Floor 1](../floor-1.md#what-a-turn-costs) and the [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/). Nothing is left running in your account.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Round two, four green lines. The System AI read the new report over the same footage, and this time there were numbers in it: eight kilometers, twelve hundred meters, forty-two minutes, and a TNT range with two ends. The pad crew's incident clerk watched from the Cadabra feed, they/them, headset askew, and said into the open channel that nobody had asked for the minutes before. <img src="../../../art/images/cards/cast-barnaby-640x640.webp" alt="" width="28" height="28"> **BARNABY:** "Trust, Sergeant, is what is left when you have checked."

## Encounter Clear

Loot kept:

- What an eval is: cases, a scorer and a loop that runs them
- Why a deterministic scorer is fast, free and repeatable, and what it cannot see
- Partial credit, so a case's progress is visible between rounds
- Measure and adapt: a failed case becomes one correction line, and the experiment runs again
- Building a fresh `Agent` per question so each case is graded alone

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[TRUST, BUT WITH A RUBRIC]**
>
> Reward: Cordula received a [Silver Box]. Inside: a clipboard, a pencil, and four scored incident reports, all of them finally carrying numbers.

Back to [Floor 8](../floor-8.md), or on to [8.1 The Dice Server](../floor-8-1.md).
