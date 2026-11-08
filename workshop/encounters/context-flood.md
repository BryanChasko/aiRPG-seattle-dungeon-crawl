# Side Passage: The Context Flood (Floor 7 Boss Battle)

[Back to Floor 7](../floor-7.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-7-context-flood/context_flood.py`](../../encounters/floor-7-context-flood/context_flood.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 7.** Sixty turns. That is how long the campaign had run by the time we reached the bottom of the bluffs, and the System was carrying every word of it, every roll, every opponent, every bad joke, on every single call. It was getting slow, and it was getting expensive, and the tide was coming up the cliff path. Somebody had to decide what the System could afford to forget. Barnaby had one condition. "Whatever goes, Sergeant, our names stay."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Boss battle: the Context Flood. It has no face and no lanyard. It is sixty turns of your own campaign, coming back to drown you. Choose what I forget, Crawlers. Choose badly and I forget you."

## The Brief

| | |
|---|---|
| type | boss battle |
| starts from | [Floor 7](../floor-7.md), finished; the code uses the plain SDK `Agent`, as on Floors 1 to 5 |
| you build | three Narrators that face the same 60-turn history: a sliding window, the same window with the cast sheets pinned, and a summarizing manager |
| teaches | [`SlidingWindowConversationManager`](https://strandsagents.com/docs/api/python/strands.agent.conversation_manager.sliding_window_conversation_manager/), [`SummarizingConversationManager`](https://strandsagents.com/docs/api/python/strands.agent.conversation_manager.summarizing_conversation_manager/), [`pin_message`](https://strandsagents.com/docs/api/python/strands.agent.conversation_manager.compression.pin_message/) |
| time | about 25 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

An agent keeps its conversation in `agent.messages` and sends all of it to the model on every call. Nova 2 Lite's context window holds far more than sixty turns, so the flood is not about running out of room: it is about paying, every call, to resend turns nobody needs. A conversation manager trims the history. The sliding window keeps the latest messages and drops the oldest. The summarizing manager asks the model to fold the oldest messages into one summary. Both drop the first messages first, and in this campaign the first messages are the party's cast sheets. Pinning a message protects it from every manager. See [Conversation Management](https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/).

The given code builds the flood for you: `campaign_log()` writes 122 messages, the cast sheets and their receipt, then 60 turns of dance-offs. `flood()` loads them into a Narrator and calls `reduce_context`, the same call Strands makes when a conversation overflows the model's window. Then each Narrator gets the same question: Cordula's Constitution score, from the cast sheets, and the opponent of turn 3, from the oldest turns.

How you know it worked: the unpinned window forgets both answers, the pinned window remembers the score and forgets turn 3, and the summarizing Narrator, with the cast sheets pinned, can answer both.

Go to the encounter folder:

```bash
cd aiRPG-seattle-dungeon-crawl/encounters/floor-7-context-flood
```

## Step 1: Import the Pin

```python
# TODO: Step 1 - Import pin_message from strands.agent.conversation_manager.compression.pin_message
```

`pin_message(messages, index)` marks one message as pinned, in place: it sets `metadata.custom.pinned` on it, and every conversation manager leaves pinned messages where they are. See [Message Pinning](https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/#message-pinning).

<details>
<summary>Show me the code for Step 1</summary>

```python
from strands.agent.conversation_manager import SlidingWindowConversationManager, SummarizingConversationManager
# TODO: Step 1 - Import pin_message from strands.agent.conversation_manager.compression.pin_message
from strands.agent.conversation_manager.compression.pin_message import pin_message
```

</details>

## Step 2: The Sliding Window

```python
# TODO: Step 2 - Return a SlidingWindowConversationManager that keeps WINDOW messages
```

`window_size` is the number of messages the window keeps, here `WINDOW`, twenty: ten turns of play. Every agent already has a sliding window by default, with 40 messages; this one is tighter, so the flood shows. See [SlidingWindowConversationManager](https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/#slidingwindowconversationmanager).

<details>
<summary>Show me the code for Step 2</summary>

```python
def sliding_window():
    """Keep the last WINDOW messages and drop the rest."""
    # TODO: Step 2 - Return a SlidingWindowConversationManager that keeps WINDOW messages
    return SlidingWindowConversationManager(window_size=WINDOW)
```

Replace the `return None` under the TODO.

</details>

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The window is how I pack for a long patrol: the last ten days of anything, and the rest stays on the dock. It works until you need something from day one. On day sixty-one, the System could not tell me my own Constitution score. It said it had lost it. At least it did not guess.

## Step 3: Pin the Cast Sheets

```python
# TODO: Step 3 - Pin messages 0 and 1 with pin_message
```

Message 0 is the cast sheets, message 1 the System's receipt for them. Pin both: a conversation must keep its user and assistant messages in pairs, and a pinned pair stays a pair. If you know from the start which messages to keep, the managers also take `pin_first=2`, which pins the first two for you.

<details>
<summary>Show me the code for Step 3</summary>

```python
def pin_cast_sheets(messages: list[dict]) -> None:
    """Protect the first two messages, the cast sheets and their receipt, from every conversation manager."""
    # TODO: Step 3 - Pin messages 0 and 1 with pin_message
    pin_message(messages, 0)
    pin_message(messages, 1)
```

Replace the `pass` under the TODO.

</details>

## Step 4: The Summarizing Manager

```python
# TODO: Step 4 - Return a SummarizingConversationManager that summarizes 80 percent of the history and preserves the last WINDOW messages
```

`summary_ratio` is the share of the oldest messages to fold into the summary, between 0.1 and 0.8; take the most, `0.8`. `preserve_recent_messages` is how many of the latest messages it never touches, here `WINDOW`. The summary is written by the agent's own model, Amazon Nova 2 Lite, in one extra call. Pinned messages are never summarized. See [SummarizingConversationManager](https://strandsagents.com/docs/user-guide/sdk/agents/conversation-management/#summarizingconversationmanager).

<details>
<summary>Show me the code for Step 4</summary>

```python
def summarizing():
    """Fold the oldest messages into one summary, keep at least the last WINDOW as they are."""
    # TODO: Step 4 - Return a SummarizingConversationManager that ...
    return SummarizingConversationManager(summary_ratio=0.8, preserve_recent_messages=WINDOW)
```

</details>

## Fight the Flood

```bash
python context_flood.py
```

Check: three blocks. The first two are the same on every run; the third depends on the summary the model writes, and the System's answers vary in wording:

```
SLIDING WINDOW, nothing pinned
  122 messages (11,955 characters) -> 20 messages (1,927 characters)
  cast sheets still first: False
  the System: The System has lost Cordula's constitution score and the turn 3 opponent. ...

SLIDING WINDOW, cast sheets pinned
  122 messages (11,955 characters) -> 22 messages (2,354 characters)
  cast sheets still first: True
  the System: Cordula's constitution is 16. Turn 3 is lost to the System. ...

SUMMARIZING, cast sheets pinned (one extra model call writes the summary)
  122 messages (11,955 characters) -> 28 messages (...)
  cast sheets still first: True
  the System: Cordula's constitution is 16, and on turn 3 she danced against the Developer Advocate Swarm. ...
```

Twenty-eight messages: the two pinned ones, one summary in place of 95 old messages, and the 25 most recent.

The summary is written by the model, so it is the one answer that can vary: if it leaves turn 3 out, run it again, or lower `summary_ratio` so less history is folded into it.

| you see | it means | fix |
|---|---|---|
| `40 messages` (or `42`) after the flood, in the first two blocks | the default window is in charge: `sliding_window()` returned `None` | Step 2 |
| `cast sheets still first: False` in the second block | the pins are missing | Step 3 |
| `40 messages` after the flood in the third block | `summarizing()` returned `None`, so the default window ran | Step 4 |
| `122 messages -> 122 messages` in the third block | the summary call failed: reducing context this way is best-effort, and logs a warning instead of stopping | check your credentials as in [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws) |
| a Constitution score other than 16 | the System guessed | the prompt forbids it; if it happens with the sheets pinned, ask again |

## What It Costs

The flood is a bill before it is a crash. Take a real campaign turn: say each one adds 1,000 tokens to the history and makes four model calls, each resending a 5,000-token base of system prompt and tool specifications. Turn 60 then sends about 4 x (5,000 + 60,000) = 260,000 input tokens. Over all sixty turns, with no manager, that adds up to about 8.5 million input tokens: about $2.56 at Amazon Nova 2 Lite's $0.30 per million ([Floor 1](../floor-1.md#what-a-turn-costs)). With a 20-message window the history never passes 10,000 tokens, every call stays under 15,000, and the same sixty turns cost about $1.03 in input. The summarizing manager costs one extra model call per reduction, a few cents, to keep what the window throws away. The flood in this file is small: its three runs cost under a cent together.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The third Narrator wrote itself a page of notes on everything before day fifty, kept the last ten days whole, and kept our cast sheets nailed to the front. Ask it anything and it answered. Barnaby asked it what it remembered about the first morning. It said: a woman with a boat, and an octopus with a collar. That was enough for him. The tide reached the cliff path and went back down, and the Commuter Horde went by in the fog, and nobody forgot anybody.

## Encounter Clear

Loot you're keeping:

- Why every turn resends the whole conversation, and what a long campaign costs because of it
- `SlidingWindowConversationManager(window_size=...)`: keep the latest, drop the oldest
- `SummarizingConversationManager(summary_ratio=..., preserve_recent_messages=...)`: fold the oldest into a summary written by the model
- `pin_message` and `pin_first`: the messages no manager may drop

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[I REMEMBER YOU, CORDULA VANCE]**
>
> Reward: You received a [Gold Box]. Inside: two pinned messages, one summary of sixty turns, and a context window with room to breathe.

Back to [Floor 7](../floor-7.md#floor-clear), or on to [Floor 8](../floor-8.md).
