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

# infra: the OpenTofu stacks under infra/. The infra pack of
# FuguBSD/Tooling ships the shared rules (infra/CLAUDE.md) but no task
# runner yet, so this repository adds its own until a shared pack
# picks up the pattern. Neither target needs a Scaleway credential.

TOFU         ?= tofu
INFRA_STACKS ?= bootstrap persistent dev train image

CHECK_TARGETS += infra-check

infra-fmt-check:
	$(TOFU) fmt -recursive -check infra

infra-validate:
	@test -n "$(STACK)" || { echo "usage: make infra-validate STACK=<name>"; exit 1; }
	cd infra/$(STACK) && $(TOFU) init -backend=false -input=false >/dev/null && $(TOFU) validate

infra-check: infra-fmt-check
	@for stack in $(INFRA_STACKS); do \
		$(MAKE) infra-validate STACK=$$stack || exit 1; \
	done

# infra-bootstrap needs the Operator key. It creates the state bucket
# that every other stack's backend.tf names, with local state, once.
infra-bootstrap:
	cd infra/bootstrap && $(TOFU) init -input=false && $(TOFU) apply

.PHONY: infra-fmt-check infra-validate infra-check infra-bootstrap
