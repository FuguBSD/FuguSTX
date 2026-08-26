"""Strip the Project Gutenberg header and footer.

Implements corpus.md COR-SOURCES-5.
"""

from __future__ import annotations

import re

_START = "*** START OF THE PROJECT GUTENBERG EBOOK"
_END = "*** END OF THE PROJECT GUTENBERG EBOOK"

#: An HTML tag, a scan artifact some Gutenberg transcriptions leave right
#: after the start marker or right before the end marker, for example a
#: stray `</pre>` or `<pre id="pg-footer">`.
_HTML_TAG = re.compile(r"</?[A-Za-z]+(?:\s+[A-Za-z-]+=\"[^\"]*\")*\s*/?>")


def _drop_credits_paragraph(lines: list[str]) -> list[str]:
    """Drop a leading "Produced by ..." transcriber-credits paragraph.

    Some Gutenberg transcriptions repeat this paragraph right after the start
    marker, in addition to the one the pre-marker header already carries.
    """
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not lines[i].strip().startswith("Produced by"):
        return lines
    while i < len(lines) and lines[i].strip():
        i += 1
    return lines[i:]


def strip_boilerplate(text: str) -> str:
    """Return the book body, with the Project Gutenberg header and footer cut."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(_START)), None)
    end = next((i for i, line in enumerate(lines) if line.startswith(_END)), None)
    if start is None or end is None or end <= start:
        raise ValueError("no Project Gutenberg start/end marker found")

    body = [line for line in lines[start + 1 : end] if not _HTML_TAG.fullmatch(line.strip())]
    body = _drop_credits_paragraph(body)
    return "\n".join(body).strip("\n")
