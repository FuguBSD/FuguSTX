"""Render the annotation serialization of `share/annotation.gbnf`.

The grammar file is the one source of the serialization (ENG-SCHEMA-1,
ENG-SCHEMA-2). This module renders the input token list and the output
records in that serialization, for the pairs builder and the tier T1
sweep. The comment block of the grammar file states the format.
"""

from __future__ import annotations

from pathlib import Path

from .conllu import Token
from .gbnf import Grammar

#: The one committed schema file, relative to the repository root.
GRAMMAR_PATH = Path(__file__).resolve().parents[4] / "share" / "annotation.gbnf"


class SchemaError(ValueError):
    """A gold token can not serialize as a legal record."""


def load_grammar() -> Grammar:
    return Grammar.from_path(GRAMMAR_PATH)


def render_tokens(forms: list[str]) -> str:
    """The input serialization: index, tab, form, and one closing empty line."""
    if not forms:
        raise SchemaError("a token list can not be empty")
    lines = "".join(f"{index}\t{form}\n" for index, form in enumerate(forms, start=1))
    return lines + "\n"


def render_record(token: Token) -> str:
    """One output record line for one gold token."""
    if token.upos is None or token.head is None or token.deprel is None:
        raise SchemaError(f"token {token.id} ({token.form!r}) misses UPOS, head, or deprel")
    lemma = token.lemma if token.lemma is not None else "_"
    feats = token.feats if token.feats is not None else "_"
    return f"{token.upos}\t{lemma}\t{token.head}\t{token.deprel}\t{feats}\n"


def render_labels(tokens: tuple[Token, ...]) -> str:
    """The output serialization: one record line for each token."""
    if not tokens:
        raise SchemaError("a sentence without tokens can not serialize")
    return "".join(render_record(token) for token in tokens)
