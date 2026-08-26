"""Filter GUM documents by license.

Implements corpus.md COR-SOURCES-3: the wikiHow and the fiction documents of
GUM carry CC BY-NC-SA 4.0, and licensing.md LIC-RELEASE-4 forbids a
non-commercial component. The GUM `LICENSE.txt` names the restricted genres in
prose; a GUM `newdoc id` encodes its genre as `GUM_<genre>_<slug>`, for
example `GUM_whow_paperclip`.
"""

from __future__ import annotations

import re

#: The prose genre name in LICENSE.txt, mapped to its newdoc-id genre code.
_NON_COMMERCIAL_GENRE_CODES = {
    "wikihow": "whow",
    "fiction": "fiction",
}

_NEWDOC_ID = re.compile(r"^GUM_([a-z]+)_")


def non_commercial_genres(license_text: str) -> frozenset[str]:
    """Return the newdoc-id genre codes that `license_text` marks CC BY-NC-SA."""
    lowered = license_text.lower()
    return frozenset(code for name, code in _NON_COMMERCIAL_GENRE_CODES.items() if name in lowered)


def document_genre(newdoc_id: str) -> str | None:
    """Return the genre code of a GUM `newdoc id`, or `None` if it has none."""
    match = _NEWDOC_ID.match(newdoc_id)
    return match.group(1) if match else None


def is_excluded(newdoc_id: str, excluded_genres: frozenset[str]) -> bool:
    """Report whether `newdoc_id` names a document COR-SOURCES-3 excludes."""
    return document_genre(newdoc_id) in excluded_genres
