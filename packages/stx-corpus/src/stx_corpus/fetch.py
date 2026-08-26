"""Fetch the pinned corpus sources over HTTP.

Implements corpus.md COR-SOURCES-1, COR-SOURCES-2, and COR-SOURCES-4.
"""

from __future__ import annotations

import urllib.request

#: The pinned Universal Dependencies release tag. COR-SOURCES-1.
UD_RELEASE_TAG = "r2.18"

_UD_BASE = "https://raw.githubusercontent.com/UniversalDependencies"

#: name -> (repository, file prefix, the splits it ships). corpus.md's source
#: table: PUD holds one test split only.
TREEBANKS: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "ewt": ("UD_English-EWT", "en_ewt", ("train", "dev", "test")),
    "gum": ("UD_English-GUM", "en_gum", ("train", "dev", "test")),
    "pud": ("UD_English-PUD", "en_pud", ("test",)),
}

GUM_LICENSE_URL = f"{_UD_BASE}/UD_English-GUM/{UD_RELEASE_TAG}/LICENSE.txt"

#: ebook ID -> title, per COR-SOURCES-4.
GUTENBERG_BOOKS: dict[int, str] = {
    37134: "The Elements of Style",
    6409: "How to Speak and Write Correctly",
    45814: "An Advanced English Grammar",
}


def treebank_url(repo: str, prefix: str, split: str) -> str:
    return f"{_UD_BASE}/{repo}/{UD_RELEASE_TAG}/{prefix}-ud-{split}.conllu"


def gutenberg_url(ebook_id: int) -> str:
    return f"https://www.gutenberg.org/cache/epub/{ebook_id}/pg{ebook_id}.txt"


def fetch_text(url: str, timeout: float = 30.0) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8")


def fetch_treebank(name: str) -> dict[str, str]:
    """Fetch every split of a named treebank, keyed by split name."""
    repo, prefix, splits = TREEBANKS[name]
    return {split: fetch_text(treebank_url(repo, prefix, split)) for split in splits}


def fetch_gum_license() -> str:
    return fetch_text(GUM_LICENSE_URL)


def fetch_gutenberg_book(ebook_id: int) -> str:
    return fetch_text(gutenberg_url(ebook_id))
