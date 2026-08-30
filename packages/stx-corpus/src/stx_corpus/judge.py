"""The judge filter of the teacher campaign.

The teacher proposes, and this verifier disposes (decision T5). The
filter accepts a record only when the three checks of training.md
TRN-TEACH pass (TRN-TEACH-4), and it logs each rejected record with
its reason (TRN-TEACH-5). An accepted record takes the lane JSONL
shape, with a provenance tag (COR-AUG-2). A record enters the training
lane only through this filter (COR-AUG-1, LIC-RELEASE-3).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import schema, wordtable
from .gbnf import Grammar

#: The reject reasons, one per failed check of training.md TRN-TEACH.
#: `disagree` is check 1, `tree` is check 2, and `tag`, `count`, and
#: `word` are check 3: the grammar inventory, the record count, and
#: the word table.
REASONS = ("disagree", "tag", "count", "tree", "word")


@dataclass(frozen=True, slots=True)
class ParsedRecord:
    """One annotation record of a teacher pass."""

    upos: str
    lemma: str
    head: int
    deprel: str
    feats: str


def normalized(text: str) -> str:
    """One canonical completion shape for the checks.

    The grammar wants exactly one final newline, and the few-shot
    examples end with a blank separator line, so a compliant teacher
    reply can carry either. The trim must not mask a real defect: the
    record content stays untouched.
    """
    return text.strip() + "\n"


def parse_records(text: str) -> list[ParsedRecord]:
    """Parse one grammar-matched teacher pass into records."""
    records = []
    for line in text.splitlines():
        upos, lemma, head, deprel, feats = line.split("\t")
        records.append(ParsedRecord(upos, lemma, int(head), deprel, feats))
    return records


def check_tree(records: list[ParsedRecord]) -> bool:
    """Check 2: one root, fully connected, every head in range."""
    total = len(records)
    roots = [index for index, record in enumerate(records, start=1) if record.head == 0]
    if len(roots) != 1:
        return False
    if any(not 0 <= record.head <= total for record in records):
        return False
    reached = {roots[0]}
    frontier = {roots[0]}
    while frontier:
        frontier = {
            index
            for index, record in enumerate(records, start=1)
            if record.head in frontier and index not in reached
        }
        reached |= frontier
    return len(reached) == total


def check_words(
    forms: list[str], records: list[ParsedRecord], table: dict[str, frozenset[str]]
) -> bool:
    """The word-table check of check 3: a known word must carry an
    allowed UPOS, and an unknown word passes."""
    for form, record in zip(forms, records, strict=True):
        allowed = table.get(form)
        if allowed is not None and record.upos not in allowed:
            return False
    return True


def judge(
    proposal: dict[str, Any], grammar: Grammar, table: dict[str, frozenset[str]]
) -> str | None:
    """The reject reason of one proposal, or None for an accept."""
    first, second = (normalized(text) for text in proposal["passes"])
    if first != second:
        return "disagree"
    if not grammar.matches(first):
        return "tag"
    records = parse_records(first)
    if len(records) != len(proposal["forms"]):
        return "count"
    if not check_tree(records):
        return "tree"
    if not check_words(proposal["forms"], records, table):
        return "word"
    return None


def _space_after(text: str, forms: list[str]) -> list[str | None]:
    """The SpaceAfter=No marks of the lane shape.

    The record text stays reconstructible from the forms, per the
    spacing convention of COR-CONLLU-1.
    """
    flags: list[str | None] = []
    position = 0
    for form in forms:
        found = text.find(form, position)
        if found < 0:
            flags.append(None)
            continue
        end = found + len(form)
        glued = end < len(text) and not text[end].isspace()
        flags.append("SpaceAfter=No" if glued else None)
        position = end
    return flags


def accepted_record(proposal: dict[str, Any], tag: str) -> dict[str, Any]:
    """One accepted record, in the lane JSONL shape.

    The provenance tag names the teacher checkpoint (COR-AUG-2), and
    the reader of TRN-SFT-1 takes the record as it stands.
    """
    records = parse_records(normalized(proposal["passes"][0]))
    misc = _space_after(proposal["text"], proposal["forms"])
    return {
        "source": "teacher",
        "split": "train",
        "tag": tag,
        "doc_id": None,
        "sent_id": proposal["sent_id"],
        "text": proposal["text"],
        "tokens": [
            {
                "id": index,
                "form": form,
                "lemma": None if record.lemma == "_" else record.lemma,
                "upos": record.upos,
                "xpos": None,
                "feats": None if record.feats == "_" else record.feats,
                "head": record.head,
                "deprel": record.deprel,
                "misc": misc[index - 1],
            }
            for index, (form, record) in enumerate(
                zip(proposal["forms"], records, strict=True), start=1
            )
        ],
    }


def filter_proposals(
    proposals: list[dict[str, Any]],
    table: dict[str, frozenset[str]],
    tag: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Split the proposals into accepts and rejects, with a report."""
    grammar = schema.load_grammar()
    accepted: list[dict[str, Any]] = []
    rejects: list[dict[str, Any]] = []
    rejected_counts = dict.fromkeys(REASONS, 0)
    for proposal in proposals:
        reason = judge(proposal, grammar, table)
        if reason is None:
            accepted.append(accepted_record(proposal, tag))
        else:
            rejected_counts[reason] += 1
            rejects.append(
                {
                    "sent_id": proposal["sent_id"],
                    "reason": reason,
                    "text": proposal["text"],
                    "passes": proposal["passes"],
                }
            )
    report = {
        "model": tag,
        "proposed": len(proposals),
        "accepted": len(accepted),
        "rejected": rejected_counts,
        "acceptance_rate": round(len(accepted) / len(proposals), 4) if proposals else None,
    }
    return accepted, rejects, report


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The FuguSTX judge filter.")
    parser.add_argument("--proposals", type=Path, required=True)
    parser.add_argument("--model", required=True, help="the provenance tag")
    parser.add_argument("--table", type=Path, default=wordtable.TABLE_PATH)
    parser.add_argument("--accepted", type=Path, required=True)
    parser.add_argument("--rejects", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)

    with args.proposals.open(encoding="utf-8") as handle:
        proposals = [json.loads(line) for line in handle]
    accepted, rejects, report = filter_proposals(
        proposals, wordtable.read_table(args.table), args.model
    )
    _write_jsonl(accepted, args.accepted)
    _write_jsonl(rejects, args.rejects)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"judge: {report['accepted']} of {report['proposed']} accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
