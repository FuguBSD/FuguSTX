import pytest
from stx_corpus.conllu import Sentence
from stx_corpus.lanes import LaneLeakageError, Record, assert_no_leakage, build_lanes


def _sentence(sent_id: str, text: str = "text") -> Sentence:
    return Sentence(sent_id=sent_id, text=text, tokens=())


def test_build_lanes_places_splits_per_cor_lanes():
    ewt = {"train": [_sentence("ewt-train-1")], "dev": [_sentence("ewt-dev-1")]}
    ewt["test"] = [_sentence("ewt-test-1")]
    gum = {"train": [_sentence("gum-train-1")], "dev": [], "test": [_sentence("gum-test-1")]}
    pud_test = [_sentence("pud-test-1")]
    prose = [Record("prose", "train", "37134", _sentence("gutenberg-37134-0"))]

    lanes = build_lanes(ewt, gum, pud_test, prose, tag="r2.18")

    training_ids = {record.sentence.sent_id for record in lanes.training}
    eval_ids = {record.sentence.sent_id for record in lanes.eval}

    assert training_ids == {"ewt-train-1", "ewt-dev-1", "gum-train-1", "gutenberg-37134-0"}
    assert eval_ids == {"ewt-test-1", "gum-test-1", "pud-test-1"}


def test_assert_no_leakage_passes_on_disjoint_lanes():
    ewt = {"train": [_sentence("ewt-train-1")], "dev": [], "test": [_sentence("ewt-test-1")]}
    gum = {"train": [], "dev": [], "test": []}
    lanes = build_lanes(ewt, gum, [], [], tag="r2.18")
    assert_no_leakage(lanes)  # must not raise


def test_assert_no_leakage_rejects_a_shared_sent_id():
    from stx_corpus.lanes import Lanes

    shared = Record("ewt", "train", "r2.18", _sentence("shared-id"))
    leaked = Record("ewt", "test", "r2.18", _sentence("shared-id"))
    lanes = Lanes(training=(shared,), eval=(leaked,))

    with pytest.raises(LaneLeakageError):
        assert_no_leakage(lanes)
