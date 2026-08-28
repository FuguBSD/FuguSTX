import json

import pytest
from corpus_fakes import EWT_DEV, EWT_TEST, EWT_TRAIN, GUM_TRAIN, PUD_TEST
from stx_corpus.conllu import parse_sentences
from stx_corpus.lanes import Record, build_lanes
from stx_corpus.pairs import EOS, build_pairs, read_augmentation, write_pairs
from stx_corpus.schema import load_grammar


def _lanes():
    ewt = {
        "train": parse_sentences(EWT_TRAIN),
        "dev": parse_sentences(EWT_DEV),
        "test": parse_sentences(EWT_TEST),
    }
    gum = {"train": parse_sentences(GUM_TRAIN), "dev": [], "test": []}
    pud = parse_sentences(PUD_TEST)
    prose = [
        Record(
            "prose",
            "train",
            "37134",
            parse_sentences("# sent_id = prose-1\n# text = Prose text.\n")[0],
        )
    ]
    return build_lanes(ewt, gum, pud, prose, tag="r2.18")


def test_pairs_come_from_the_train_splits_only():
    lanes = _lanes()
    pairs = build_pairs(lanes)

    assert {pair.sent_id for pair in pairs} == {"ewt-train-1", "gum-train-1", "gum-train-2"}
    assert all(pair.split == "train" for pair in pairs)


def test_no_dev_split_sentence_enters_a_pair():
    # TRN-SFT-3: the dev split is a score input.
    lanes = _lanes()
    dev_ids = {r.sentence.sent_id for r in lanes.training if r.split == "dev"}
    assert dev_ids  # the fixture holds a dev sentence

    pair_ids = {pair.sent_id for pair in build_pairs(lanes)}
    assert not pair_ids & dev_ids


def test_no_eval_lane_sentence_enters_a_pair():
    # COR-LANES-4: the lane rule is absolute.
    lanes = _lanes()
    eval_ids = {r.sentence.sent_id for r in lanes.eval}
    assert eval_ids  # the fixture holds eval sentences

    pair_ids = {pair.sent_id for pair in build_pairs(lanes)}
    assert not pair_ids & eval_ids


def test_the_prose_lane_holds_no_labels_so_it_enters_no_pair():
    pairs = build_pairs(_lanes())
    assert all(pair.source != "prose" for pair in pairs)


def test_an_augmentation_record_enters_the_pairs():
    # TRN-SFT-1: the builder reads the augmentation input.
    lanes = _lanes()
    accepted = Record("aug", "train", "teacher-1", parse_sentences(EWT_TRAIN)[0])
    pairs = build_pairs(lanes, augmentation=[accepted])
    assert sum(pair.source == "aug" for pair in pairs) == 1


def test_each_pair_serialization_matches_the_grammar():
    # TRN-SFT-2: grammar-constrained labels out.
    grammar = load_grammar()
    for pair in build_pairs(_lanes()):
        token_count = pair.prompt.count("\n") - 1
        assert pair.prompt.endswith("\n\n")
        assert pair.completion.count("\n") == token_count
        assert grammar.matches(pair.completion)


def test_write_pairs_emits_the_axolotl_segment_format(tmp_path):
    path = tmp_path / "pairs.jsonl"
    write_pairs(build_pairs(_lanes()), path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    record = json.loads(lines[0])
    prompt, completion = record["segments"]
    assert prompt["label"] is False
    assert prompt["text"].endswith("\n\n")
    assert completion["label"] is True
    assert completion["text"].endswith(EOS)


def test_read_augmentation_round_trips_the_lane_shape(tmp_path):
    from stx_corpus.pipeline import _record_to_dict

    record = Record("aug", "train", "teacher-1", parse_sentences(EWT_TRAIN)[0])
    path = tmp_path / "augmentation.jsonl"
    path.write_text(json.dumps(_record_to_dict(record)) + "\n", encoding="utf-8")

    loaded = read_augmentation(path)
    assert len(loaded) == 1
    assert loaded[0].source == "aug"
    assert loaded[0].sentence.tokens == record.sentence.tokens


def test_a_gold_gap_fails_closed():
    from stx_corpus.conllu import Sentence, Token
    from stx_corpus.lanes import Lanes
    from stx_corpus.schema import SchemaError

    broken = Token(1, "cat", "cat", None, None, None, 0, "root", None)
    sentence = Sentence("broken-1", "cat", (broken,))
    lanes = Lanes(training=(Record("ewt", "train", "r2.18", sentence),), eval=())

    with pytest.raises(SchemaError):
        build_pairs(lanes)
