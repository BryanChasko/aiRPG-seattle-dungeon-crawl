# Side Passage: The Paper Trail (Floor 5 Sidequest)

[Back to Floor 5](../floor-5.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-5-paper-trail/index_audit_report.py`](../../encounters/floor-5-paper-trail/index_audit_report.py), [`encounters/floor-5-paper-trail/audit-report.pdf`](../../encounters/floor-5-paper-trail/audit-report.pdf), [`encounters/floor-5-paper-trail/make_audit_report.py`](../../encounters/floor-5-paper-trail/make_audit_report.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA'S LOG, DAY 7, SUNDAY, JUNE 17, SIDE PASSAGE OFF FLOOR 5.** After the dance-off, the Quarterly Close Accountant left in a hurry and left a binder behind on the pickleweed: AUDIT REPORT, two pages, signed. I do not read other people's mail. Barnaby does, and he says an audit of us is not other people's mail. The problem was that our rule clerk could only read Markdown, and the binder was a PDF. So we taught the rule clerk to read paper.
<!-- /cordula-log -->

> <img src="../../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "An audit, Crawlers. Of you. The System AI has read the audit. The System AI laughed at Finding 2. Feed the audit to the Rules Agent and find out what an accountant thinks of your bookkeeping."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 5](../floor-5.md), finished: the knowledge base built and the Rules Agent working |
| to build | a script that reads a PDF with `pypdf`, cuts it into passages and adds them to the Rules Agent's ChromaDB collection |
| teaches | [`pypdf.PdfReader`](https://pypdf.readthedocs.io/en/stable/modules/PdfReader.html) and [text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html); adding documents to an existing knowledge base |
| time | about 20 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

The workshop this crawl is built on indexed its rule book from a PDF. The crawl keeps its rules in Markdown, so the PDF technique returns here. The Floor 5 knowledge base is a ChromaDB collection of passages, each with a section name; a PDF is another source of passages. Read each page's text, cut the text the same way as the handbook, give every passage a section the Rules Agent can cite, and add it to the same collection. The Rules Agent needs no change: it searches the collection, whatever the collection holds.

Success check: the script reports the passages added, and the Rules Agent answers a question about the audit with `[Audit Report, page 1]` or `page 2` in its sources.

`audit-report.pdf` ships in the folder. `make_audit_report.py` is the script that wrote it, with nothing but the Python standard library, so the file visibly holds only text; running it is optional. `pypdf` is in the workshop dependencies: if `uv sync` ran before this encounter existed, run `uv sync` again.

Go to the encounter folder:

```bash
cd seattle-strands-dungeon-crawl/dungeon/encounters/floor-5-paper-trail
```

## Step 1: Import the Reader

```python
# TODO: Step 1 - Import PdfReader from pypdf
```

`PdfReader` opens a PDF and returns its pages. See [PdfReader](https://pypdf.readthedocs.io/en/stable/modules/PdfReader.html).

<details>
<summary>Show me the code for Step 1</summary>

```python
import chromadb
# TODO: Step 1 - Import PdfReader from pypdf
from pypdf import PdfReader
```

</details>

## Step 2: Read Every Page

```python
# TODO: Step 2 - Open the PDF with PdfReader and return the extract_text() of each of its pages
```

`PdfReader(path).pages` is a list of pages, and `page.extract_text()` returns the text of one page as a string. Return one string per page, in order: Step 3 needs the page numbers. See [Extract Text from a PDF](https://pypdf.readthedocs.io/en/stable/user/extract-text.html).

<details>
<summary>Show me the code for Step 2</summary>

```python
def read_pages(path: Path) -> list[str]:
    """The text of every page of the PDF, in order."""
    # TODO: Step 2 - Open the PDF with PdfReader and return the extract_text() of each of its pages
    return [page.extract_text() for page in PdfReader(path).pages]
```

Replace the `return []` under the TODO.

</details>

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** A PDF is a picture of a page with words under it. Pulling the words back out is the whole trick. This PDF came out clean, two pages, five findings, one management response. Barnaby read Finding 2 and went the color of a stop sign.

## Step 3: Cut and Label the Passages

```python
# TODO: Step 3 - Cut each page into passages. Number pages from 1; give each passage the id "audit-report_p<page>_<n>" and the metadata {"section": "Audit Report, page <page>", "source": "audit-report.pdf"}
```

`cut(text)` is given: the Floor 5 cut, passages of about 1,000 characters that overlap by 200. Loop over the pages with their numbers (`enumerate(pages, start=1)`), cut each one, and build one dictionary per passage with three keys: `id`, `text` and `metadata`. The section is what the Rules Agent prints in front of each passage, `[Audit Report, page 2]`, the way handbook passages show `[Final Beat]`. Each id must be unique in the collection, hence the page and the passage number.

<details>
<summary>Show me the code for Step 3</summary>

```python
def passages(pages: list[str]) -> list[dict]:
    """Every passage of the report, ready for ChromaDB: an id, the text, and the section it cites."""
    # TODO: Step 3 - Cut each page into passages. ...
    found = []
    for page_number, text in enumerate(pages, start=1):
        for n, passage in enumerate(cut(text)):
            found.append({
                "id": f"audit-report_p{page_number}_{n}",
                "text": passage,
                "metadata": {"section": f"Audit Report, page {page_number}", "source": "audit-report.pdf"},
            })
    return found
```

</details>

## Run It

```bash
python index_audit_report.py
```

Check: one line, `3 passages from audit-report.pdf are in 'crawl_handbook' (N passages in all)`, where N is the handbook's passages plus three. Run it twice: the count stays the same, because the script upserts by id instead of adding.

| output | cause | fix |
|---|---|---|
| `No knowledge base at ...` | the Floor 5 knowledge base is not built | run `python create_knowledge_base.py` from `5_a2a_integration/utils` |
| `No passages: complete Steps 2 and 3` | `read_pages` or `passages` still returns `[]` | Steps 2 and 3 |
| `ModuleNotFoundError: No module named 'pypdf'` | the environment predates this encounter | `uv sync` from the repository root |
| the count grows on every run | the ids change between runs | build them from the page and passage numbers only |

Then ask the party. Start the Rules Agent, the Character Agent, the dice server and the Narrator as on [Floor 5, Part 4](../floor-5-3.md#part-4-test-the-system), and send:

```bash
curl -X POST http://0.0.0.0:8009/inquire \
  -H "Content-Type: application/json" \
  -d '{"question": "Ask the Rules Agent what the Quarterly Close Accountant'\''s audit report found about our Groove, and whether the accountant has danced before."}'
```

The Rules Agent terminal shows the passages it found, `[Audit Report, page 1]` and `[Audit Report, page 2]` among them, and the answer cites Finding 1 (Groove is a stat, not money) and Finding 4 (one dance-off, at a 2019 holiday party). After rebuilding the knowledge base with `create_knowledge_base.py`, which deletes the collection and starts over, run `index_audit_report.py` again.

## What It Costs

Nothing on AWS for the indexing: `pypdf` and ChromaDB run on the local machine, and the embedding model is the one Floor 5 already downloaded: `all-MiniLM-L6-v2`, 79.3 MB, which took about 2 to 3 minutes in the live run, downloads once and is cached after that. The question costs a Narrator turn, under one cent ([Floor 5](../floor-5-3.md#what-a-narrator-turn-costs)).

> <img src="../../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The rule clerk read the audit back to us with section and page, in the same bored voice it uses for the Final Beat. Finding 1 was fair. Finding 3 was fair too: I had not checked the tide before the dance-off, and the tide matters on this floor. The tide check is on my checklist now. Finding 5 we kept to ourselves. Barnaby has filed a formal dispute of Finding 2. The dispute is four pages long. I have not read the dispute.

## Encounter Clear

Loot kept:

- How to read a PDF's text with `pypdf.PdfReader` and `extract_text()`
- How to add a new source to an existing knowledge base: same cut, same collection, a section name to cite
- Why `upsert` with stable ids makes an indexing script safe to run twice

> <img src="../../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[AUDITED AND UNBOTHERED]**
>
> Reward: a [Bronze Box]. Inside: a PDF reader, three new passages, and one management response the System AI has framed.

Back to [Floor 5](../floor-5-3.md#floor-clear), or on to [Floor 6](../floor-6.md).
