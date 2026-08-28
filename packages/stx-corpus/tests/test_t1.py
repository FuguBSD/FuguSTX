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


def _lanes():
    ewt = {
        "train": parse_sentences(EWT_TRAIN),
        "dev": parse_sentences(EWT_DEV),
        "test": parse_sentences(EWT_TEST),
    }
    gum = {"train": parse_sentences(GUM_TRAIN), "dev": [], "test": []}
    return build_lanes(ewt, gum, parse_sentences(PUD_TEST), [], tag="r2.18")


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


def test_split_records_selects_the_score_inputs():
    lanes = _lanes()
    dev = split_records(lanes, "dev")
    assert {record.sentence.sent_id for record in dev} == {"ewt-dev-1"}
    holdout = split_records(lanes, "eval")
    assert {record.split for record in holdout} == {"test"}
    with pytest.raises(ValueError):
        split_records(lanes, "train")


def test_shard_records_partition():
    records = split_records(_lanes(), "eval")
    shards = [shard_records(records, f"{index}/2") for index in range(2)]
    assert sum(len(shard) for shard in shards) == len(records)
    assert shard_records(records, None) == records
    with pytest.raises(ValueError):
        shard_records(records, "2/2")


def test_score_replies_full_credit_on_a_perfect_reply():
    records = split_records(_lanes(), "eval")
    counts = score_replies(records, [_perfect_reply(record) for record in records])
    rates = scores(counts)
    for source in ("ewt", "pud"):
        assert rates[source] == {"upos": 1.0, "lemma": 1.0, "las": 1.0}
    assert counts["ewt"]["failures"] == 0


def test_score_replies_zero_credit_on_a_failed_sentence():
    records = split_records(_lanes(), "dev")
    counts = score_replies(records, [{"error": "2 records for 3 tokens"}])
    assert counts["ewt"]["failures"] == 1
    assert counts["ewt"]["tokens"] > 0
    assert scores(counts)["ewt"] == {"upos": 0.0, "lemma": 0.0, "las": 0.0}


def test_merge_counts_and_aggregate(tmp_path):
    records = split_records(_lanes(), "eval")
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
    records = split_records(_lanes(), "eval")
    replies = label_records(records, f"{sys.executable} {fake}")
    assert len(replies) == len(records)
    counts = score_replies(records, replies)
    assert counts["ewt"]["failures"] == 0
    assert 0.0 < scores(counts)["ewt"]["upos"] < 1.0


def test_label_records_fails_on_a_dead_harness(tmp_path):
    fake = tmp_path / "dead_stx.py"
    fake.write_text("import sys; sys.exit(3)\n")
    records = split_records(_lanes(), "dev")
    with pytest.raises(RuntimeError):
        label_records(records, f"{sys.executable} {fake}")


def test_sha256_file(tmp_path):
    import hashlib

    path = tmp_path / "model.gguf"
    path.write_bytes(b"gguf")
    assert sha256_file(path) == hashlib.sha256(b"gguf").hexdigest()
