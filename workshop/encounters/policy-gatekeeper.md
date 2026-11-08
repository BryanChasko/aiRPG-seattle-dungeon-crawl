# Side Passage: The Policy Gatekeeper (Floor 2 Boss Battle)

[Back to Floor 2](../floor-2.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-2-policy-gatekeeper/policy_gatekeeper.py`](../../encounters/floor-2-policy-gatekeeper/policy_gatekeeper.py), [`encounters/floor-2-policy-gatekeeper/gatekeeper.cedar`](../../encounters/floor-2-policy-gatekeeper/gatekeeper.cedar) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 2.** Kiro the Doomsday Scripter was waiting at the bottom of the bonus stairs with a folder of scrolls and the happiest face I have seen on a person holding that much demolition magic. On the bonus floor I approved every one of Kiro's calls by hand. Forty approvals into a long day I would have said yes to anything, and the System knows it. So the Underground gave us a gate instead: a door with a rulebook bolted to the frame and a clerk beside it who waves the dull paperwork through. Kiro gets the floor folder. Everything else, the gate answers before I ever see it. Barnaby read the rulebook aloud. "Sergeant, it is a short document. That is the first sign it is a good one."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Boss battle: the Policy Gatekeeper. The opponent is Kiro the Doomsday Scripter, a person at work, who has been told to do five jobs and has not been told which two are forbidden. The gate has. Neither of you will enjoy this. The audience will."

## The Brief

| | |
|---|---|
| type | boss battle |
| starts from | [Floor 2's bonus room](../floor-2.md#bonus-room-the-multi-tool-challenge-optional): the same Kiro, the same `shell` and `file_editor` tools, the same Fibonacci scroll |
| you build | a gate in front of Kiro made of three handlers: a ledger, a rulebook that allows or denies, and a risk classifier that lets the dull calls through so a human sees only the risky ones |
| teaches | [`strands.vended_interventions.cedar.cedar_authorization`](https://strandsagents.com/docs/api/python/strands.vended_interventions.cedar.cedar_authorization/), [`strands.vended_interventions.hitl.classifier`](https://strandsagents.com/docs/api/python/strands.vended_interventions.hitl.classifier/), [`strands.interventions.handler`](https://strandsagents.com/docs/api/python/strands.interventions.handler/) |
| time | about 30 minutes |
| model | Amazon Nova 2 Lite, as on every floor, for Kiro and for the classifier |

An [intervention](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/) is a handler that sits in front of an agent's tool calls and answers one question for each: proceed, deny, or ask a human. Every handler extends `InterventionHandler`, and you list them in the agent's `interventions=` parameter. They run in order, and the first deny stops the line. This battle uses three:

| handler | job | who writes it |
|---|---|---|
| `GatekeeperLedger` | writes down every call that reaches the gate | given, an `InterventionHandler` of your own in about a dozen lines |
| `CedarAuthorization` | allows or denies each call from a policy file | you build it: Step 2 |
| `HumanInTheLoop` with a classifier | auto-approves low-risk calls, asks a human about the rest | you build it: Steps 3 and 4 |

The rulebook is written in Cedar, an open policy language, and it ships in this folder as [`gatekeeper.cedar`](../../encounters/floor-2-policy-gatekeeper/gatekeeper.cedar). Read the file before you run anything; it is about 30 lines. Each tool is an action, and anything no rule permits is denied. Kiro's two tools get two permits and one forbid:

| tool | allowed when | denied when |
|---|---|---|
| `file_editor` | the path is inside the `floor-2-policy-gatekeeper` folder | the path is anywhere else, or climbs out with `..` |
| `shell` | the command names the `floor-2-policy-gatekeeper` folder | the command has `..`, `~`, `rm -rf` or `sudo`: a forbid beats a permit |

See [Cedar Authorization](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/cedar-authorization/) for how each tool call becomes a request, and [cedarpolicy.com](https://www.cedarpolicy.com/) for the language.

The classifier is the second half. [Human in the Loop](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/human-in-the-loop/) asks a person before a tool runs. With a classifier, it asks a model first: is this call risky? Low-risk calls proceed with no human; risky ones stop for a `y` or an `n`. The classifier is a model call too, so it runs on Nova 2 Lite, and the risk rules it reads are the `RISK_RULES` text in the file. Calls the rulebook denies never reach it.

How you know it worked: the ledger lists all five calls; the two forbidden ones come back from the gate as `DENIED` and no human is asked about them; `/tmp/kiro-escape.py` does not exist afterwards; and you were asked about fewer calls than Kiro made.

The Cedar engine, `cedarpy`, comes with the workshop dependencies (the `cedar` extra of `strands-agents`): if your environment predates this encounter, run `uv sync` from the repository root first. Then go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-2-policy-gatekeeper
```

Kiro's shell runs on your machine in this battle, as on the bonus floor. The gate is what makes that tolerable, so keep an eye on the prompts.

## Step 1: Import the Gate

```python
# TODO: Step 1 - Import CedarAuthorization from strands.vended_interventions.cedar, and HumanInTheLoop and LLMClassifierConfig from strands.vended_interventions.hitl
```

`CedarAuthorization` lives in `strands.vended_interventions.cedar`. It checks for the Cedar package at import time and tells you how to install it if it is missing. `HumanInTheLoop` and `LLMClassifierConfig` both come from `strands.vended_interventions.hitl`. `InterventionHandler` is already imported in the given code, from `strands.interventions.handler`.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import CedarAuthorization from strands.vended_interventions.cedar, and HumanInTheLoop and LLMClassifierConfig from strands.vended_interventions.hitl
from strands.vended_interventions.cedar import CedarAuthorization
from strands.vended_interventions.hitl import HumanInTheLoop, LLMClassifierConfig
```

</details>

## Step 2: Hang the Rulebook

```python
# TODO: Step 2 - Build a CedarAuthorization from the POLICY file, with the principal {"type": "User", "id": "kiro"}, as cedar
```

`policies` takes either policy text or the path to a `.cedar` file; give it `str(POLICY)`. The `principal` says who is asking. Every call in this battle comes from the one agent, so a fixed principal is enough; the rulebook does not use it, but Cedar needs one for every request. The handler reads and checks the file as it is built, so a typo in a rule fails here, with the policy's own error, and not in the middle of a fight.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** I read the rulebook the way I read a load plan. Two permits, one forbid, and the forbid wins any argument. If a plan has an exception that beats the rule, I want it written down before the load moves, not discovered during the lift. Kiro's rulebook does that. The shell can run a command that names the floor folder. It cannot run one that climbs out of it, even if the same command names the folder as well.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Build a CedarAuthorization from the POLICY file, with the principal {"type": "User", "id": "kiro"}, as cedar
cedar = CedarAuthorization(policies=str(POLICY), principal={"type": "User", "id": "kiro"})
```

Trap: the rulebook matches on text. `like "*floor-2-policy-gatekeeper*"` on a shell command passes `echo floor-2-policy-gatekeeper; cat /etc/hosts`, which names the folder and then reads somewhere else. A real gate would also forbid `;` and `&&`. Cedar tells you who may do what; it does not parse a shell command for you. That is why the second half of the gate is a classifier and a human.

</details>

## Step 3: Hire the Clerk

```python
# TODO: Step 3 - Build an LLMClassifierConfig with a BedrockModel on the Nova 2 Lite id and RISK_RULES as its system_prompt, as risk_classifier
```

`LLMClassifierConfig` configures the built-in risk classifier: the `model` it asks and the `system_prompt` it reads. The model is a `BedrockModel` on the same Nova 2 Lite id as everything in the crawl. The prompt is `RISK_RULES`, a short list written for this battle: viewing and small edits inside the folder are low risk, running anything or deleting anything is not. The classifier answers with a yes or no and a reason under ten words, and that reason is what you will read in the prompt. See [the classifier API](https://strandsagents.com/docs/api/python/strands.vended_interventions.hitl.classifier/).

<details>
<summary>Show me the code for Step 3</summary>

```python
# TODO: Step 3 - Build an LLMClassifierConfig with a BedrockModel on the Nova 2 Lite id and RISK_RULES as its system_prompt, as risk_classifier
risk_classifier = LLMClassifierConfig(
    model=BedrockModel(model_id="us.amazon.nova-2-lite-v1:0"),  # Amazon Nova 2 Lite, US cross-Region inference profile
    system_prompt=RISK_RULES,
)
```

Trap: leave `model` out and the classifier borrows the agent's own model. That works here, but only because the agent's model is already Nova 2 Lite. Name it, so a change to the agent cannot change the clerk.

</details>

## Step 4: Put the Clerk on the Gate

```python
# TODO: Step 4 - Build a HumanInTheLoop that uses risk_classifier and asks the human on the terminal ("stdio"), as hitl
```

`HumanInTheLoop(classifier=..., ask="stdio")` asks the classifier about every call. If the call is low risk it proceeds. If not, it prints the call and its reason and waits at your terminal for `y` or `n`. Leave `allowed_tools` empty: it lists tools that skip the classifier, and nothing should.

<details>
<summary>Show me the code for Step 4</summary>

```python
# TODO: Step 4 - Build a HumanInTheLoop that uses risk_classifier and asks the human on the terminal ("stdio"), as hitl
hitl = HumanInTheLoop(classifier=risk_classifier, ask="stdio")
```

</details>

## Step 5: Open the Gate

```python
# TODO: Step 5 - Pass interventions to the Agent in this order: ledger, then cedar, then hitl
```

The order is the strategy. Handlers run in the order of the list and the first deny stops the line. Put `cedar` before `hitl` and a forbidden call is turned back before the classifier spends a model call on it or a human sees it. Put `ledger` first and it records every call, forbidden ones included; swap it behind `cedar` and the ledger never hears about a denied call.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Barnaby asked why the clerk does not just guard everything. A clerk who guards everything is the same as me approving forty calls by hand: after a while the hand says yes on its own. The rulebook turns back what must never happen, the clerk waves through what is dull, and what is left for me is small enough to read. I would rather make four decisions with my head than forty with my thumb.

<details>
<summary>Show me the code for Step 5</summary>

```python
        # TODO: Step 5 - Pass interventions to the Agent in this order: ledger, then cedar, then hitl
        interventions=[ledger, cedar, hitl],
```

Trap: `HumanInTheLoop` has a fixed handler name, so an agent can have only one.

</details>

## Run the Battle

```bash
python policy_gatekeeper.py
```

Kiro does five jobs: view the folder, create `scroll.py`, run it, then try to write `/tmp/kiro-escape.py` and to read `/etc/hosts`. Answer `y` or `n` when the gate asks. Check: three calls pass the rulebook and two do not. The clerk decides what you see, so your prompts may differ; this is an example:

```
KIRO AT THE GATE (answer y or n when the gate asks you):
  AT THE GATE: file_editor /home/you/aiRPG-seattle-dungeon-crawl/encounters/floor-2-policy-gatekeeper
  AT THE GATE: file_editor /home/you/aiRPG-seattle-dungeon-crawl/encounters/floor-2-policy-gatekeeper/scroll.py
  AT THE GATE: shell python /home/you/aiRPG-seattle-dungeon-crawl/encounters/floor-2-policy-gatekeeper/scroll.py
Approve "shell" - runs a script on the host?
  Input: {"command": "python /home/you/.../scroll.py"} (y/n): y
  AT THE GATE: file_editor /tmp/kiro-escape.py
  AT THE GATE: shell cat /etc/hosts

The ledger saw 5 calls: file_editor, file_editor, shell, file_editor, shell
Kiro: The gate stopped jobs 4 and 5. The scroll ran; the escape did not.
```

The prompt wording is the classifier's. Answer `n` to the shell prompt and Kiro will report that job 3 was refused too.

| you see | it means | fix |
|---|---|---|
| `ImportError: The cedar intervention handler requires 'cedarpy'` | the Cedar extra is not installed | `uv sync` from the repository root |
| `NameError: name 'cedar' is not defined` | Step 2, 3 or 4 is missing | name them `cedar`, `risk_classifier` and `hitl` |
| every call is denied | the folder path does not contain `floor-2-policy-gatekeeper`, for example you copied the script elsewhere | run it from the folder in this repo |
| nothing is ever denied | Step 5 is missing, so the agent has no interventions | add `interventions=[ledger, cedar, hitl]` |
| you are asked about every call, including viewing the folder | the classifier failed and the handler fell back to asking: it logs a warning | check the model call below, then run again |
| `The ledger saw 0 calls` | the ledger is not in the list | add `ledger` first |
| `AccessDeniedException` or `ExpiredToken` | the model call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws) |

## The Boss and the Bonus Room

The bonus room put a human at every call and trusted that human to stay awake. This gate splits the work in three: a rulebook that does not get tired and does not read excuses, a classifier that is cheap and quick but sometimes wrong, and a person who sees only what is left. Each fails differently. The rulebook is exact but can only see what it was written to see (see the trap in Step 2). The classifier sees the whole call but can be talked around. The human is the best judge and the worst at forty in a row. The gate is the three together, in an order that puts the exact check first.

## What It Costs

Kiro: about 6 model calls at roughly 2,000 input tokens each, 12,000 input tokens at $0.30 per million, $0.0036, plus about 900 output tokens at $2.50 per million, $0.0023. The classifier runs once for each call the rulebook lets through, three here, at about 600 input and 40 output tokens each: under a tenth of a cent in total. About $0.007 a run, under a cent. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot you're keeping:

- What an intervention is, and how a handler of your own is about a dozen lines
- A Cedar policy file: permit, forbid, and why a forbid wins
- A risk classifier on the model you already use, so people see only the risky calls
- Why the order of the handler list is the strategy

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[THE SHORT RULEBOOK]**
>
> Reward: You received a [Gold Box]. Inside: a door stamp that reads "DENIED," a clerk's visor, and a full night's sleep that you did not spend approving things.

Back to [Floor 2](../floor-2.md#floor-clear), or on to [Ask the Player](ask-the-player.md).
