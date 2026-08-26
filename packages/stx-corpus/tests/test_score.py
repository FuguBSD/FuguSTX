from pathlib import Path

import pytest
from stx_corpus.score import Scores, score

FIXTURES = Path(__file__).parent / "fixtures"


def test_score_matches_a_perfect_system():
    gold = (FIXTURES / "score_gold.conllu").read_text(encoding="utf-8")
    result = score(gold, gold)
    assert result == Scores(upos_accuracy=1.0, lemma_accuracy=1.0, las=1.0, tokens=5)


def test_score_matches_the_ud_tools_eval_fixture():
    """EVL-TIERS-6: matches `udeval` (the UD tools `eval.py` scorer) on this
    fixture pair: `udeval --counts score_gold.conllu score_system.conllu`
    reports UPOS 4/5, Lemmas 4/5, and LAS 4/5.
    """
    gold = (FIXTURES / "score_gold.conllu").read_text(encoding="utf-8")
    system = (FIXTURES / "score_system.conllu").read_text(encoding="utf-8")

    result = score(gold, system)

    assert result == Scores(upos_accuracy=0.8, lemma_accuracy=0.8, las=0.8, tokens=5)


def test_score_rejects_a_sentence_count_mismatch():
    gold = (FIXTURES / "score_gold.conllu").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="sentence count"):
        score(gold, "# text = only one sentence\n1\tA\ta\tX\t_\t_\t0\troot\t_\t_\n")


def test_score_rejects_a_token_count_mismatch():
    gold = "# sent_id = s1\n# text = A B\n1\tA\ta\tX\t_\t_\t0\troot\t_\t_\n2\tB\tb\tX\t_\t_\t1\tdep\t_\t_\n"
    system = "# sent_id = s1\n# text = A\n1\tA\ta\tX\t_\t_\t0\troot\t_\t_\n"
    with pytest.raises(ValueError, match="token count"):
        score(gold, system)


def test_score_rejects_an_empty_gold_file():
    with pytest.raises(ValueError, match="no token"):
        score("", "")
