"""Split the corpus into the training lane and the eval lane.

Implements corpus.md COR-LANES-1 through COR-LANES-4.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .conllu import Sentence, Token


class LaneLeakageError(RuntimeError):
    """COR-LANES-4: eval data must never enter training."""


@dataclass(frozen=True, slots=True)
class Record:
    """One training pair, with its provenance."""

    source: str  # "ewt" | "gum" | "pud" | "prose" | "teacher"
    split: str  # "train" | "dev" | "test"
    tag: str  # the UD release tag, a Gutenberg ebook ID, or the teacher checkpoint
    sentence: Sentence


@dataclass(frozen=True, slots=True)
class Lanes:
    training: tuple[Record, ...]
    eval: tuple[Record, ...]


def build_lanes(
    ewt: dict[str, list[Sentence]],
    gum: dict[str, list[Sentence]],
    pud_test: list[Sentence],
    prose: list[Record],
    tag: str,
) -> Lanes:
    """Build the two lanes.

    COR-LANES-1: EWT and GUM train/dev go to the training lane.
    COR-LANES-2: `prose` (the CPT rehearsal records) joins the training lane.
    COR-LANES-3: EWT/GUM test and PUD go to the eval lane.
    """
    training: list[Record] = []
    holdout: list[Record] = []

    for source, splits in (("ewt", ewt), ("gum", gum)):
        for split, sentences in splits.items():
            records = [Record(source, split, tag, sentence) for sentence in sentences]
            target = training if split in ("train", "dev") else holdout
            target.extend(records)

    holdout.extend(Record("pud", "test", tag, sentence) for sentence in pud_test)
    training.extend(prose)

    lanes = Lanes(tuple(training), tuple(holdout))
    assert_no_leakage(lanes)
    return lanes


def read_records(path: Path) -> list[Record]:
    """Read lane records from the JSONL shape that the pipeline writes."""
    records: list[Record] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            data = json.loads(line)
            tokens = tuple(Token(**token) for token in data["tokens"])
            sentence = Sentence(data["sent_id"], data["text"], tokens, data.get("doc_id"))
            records.append(Record(data["source"], data["split"], data["tag"], sentence))
    return records


def assert_no_leakage(lanes: Lanes) -> None:
    """Raise `LaneLeakageError` if any eval record also appears in training."""
    eval_keys = {
        (record.source, record.sentence.sent_id)
        for record in lanes.eval
        if record.sentence.sent_id is not None
    }
    for record in lanes.training:
        if record.sentence.sent_id is None:
            continue
        key = (record.source, record.sentence.sent_id)
        if key in eval_keys:
            raise LaneLeakageError(f"{key!r} appears in both the training and the eval lane")
