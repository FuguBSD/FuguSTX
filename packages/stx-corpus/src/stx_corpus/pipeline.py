"""Build the corpus lanes and write them to a local directory.

Implements corpus.md COR-LANES, COR-SOURCES, and COR-CONLLU end to end.

Phase P1 has no Scaleway bucket. COR-BUCKETS waits on phase P2's persistent
stack. This module writes to a local directory as a placeholder for the
future bucket path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import fetch, gum_license, gutenberg
from .conllu import Sentence, parse_sentences
from .lanes import Lanes, Record, build_lanes

#: The default output directory: a local placeholder, not a bucket path.
DEFAULT_OUTPUT = Path("explore/corpus")


def _prose_records(ebook_id: int) -> list[Record]:
    raw = fetch.fetch_gutenberg_book(ebook_id)
    body = gutenberg.strip_boilerplate(raw)
    paragraphs = [paragraph.strip() for paragraph in body.split("\n\n") if paragraph.strip()]
    return [
        Record(
            source="prose",
            split="train",
            tag=str(ebook_id),
            sentence=Sentence(sent_id=f"gutenberg-{ebook_id}-{i}", text=paragraph, tokens=()),
        )
        for i, paragraph in enumerate(paragraphs)
    ]


def build() -> Lanes:
    """Fetch every source, filter it, parse it, and split it into lanes."""
    ewt_raw = fetch.fetch_treebank("ewt")
    gum_raw = fetch.fetch_treebank("gum")
    pud_raw = fetch.fetch_treebank("pud")
    excluded_genres = gum_license.non_commercial_genres(fetch.fetch_gum_license())

    ewt = {split: parse_sentences(text) for split, text in ewt_raw.items()}

    gum: dict[str, list[Sentence]] = {}
    for split, text in gum_raw.items():
        gum[split] = [
            # COR-SOURCES-6: a sentence with no doc_id carries no provable
            # license, so it is excluded, not defaulted to included.
            sentence
            for sentence in parse_sentences(text)
            if sentence.doc_id is not None
            and not gum_license.is_excluded(sentence.doc_id, excluded_genres)
        ]

    pud_test = parse_sentences(pud_raw["test"])

    prose: list[Record] = []
    for ebook_id in fetch.GUTENBERG_BOOKS:
        prose.extend(_prose_records(ebook_id))

    return build_lanes(ewt, gum, pud_test, prose, fetch.UD_RELEASE_TAG)


def _record_to_dict(record: Record) -> dict[str, Any]:
    sentence = record.sentence
    return {
        "source": record.source,
        "split": record.split,
        "tag": record.tag,
        "doc_id": sentence.doc_id,
        "sent_id": sentence.sent_id,
        "text": sentence.text,
        "tokens": [
            {
                "id": token.id,
                "form": token.form,
                "lemma": token.lemma,
                "upos": token.upos,
                "xpos": token.xpos,
                "feats": token.feats,
                "head": token.head,
                "deprel": token.deprel,
                "misc": token.misc,
            }
            for token in sentence.tokens
        ],
    }


def write_lanes(lanes: Lanes, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for lane_name, records in (("training", lanes.training), ("eval", lanes.eval)):
        path = output_dir / f"{lane_name}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(_record_to_dict(record)) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the FuguSTX corpus lanes.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    lanes = build()
    write_lanes(lanes, args.output)
    print(
        f"training: {len(lanes.training)} records, eval: {len(lanes.eval)} records -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
