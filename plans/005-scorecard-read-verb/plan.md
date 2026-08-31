# 005 — The scorecard read verb

Each promotion writes a scorecard to the artifacts bucket (EVL-TIERS-1). No
command reads one back. This plan adds one read command, and it prints the
scores of every scorecard in the bucket.

- Implements: EVL-TIERS without EVL-TIERS-4

## Status

The read command, its tests, and the make target can land now. No decision
blocks this plan. The bucket set exists, and the applied bucket holds the
scorecards of two campaigns.

EVL-TIERS stays partial. The tier T2 artifact suite (EVL-TIERS-4) waits for
phase P5, so this plan excludes that rule.

The command reports, and it holds no threshold. The promotion review compares a
scorecard against [the thresholds](../../spec/evaluation.md#evl-tiers) by hand,
and this plan keeps that policy. A gate needs a change to
[the evaluation document](../../spec/evaluation.md) and human approval first.

## The reason

Three facts make the read path hard today:

1. `bucket.get_text` holds no caller, and `bucket.py` offers no listing call.
2. `scripts/train` reads one scorecard by an exact key, and it takes the model
   hash from the text with a pattern match. It reads no score.
3. The Perl path calls the `aws` command, and the operator host has none.

So an operator writes a throwaway script for each read. The command removes that
step.

## Order of work

1. Add `list_keys` to `packages/stx-corpus/src/stx_corpus/bucket.py`. It returns
   every key under one prefix, in key order.
2. Add the named-profile path to `bucket.client`. An environment key pair keeps
   priority, so each CI job behaves as before. A profile in `AWS_PROFILE` or in
   `SCW_PROFILE` gives the operator path of the synced `infra/CLAUDE.md`
   (IAC-APPLY-4). With neither one, the call raises as before.
3. Add `packages/stx-corpus/src/stx_corpus/cards.py`. It lists the `runs/`
   prefix, keeps each `scorecard-` key, reads each one, and prints one row for
   each scorecard and treebank pair. The options are `--bucket`, `--run`, and
   `--json`.
4. Add `packages/stx-corpus/tests/test_cards.py`. The tests fake the two bucket
   calls, so no test touches the network.
5. Add the `scorecards` target to `mk/local.mk`. The target stays outside
   `make check`, because it needs a credential and the network.
6. Append one rule to the EVL-TIERS unit of
   [the evaluation document](../../spec/evaluation.md): the project must hold
   one command that reads each scorecard and prints the scores. Set the
   EVL-TIERS note in [the register](../../spec/STATUS.md), and name the verb in
   the `evaluate` row of `train/RUNBOOK.md`.
7. Run the command against the applied bucket. The tier T1 row of `sft-cpt` must
   equal the threshold table, because that run fixed each threshold
   (EVL-TIERS-5).

## Out of scope

- A threshold gate, or a pass and fail exit status.
- A delta column between two scorecards.
- The bucket-name drift: `t1.py` holds a constant, and `train/config.env` holds
  `ARTIFACTS_BUCKET`. One change must remove one of the two.
- A report page, and a plotting dependency.
