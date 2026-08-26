"""The tier T0 CI job.

Implements evaluation.md EVL-TIERS-2. CI must run the score script on the
CPU, on every commit.

No trained model exists before phase P3 (EVL-TIERS-5). This job builds the
corpus lanes, then scores the dev split against itself. This is a
self-consistency check. It proves the pipeline and the score script
integrate.

EVL-TIERS-6 needs a comparison against the UD tools `eval.py`. That test
lives in `tests/test_score.py`, against a fixture pair. It needs no network.
"""

from __future__ import annotations

from .conllu import Sentence
from .pipeline import build
from .score import Scores, score_sentences


def dev_split_sentences() -> list[Sentence]:
    """Return the dev-split sentences of the built training lane."""
    lanes = build()
    return [record.sentence for record in lanes.training if record.split == "dev"]


def self_check() -> Scores:
    sentences = dev_split_sentences()
    return score_sentences(sentences, sentences)


def main() -> int:
    result = self_check()
    print(
        f"tier T0 self-check: tokens={result.tokens} "
        f"upos={result.upos_accuracy:.4f} "
        f"lemma={result.lemma_accuracy:.4f} "
        f"las={result.las:.4f}"
    )
    if (result.upos_accuracy, result.lemma_accuracy, result.las) != (1.0, 1.0, 1.0):
        print("tier T0 self-check failed: a file must score 1.0 against itself")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
