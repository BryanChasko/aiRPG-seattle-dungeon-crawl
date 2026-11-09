"""Floor 5 encounter, The Paper Trail: add a PDF to the Rules Agent's knowledge base.

The Quarterly Close Accountant left an audit report on the pickleweed. This script reads it with
pypdf, cuts it into passages the same way Floor 5 cut the Crawl Handbook, and adds them to the
same ChromaDB collection, so the Rules Agent finds and cites them like any handbook section.

Build the Floor 5 knowledge base first (5_a2a_integration/utils/create_knowledge_base.py), then
run this from this folder, with the workshop environment active:
    python index_audit_report.py
"""

from pathlib import Path

import chromadb
# TODO: Step 1 - Import PdfReader from pypdf
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
REPORT = HERE / "audit-report.pdf"
KB_PATH = HERE.parent.parent / "5_a2a_integration" / "utils" / "rules_knowledge_base"
COLLECTION = "crawl_handbook"
CHUNK_SIZE = 1000    # characters per passage, as in Floor 5
CHUNK_OVERLAP = 200  # characters shared by two consecutive passages, as in Floor 5


def cut(text: str) -> list[str]:
    """The Floor 5 cut: passages of about 1,000 characters that overlap by 200, split between words."""
    text = text.strip()
    pieces, start = [], 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            split = max(text.rfind("\n", start + CHUNK_SIZE // 2, end), text.rfind(" ", start + CHUNK_SIZE // 2, end))
            if split != -1:
                end = split
        passage = text[start:end].strip()
        if len(passage) > 50:
            pieces.append(passage)
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return pieces


def read_pages(path: Path) -> list[str]:
    """The text of every page of the PDF, in order."""
    # TODO: Step 2 - Open the PDF with PdfReader and return the extract_text() of each of its pages
    return [page.extract_text() for page in PdfReader(path).pages]


def passages(pages: list[str]) -> list[dict]:
    """Every passage of the report, ready for ChromaDB: an id, the text, and the section it cites."""
    # TODO: Step 3 - Cut each page into passages. Number pages from 1; give each passage the id "audit-report_p<page>_<n>" and the metadata {"section": "Audit Report, page <page>", "source": "audit-report.pdf"}
    found = []
    for page_number, text in enumerate(pages, start=1):
        for n, passage in enumerate(cut(text)):
            found.append({
                "id": f"audit-report_p{page_number}_{n}",
                "text": passage,
                "metadata": {"section": f"Audit Report, page {page_number}", "source": "audit-report.pdf"},
            })
    return found


if __name__ == "__main__":
    if not KB_PATH.is_dir():
        raise SystemExit(f"No knowledge base at {KB_PATH}: build it first with 5_a2a_integration/utils/create_knowledge_base.py")
    found = passages(read_pages(REPORT))
    if not found:
        raise SystemExit("No passages: complete Steps 2 and 3")
    collection = chromadb.PersistentClient(path=str(KB_PATH)).get_collection(COLLECTION)
    # upsert, not add: run it twice and the passages are replaced, not doubled
    collection.upsert(
        ids=[p["id"] for p in found],
        documents=[p["text"] for p in found],
        metadatas=[p["metadata"] for p in found],
    )
    print(f"{len(found)} passages from {REPORT.name} are in '{COLLECTION}' ({collection.count()} passages in all)")
