from corpus_fakes import patch_fetch
from stx_corpus import fetch, t0


def test_dev_split_sentences_holds_only_the_dev_split(monkeypatch):
    patch_fetch(monkeypatch, fetch)
    sentences = t0.dev_split_sentences()
    sent_ids = {sentence.sent_id for sentence in sentences}
    assert sent_ids == {"ewt-dev-1", "gum-dev-1"}


def test_self_check_scores_a_perfect_match(monkeypatch):
    patch_fetch(monkeypatch, fetch)
    result = t0.self_check()
    assert (result.upos_accuracy, result.lemma_accuracy, result.las) == (1.0, 1.0, 1.0)


def test_main_reports_success(monkeypatch, capsys):
    patch_fetch(monkeypatch, fetch)
    assert t0.main() == 0
    assert "tier T0 self-check" in capsys.readouterr().out
