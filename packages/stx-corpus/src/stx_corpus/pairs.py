"""Build the SFT pairs from the training lane.

Implements training.md TRN-SFT-1 through TRN-SFT-3. A pair holds the
input token list and the grammar-constrained labels, in the
serialization of `share/annotation.gbnf` (TRN-SFT-2). The treebank
pairs come from the train splits only: the dev split is a score input,
and it must not enter a pair (TRN-SFT-3). Eval data must not enter
training (COR-LANES-4).

The builder also reads the augmentation input of TRN-SFT-1. The input
stays empty until the teacher campaign: a record enters it only through
the judge filter (COR-AUG-1).
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from . import schema
from .conllu import Sentence, Token
from .lanes import Lanes, Record
from .pipeline import build

#: The sources that carry treebank annotations. The prose lane carries
#: raw text for the CPT rehearsal, and it holds no labels.
_TREEBANK_SOURCES = ("ewt", "gum")

#: The end-of-sequence string of the base model tokenizer. The training
#: label segment ends with it, so greedy decoding stops after the last
#: record.
EOS = "<|endoftext|>"


@dataclass(frozen=True, slots=True)
class Pair:
    """One training pair, with its provenance."""

    source: str
    split: str
    sent_id: str | None
    prompt: str
    completion: str


def _pair(record: Record) -> Pair:
    sentence = record.sentence
    return Pair(
        source=record.source,
        split=record.split,
        sent_id=sentence.sent_id,
        prompt=schema.render_tokens([token.form for token in sentence.tokens]),
        completion=schema.render_labels(sentence.tokens),
    )


def build_pairs(lanes: Lanes, augmentation: Iterable[Record] = ()) -> list[Pair]:
    """The pairs of one SFT pass.

    The treebank pairs come from the train splits of the training lane
    (TRN-SFT-3). Each accepted augmentation record joins them
    (TRN-SFT-1). The eval lane never enters this function: it reads
    `lanes.training` only (COR-LANES-4).
    """
    pairs = [
        _pair(record)
        for record in lanes.training
        if record.source in _TREEBANK_SOURCES and record.split == "train"
    ]
    pairs.extend(_pair(record) for record in augmentation)
    return pairs


def write_pairs(pairs: list[Pair], path: Path) -> None:
    """Write the pairs in the Axolotl `input_output` segment format."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for pair in pairs:
            record = {
                "segments": [
                    {"label": False, "text": pair.prompt},
                    {"label": True, "text": pair.completion + EOS},
                ]
            }
            handle.write(json.dumps(record) + "\n")


def read_augmentation(path: Path) -> list[Record]:
    """Read accepted augmentation records, in the lane JSONL shape."""
    records: list[Record] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            data = json.loads(line)
            tokens = tuple(Token(**token) for token in data["tokens"])
            sentence = Sentence(data["sent_id"], data["text"], tokens, data.get("doc_id"))
            records.append(Record(data["source"], data["split"], data["tag"], sentence))
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the FuguSTX SFT pairs.")
    parser.add_argument("--output", type=Path, default=Path("explore/corpus/pairs.jsonl"))
    parser.add_argument("--augmentation", type=Path, default=None)
    args = parser.parse_args(argv)

    augmentation = read_augmentation(args.augmentation) if args.augmentation else []
    pairs = build_pairs(build(), augmentation)
    write_pairs(pairs, args.output)
    print(f"pairs: {len(pairs)} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
