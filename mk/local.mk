# This repository's own make fragment. Unlike the other mk/*.mk files,
# FuguBSD/Tooling does not own this one: it holds rules specific to
# FuguSTX, until a shared pack picks up the pattern.
#
# TEST_GLOBS: the org fragment covers t/ci/*.t. This repository also
# holds harness and infra tests directly under t/.
TEST_GLOBS = t/*.t t/ci/*.t

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

# The validate run keeps its own data directory, nested inside the
# gitignored .terraform/. A checkout that applied a stack holds a
# backend-initialized .terraform/, and a plain init -backend=false
# would demand the backend credential there.
infra-validate:
	@test -n "$(STACK)" || { echo "usage: make infra-validate STACK=<name>"; exit 1; }
	cd infra/$(STACK) && TF_DATA_DIR=.terraform/validate $(TOFU) init -backend=false -input=false >/dev/null && TF_DATA_DIR=.terraform/validate $(TOFU) validate

infra-check: infra-fmt-check
	@for stack in $(INFRA_STACKS); do \
		$(MAKE) infra-validate STACK=$$stack || exit 1; \
	done

# infra-bootstrap needs the Operator key. It creates the state bucket
# that every other stack's backend.tf names, with local state, once.
infra-bootstrap:
	cd infra/bootstrap && $(TOFU) init -input=false && $(TOFU) apply

# The task runner of the shared instructions. scripts/infra holds the
# logic: the live price read and the forecast check before an apply
# (TRN-INST-1, TRN-BUDGET-1), the bucket versioning check of
# infra-status (COR-BUCKETS-2), and the watchdog decisions. The train
# options: TRAIN_OFFER selects the offer, and TRAIN_HOURS sets the
# lease.
INFRA        = scripts/infra
TRAIN_OFFER ?= H100-1-80G
TRAIN_HOURS ?= 4

# The single quotes keep a variable value out of shell syntax: the
# hours value arrives from a workflow input.
infra-plan:
	@test -n "$(STACK)" || { echo "usage: make infra-plan STACK=<name>"; exit 1; }
	$(INFRA) plan $(STACK) --offer '$(TRAIN_OFFER)' --hours '$(TRAIN_HOURS)'

infra-plan-ro:
	@test -n "$(STACK)" || { echo "usage: make infra-plan-ro STACK=<name>"; exit 1; }
	$(INFRA) plan-ro $(STACK) --offer '$(TRAIN_OFFER)' --hours '$(TRAIN_HOURS)'

infra-up:
	@test -n "$(STACK)" || { echo "usage: make infra-up STACK=<name>"; exit 1; }
	$(INFRA) up $(STACK) --offer '$(TRAIN_OFFER)' --hours '$(TRAIN_HOURS)'

infra-down:
	@test -n "$(STACK)" || { echo "usage: make infra-down STACK=<name>"; exit 1; }
	$(INFRA) down $(STACK)

infra-price:
	@test -n "$(STACK)" || { echo "usage: make infra-price STACK=<name>"; exit 1; }
	$(INFRA) price $(STACK) --offer '$(TRAIN_OFFER)'

infra-status:
	$(INFRA) status

infra-cost:
	$(INFRA) cost

infra-watchdog:
	$(INFRA) watchdog

.PHONY: infra-fmt-check infra-validate infra-check infra-bootstrap
.PHONY: infra-plan infra-plan-ro infra-up infra-down infra-price
.PHONY: infra-status infra-cost infra-watchdog

# The training runs (TRN-EXEC-3), against a provisioned instance.
# SFT_FROM selects the SFT start point: base, or cpt (decision T4).
SFT_FROM ?= base

train-cpt:
	scripts/train cpt

train-sft:
	scripts/train sft-$(SFT_FROM)

.PHONY: train-cpt train-sft
