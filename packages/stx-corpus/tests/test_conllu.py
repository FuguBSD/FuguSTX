from pathlib import Path

from stx_corpus.conllu import parse_sentences

FIXTURES = Path(__file__).parent / "fixtures"


def test_multiword_range_is_expanded_and_excluded():
    text = (FIXTURES / "friday.conllu").read_text(encoding="utf-8")
    sentences = parse_sentences(text)

    assert len(sentences) == 1
    sentence = sentences[0]
    assert sentence.text == "From Friday's Daily Star"
    assert [token.id for token in sentence.tokens] == [1, 2, 3, 4, 5]
    assert [token.form for token in sentence.tokens] == ["From", "Friday", "'s", "Daily", "Star"]


def test_text_comes_from_the_text_comment_not_the_forms():
    text = (FIXTURES / "friday.conllu").read_text(encoding="utf-8")
    sentence = parse_sentences(text)[0]

    # The FORM column alone would read "From Friday 's Daily Star".
    assert sentence.text == "From Friday's Daily Star"


def test_decimal_id_and_deps_and_gum_payload_are_stripped():
    text = (FIXTURES / "extras.conllu").read_text(encoding="utf-8")
    sentence = parse_sentences(text)[0]

    assert [token.id for token in sentence.tokens] == [1, 2, 3, 4, 5, 6, 7]
    quote_mark = next(token for token in sentence.tokens if token.id == 4)
    closing_quote = next(token for token in sentence.tokens if token.id == 5)

    assert quote_mark.misc == "SpaceAfter=No"  # Entity= is stripped
    assert closing_quote.misc == "SpaceAfter=No"  # Discourse= is stripped


def test_literal_underscore_form_is_kept():
    text = (FIXTURES / "extras.conllu").read_text(encoding="utf-8")
    sentence = parse_sentences(text)[0]

    quote_mark = next(token for token in sentence.tokens if token.id == 4)
    assert quote_mark.form == "_"
    assert quote_mark.upos == "PUNCT"
