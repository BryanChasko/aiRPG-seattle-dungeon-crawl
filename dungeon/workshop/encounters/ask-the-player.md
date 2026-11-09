# Side Passage: Ask the Player (Floor 2 Sidequest)

[Back to Floor 2](../floor-2.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-2-ask-the-player/ask_the_player.py`](../../encounters/floor-2-ask-the-player/ask_the_player.py), [`encounters/dance_floor.py`](../../encounters/dance_floor.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 2, TUESDAY, JUNE 12, SIDE PASSAGE OFF FLOOR 2.** Until now the System AI has called every dance-off as if the outcome was already settled. The System AI picked the Move Call, rolled the dice, and the first I heard of my own footwork was the replay. I do not like a plan someone else settles over my head. In the eelgrass the System AI had cleared the floor for a round against the Quarterly Close Accountant, the lights were up and the music was waiting. Then the System AI stopped, mid-sentence, and asked me which move I wanted to call. A handoff works that way on a flight line: the one who owns the decision says it out loud, and everyone else waits for it. Barnaby leaned on my shoulder. "Sergeant, I believe it is a question for you." Shelly had dug in at my heel and said nothing, which is how Shelly agrees.
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "Sidequest: Ask the Player. I will now stop the show and ask the player a question. The interruption is irregular. The dice, I assure you, remain fair."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 2](../floor-2.md), finished: vended tools are already in the toolbox |
| build | a Narrator that pauses its own turn to ask the player which Move Call to make, and a loop that resumes it with the answer |
| teaches | [`strands.vended_tools.handoff_to_user`](https://strandsagents.com/docs/api/python/strands.vended_tools.handoff_to_user.handoff_to_user/) |
| time | about 15 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

Most tools do something and hand back a result. [`handoff_to_user`](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/handoff-to-user/) does the opposite: it stops the agent. Amazon Nova 2 Lite calls it with a question, the agent's turn ends right there, and the result carries the question instead of an answer. The agent is not finished; the agent is waiting. Call the same agent again with the person's reply and the agent picks the turn up where it stopped and the reply becomes the tool's result. That pause-and-resume cycle is Strands' [interrupt](https://strandsagents.com/docs/user-guide/sdk/interrupts/) mechanism, and `handoff_to_user` is the easiest way to use it: no custom tool, no approval prompt, only a question.

Two details carry the lesson. The stopped result has `stop_reason == "interrupt"`, and its `interrupts` list holds the question as the interrupt's `reason`. The resume is not a new question; the resume is a content block that names the interrupt it answers, so the agent matches the answer to its question.

The dice stay in code. The Narrator asks which Move Call, the player picks, and the shared `dance_round` from [`dance_floor.py`](../../encounters/dance_floor.py) rolls and scores it, as in every dance-off. Amazon Nova 2 Lite decides when to ask. The Python code decides what a valid answer looks like.

Success looks like this: the show stops with a question from the Narrator and waits for the player to type; after the player answers with a Move Call, the Narrator reports the round with both totals and the winner, and the scoreboard line below the report matches the Move Call typed.

Open the encounter folder:

```bash
cd seattle-strands-dungeon-crawl/dungeon/encounters/floor-2-ask-the-player
```

## Step 1: Import the Tool

```python
# TODO: Step 1 - Import handoff_to_user from strands.vended_tools
```

`handoff_to_user` ships with the SDK, like the Floor 2 tools. The given code already imports `dance_round` from the shared dance floor.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import handoff_to_user from strands.vended_tools
from strands.vended_tools import handoff_to_user
```

</details>

## Step 2: Give the Narrator Both Tools

```python
# TODO: Step 2 - Add the handoff_to_user and dance_round tools to the agent
```

The prompt in the file tells the Narrator the Move Call is the player's to make, to ask before rolling, and to list the six choices in its question. Without that instruction, Amazon Nova 2 Lite, given `dance_round`, picks a Move Call and rolls; the tool alone is not enough. The prompt also says to call `handoff_to_user` once, so the show stops once, not on every sentence.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** A good question has the answers in it. The System AI does not say "what do you want to do?" It lists the six moves. I read the list, I know my numbers, Footwork is plus one and Power is plus three, and I call Power. The accountant brought a calculator and no warm-up. I like my odds.

<details>
<summary>Show me the code for Step 2</summary>

```python
    tools=[
        # TODO: Step 2 - Add the handoff_to_user and dance_round tools to the agent
        handoff_to_user,
        dance_round,
    ],
```

</details>

## Step 3: Notice the Pause

```python
# TODO: Step 3 - Return whether the result's stop_reason is "interrupt"
```

When an agent finishes normally, `stop_reason` is `end_turn`. When a tool stops the agent to ask a question, `stop_reason` is `interrupt`. `asking(result)` is the check the main loop runs after every call: did the Narrator finish, or is the Narrator waiting for the player? See [Interrupts](https://strandsagents.com/docs/user-guide/sdk/interrupts/).

<details>
<summary>Show me the code for Step 3</summary>

```python
    # TODO: Step 3 - Return whether the result's stop_reason is "interrupt"
    return result.stop_reason == "interrupt"
```

</details>

## Step 4: Answer the Right Question

```python
# TODO: Step 4 - Return an "interruptResponse" block holding the interrupt's id as "interruptId" and the answer as "response"
```

To resume, call the same `narrator` again, and the prompt is a list holding one block: `{"interruptResponse": {"interruptId": ..., "response": ...}}`. The id comes from the interrupt in `result.interrupts`; the SDK generates the id, so copy the id and never build one. The response is the value the tool returns, here the typed Move Call. See the [interrupt types](https://strandsagents.com/docs/api/python/strands.types.interrupt/).

<details>
<summary>Show me the code for Step 4</summary>

```python
    # TODO: Step 4 - Return an "interruptResponse" block holding the interrupt's id as "interruptId" and the answer as "response"
    return {"interruptResponse": {"interruptId": interrupt.id, "response": answer}}
```

Trap: resume the same `narrator` object. The paused turn lives in the narrator's state. A second `Agent(...)` has nothing to resume, and the SDK refuses with a message that the agent is not in an interrupt state.

</details>

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The id on the answer matters. On a flight line you do not say "yes" to the air and hope the right aircraft hears it. You say it to the one that called. The block names the question it answers, and a handoff is nothing more: the right answer reaching the right asker.

## Run It

```bash
python ask_the_player.py
```

Check: the Narrator stops, the player types one of the six moves, and the round plays. The question wording comes from Amazon Nova 2 Lite and the dice are random, so this output is an example:

```
THE NARRATOR STOPS THE SHOW: Cordula, the Quarterly Close Accountant is ready. Which Move Call will you make: Power, Footwork, Endurance, Choreography, Read the Room or Presence?
Your Move Call: Power

Narrator: Cordula comes in with a 14 + 3 = 17 against the Quarterly Close Accountant's 9 + 0 = 9. The party takes the round, and the calculator takes a hit.
  Power: Cordula: 14 + 3 = 17 against the Quarterly Close Accountant: 9 + 0 = 9 -> party
```

| you see | it means | fix |
|---|---|---|
| `NameError: name 'handoff_to_user' is not defined` | Step 1 is missing | add the import |
| the Narrator picks a move and rolls without asking | the tool list lacks `handoff_to_user`, or Amazon Nova 2 Lite chose not to ask | finish Step 2, and keep the prompt's "The Move Call is the player's to make" |
| the run ends right after the question without waiting for the player | `asking` returns `False` | finish Step 3 |
| `ValueError: Received interrupt responses but agent is not in interrupt state` | the loop resumed a different agent object | resume the same `narrator` |
| `KeyError` or no matching interrupt on resume | the block does not carry the interrupt's id | finish Step 4: `interruptId` must be `interrupt.id` |
| the round says the Move Call is not valid | the typed answer is not one of the six moves | type one exactly: Power, Footwork, Endurance, Choreography, Read the Room or Presence |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Question or Approval

Floor 2's bonus room asks the person a different question: may the agent run this tool? The answer is a yes or a no about a call the agent already decided to make. `handoff_to_user` asks a question only the person can answer: which Move Call should the round use? The answer becomes data the agent uses. Use approval when the risk is in the action, and a handoff when the missing piece is a choice. The [interventions](policy-gatekeeper.md) side passage shows approval at scale.

## What It Costs

The pause costs nothing; the turn ends. A run takes two Narrator turns instead of one: the Narrator runs up to the question, and again after the player's answer. About 3 calls at roughly 1,500 input tokens each is 4,500 input tokens at $0.30 per million, $0.0014, plus about 300 output tokens at $2.50 per million, $0.00075. About two tenths of a cent a run. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot to keep:

- `handoff_to_user`: a tool that stops the turn to ask the player something
- Pause and resume: `stop_reason == "interrupt"` and the `interruptResponse` block
- The difference between asking a person for permission and asking for a choice
- A Narrator that leaves the Move Call to the player and the rolls to code

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[YOUR CALL, CRAWLER]**
>
> Reward: You received a [Bronze Box]. Inside: a whistle on a lanyard, a clipboard with one question on it, and an answer in Barnaby's handwriting.

Back to [Floor 2](../floor-2.md#floor-clear), or on to [Floor 3](../floor-3.md).
