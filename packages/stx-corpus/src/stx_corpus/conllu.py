"""Read a CoNLL-U treebank file into sentences.

Implements corpus.md COR-CONLLU-1 through COR-CONLLU-5.
"""

from __future__ import annotations

from dataclasses import dataclass

#: MISC keys that carry the GUM discourse and entity payload. COR-CONLLU-4
#: strips these; every other MISC key, for example SpaceAfter, stays.
_STRIPPED_MISC_PREFIXES = ("Discourse=", "Entity=", "Bridge=", "SplitAnte=")


@dataclass(frozen=True, slots=True)
class Token:
    """One annotated token.

    COR-CONLLU-5: `form` keeps a literal underscore. It is never `None`.
    Every other field is `None` when its CoNLL-U column holds `_`.
    """

    id: int
    form: str
    lemma: str | None
    upos: str | None
    xpos: str | None
    feats: str | None
    head: int | None
    deprel: str | None
    misc: str | None


@dataclass(frozen=True, slots=True)
class Sentence:
    """One sentence. `text` is the raw `# text` comment, per COR-CONLLU-1."""

    sent_id: str | None
    text: str
    tokens: tuple[Token, ...]
    doc_id: str | None = None


def _field(value: str) -> str | None:
    return None if value == "_" else value


def _clean_misc(raw: str) -> str | None:
    if raw == "_":
        return None
    kept = [part for part in raw.split("|") if not part.startswith(_STRIPPED_MISC_PREFIXES)]
    return "|".join(kept) if kept else None


def parse_sentences(text: str) -> list[Sentence]:
    """Parse a CoNLL-U document into sentences.

    A range ID line (`2-3`) and a decimal ID line (`5.1`) are excluded from
    the token list, per COR-CONLLU-2 and COR-CONLLU-3. A `# meta::` comment
    and a `global.Entity` comment are dropped, per COR-CONLLU-4.
    """
    sentences: list[Sentence] = []
    sent_id: str | None = None
    sent_text: str | None = None
    doc_id: str | None = None
    tokens: list[Token] = []

    def flush() -> None:
        nonlocal sent_id, sent_text, tokens
        if sent_text is not None or tokens:
            sentences.append(Sentence(sent_id, sent_text or "", tuple(tokens), doc_id))
        sent_id, sent_text, tokens = None, None, []

    for line in text.splitlines():
        if not line:
            flush()
            continue

        if line.startswith("#"):
            comment = line[1:].strip()
            if comment.startswith(("meta::", "global.Entity")):
                continue
            key, _, value = comment.partition("=")
            key = key.strip()
            if key == "sent_id":
                sent_id = value.strip()
            elif key == "text":
                sent_text = value.strip()
            elif key == "newdoc id":
                doc_id = value.strip()
            continue

        columns = line.split("\t")
        if len(columns) < 10:
            continue
        raw_id = columns[0]
        if "-" in raw_id or "." in raw_id:
            continue  # COR-CONLLU-2, COR-CONLLU-3: multiword range, empty node

        raw_head = columns[6]
        tokens.append(
            Token(
                id=int(raw_id),
                form=columns[1],
                lemma=_field(columns[2]),
                upos=_field(columns[3]),
                xpos=_field(columns[4]),
                feats=_field(columns[5]),
                head=None if raw_head == "_" else int(raw_head),
                deprel=_field(columns[7]),
                # columns[8] is DEPS: stripped per COR-CONLLU-3
                misc=_clean_misc(columns[9]),
            )
        )

    flush()
    return sentences
