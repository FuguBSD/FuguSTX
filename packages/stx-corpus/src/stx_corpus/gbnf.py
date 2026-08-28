"""Parse a llama.cpp GBNF grammar, and match text against it.

ENG-SCHEMA-1 makes the GBNF grammar the one constraint on the model
output. The tests match rendered records against the same grammar file
that llama.cpp loads, so the serialization and the grammar agree.

The parser covers the GBNF subset that `share/annotation.gbnf` uses:
rules, alternation, sequences, string literals, character classes,
groups, and the `*`, `+`, and `?` repetitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class GrammarError(ValueError):
    """The grammar text does not parse."""


_ESCAPES = {"t": "\t", "n": "\n", "r": "\r", '"': '"', "\\": "\\", "[": "[", "]": "]", "^": "^"}


@dataclass(frozen=True, slots=True)
class _Item:
    """One sequence element: a literal, a class, a rule ref, or a group."""

    kind: str  # "lit" | "class" | "ref" | "group"
    value: object
    repeat: str  # "" | "?" | "*" | "+"


class _Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def error(self, message: str) -> GrammarError:
        line = self.text.count("\n", 0, self.pos) + 1
        return GrammarError(f"line {line}: {message}")

    def skip_space(self, *, newlines: bool) -> None:
        spaces = " \t\r\n" if newlines else " \t\r"
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char == "#":
                end = self.text.find("\n", self.pos)
                self.pos = len(self.text) if end < 0 else end
            elif char in spaces:
                self.pos += 1
            else:
                return

    def at_rule_start(self) -> bool:
        rest = self.text[self.pos :]
        name = rest.split("::=", 1)[0].splitlines()[0] if "::=" in rest else ""
        return "\n" not in name and name.strip("-abcdefghijklmnopqrstuvwxyz \t") == ""

    def parse_name(self) -> str:
        start = self.pos
        while self.pos < len(self.text) and (
            self.text[self.pos].isalnum() or self.text[self.pos] == "-"
        ):
            self.pos += 1
        if self.pos == start:
            raise self.error("a rule name is expected")
        return self.text[start : self.pos]

    def expect(self, token: str) -> None:
        if not self.text.startswith(token, self.pos):
            raise self.error(f"{token!r} is expected")
        self.pos += len(token)

    def parse_escaped(self) -> str:
        char = self.text[self.pos]
        self.pos += 1
        if char != "\\":
            return char
        escape = self.text[self.pos]
        self.pos += 1
        if escape not in _ESCAPES:
            raise self.error(f"unknown escape: \\{escape}")
        return _ESCAPES[escape]

    def parse_literal(self) -> str:
        self.expect('"')
        chars: list[str] = []
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            chars.append(self.parse_escaped())
        self.expect('"')
        if not chars:
            raise self.error("an empty literal")
        return "".join(chars)

    def parse_class(self) -> tuple[bool, tuple[tuple[str, str], ...]]:
        self.expect("[")
        negated = self.text.startswith("^", self.pos)
        if negated:
            self.pos += 1
        ranges: list[tuple[str, str]] = []
        while self.pos < len(self.text) and self.text[self.pos] != "]":
            low = self.parse_escaped()
            high = low
            if self.text.startswith("-", self.pos) and not self.text.startswith("-]", self.pos):
                self.pos += 1
                high = self.parse_escaped()
            ranges.append((low, high))
        self.expect("]")
        if not ranges:
            raise self.error("an empty character class")
        return negated, tuple(ranges)

    def parse_item(self) -> _Item | None:
        self.skip_space(newlines=False)
        if self.pos >= len(self.text):
            return None
        char = self.text[self.pos]
        if char == '"':
            item = _Item("lit", self.parse_literal(), "")
        elif char == "[":
            item = _Item("class", self.parse_class(), "")
        elif char == "(":
            self.pos += 1
            group = self.parse_alternatives()
            self.expect(")")
            item = _Item("group", group, "")
        elif char.isalpha():
            item = _Item("ref", self.parse_name(), "")
        else:
            return None
        if self.pos < len(self.text) and self.text[self.pos] in "*+?":
            item = _Item(item.kind, item.value, self.text[self.pos])
            self.pos += 1
        return item

    def parse_sequence(self) -> tuple[_Item, ...]:
        items: list[_Item] = []
        while True:
            saved = self.pos
            self.skip_space(newlines=False)
            if self.pos < len(self.text) and self.text[self.pos] == "\n":
                self.pos += 1
                self.skip_space(newlines=True)
                if self.at_rule_start() or self.pos >= len(self.text):
                    self.pos = saved
                    return tuple(items)
                continue
            item = self.parse_item()
            if item is None:
                return tuple(items)
            items.append(item)

    def parse_alternatives(self) -> tuple[tuple[_Item, ...], ...]:
        alternatives = [self.parse_sequence()]
        while True:
            self.skip_space(newlines=False)
            if not self.text.startswith("|", self.pos):
                return tuple(alternatives)
            self.pos += 1
            alternatives.append(self.parse_sequence())

    def parse_rules(self) -> dict[str, tuple[tuple[_Item, ...], ...]]:
        rules: dict[str, tuple[tuple[_Item, ...], ...]] = {}
        while True:
            self.skip_space(newlines=True)
            if self.pos >= len(self.text):
                return rules
            name = self.parse_name()
            self.skip_space(newlines=False)
            self.expect("::=")
            body = self.parse_alternatives()
            if name in rules:
                raise self.error(f"duplicate rule: {name}")
            if not any(body):
                raise self.error(f"an empty rule body: {name}")
            rules[name] = body


class Grammar:
    """A parsed grammar, with an exact whole-string matcher."""

    def __init__(self, rules: dict[str, tuple[tuple[_Item, ...], ...]]) -> None:
        for body in rules.values():
            for sequence in body:
                for item in sequence:
                    if item.kind == "ref" and item.value not in rules:
                        raise GrammarError(f"an undefined rule: {item.value}")
        self.rules = rules

    @classmethod
    def parse(cls, text: str) -> Grammar:
        return cls(_Parser(text).parse_rules())

    @classmethod
    def from_path(cls, path: Path) -> Grammar:
        return cls.parse(path.read_text(encoding="utf-8"))

    def matches(self, text: str, start: str = "root") -> bool:
        """True when the whole text derives from the start rule."""
        if start not in self.rules:
            raise GrammarError(f"an undefined start rule: {start}")
        memo: dict[tuple[int, int], frozenset[int]] = {}

        def match_rule(name: str, pos: int) -> frozenset[int]:
            key = (id(self.rules[name]), pos)
            if key in memo:
                return memo[key]
            memo[key] = frozenset()  # a cycle yields nothing
            ends = frozenset(
                end for sequence in self.rules[name] for end in match_sequence(sequence, 0, pos)
            )
            memo[key] = ends
            return ends

        def match_once(item: _Item, pos: int) -> frozenset[int]:
            if item.kind == "lit":
                literal: str = item.value  # type: ignore[assignment]
                if text.startswith(literal, pos):
                    return frozenset((pos + len(literal),))
                return frozenset()
            if item.kind == "class":
                negated, ranges = item.value  # type: ignore[misc]
                if pos >= len(text):
                    return frozenset()
                hit = any(low <= text[pos] <= high for low, high in ranges)
                return frozenset((pos + 1,)) if hit != negated else frozenset()
            if item.kind == "ref":
                return match_rule(item.value, pos)  # type: ignore[arg-type]
            return frozenset(
                end
                for sequence in item.value  # type: ignore[union-attr]
                for end in match_sequence(sequence, 0, pos)
            )

        def match_item(item: _Item, pos: int) -> frozenset[int]:
            if item.repeat == "":
                return match_once(item, pos)
            if item.repeat == "?":
                return frozenset({pos}) | match_once(item, pos)
            ends = {pos}
            frontier = {pos}
            while frontier:
                frontier = {
                    end
                    for at in frontier
                    for end in match_once(item, at)
                    if end not in ends and end > at
                }
                ends |= frontier
            if item.repeat == "+":
                ends.discard(pos)
            return frozenset(ends)

        def match_sequence(sequence: tuple[_Item, ...], index: int, pos: int) -> frozenset[int]:
            if index == len(sequence):
                return frozenset((pos,))
            return frozenset(
                end
                for middle in match_item(sequence[index], pos)
                for end in match_sequence(sequence, index + 1, middle)
            )

        return len(text) in match_rule(start, 0)
