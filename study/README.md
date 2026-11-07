# Ask the System: the Study Companion

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "You may ask me questions. I will answer them correctly and make you feel slightly worse about needing to ask."

`ask_the_system.py` is a help desk for the crawl, built with the same SDK you are learning. Ask it about any floor, any TODO, any error message or any Strands API. It answers in the System's voice from two sources only, this repository's pages and the Strands API reference, and it cites both.

```bash
python study/ask_the_system.py                                   # chat; type exit to leave
python study/ask_the_system.py "what is an agent card for?"      # one question
```

It needs the same AWS credentials as the floors (Amazon Nova 2 Lite in us-west-2). The search index and your chat session live in `study/.state/`, which is gitignored; delete the folder to start fresh.

## How It Is Built

Read the file once you have cleared Floor 3. Every piece is something the workshop teaches, or a step past it:

| piece | Strands API | floor |
|---|---|---|
| three `@tool` functions whose docstrings tell the model when to use them | `strands.tools.decorator` | 3 |
| full-text search over the pages, no embeddings, no database server | `strands.storage.LocalFileStorage`, `strands.storage.search.bm25.Bm25SearchStrategy` | past 5 |
| a chat that survives restarts | `strands.session.file_session_manager.FileSessionManager` | 7 (the harness does the same) |
| a long study session that never overflows the context | `strands.agent.conversation_manager.SlidingWindowConversationManager` | past 7 |
| tools that refuse anything outside their lane: only workshop pages, only `strands.*` modules | plain Python guards | 2 (the same idea as `HumanInTheLoop`, enforced in code) |

It gives hints before answers: when you are stuck on a TODO, it points you at the page and the API first, and only hands over the answer when you ask. The answers live on the `solution` branch.

## The Knowledge Pack

`build_pack.py` writes `knowledge-pack.md`: every floor's objective, its SYSTEM DESIGN layer and every TODO step, word for word, then the party's cast sheets and the whole Crawl Handbook. It runs about 30 KB, small enough for one system prompt, so a chat with no tools and no retrieval can still answer from the real text. The companion site's chat ships this file.

```bash
python study/build_pack.py          # rewrite the pack after you change a page
python study/build_pack.py --check  # fails if the pack is stale
```
