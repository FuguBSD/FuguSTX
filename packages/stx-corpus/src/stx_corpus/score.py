"""Score a system CoNLL-U file against a gold CoNLL-U file.

Implements evaluation.md EVL-TIERS-2 and EVL-TIERS-6.

This scorer assumes the system file matches the gold file's tokenization.
Word alignment across a different segmentation is a UD tools `eval.py`
feature. Phase P1 does not need it. No trained model exists before phase P3
(EVL-TIERS-1, EVL-TIERS-3 wait on phase P2 and phase P3). Every call in this
phase compares a file against itself, or against a fixture pair with
matching tokenization.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .conllu import Sentence, parse_sentences


@dataclass(frozen=True, slots=True)
class Scores:
    upos_accuracy: float
    lemma_accuracy: float
    las: float
    tokens: int


def score_sentences(gold_sentences: list[Sentence], system_sentences: list[Sentence]) -> Scores:
    """Score `system_sentences` against `gold_sentences` on UPOS, lemma, and LAS."""
    if len(gold_sentences) != len(system_sentences):
        raise ValueError("the gold and the system hold a different sentence count")

    upos_correct = lemma_correct = las_correct = total = 0
    for gold_sentence, system_sentence in zip(gold_sentences, system_sentences, strict=True):
        if len(gold_sentence.tokens) != len(system_sentence.tokens):
            raise ValueError(f"sentence {gold_sentence.sent_id!r} holds a different token count")
        for gold_token, system_token in zip(
            gold_sentence.tokens, system_sentence.tokens, strict=True
        ):
            total += 1
            if gold_token.upos == system_token.upos:
                upos_correct += 1
            if gold_token.lemma == system_token.lemma:
                lemma_correct += 1
            if gold_token.head == system_token.head and gold_token.deprel == system_token.deprel:
                las_correct += 1

    if total == 0:
        raise ValueError("the gold file holds no token to score")

    return Scores(
        upos_accuracy=upos_correct / total,
        lemma_accuracy=lemma_correct / total,
        las=las_correct / total,
        tokens=total,
    )


def score(gold_text: str, system_text: str) -> Scores:
    """Score `system_text` against `gold_text` on UPOS, lemma, and LAS."""
    return score_sentences(parse_sentences(gold_text), parse_sentences(system_text))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score a system CoNLL-U file against gold.")
    parser.add_argument("gold", type=Path)
    parser.add_argument("system", type=Path)
    args = parser.parse_args(argv)

    result = score(
        args.gold.read_text(encoding="utf-8"),
        args.system.read_text(encoding="utf-8"),
    )
    print(
        f"tokens={result.tokens} "
        f"upos={result.upos_accuracy:.4f} "
        f"lemma={result.lemma_accuracy:.4f} "
        f"las={result.las:.4f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
