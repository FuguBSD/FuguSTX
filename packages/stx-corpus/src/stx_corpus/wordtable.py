"""Build the interim word table of the judge filter.

Check 3 of the judge filter (training.md TRN-TEACH) runs on this
table: each word of the train splits, with its observed UPOS set. The
dev split is a score input, and it must not shape the table
(TRN-SFT-3). The table is not the approved dictionary of ENG-LEXICON.

The committed table lives next to this module, and `main` rebuilds it
from the pinned sources. `licensing.md` names the table license and
its treebank attribution.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .lanes import Record

#: The committed table, relative to this module.
TABLE_PATH = Path(__file__).resolve().parent / "data" / "word-table.tsv"

#: The sources that shape the table: the treebanks of the training
#: lane. The prose lane holds no labels.
_TREEBANK_SOURCES = ("ewt", "gum")


def build_table(records: Iterable[Record]) -> dict[str, frozenset[str]]:
    """Each train-split word, with its observed UPOS set.

    Only a treebank record of the train split shapes the table: the
    dev split is a score input, and the eval lane never reaches this
    builder (COR-LANES-4).
    """
    table: dict[str, set[str]] = {}
    for record in records:
        if record.source not in _TREEBANK_SOURCES or record.split != "train":
            continue
        for token in record.sentence.tokens:
            if token.upos is not None:
                table.setdefault(token.form, set()).add(token.upos)
    return {form: frozenset(tags) for form, tags in table.items()}


def write_table(table: dict[str, frozenset[str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for form in sorted(table):
            handle.write(f"{form}\t{','.join(sorted(table[form]))}\n")


def read_table(path: Path = TABLE_PATH) -> dict[str, frozenset[str]]:
    table: dict[str, frozenset[str]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            form, _, tags = line.rstrip("\n").partition("\t")
            table[form] = frozenset(tags.split(","))
    return table


def main(argv: list[str] | None = None) -> int:
    import argparse

    from .pipeline import build

    parser = argparse.ArgumentParser(description="Rebuild the FuguSTX word table.")
    parser.add_argument("--output", type=Path, default=TABLE_PATH)
    args = parser.parse_args(argv)

    table = build_table(build().training)
    write_table(table, args.output)
    print(f"word table: {len(table)} words -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
