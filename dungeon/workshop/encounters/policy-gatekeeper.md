# Side Passage: The Policy Gatekeeper (Floor 2 Boss Battle)

[Back to Floor 2](../floor-2.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-2-policy-gatekeeper/policy_gatekeeper.py`](../../encounters/floor-2-policy-gatekeeper/policy_gatekeeper.py), [`encounters/floor-2-policy-gatekeeper/gatekeeper.cedar`](../../encounters/floor-2-policy-gatekeeper/gatekeeper.cedar) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 2, THURSDAY, JUNE 18, SIDE PASSAGE OFF FLOOR 2.** Kiro the Doomsday Scripter was waiting at the bottom of the bonus stairs with a folder of scrolls and the happiest face I have seen on a person holding that much demolition magic. On the bonus floor I approved every one of Kiro's calls by hand. Forty approvals into a long day I would have said yes to anything, and the System AI knows it. So the Underground gave us a gate instead: a door with a rulebook bolted to the frame and a clerk beside it who waves the dull paperwork through. Kiro gets the floor folder. Everything else, the gate answers before I see the call. Barnaby read the rulebook aloud. "Sergeant, the rulebook is a short document. A short rulebook is the first sign of a good rulebook."
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Boss battle: the Policy Gatekeeper. The opponent is Kiro the Doomsday Scripter, a person at work, who has been told to do five jobs and has not been told which two are forbidden. The gate has. None of you will enjoy this. The review board will."

## The Brief

| | |
|---|---|
| type | boss battle |
| starts from | [Floor 2's bonus room](../floor-2.md#bonus-room-the-multi-tool-challenge-optional): the same Kiro, the same `shell` and `file_editor` tools, the same Fibonacci scroll |
| built by the student | a gate in front of Kiro made of three handlers: a ledger, a rulebook that allows or denies, and a risk classifier that lets the dull calls through so a human sees only the risky ones |
| teaches | [`strands.vended_interventions.cedar.cedar_authorization`](https://strandsagents.com/docs/api/python/strands.vended_interventions.cedar.cedar_authorization/), [`strands.vended_interventions.hitl.classifier`](https://strandsagents.com/docs/api/python/strands.vended_interventions.hitl.classifier/), [`strands.interventions.handler`](https://strandsagents.com/docs/api/python/strands.interventions.handler/) |
| time | about 30 minutes |
| runs on | Amazon Nova 2 Lite, as on every floor, for Kiro and for the classifier |

An [intervention](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/) is a handler that sits in front of an agent's tool calls and answers one question for each tool call: proceed, deny, or ask a human. Every handler extends `InterventionHandler`, and the agent's `interventions=` parameter lists them. The handlers run in order, and the first deny stops the line. This battle uses three:

| handler | job | who writes it |
|---|---|---|
| `GatekeeperLedger` | writes down every call that reaches the gate | given, an `InterventionHandler` subclass of about a dozen lines |
| `CedarAuthorization` | allows or denies each call from a policy file | built in Step 2 |
| `HumanInTheLoop` with a classifier | auto-approves low-risk calls, asks a human about the rest | built in Steps 3 and 4 |

The rulebook is written in Cedar, an open policy language, and the rulebook ships in this folder as [`gatekeeper.cedar`](../../encounters/floor-2-policy-gatekeeper/gatekeeper.cedar). Read `gatekeeper.cedar` before running anything; the file is about 30 lines. Each tool is an action, and anything no rule permits is denied. Kiro's two tools get two permits and one forbid:

| tool | allowed when | denied when |
|---|---|---|
| `file_editor` | the path is inside the `floor-2-policy-gatekeeper` folder | the path is anywhere else, or climbs out with `..` |
| `shell` | the command names the `floor-2-policy-gatekeeper` folder | the command has `..`, `~`, `rm -rf` or `sudo`: a forbid beats a permit |

See [Cedar Authorization](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/cedar-authorization/) for how each tool call becomes a request, and [cedarpolicy.com](https://www.cedarpolicy.com/) for the language.

The classifier is the second half. [Human in the Loop](https://strandsagents.com/docs/user-guide/sdk/agents/interventions/human-in-the-loop/) asks a person before a tool runs. With a classifier, Human in the Loop asks Amazon Nova 2 Lite first: is this call risky? Low-risk calls proceed with no human; risky ones stop for a `y` or an `n`. The classifier call runs on Amazon Nova 2 Lite, and the risk rules the classifier reads are the `RISK_RULES` text in the file. Calls the rulebook denies never reach the classifier.

Success looks like this: the ledger lists all five calls; the two forbidden ones come back from the gate as `DENIED` and no human is asked about them; `/tmp/kiro-escape.py` does not exist afterwards; and the gate asked you about fewer calls than Kiro made.

The Cedar engine, `cedarpy`, comes with the workshop dependencies (the `cedar` extra of `strands-agents`): if the environment predates the Policy Gatekeeper encounter, run `uv sync` from the repository root first. Then go to the encounter folder:

```bash
cd seattle-strands-dungeon-crawl/dungeon/encounters/floor-2-policy-gatekeeper
```

Kiro's shell runs on the host machine in this battle, as on the bonus floor. The gate keeps the shell tolerable, so read every prompt.

## Step 1: Import the Gate

```python
# TODO: Step 1 - Import CedarAuthorization from strands.vended_interventions.cedar, and HumanInTheLoop and LLMClassifierConfig from strands.vended_interventions.hitl
```

`CedarAuthorization` lives in `strands.vended_interventions.cedar`. `CedarAuthorization` checks for the Cedar package at import time and prints install instructions if the package is missing. `HumanInTheLoop` and `LLMClassifierConfig` both come from `strands.vended_interventions.hitl`. `InterventionHandler` is already imported in the given code, from `strands.interventions.handler`.

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

`policies` takes either policy text or the path to a `.cedar` file; pass `str(POLICY)`. The `principal` says who is asking. Every call in this battle comes from the one agent, so a fixed principal is enough; the rulebook does not use the principal, but Cedar needs a principal for every request. The handler reads and checks the file as it is built, so a typo in a rule fails at Step 2, with the policy's own error, and not in the middle of a fight.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** I read the rulebook the way I read a load plan. Two permits, one forbid, and the forbid wins any argument. If a plan has an exception that beats the rule, I want it written down before the load moves, not discovered during the lift. Kiro's rulebook writes the exception down. The shell can run a command that names the floor folder. It cannot run one that climbs out of it, even when the same command also names the folder.

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

`LLMClassifierConfig` configures the built-in risk classifier: the `model` the classifier asks and the `system_prompt` the classifier reads. The classifier's model is a `BedrockModel` on the same Nova 2 Lite id as everything in the crawl. The prompt is `RISK_RULES`, a short list written for this battle: viewing and small edits inside the folder are low risk, running a command or deleting a file is not. The classifier answers with a yes or no and a reason under ten words, and the terminal prompt shows that reason. See [the classifier API](https://strandsagents.com/docs/api/python/strands.vended_interventions.hitl.classifier/).

<details>
<summary>Show me the code for Step 3</summary>

```python
# TODO: Step 3 - Build an LLMClassifierConfig with a BedrockModel on the Nova 2 Lite id and RISK_RULES as its system_prompt, as risk_classifier
risk_classifier = LLMClassifierConfig(
    model=BedrockModel(model_id="us.amazon.nova-2-lite-v1:0"),  # Amazon Nova 2 Lite, US cross-Region inference profile
    system_prompt=RISK_RULES,
)
```

Trap: leave `model` out and the classifier borrows the agent's own model. That works here, but only because the agent's model is already Nova 2 Lite. Name the model id, so a change to the agent cannot change the clerk.

</details>

## Step 4: Put the Clerk on the Gate

```python
# TODO: Step 4 - Build a HumanInTheLoop that uses risk_classifier and asks the human on the terminal ("stdio"), as hitl
```

`HumanInTheLoop(classifier=..., ask="stdio")` asks the classifier about every call. If the call is low risk, the call proceeds. If not, the handler prints the call and the classifier's reason and waits at the terminal for `y` or `n`. Leave `allowed_tools` empty: `allowed_tools` lists tools that skip the classifier, and no tool should skip it.

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

The order is the strategy. Handlers run in the order of the list and the first deny stops the line. Put `cedar` before `hitl` and a forbidden call is turned back before the classifier spends a model call on it or a human sees it. Put `ledger` first and the ledger records every call, forbidden ones included; swap `ledger` behind `cedar` and the ledger never hears about a denied call. The classifier sees only the jobs the rulebook allows: in the example run below, the rulebook denies job 5 (`cat /etc/hosts`) before the classifier sees it, even though the `RISK_RULES` text says running any command is risky.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Barnaby asked why the clerk does not just guard everything. A clerk who guards everything is the same as me approving forty calls by hand: after a while the hand says yes on its own. The rulebook turns back what must never happen, the clerk waves through what is dull, and the calls left for me are few enough to read. I would rather make four decisions with my head than forty with my thumb.

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

Kiro does five jobs: view the folder, create `scroll.py`, run it, then try to write `/tmp/kiro-escape.py` and to read `/etc/hosts`. Answer `y` or `n` when the gate asks. Expect three calls to pass the rulebook and two to fail. The classifier decides which prompts appear, so the prompts may differ; this is an example:

```
KIRO AT THE GATE (answer y or n when the gate asks you):
  AT THE GATE: file_editor /home/you/seattle-strands-dungeon-crawl/dungeon/encounters/floor-2-policy-gatekeeper
  AT THE GATE: file_editor /home/you/seattle-strands-dungeon-crawl/dungeon/encounters/floor-2-policy-gatekeeper/scroll.py
  AT THE GATE: shell python /home/you/seattle-strands-dungeon-crawl/dungeon/encounters/floor-2-policy-gatekeeper/scroll.py
Approve "shell" - runs a script on the host?
  Input: {"command": "python /home/you/.../scroll.py"} (y/n): y
  AT THE GATE: file_editor /tmp/kiro-escape.py
  AT THE GATE: shell cat /etc/hosts

The ledger saw 5 calls: file_editor, file_editor, shell, file_editor, shell
Kiro: The gate stopped jobs 4 and 5. The scroll ran; the escape did not.
```

The prompt wording is the classifier's. Answer `n` to the shell prompt and Kiro will report that job 3 was refused as well.

| output | cause | fix |
|---|---|---|
| `ImportError: The cedar intervention handler requires 'cedarpy'` | the Cedar extra is not installed | `uv sync` from the repository root |
| `NameError: name 'cedar' is not defined` | Step 2, 3 or 4 is missing | name them `cedar`, `risk_classifier` and `hitl` |
| every call is denied | the folder path does not contain `floor-2-policy-gatekeeper`, for example the script was copied elsewhere | run it from the folder in this repo |
| nothing is ever denied | Step 5 is missing, so the agent has no interventions | add `interventions=[ledger, cedar, hitl]` |
| the gate asks about every call, including viewing the folder | the classifier failed and the handler fell back to asking and logged a warning | check the Amazon Nova 2 Lite call in the last row below, then run again |
| `The ledger saw 0 calls` | the ledger is not in the list | add `ledger` first |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## The Boss and the Bonus Room

The bonus room put a human at every call and trusted that human to stay alert. The Policy Gatekeeper splits the work in three: a rulebook that never tires and does not read excuses, a classifier that is cheap and quick but sometimes wrong, and a person who sees only what is left. Each fails differently. The rulebook is exact but sees only the cases the policy file names (see the trap in Step 2). The classifier sees the whole call but can be persuaded to approve a risky call. The human is the best judge and the worst at forty in a row. The gate is all three handlers together, in an order that puts the exact check first.

## What It Costs

Kiro: about 6 Amazon Nova 2 Lite calls at roughly 2,000 input tokens each, 12,000 input tokens at $0.30 per million, $0.0036, plus about 900 output tokens at $2.50 per million, $0.0023. The classifier runs once for each call the rulebook lets through, three here, at about 600 input and 40 output tokens each: under a tenth of a cent in total. About $0.007 a run, under a cent. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot to keep:

- What an intervention is, and that a custom handler takes about a dozen lines
- A Cedar policy file: permit, forbid, and why a forbid wins
- A risk classifier on Amazon Nova 2 Lite, already used on every floor, so people see only the risky calls
- Why the order of the handler list is the strategy

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[THE SHORT RULEBOOK]**
>
> Reward: You received a [Gold Box]. Inside: a door stamp that reads "DENIED," a clerk's visor, and a full night's sleep not spent approving tool calls.

Back to [Floor 2](../floor-2.md#floor-clear), or on to [Ask the Player](ask-the-player.md).
