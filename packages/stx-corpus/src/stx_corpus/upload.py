"""Write the lanes and the pairs, locally or to the corpus buckets.

Plan step 3 of phase P3: the training lane and the pairs go to
`stx-corpus`, and the eval lane goes to `stx-evalcorpus`. A manifest
in each bucket records the pinned UD release tag (COR-SOURCES-1). The
lane rule stays absolute: no eval file touches `stx-corpus`
(COR-LANES-4).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import bucket
from .fetch import GUTENBERG_BOOKS, UD_RELEASE_TAG
from .lanes import Lanes
from .pairs import build_pairs, write_pairs
from .pipeline import _record_to_dict, build

CORPUS_BUCKET = "stx-corpus"
EVAL_BUCKET = "stx-evalcorpus"


def write_corpus_files(lanes: Lanes, directory: Path) -> list[Path]:
    """The training-lane files: the lane record copy, the CPT prose,
    and the SFT pairs."""
    directory.mkdir(parents=True, exist_ok=True)

    training = directory / "training.jsonl"
    with training.open("w", encoding="utf-8") as handle:
        for record in lanes.training:
            handle.write(json.dumps(_record_to_dict(record)) + "\n")

    prose = directory / "prose.jsonl"
    with prose.open("w", encoding="utf-8") as handle:
        for record in lanes.training:
            if record.source == "prose":
                handle.write(json.dumps({"text": record.sentence.text}) + "\n")

    pairs_path = directory / "pairs.jsonl"
    pairs = build_pairs(lanes)
    write_pairs(pairs, pairs_path)

    manifest = directory / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "ud_release": UD_RELEASE_TAG,
                "gutenberg_books": sorted(GUTENBERG_BOOKS),
                "training_records": len(lanes.training),
                "pairs": len(pairs),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return [training, prose, pairs_path, manifest]


def write_eval_files(lanes: Lanes, directory: Path) -> list[Path]:
    """The eval-lane files, for `stx-evalcorpus` only."""
    directory.mkdir(parents=True, exist_ok=True)

    eval_path = directory / "eval.jsonl"
    with eval_path.open("w", encoding="utf-8") as handle:
        for record in lanes.eval:
            handle.write(json.dumps(_record_to_dict(record)) + "\n")

    manifest = directory / "manifest.json"
    manifest.write_text(
        json.dumps({"ud_release": UD_RELEASE_TAG, "eval_records": len(lanes.eval)}) + "\n",
        encoding="utf-8",
    )
    return [eval_path, manifest]


def upload(lanes: Lanes, directory: Path) -> None:
    for path in write_corpus_files(lanes, directory / "corpus"):
        bucket.put_file(CORPUS_BUCKET, path.name, path)
    for path in write_eval_files(lanes, directory / "eval"):
        bucket.put_file(EVAL_BUCKET, path.name, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upload the FuguSTX corpus lanes.")
    parser.add_argument("--directory", type=Path, default=Path("explore/upload"))
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="write the files under --directory, and upload nothing",
    )
    args = parser.parse_args(argv)

    lanes = build()
    if args.local_only:
        corpus = write_corpus_files(lanes, args.directory / "corpus")
        holdout = write_eval_files(lanes, args.directory / "eval")
        print(f"local: {len(corpus) + len(holdout)} files under {args.directory}")
        return 0
    upload(lanes, args.directory)
    print(f"upload: {CORPUS_BUCKET} and {EVAL_BUCKET} hold the {UD_RELEASE_TAG} lanes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
