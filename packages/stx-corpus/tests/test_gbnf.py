import pytest
from stx_corpus.gbnf import Grammar, GrammarError


def test_literal_and_reference():
    grammar = Grammar.parse('root ::= "a" tail\ntail ::= "b" | "c"\n')
    assert grammar.matches("ab")
    assert grammar.matches("ac")
    assert not grammar.matches("a")
    assert not grammar.matches("abc")


def test_character_class_and_negation():
    grammar = Grammar.parse("root ::= [a-c]+ [^\\t\\n]\n")
    assert grammar.matches("abcx")
    assert grammar.matches("a ")
    assert not grammar.matches("a\t")
    assert not grammar.matches("x")


def test_repeats():
    grammar = Grammar.parse('root ::= "a"* "b"? "c"+\n')
    assert grammar.matches("c")
    assert grammar.matches("aabccc")
    assert grammar.matches("bc")
    assert not grammar.matches("ab")
    assert not grammar.matches("")


def test_group_repeat():
    grammar = Grammar.parse('root ::= "x" ("," "x")*\n')
    assert grammar.matches("x")
    assert grammar.matches("x,x,x")
    assert not grammar.matches("x,")


def test_escapes_in_literals():
    grammar = Grammar.parse('root ::= "a\\tb\\n"\n')
    assert grammar.matches("a\tb\n")
    assert not grammar.matches("a b\n")


def test_comment_lines_are_skipped():
    grammar = Grammar.parse('# a comment\nroot ::= "a" # a trailing comment\n')
    assert grammar.matches("a")


def test_undefined_rule_is_refused():
    with pytest.raises(GrammarError):
        Grammar.parse("root ::= missing\n")


def test_duplicate_rule_is_refused():
    with pytest.raises(GrammarError):
        Grammar.parse('root ::= "a"\nroot ::= "b"\n')


def test_unknown_start_rule_is_refused():
    grammar = Grammar.parse('root ::= "a"\n')
    with pytest.raises(GrammarError):
        grammar.matches("a", start="record")
