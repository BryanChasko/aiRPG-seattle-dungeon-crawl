# Side Passage: Sponsor Interrupt (Floor 6 Sidequest)

[Back to Floor 6](../floor-6.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-6-sponsor-interrupt/sponsor_interrupt.py`](../../encounters/floor-6-sponsor-interrupt/sponsor_interrupt.py), [`web/src/components/SponsorDealDialog.vue`](../../../site/web/src/components/SponsorDealDialog.vue), [`web/src/composables/useGameApi.ts`](../../../site/web/src/composables/useGameApi.ts), [`web/src/stores/gameStore.ts`](../../../site/web/src/stores/gameStore.ts), [`web/src/views/GameView.vue`](../../../site/web/src/views/GameView.vue) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 8, WEDNESDAY, JUNE 24, SIDE PASSAGE OFF FLOOR 6.** The Pitch-Deck Founder caught us between rounds with a clicker in one hand and a contract in the other. The Bellevue Consortium pays for the opponents, and the Consortium had a deal for us: wear the logo for a floor, receive a box. The Troll said nothing. Barnaby read the first line out loud and then the System AI cut in and held the clock. Here is what I learned. The System AI can stop the turn. It cannot answer for us. When the deal came, the turn waited on me, and I took my time.
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "A sponsor is on the line. The status feed is holding. Please enjoy this tasteful pause while the Crawler reads the terms. The terms are long. The review board is patient. The review board is not as patient."

<img src="../../../art/images/cards/opponent-founder-640x640.webp" alt="The Pitch-Deck Founder in a black turtleneck and white sneakers, slide clicker held high, a glowing arrow chart rising behind her" width="240">

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 6](../floor-6.md), finished: the Floor 5 Narrator on port 8009 and the web interface in `web/` |
| you build | a hook that stops the turn before a sponsor deal runs, a `POST /respond` route that resumes it, and a dialog in the web interface where the player accepts or refuses |
| teaches | [`strands.interrupt`](https://strandsagents.com/docs/api/python/strands.interrupt/): `Interrupt`, the interrupt state; [`strands.types.interrupt`](https://strandsagents.com/docs/api/python/strands.types.interrupt/): how a hook raises one and how the agent resumes; [`strands.hooks.events`](https://strandsagents.com/docs/api/python/strands.hooks.events/): `BeforeToolCallEvent` |
| time | about 25 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

An interrupt pauses the agent loop and hands a question to a human. Strands calls this pause human-in-the-loop. A hook calls `event.interrupt(name, reason=...)`. On the first call, no answer exists yet: the loop stops, and the agent result comes back with `stop_reason == "interrupt"` and a list of `interrupts`, each with an `id`, the `name` and `reason` the hook passed. To resume, call the same agent again with a list of `interruptResponse` blocks, one per interrupt, holding the `id` and the answer. The hook runs a second time, and this time `event.interrupt(...)` returns the answer instead of stopping. See [Interrupts](https://strandsagents.com/docs/user-guide/sdk/interrupts/).

Here the interrupt guards a tool. The Narrator in this folder is the Floor 5 Narrator, copied and extended, with one new tool, `sponsor_offer(sponsor, offer, reward, cost)`, which the Narrator calls when a sponsor makes a deal, and which the System AI announces. A hook on `BeforeToolCallEvent` runs immediately before any tool and, for `sponsor_offer`, raises the interrupt. If the player accepts, the tool runs. If the player refuses, the hook cancels the tool with a message, and the Narrator retells the refusal in the System AI's voice.

The route work is a protocol with the web interface:

| call | what comes back |
|---|---|
| `POST /inquire` | the usual `{"response": ...}`, plus an `interrupt` field (`id`, `name`, `reason`) when the turn paused on a deal |
| `POST /respond` with `{"interrupt_id": "...", "accepted": true}` | the rest of the same turn, in the same shape, and a new `interrupt` if there is another deal |

When a turn pauses, `response` is a short holding notice in the `StoryOutput` shape, so a page that knows nothing about deals still has a story to draw.

Check: in the web interface a dialog opens with the sponsor, the offer, the reward and the cost; Accept and Refuse each finish the turn, and the System AI's story reflects the answer.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/dungeon/encounters/floor-6-sponsor-interrupt
```

## Step 1: Listen Before Every Tool

```python
# TODO: Step 1 - Register self.ask_the_player with registry.add_callback for BeforeToolCallEvent
```

`BeforeToolCallEvent` fires immediately before a tool runs. The event carries the tool call (`event.tool_use`, with the tool's name and the input the Narrator chose) and a hook can change the event: setting `event.cancel_tool` stops the call. `ask_the_player` checks the name and ignores every tool but `sponsor_offer`, so dice, the Rules Agent and the Character Agent never wait on a person.

<details>
<summary>Show me the code for Step 1</summary>

```python
def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
    # TODO: Step 1 - Register self.ask_the_player with registry.add_callback for BeforeToolCallEvent
    registry.add_callback(BeforeToolCallEvent, self.ask_the_player)
```

Replace the `pass`. The Agent already receives the provider with `hooks=[sponsor_deals]`.

</details>

## Step 2: Raise the Interrupt

```python
# TODO: Step 2 - Raise the interrupt with event.interrupt("sponsor_deal", reason=reason) and keep the player's answer
```

`event.interrupt("sponsor_deal", reason=reason)` is the whole mechanism. The name identifies the interrupt, and the name must be unique among the interrupts the hooks raise. The reason is any JSON-friendly value; here the reason holds the sponsor, the offer, the reward and the cost, which is exactly what the dialog needs. On the first pass the call raises an exception that Strands catches to stop the loop. On the resume it returns whatever the player answered, so the line reads like a plain function call and the code after the call runs only once there is an answer.

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** One call, and the turn stopped. No flag to set, no state to save. The pause was a checklist item I could not tick until somebody signed. I have flown with worse systems. I have flown with no systems.

## Step 3: Let a Refusal Cancel the Tool

```python
# TODO: Step 3 - When the answer is not "accept", cancel the tool call by setting event.cancel_tool to a message the System AI can retell
```

Setting `event.cancel_tool` to a string cancels the call; the string goes back to the Narrator as the tool's result, with an error status. Write the string as an instruction the Narrator can retell: the Crawler refused, the sponsor sulks. If `event.cancel_tool` is set to `True` instead, Strands uses a default message.

<details>
<summary>Show me the code for Steps 2 and 3</summary>

```python
        # TODO: Step 2 - Raise the interrupt with event.interrupt("sponsor_deal", reason=reason) and keep the player's answer
        answer = event.interrupt("sponsor_deal", reason=reason)
        # TODO: Step 3 - When the answer is not "accept", cancel the tool call by setting event.cancel_tool to a message the System AI can retell
        if answer != "accept":
            event.cancel_tool = "The Crawler refused the deal. Tell them the sponsor sulks, then carry on."
```

Replace the placeholder line `answer = "accept"`. The trap: anything before the `event.interrupt` line runs twice, once on the pause and once on the resume, so keep that code free of side effects.

</details>

## Step 4: Tell the Browser the Turn Paused

```python
# TODO: Step 4 - When result.stop_reason is "interrupt", also return the first interrupt as id, name and reason
```

A paused turn has no `structured_output`: the Narrator has not finished the story. `result.interrupts` lists what is waiting, and each `Interrupt` has an `id`, a `name` and the `reason` the hook gave. `turn_payload` is the one function that turns an agent result into JSON, so `/inquire` and `/respond` answer in the same shape.

<details>
<summary>Show me the code for Step 4</summary>

```python
def turn_payload(result) -> dict:
    """The JSON for one turn: the story, plus the interrupt when the turn paused on a sponsor deal."""
    # TODO: Step 4 - When result.stop_reason is "interrupt", also return the first interrupt as id, name and reason
    if result.stop_reason == "interrupt" and result.interrupts:
        first = result.interrupts[0]
        sponsor = (first.reason or {}).get("sponsor", "A sponsor")
        holding = {
            "response": f"SPONSOR LINE: {sponsor} is on the line. The broadcast holds the turn until the Crawler answers.",
            "actions_suggestions": [],
            "details": "interrupt",
            "dice_rolls": [],
        }
        return {"response": holding, "interrupt": {"id": first.id, "name": first.name, "reason": first.reason}}
    return {"response": result.structured_output.model_dump()}
```

The `id` is opaque: return the `id` unchanged; never build or parse it.

</details>

## Step 5: Resume with the Answer

```python
# TODO: Step 5 - Resume the agent with a list of one interruptResponse block: the interrupt id and "accept" or "refuse"
```

The agent is in an interrupt state until the agent receives answers. Its next input must be a list of `interruptResponse` blocks, each with the `interruptId` and the `response`. Any other input raises an error. The agent keeps the paused turn in memory, so the same `Agent` object must answer: the script keeps one for the whole run. A restart loses the paused turn, unless the script adds a session manager.

<details>
<summary>Show me the code for Step 5</summary>

```python
@app.post("/respond")
async def respond_to_sponsor(answer: DealAnswer):
    print("Resuming the turn...")
    try:
        # TODO: Step 5 - Resume the agent with a list of one interruptResponse block: the interrupt id and "accept" or "refuse"
        resume = [{"interruptResponse": {"interruptId": answer.interrupt_id,
                                         "response": "accept" if answer.accepted else "refuse"}}]
        response = await agent.invoke_async(resume)
        return JSONResponse(content=turn_payload(response))
```

Replace `resume = []`. The same hook runs again, `event.interrupt` returns `"accept"` or `"refuse"`, and Step 3 decides.

</details>

## The Dialog in the Web Interface

The web interface already ships the dialog. `useGameApi` posts the turn and reads the `interrupt` field; `GameView.vue` keeps the deal in the game store and shows `SponsorDealDialog.vue` above the text box, with Accept and Refuse. While a deal is open the suggestions and the text box are off, because the turn is waiting on exactly one answer. Each button calls `POST /respond`, adds the System AI's finished story to the log, and clears the dialog; if the Narrator pauses again on a second deal, the dialog opens again.

The dialog is optional, like the Hype panel. A Narrator that never sends `interrupt` never opens the dialog, and the Floor 5 Narrator works with the same page. Run the interface from this repository, as in [Floor 6](../floor-6.md#web-interface):

```bash
cd aiRPG-seattle-dungeon-crawl/site/web
npm ci
npm run dev
```

## Run It

Stop the Floor 5 Narrator first: both listen on port 8009. Keep the dice server and the Rules and Character agents running.

```bash
python sponsor_interrupt.py
```

In the web interface, enter the dungeon and type: "The Pitch-Deck Founder says the Bellevue Consortium has a sponsor deal for us. Hear it."

Check: the log shows a SPONSOR LINE notice, and a dialog opens. The wording changes between runs. An example:

```
The Bellevue Consortium wants a word
Wear the logo for one floor.
YOU GET: a Silver Box
YOU OWE: one photo with the Fremont Troll
[Accept the deal] [Refuse the deal]
```

Press Accept: the turn finishes and the System AI hands over the box. Ask again and press Refuse: the System AI says the sponsor sulks. The terminal prints `Resuming the turn...` for each answer.

| symptom | cause | fix |
|---|---|---|
| `Address already in use` | the Floor 5 Narrator is still on port 8009 | stop the Floor 5 Narrator, then run `sponsor_interrupt.py` |
| the System AI announces a deal and no dialog opens | the Narrator is running, but the hook is not registered, or `turn_payload` has no interrupt branch | Steps 1 and 4 |
| the turn never pauses, the Narrator carries on | `answer = "accept"` is still the placeholder | Step 2 |
| Refuse does not change the story | a refusal does not cancel the tool | Step 3 |
| the browser shows "Request failed with status 500" after a button press | `resume` is still an empty list, or the Narrator restarted and lost the paused turn | Step 5, then start a new turn |
| `POST /respond` answers 500 right after you restarted the server | the interrupt id is only valid for the life of the server process, so a restart between `POST /inquire` and `POST /respond` loses it | send `POST /inquire` again after any restart, then answer the new interrupt |
| typing while a deal is open | the text box is off on purpose | answer the deal |
| `AccessDeniedException` or `ExpiredToken` | the Amazon Nova 2 Lite call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-amazon-nova-2-lite-aws) |

## Interrupt or Ask the Player?

The Narrator could ask the player a question in its story, in the System AI's voice, and wait for the next message. The Narrator does that every turn. An interrupt is different: the code stops at an exact line, with the tool still unrun, and nothing proceeds on a guess. For a sponsor deal the stop matters, because the tool is the commitment. The cost: the script must keep the paused agent alive and give the browser a way to answer.

## What It Costs

The pause costs nothing: while the turn waits, Amazon Nova 2 Lite does not run and no tokens are billed. The deal adds about one extra pass through Amazon Nova 2 Lite, the pass that makes the `sponsor_offer` call. Assume 6,000 tokens in and 150 out.

- 6,000 x $0.30 per million is $0.0018 in, 150 x $2.50 per million is $0.000375 out, about $0.002 per deal
- a refused deal costs the same: the Narrator still retells the refusal in the story the Narrator was already writing

Rates are the Nova 2 Lite prices from [Floor 1](../floor-1.md#what-a-turn-costs).

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** I refused the first deal. The Founder took it well, for a person who had just rehearsed it for four hours. The second deal had a fine-print clause about the Troll. I accepted the deal before Barnaby could finish reading, and I will hear about that. Two answers, two different turns, and both were mine.

## Encounter Clear

Loot to keep:

- A hook raises an interrupt with `event.interrupt(name, reason=...)`; the loop stops and the result has `stop_reason == "interrupt"` and a list of `interrupts`
- Resume by calling the same agent with `interruptResponse` blocks (the `interruptId` and the `response`); the hook runs again and `event.interrupt` returns the answer
- `event.cancel_tool` turns a refusal into a tool result the Narrator can retell
- A web interface can feature-detect a new field and open a dialog only when it appears

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[READ THE FINE PRINT]**
>
> Reward: You received a [Bronze Box]. Inside: one reading lamp, one highlighter, and a sponsor's guarantee that the terms were "mostly legible".

Back to [Floor 6](../floor-6.md#floor-clear), or on to [Floor 7](../floor-7.md).
