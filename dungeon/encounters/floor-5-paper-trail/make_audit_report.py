"""Write audit-report.pdf, the Quarterly Close Accountant's audit, with nothing but the standard library.

The PDF ships with the repository, so you never need to run this. It is here so the file is
reproducible and you can see there is nothing in it but text:
    python make_audit_report.py
"""

from pathlib import Path

PAGES = [
    [
        "QUARTERLY CLOSE AUDIT REPORT",
        "Dungeon Crawl: Seattle, Floor 5, the Estuary",
        "Prepared by: the Quarterly Close Accountant, Office of the Controller",
        "Scope: round one of the dance-off at the Pier 59 collapse, and the party's Groove ledger",
        "",
        "Finding 1: Groove booked as revenue.",
        "The party recorded the Groove it kept after round one as income. Groove is a derived",
        "stat, not money. It cannot be banked, sold or carried into the next quarter, and it",
        "comes back in full when a Crawler rests in a Safe Room (Crawl Handbook, Groove, Mana,",
        "Benched and Cancelled). Recommended remediation: stop asking the auditor to invoice it.",
        "",
        "Finding 2: Unreported Ink Cloud.",
        "During round one, the party leader, Barnaby, released an Ink Cloud that left the",
        "pickleweed slick for two rounds. No receipt was filed. The auditor danced Off-Beat for",
        "both rounds and wishes this noted in the record.",
        "",
        "Finding 3: Tide schedule not disclosed.",
        "The Estuary dance floor floods twice a day. Neither party disclosed the tide table",
        "before the dance-off began. The auditor recommends that every future dance-off on this",
        "floor start with a look at the tide.",
    ],
    [
        "Finding 4: Auditor self-assessment.",
        "In the interest of full disclosure: the auditor's dance record before this quarter is",
        "one dance-off, at the 2019 holiday party, result not recorded. Footwork modifier +0.",
        "Recommended remediation: practice, after the close.",
        "",
        "Finding 5: Known control weakness.",
        "The auditor loses the tempo when anyone asks about their weekend. The auditor has",
        "documented this weakness and has not yet remediated it. The weekend was very nice.",
        "",
        "Management response",
        "The party leader disputes Finding 2 and requests a recount with fewer arms involved.",
        "Sergeant Cordula Vance accepts Findings 1 and 3, and has added the tide table to her",
        "pre-dance checklist.",
        "",
        "Opinion",
        "The party's records present fairly, in all material respects, a group that dances",
        "better than it keeps books. Audit status: closed, pending the next quarter.",
        "",
        "Signed, the Quarterly Close Accountant",
    ],
]


def escape(line: str) -> str:
    return line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def content_stream(lines: list[str]) -> bytes:
    body = ["BT", "/F1 11 Tf", "15 TL", "72 740 Td"]
    for line in lines:
        body.append(f"({escape(line)}) Tj T*")
    body.append("ET")
    return "\n".join(body).encode("ascii")


def build() -> bytes:
    """One catalog, one page tree, one font, and a page plus a content stream per page."""
    page_ids = [4 + 2 * i for i in range(len(PAGES))]
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{' '.join(f'{p} 0 R' for p in page_ids)}] /Count {len(PAGES)} >>".encode(),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    }
    for page_id, lines in zip(page_ids, PAGES):
        stream = content_stream(lines)
        objects[page_id] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {page_id + 1} 0 R >>").encode()
        objects[page_id + 1] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
    out = bytearray(b"%PDF-1.4\n")
    offsets = {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out += b"%d 0 obj\n" % number + objects[number] + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for number in sorted(objects):
        out += b"%010d 00000 n \n" % offsets[number]
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return bytes(out)


if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "audit-report.pdf"
    target.write_bytes(build())
    print(f"wrote {target.name} ({target.stat().st_size} bytes, {len(PAGES)} pages)")
