"""Run the model over one split through the stx harness, and score it.

The tier T1 promotion sweep runs on the eval lane, on the CPU, and each
promotion writes a scorecard to the artifacts bucket (EVL-TIERS-1,
EVL-TIERS-3). The first baseline run fixes each tier T1 threshold
(EVL-TIERS-5). The same runner scores the dev split for the TRN-CPT-2
comparison: the dev split is a score input, never a training input
(TRN-SFT-3).

The stx harness drives every llama.cpp call: this module feeds token
lists to `bin/stx label` and reads label records back (ENG-SPLIT-4).

The scorecard holds UPOS, lemma, and LAS per treebank, plus the
llama.cpp version, the thread count, the model hash, the UD release
tag, and the run identifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import threading
from pathlib import Path
from typing import Any

from . import bucket
from .fetch import UD_RELEASE_TAG
from .lanes import Lanes, Record
from .pipeline import build

ARTIFACTS_BUCKET = "stx-artifacts"

#: The count fields of one treebank entry. The score rates derive from
#: them at aggregation time, so shards stay mergeable.
_COUNTS = ("sentences", "failures", "tokens", "upos", "lemma", "las")


def split_records(lanes: Lanes, split: str) -> list[Record]:
    if split == "dev":
        return [record for record in lanes.training if record.split == "dev"]
    if split == "eval":
        return list(lanes.eval)
    raise ValueError(f"unknown split: {split}")


def shard_records(records: list[Record], shard: str | None) -> list[Record]:
    if shard is None:
        return records
    index, total = (int(part) for part in shard.split("/", 1))
    if not 0 <= index < total:
        raise ValueError(f"a shard must be k/N with 0 <= k < N: {shard}")
    return [record for position, record in enumerate(records) if position % total == index]


def label_records(records: list[Record], stx_command: str) -> list[dict[str, Any]]:
    """Feed every token list through one stx process."""
    process = subprocess.Popen(
        shlex.split(stx_command),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    def feed() -> None:
        assert process.stdin is not None
        for record in records:
            forms = [token.form for token in record.sentence.tokens]
            process.stdin.write(json.dumps({"tokens": forms}) + "\n")
        process.stdin.close()

    writer = threading.Thread(target=feed)
    writer.start()
    assert process.stdout is not None
    replies = [json.loads(line) for line in process.stdout]
    writer.join()
    process.wait()
    if process.returncode:
        raise RuntimeError(f"the stx harness failed with status {process.returncode}")
    if len(replies) != len(records):
        raise RuntimeError(f"{len(replies)} replies for {len(records)} sentences")
    return replies


def score_replies(
    records: list[Record], replies: list[dict[str, Any]]
) -> dict[str, dict[str, int]]:
    """Count the UPOS, lemma, and LAS matches per treebank.

    A failed sentence counts its tokens as wrong: a model that answers
    nothing scores nothing.
    """
    counts: dict[str, dict[str, int]] = {}
    for record, reply in zip(records, replies, strict=True):
        bank = counts.setdefault(record.source, dict.fromkeys(_COUNTS, 0))
        tokens = record.sentence.tokens
        bank["sentences"] += 1
        bank["tokens"] += len(tokens)
        labels = reply.get("labels")
        if not labels or len(labels) != len(tokens):
            bank["failures"] += 1
            continue
        for token, label in zip(tokens, labels, strict=True):
            if token.upos == label["upos"]:
                bank["upos"] += 1
            if (token.lemma or "_") == label["lemma"]:
                bank["lemma"] += 1
            if token.head == label["head"] and (token.deprel or "_") == label["deprel"]:
                bank["las"] += 1
    return counts


def scores(counts: dict[str, dict[str, int]]) -> dict[str, dict[str, float]]:
    """The UPOS, lemma, and LAS rates per treebank."""
    return {
        source: {
            "upos": round(bank["upos"] / bank["tokens"], 4),
            "lemma": round(bank["lemma"] / bank["tokens"], 4),
            "las": round(bank["las"] / bank["tokens"], 4),
        }
        for source, bank in counts.items()
        if bank["tokens"]
    }


def merge_counts(parts: list[dict[str, dict[str, int]]]) -> dict[str, dict[str, int]]:
    merged: dict[str, dict[str, int]] = {}
    for part in parts:
        for source, bank in part.items():
            into = merged.setdefault(source, dict.fromkeys(_COUNTS, 0))
            for count in _COUNTS:
                into[count] += bank[count]
    return merged


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def scorecard(counts: dict[str, dict[str, int]], meta: dict[str, Any]) -> dict[str, Any]:
    return {**meta, "counts": counts, "scores": scores(counts)}


def aggregate(paths: list[Path]) -> dict[str, Any]:
    """Merge shard scorecards into one. Each pin must agree."""
    shards = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    meta = {key: shards[0][key] for key in shards[0] if key not in ("counts", "scores", "shard")}
    for shard in shards[1:]:
        for key, value in meta.items():
            if shard.get(key) != value:
                raise ValueError(f"the shards disagree on {key}")
    return scorecard(merge_counts([shard["counts"] for shard in shards]), meta)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The FuguSTX model sweep.")
    parser.add_argument("--split", choices=("dev", "eval"), default="eval")
    parser.add_argument("--stx", default="bin/stx label")
    parser.add_argument("--model", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--llama-version", required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--shard", default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--aggregate", nargs="+", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.aggregate:
        card = aggregate(args.aggregate)
    else:
        if args.model is None:
            parser.error("--model is required outside --aggregate")
        records = shard_records(split_records(build(), args.split), args.shard)
        replies = label_records(records, args.stx)
        card = scorecard(
            score_replies(records, replies),
            {
                "split": args.split,
                "run_id": args.run_id,
                "model_hash": sha256_file(args.model),
                "llama_version": args.llama_version,
                "threads": args.threads,
                "ud_release": UD_RELEASE_TAG,
                "shard": args.shard,
            },
        )

    text = json.dumps(card, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    if args.upload:
        shard = f"-shard{args.shard.replace('/', 'of')}" if args.shard else ""
        key = (
            f"runs/{card['run_id']}/scorecard-t1.json"
            if args.aggregate
            else f"runs/{card['run_id']}/scorecard-{args.split}{shard}.json"
        )
        bucket.put_text(ARTIFACTS_BUCKET, key, text)
        print(f"upload: s3://{ARTIFACTS_BUCKET}/{key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
