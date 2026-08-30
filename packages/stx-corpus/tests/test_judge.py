import json

from stx_corpus.judge import accepted_record, filter_proposals, judge
from stx_corpus.lanes import Lanes
from stx_corpus.pairs import build_pairs, read_augmentation
from stx_corpus.schema import load_grammar

_TABLE = {"cat": frozenset({"NOUN"}), "sat": frozenset({"VERB"})}

_GOOD_PASS = (
    "DET\ta\t2\tdet\t_\n"
    "NOUN\tcat\t3\tnsubj\t_\n"
    "VERB\tsit\t0\troot\tTense=Past\n"
    "PUNCT\t.\t3\tpunct\t_\n"
)


def _proposal(**overrides):
    proposal = {
        "sent_id": "teach-run-1-batch-1-1",
        "text": "A cat sat.",
        "forms": ["A", "cat", "sat", "."],
        "passes": [_GOOD_PASS, _GOOD_PASS],
    }
    proposal.update(overrides)
    return proposal


def _judge(proposal, table=_TABLE):
    return judge(proposal, load_grammar(), table)


def test_a_clean_proposal_is_accepted():
    assert _judge(_proposal()) is None


def test_the_completion_shape_normalizes_before_the_checks():
    # The grammar wants exactly one final newline, and the few-shot
    # examples end with a blank separator line.
    bare = _GOOD_PASS.rstrip("\n")
    trailing = _GOOD_PASS + "\n"
    assert _judge(_proposal(passes=[bare, bare])) is None
    assert _judge(_proposal(passes=[trailing, trailing])) is None
    assert _judge(_proposal(passes=[bare, trailing])) is None


def test_check_1_rejects_a_pass_disagreement():
    second = _GOOD_PASS.replace("Tense=Past", "_")
    assert _judge(_proposal(passes=[_GOOD_PASS, second])) == "disagree"


def test_check_3_rejects_a_tag_outside_the_grammar():
    bad = _GOOD_PASS.replace("PUNCT", "PUNKT")
    assert _judge(_proposal(passes=[bad, bad])) == "tag"


def test_check_3_rejects_a_record_count_mismatch():
    short = "NOUN\tcat\t0\troot\t_\n"
    assert _judge(_proposal(passes=[short, short])) == "count"


def test_check_2_rejects_a_second_root():
    bad = _GOOD_PASS.replace("3\tpunct", "0\tpunct")
    assert _judge(_proposal(passes=[bad, bad])) == "tree"


def test_check_2_rejects_a_disconnected_tree():
    # Tokens 1 and 2 point at each other, away from the root.
    bad = "NOUN\ta\t2\tnsubj\t_\nNOUN\tb\t1\tnmod\t_\nVERB\tc\t0\troot\t_\n"
    assert _judge(_proposal(forms=["a", "b", "c"], passes=[bad, bad])) == "tree"


def test_check_3_rejects_a_known_word_with_a_wrong_upos():
    bad = _GOOD_PASS.replace("NOUN\tcat", "VERB\tcat")
    assert _judge(_proposal(passes=[bad, bad])) == "word"


def test_check_3_lets_an_unknown_word_pass():
    # The interim table constrains a known word only.
    assert _judge(_proposal(), table={}) is None


def test_an_accepted_record_takes_the_lane_shape(tmp_path):
    record = accepted_record(_proposal(), tag="Qwen/Qwen3-32B-FP8")
    assert record["source"] == "teacher"
    assert record["split"] == "train"
    assert record["tag"] == "Qwen/Qwen3-32B-FP8"  # the provenance tag
    assert [token["form"] for token in record["tokens"]] == ["A", "cat", "sat", "."]
    assert record["tokens"][2]["feats"] == "Tense=Past"
    assert record["tokens"][0]["xpos"] is None
    # The text stays reconstructible from the forms (COR-CONLLU-1).
    assert [token["misc"] for token in record["tokens"]] == [None, None, "SpaceAfter=No", None]

    # The reader of TRN-SFT-1 takes the record, and the pair matches
    # the grammar.
    path = tmp_path / "accepted.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    loaded = read_augmentation(path)
    pairs = build_pairs(Lanes(training=(), eval=()), augmentation=loaded)
    assert len(pairs) == 1
    assert load_grammar().matches(pairs[0].completion)


def test_filter_proposals_logs_each_reject_with_its_reason():
    disagreeing = _proposal(
        sent_id="teach-run-1-batch-1-2",
        passes=[_GOOD_PASS, _GOOD_PASS.replace("Tense=Past", "_")],
    )
    accepted, rejects, report = filter_proposals(
        [_proposal(), disagreeing], _TABLE, tag="Qwen/Qwen3-32B-FP8"
    )

    assert len(accepted) == 1
    assert [reject["reason"] for reject in rejects] == ["disagree"]
    assert rejects[0]["sent_id"] == "teach-run-1-batch-1-2"
    assert report["proposed"] == 2
    assert report["accepted"] == 1
    assert report["rejected"]["disagree"] == 1
    assert report["acceptance_rate"] == 0.5
