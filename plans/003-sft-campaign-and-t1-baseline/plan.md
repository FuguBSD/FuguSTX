# 003 — The first SFT campaign and the tier T1 baseline

Implements: TRN-INST, TRN-CPT, TRN-SFT, TRN-EXEC, TRN-BUDGET, ENG-SCHEMA,
COR-BUCKETS, IAC-APPLY, EVL-TIERS without EVL-TIERS-4, LRN-DELIVER without
LRN-DELIVER-2 without LRN-DELIVER-3

Defers: COR-AUG, TRN-TEACH, ENG-SPLIT, ENG-DETERM

## Status

The schema, the pairs builder, the train stack, the task runner, and the CI jobs
can land now. No decision blocks this plan. Decisions
[T2](../../spec/DECISIONS.md#t2), [T3](../../spec/DECISIONS.md#t3),
[T4](../../spec/DECISIONS.md#t4), and [T6](../../spec/DECISIONS.md#t6) shape it.

Three prerequisites wait on a human, before the first campaign:

- A human creates a key on the pipeline application, and sets it in the CI
  secrets, per [the shared credentials](../../infra/CLAUDE.md#credentials). The
  CI jobs of this plan use that key.
- A human adds billing read to the campaign credential. A live probe on
  2026-08-25 created every train resource type, and the platform denied the
  consumption read. The [forecast check](../../infra/CLAUDE.md#spend-guardrails)
  needs that read.
- A human records the H100-1-80G quota grant in
  [the runbook](../../infra/persistent/RUNBOOK.md). The same probe created an
  H100-1-80G server, so the platform grants the quota today. The runbook record
  is stale.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. This plan
excludes both: a FuguTTX plan lands each change.

EVL-TIERS-4 — the tier T2 suite in OpenBSD guests — waits for phase P5.

COR-AUG and TRN-TEACH wait for phase P4. The pairs builder reads an augmentation
input, and that input stays empty until the teacher campaign.

ENG-SPLIT and ENG-DETERM wait for the engine, in phase P6. The tier T1 sweep
calls llama.cpp directly, as a measurement tool. ENG-SPLIT-4 constrains the
engine, and no engine code exists before that phase.

IAC-APPLY stays partial after this plan. The state encryption, the CI-webhook
alert channel, and the push-to-main apply jobs stay absent. A later plan lands
each one.

## Order of work

1. Define the annotation schema serialization and its llama.cpp GBNF grammar
   (ENG-SCHEMA-1, ENG-SCHEMA-2), in one committed file. The pairs builder, the
   sweep, and the future engine must read the same file.
2. Extend `packages/stx-corpus` with a pairs builder: a token list in, schema
   labels out (TRN-SFT-2), from the training lane. The builder also reads the
   augmentation input of TRN-SFT-1. A test must prove that no eval-lane sentence
   enters a pair (COR-LANES-4).
3. Upload the training lane and the pairs to `stx-corpus`, and the eval lane to
   `stx-evalcorpus`. The train instance and the CI jobs read the buckets.
4. Grow `infra/train`: one GPU server, the root and the scratch volumes, and one
   routed IPv4 address. A variable selects the offer. H100-1-80G is the default,
   and L40S-1-48G is the budget escape (TRN-INST, decision T3). Build the tags
   from one map in `locals.tf`, per
   [the shared tags](../../infra/CLAUDE.md#tags).
5. Add `make infra-plan`, `infra-up`, `infra-down`, `infra-price`,
   `infra-status`, `infra-cost`, and `infra-watchdog` to `mk/local.mk`, per
   [the shared task runner](../../infra/CLAUDE.md#task-runner). `infra-up` must
   read the live price first (TRN-INST-1), and it must run the forecast check. A
   forecast must not assume a run cheaper than one hour (TRN-BUDGET-1).
   `infra-status` must report the versioning of each bucket (COR-BUCKETS-2).
6. Implement the watchdog, per
   [the shared spend guardrails](../../infra/CLAUDE.md#spend-guardrails). It
   destroys the train stack on a stale heartbeat, or past `stx:expires`. It must
   report, and must not destroy, a resource with no `stx:managed` tag.
7. Add the `workflow_dispatch` CI jobs under the `infra-apply` environment:
   stack up, train, and stack down, plus the watchdog on a 30-minute schedule.
   One concurrency group serializes each stack apply. At up, CI creates a train
   key with an expiry, and it delivers the key over SSH after boot, per
   [the train credential](../../infra/CLAUDE.md#the-train-credential). At down,
   CI deletes the key. The operator network resets SSH, so the delivery runs
   from CI ([the LEARNING entries](../../spec/LEARNING.md#lrn-entries)).
8. Add `make train-cpt` and `make train-sft` (TRN-EXEC-3). `train-cpt` runs one
   epoch at a low learning rate on the prose lane (TRN-CPT-1). `train-sft` runs
   the QLoRA SFT pass on the pairs (TRN-SFT-1). Both run in the published
   Axolotl CUDA Docker image (TRN-EXEC-1), and every configuration lives in the
   repository (TRN-EXEC-2). The driver claims the stack once with a conditional
   write, and it writes the heartbeat every 60 seconds. It synchronizes each
   checkpoint to `stx-checkpoints` after each epoch (TRN-EXEC-4). A checkpoint
   key carries the run identifier and the step number (COR-BUCKETS-3).
9. Run the campaign: the CPT rehearsal, then two SFT runs — one from the base
   model, and one from the CPT output. Score both runs on the dev split with the
   tier T0 scorer. The comparison decides TRN-CPT-2. When the CPT pass does not
   move the scores, drop it, and record why (TRN-CPT-3).
10. Merge the chosen adapter, convert it to GGUF at Q8_0 (decision T2), record
    the model hash, and upload the artifact to `stx-artifacts`.
11. Run the tier T1 baseline sweep: the GGUF under llama.cpp, on the CPU, with
    greedy decoding, under the grammar, over the eval lane. The scorecard holds
    UPOS, lemma, and LAS per treebank, plus the llama.cpp version, the thread
    count, the model hash, the UD release tag, and the run identifier. The sweep
    writes the scorecard to `stx-artifacts` (EVL-TIERS-1). Write each measured
    baseline score into [evaluation.md](../../spec/evaluation.md#evl-tiers) as
    the tier T1 threshold (EVL-TIERS-5).
12. Wire the gated tier T1 sweep into CI, on the CPU (EVL-TIERS-3). The job runs
    on a manual dispatch, before a promotion.
13. Write the LEARNING entries: the quota state and its response time
    (TRN-INST-2), the live price against the table, the stack up and down and
    the teardown completeness, the train key delivery, the watchdog and the
    claim protocol, Axolotl in Docker, the checkpoint sync, the CPT decision,
    and the SFT scores. Map each entry to its FuguTTX units, per
    [the planned rehearsals](../../spec/LEARNING.md#lrn-map).
14. Set [STATUS.md](../../spec/STATUS.md): TRN-INST, TRN-CPT, TRN-SFT, TRN-EXEC,
    TRN-BUDGET, ENG-SCHEMA, and COR-BUCKETS per the campaign result. Trim the
    EVL-TIERS, IAC-APPLY, and LRN-DELIVER notes. Set the code roots of
    training.md and engine.md.

## The lane rule

The pairs builder must read the training lane only (COR-LANES-4, decision T6).
The sweep reads the eval lane at measurement time only. No eval sentence, no
eval score sample, and no eval error sample can enter a training input.

## Open questions

- The CPT branch. TRN-CPT-2 has two outcomes, and this plan cannot state the
  result before the runs. When the pass moves the scores, `make train-cpt`
  stays. When it does not, the product drops the pass, and
  [training.md](../../spec/training.md#trn-cpt) changes in the same change.
- The threshold values. EVL-TIERS-5 forbids a guess in the specification. The
  implementation writes the measured values after the baseline run, in the same
  change as the scorecard.
