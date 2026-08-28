import json
import sys

import pytest
from corpus_fakes import EWT_DEV, EWT_TEST, EWT_TRAIN, GUM_TRAIN, PUD_TEST
from stx_corpus.conllu import parse_sentences
from stx_corpus.lanes import Record, build_lanes
from stx_corpus.t1 import (
    aggregate,
    label_records,
    merge_counts,
    score_replies,
    scorecard,
    scores,
    sha256_file,
    shard_records,
    split_records,
)


def _records():
    ewt = {
        "train": parse_sentences(EWT_TRAIN),
        "dev": parse_sentences(EWT_DEV),
        "test": parse_sentences(EWT_TEST),
    }
    gum = {"train": parse_sentences(GUM_TRAIN), "dev": [], "test": []}
    lanes = build_lanes(ewt, gum, parse_sentences(PUD_TEST), [], tag="r2.18")
    return list(lanes.training) + list(lanes.eval)


def _perfect_reply(record: Record) -> dict:
    return {
        "labels": [
            {
                "upos": token.upos,
                "lemma": token.lemma or "_",
                "head": token.head,
                "deprel": token.deprel or "_",
                "feats": token.feats or "_",
            }
            for token in record.sentence.tokens
        ]
    }


def test_split_records_selects_the_score_inputs(tmp_path):
    from stx_corpus.lanes import read_records
    from stx_corpus.pipeline import _record_to_dict

    # The records come from the uploaded lane shape, per plan step 3.
    path = tmp_path / "training.jsonl"
    path.write_text(
        "".join(json.dumps(_record_to_dict(record)) + "\n" for record in _records()),
        encoding="utf-8",
    )
    records = read_records(path)

    dev = split_records(records, "dev")
    assert {record.sentence.sent_id for record in dev} == {"ewt-dev-1"}
    holdout = split_records(records, "eval")
    assert {record.split for record in holdout} == {"test"}
    with pytest.raises(ValueError):
        split_records(records, "train")


def test_shard_records_partition():
    records = split_records(_records(), "eval")
    shards = [shard_records(records, f"{index}/2") for index in range(2)]
    assert sum(len(shard) for shard in shards) == len(records)
    assert shard_records(records, None) == records
    with pytest.raises(ValueError):
        shard_records(records, "2/2")


def test_score_replies_full_credit_on_a_perfect_reply():
    records = split_records(_records(), "eval")
    counts = score_replies(records, [_perfect_reply(record) for record in records])
    rates = scores(counts)
    for source in ("ewt", "pud"):
        assert rates[source] == {"upos": 1.0, "lemma": 1.0, "las": 1.0}
    assert counts["ewt"]["failures"] == 0


def test_score_replies_zero_credit_on_a_failed_sentence():
    records = split_records(_records(), "dev")
    counts = score_replies(records, [{"error": "2 records for 3 tokens"}])
    assert counts["ewt"]["failures"] == 1
    assert counts["ewt"]["tokens"] > 0
    assert scores(counts)["ewt"] == {"upos": 0.0, "lemma": 0.0, "las": 0.0}


def test_merge_counts_and_aggregate(tmp_path):
    records = split_records(_records(), "eval")
    replies = [_perfect_reply(record) for record in records]
    counts = score_replies(records, replies)
    halves = [
        score_replies(
            shard_records(records, f"{index}/2"),
            [reply for position, reply in enumerate(replies) if position % 2 == index],
        )
        for index in range(2)
    ]
    assert merge_counts(halves) == counts

    meta = {
        "split": "eval",
        "run_id": "run-1",
        "model_hash": "abc",
        "llama_version": "b10665",
        "threads": 4,
        "ud_release": "r2.18",
    }
    paths = []
    for index, half in enumerate(halves):
        path = tmp_path / f"shard-{index}.json"
        path.write_text(json.dumps(scorecard(half, {**meta, "shard": f"{index}/2"})))
        paths.append(path)
    merged = aggregate(paths)
    assert merged["counts"] == counts
    assert merged["model_hash"] == "abc"

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(scorecard(halves[0], {**meta, "model_hash": "zzz"})))
    with pytest.raises(ValueError):
        aggregate([paths[0], bad])


def test_label_records_streams_through_one_process(tmp_path):
    # A fake stx labels every token NOUN, so the plumbing is proven
    # without llama.cpp.
    fake = tmp_path / "fake_stx.py"
    fake.write_text(
        "import json, sys\n"
        "for line in sys.stdin:\n"
        "    tokens = json.loads(line)['tokens']\n"
        "    labels = [{'upos': 'NOUN', 'lemma': form, 'head': 0,\n"
        "               'deprel': 'root', 'feats': '_'} for form in tokens]\n"
        "    print(json.dumps({'labels': labels}))\n"
    )
    records = split_records(_records(), "eval")
    replies = label_records(records, f"{sys.executable} {fake}")
    assert len(replies) == len(records)
    counts = score_replies(records, replies)
    assert counts["ewt"]["failures"] == 0
    assert 0.0 < scores(counts)["ewt"]["upos"] < 1.0


def test_label_records_fails_on_a_dead_harness(tmp_path):
    fake = tmp_path / "dead_stx.py"
    fake.write_text("import sys; sys.exit(3)\n")
    records = split_records(_records(), "dev")
    with pytest.raises(RuntimeError):
        label_records(records, f"{sys.executable} {fake}")


def test_sha256_file(tmp_path):
    import hashlib

    path = tmp_path / "model.gguf"
    path.write_bytes(b"gguf")
    assert sha256_file(path) == hashlib.sha256(b"gguf").hexdigest()


def test_score_replies_matches_the_tier_t0_scorer():
    # EVL-TIERS-6 chains through score.py: the sweep counting must
    # agree with the tier T0 scorer on the same system output.
    from dataclasses import replace

    from stx_corpus.score import score_sentences

    records = [record for record in _records() if record.source == "ewt"]
    replies = [_perfect_reply(record) for record in records]

    # Degrade one label, so the agreement covers a non-trivial score.
    first = replies[0]["labels"][0]
    replies[0]["labels"][0] = {**first, "upos": "X", "lemma": "wrong"}

    system_sentences = [
        replace(
            record.sentence,
            tokens=tuple(
                replace(
                    token,
                    upos=label["upos"],
                    lemma=label["lemma"],
                    head=label["head"],
                    deprel=label["deprel"],
                )
                for token, label in zip(record.sentence.tokens, reply["labels"], strict=True)
            ),
        )
        for record, reply in zip(records, replies, strict=True)
    ]
    reference = score_sentences([record.sentence for record in records], system_sentences)

    rates = scores(score_replies(records, replies))["ewt"]
    assert rates["upos"] == round(reference.upos_accuracy, 4)
    assert rates["lemma"] == round(reference.lemma_accuracy, 4)
    assert rates["las"] == round(reference.las, 4)
