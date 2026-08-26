# This repository's own make fragment. Unlike the other mk/*.mk files,
# FuguBSD/Tooling does not own this one: it holds rules specific to
# FuguSTX, until a shared pack picks up the pattern.
#
# test-py: the python pack's mk/python.mk defines no test-py target,
# because `uv run pytest` fails on an empty tree (packages/CLAUDE.md).
# packages/stx-corpus/tests now exists, so this repository adds its own.

TEST_TARGETS += test-py

test-py:
	uv run --locked pytest packages

.PHONY: test-py
