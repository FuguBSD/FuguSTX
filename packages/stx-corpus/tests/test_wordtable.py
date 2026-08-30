from corpus_fakes import EWT_DEV, EWT_TEST, EWT_TRAIN, GUM_TRAIN, PUD_TEST
from stx_corpus.conllu import parse_sentences
from stx_corpus.gbnf import Grammar
from stx_corpus.lanes import Record, build_lanes
from stx_corpus.schema import GRAMMAR_PATH
from stx_corpus.wordtable import TABLE_PATH, build_table, read_table, write_table


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
            parse_sentences("# sent_id = prose-1\n# text = Prose words here.\n")[0],
        )
    ]
    return build_lanes(ewt, gum, pud, prose, tag="r2.18")


def test_the_table_holds_the_train_split_words():
    table = build_table(_lanes().training)
    assert table["cat"] == frozenset({"NOUN"})
    assert table["Fold"] == frozenset({"VERB"})


def test_no_dev_split_entry_shapes_the_table():
    # The dev split is a score input, and it must not shape the table.
    # A form that the train split also holds stays a legal entry, so
    # the guard checks the dev-only forms.
    lanes = _lanes()
    dev_forms = {
        token.form
        for record in lanes.training
        if record.split == "dev"
        for token in record.sentence.tokens
    }
    train_forms = {
        token.form
        for record in lanes.training
        if record.split == "train"
        for token in record.sentence.tokens
    }
    dev_only = dev_forms - train_forms
    assert "Dogs" in dev_only  # the fixture holds a dev-only form

    table = build_table(lanes.training)
    assert not dev_only & set(table)


def test_no_eval_lane_entry_shapes_the_table():
    lanes = _lanes()
    table = build_table(list(lanes.training) + list(lanes.eval))
    eval_forms = {token.form for record in lanes.eval for token in record.sentence.tokens}
    assert eval_forms
    assert not eval_forms & set(table)


def test_the_prose_lane_shapes_no_entry():
    table = build_table(_lanes().training)
    assert "Prose" not in table


def test_the_table_round_trips(tmp_path):
    table = build_table(_lanes().training)
    path = tmp_path / "word-table.tsv"
    write_table(table, path)
    assert read_table(path) == table


def test_the_committed_table_holds_inventory_tags_only():
    # Check 3 of the judge filter reads this file, so each tag must be
    # in the UPOS inventory of share/annotation.gbnf.
    grammar = Grammar.from_path(GRAMMAR_PATH)
    table = read_table(TABLE_PATH)
    assert len(table) > 10_000
    tags = {tag for allowed in table.values() for tag in allowed}
    for tag in tags:
        assert grammar.matches(f"{tag}\t_\t0\troot\t_\n")
