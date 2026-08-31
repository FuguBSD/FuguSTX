"""Read the scorecards of the artifacts bucket, and print the scores.

Each promotion writes a scorecard to the artifacts bucket (EVL-TIERS-1),
and `t1.py` is the writer. This module is the reader (EVL-TIERS-7). It
lists the run prefix of the key layout, reads each scorecard, and
prints one row for each scorecard and treebank pair.

The reader takes the prefix and the name from the writer, so one
definition of the key layout serves both (EVL-TIERS-8).

The module holds no threshold, and it makes no decision. The evaluation
document holds the threshold policy.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import bucket
from .t1 import ARTIFACTS_BUCKET, CARD_NAME, RUNS_PREFIX

#: The column titles, in order. The last three hold a rate. The shard
#: column separates a part sweep from a full sweep of the same run.
_HEADER = ("run", "label", "split", "device", "shard", "treebank", "upos", "lemma", "las")

#: The count of rate columns. A rate column aligns to the right.
_RATES = 3


def card_keys(keys: list[str]) -> list[str]:
    """Every scorecard key of the key layout (EVL-TIERS-8). A run
    prefix also holds the GGUF file, the teach reports, and the reject
    logs of the run."""
    return [
        key
        for key in keys
        if key.rsplit("/", 1)[-1].startswith(f"{CARD_NAME}-") and key.endswith(".json")
    ]


def prefix(run: str | None = None) -> str:
    """The read prefix, from the key layout of the writer. A run
    identifier narrows the read to one run."""
    return f"{RUNS_PREFIX}{run}/" if run else RUNS_PREFIX


def read_cards(name: str = ARTIFACTS_BUCKET, run: str | None = None) -> list[dict[str, Any]]:
    """Every scorecard of one bucket, in key order. A run identifier
    narrows the read to one campaign run."""
    # One client reads every object: each client call resolves the
    # credential again.
    s3 = bucket.client()
    keys = card_keys(bucket.list_keys(name, prefix(run), s3))
    return [json.loads(bucket.get_text(name, key, s3)) for key in keys]


def rows(cards: list[dict[str, Any]]) -> list[tuple[str, ...]]:
    """One row for each scorecard and treebank pair. A treebank with
    zero tokens carries no rate, and it gives no row."""
    table = []
    for card in cards:
        for treebank, score in sorted(card.get("scores", {}).items()):
            table.append(
                (
                    card.get("run_id", "-"),
                    card.get("label") or "-",
                    card.get("split", "-"),
                    card.get("device", "-"),
                    card.get("shard") or "-",
                    treebank,
                    f"{score['upos']:.4f}",
                    f"{score['lemma']:.4f}",
                    f"{score['las']:.4f}",
                )
            )
    return table


def render(table: list[tuple[str, ...]]) -> str:
    """The table, with a header line. Two spaces separate two columns,
    and a rate column aligns to the right."""
    lines = [_HEADER, *table]
    widths = [max(len(line[index]) for line in lines) for index in range(len(_HEADER))]
    out = []
    for line in lines:
        cells = [
            cell.rjust(width) if index >= len(_HEADER) - _RATES else cell.ljust(width)
            for index, (cell, width) in enumerate(zip(line, widths, strict=True))
        ]
        out.append("  ".join(cells).rstrip())
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the FuguSTX scorecards.")
    parser.add_argument("--bucket", default=ARTIFACTS_BUCKET, help="the artifacts bucket")
    parser.add_argument("--run", default=None, help="one run identifier")
    parser.add_argument("--json", action="store_true", help="print the scorecards, not the table")
    args = parser.parse_args(argv)

    cards = read_cards(args.bucket, args.run)
    if not cards:
        # An empty table and a wrong name look the same. Name the
        # place that the read found nothing in.
        print(f"no scorecard under s3://{args.bucket}/{prefix(args.run)}", file=sys.stderr)
    if args.json:
        print(json.dumps(cards, indent=2, sort_keys=True))
        return 0
    print(render(rows(cards)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
