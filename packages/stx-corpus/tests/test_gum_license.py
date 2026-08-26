from pathlib import Path

from stx_corpus.gum_license import document_genre, is_excluded, non_commercial_genres

FIXTURES = Path(__file__).parent / "fixtures"


def test_non_commercial_genres_reads_whow_and_fiction():
    text = (FIXTURES / "gum_license.txt").read_text(encoding="utf-8")
    assert non_commercial_genres(text) == {"whow", "fiction"}


def test_document_genre_reads_the_newdoc_id_prefix():
    assert document_genre("GUM_whow_paperclip") == "whow"
    assert document_genre("GUM_bio_byron") == "bio"
    assert document_genre("not-a-gum-id") is None


def test_is_excluded_matches_only_the_restricted_genres():
    excluded = frozenset({"whow", "fiction"})
    assert is_excluded("GUM_whow_paperclip", excluded)
    assert is_excluded("GUM_fiction_beast", excluded)
    assert not is_excluded("GUM_bio_byron", excluded)
