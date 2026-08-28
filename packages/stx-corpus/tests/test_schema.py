import pytest
from corpus_fakes import EWT_TRAIN, GUM_TRAIN
from stx_corpus.conllu import Token, parse_sentences
from stx_corpus.schema import (
    GRAMMAR_PATH,
    SchemaError,
    load_grammar,
    render_labels,
    render_record,
    render_tokens,
)


def _token(**overrides) -> Token:
    fields = {
        "id": 1,
        "form": "cat",
        "lemma": "cat",
        "upos": "NOUN",
        "xpos": None,
        "feats": "Number=Sing",
        "head": 0,
        "deprel": "root",
        "misc": None,
    }
    fields.update(overrides)
    return Token(**fields)


def test_grammar_file_exists_and_parses():
    assert GRAMMAR_PATH.is_file()
    load_grammar()


def test_render_tokens_serialization():
    assert render_tokens(["From", "Friday"]) == "1\tFrom\n2\tFriday\n\n"
    with pytest.raises(SchemaError):
        render_tokens([])


def test_render_record_maps_absent_fields_to_underscore():
    record = render_record(_token(lemma=None, feats=None))
    assert record == "NOUN\t_\t0\troot\t_\n"


def test_render_record_refuses_a_gold_gap():
    for gap in ({"upos": None}, {"head": None}, {"deprel": None}):
        with pytest.raises(SchemaError):
            render_record(_token(**gap))


def test_grammar_accepts_each_legal_record():
    grammar = load_grammar()
    for text in (EWT_TRAIN, GUM_TRAIN):
        for sentence in parse_sentences(text):
            assert grammar.matches(render_labels(sentence.tokens))
    edge_cases = [
        "PROPN\tFriday\t5\tnmod:poss\tNumber=Sing\n",
        "VERB\tsit\t0\troot\tMood=Ind|Number=Sing|Tense=Past\n",
        "X\t_\t2\tgoeswith\t_\n",
        "NUM\t100,000\t3\tnummod\tNumForm=Digit,Word\n",
        "PRON\the\t2\tnsubj\tNumber[psor]=Sing\n",
    ]
    for record in edge_cases:
        assert grammar.matches(record), record


def test_grammar_rejects_each_illegal_record():
    grammar = load_grammar()
    illegal = [
        "",  # no record
        "FOO\tcat\t0\troot\t_\n",  # an unknown UPOS tag
        "NOUN\tcat\t0\troot\n",  # a missing field
        "NOUN\tcat\t0\troot\t_\t0:3\n",  # an offset field (ENG-SPLIT-3)
        "NOUN\t\t0\troot\t_\n",  # an empty lemma
        "NOUN\tcat\tx\troot\t_\n",  # a head that is not an index
        "NOUN\tcat\t01\troot\t_\n",  # a zero-padded head
        "NOUN\tcat\t0\tnotarel\t_\n",  # an unknown relation
        "NOUN\tcat\t0\troot\tNumber\n",  # a feature without a value
        "NOUN\tcat\t0\troot\t_",  # no closing newline
    ]
    for record in illegal:
        assert not grammar.matches(record), record


def test_render_labels_round_trip_through_the_grammar():
    grammar = load_grammar()
    sentence = parse_sentences(EWT_TRAIN)[0]
    labels = render_labels(sentence.tokens)
    assert labels.count("\n") == len(sentence.tokens)
    assert grammar.matches(labels)
    with pytest.raises(SchemaError):
        render_labels(())
