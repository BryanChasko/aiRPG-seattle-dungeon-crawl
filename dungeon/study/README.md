# Ask the System: the Study Companion

> <img src="../../images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "You may ask me questions. I will answer them correctly and make you feel slightly worse about needing to ask."

`ask_the_system.py` is a help desk for the crawl, built with the Strands Agents SDK this workshop teaches. Ask the System about any floor, any TODO, any error message or any Strands API. The System answers in its voice from two sources only, this repository's pages and the Strands API reference, and cites both.

```bash
python dungeon/study/ask_the_system.py                                   # chat; type exit to leave
python dungeon/study/ask_the_system.py "what is an agent card for?"      # one question
```

`ask_the_system.py` needs the same AWS credentials as the floors (Amazon Nova 2 Lite in us-west-2). The search index and the chat session live in `dungeon/study/.state/`, which is gitignored; delete the folder to reset the index and the chat session.

## How It Is Built

Read `ask_the_system.py` after clearing Floor 3. Each piece comes from a floor, or goes one step past a floor:

| piece | Strands API | floor |
|---|---|---|
| three `@tool` functions whose docstrings tell Amazon Nova 2 Lite when to call them | `strands.tools.decorator` | 3 |
| full-text search over the pages, no embeddings, no database server | `strands.storage.LocalFileStorage`, `strands.storage.search.bm25.Bm25SearchStrategy` | past 5 |
| a chat that survives restarts | `strands.session.file_session_manager.FileSessionManager` | 7 (the harness does the same) |
| a long study session that never overflows the context | `strands.agent.conversation_manager.SlidingWindowConversationManager` | past 7 |
| tools that refuse anything outside their lane: only workshop pages, only `strands.*` modules | plain Python guards | 2 (the same idea as `HumanInTheLoop`, enforced in code) |

`ask_the_system.py` gives hints before answers: when a TODO blocks progress, the System points to the page and the API first, and gives the answer only when asked. The answers live on the `solution` branch.

## The Knowledge Pack

`build_pack.py` writes `knowledge-pack.md`: every floor's objective, its SYSTEM DESIGN layer and every TODO step, word for word, then the party's cast sheets and the whole Crawl Handbook. The pack runs about 30 KB, small enough for one system prompt, so a chat with no tools and no retrieval can answer from the real text. The companion site's chat ships this file.

```bash
python dungeon/study/build_pack.py          # rewrite the pack after you change a page
python dungeon/study/build_pack.py --check  # fails if the pack is stale
```
