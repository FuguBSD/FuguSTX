# 003 — The first SFT campaign and the tier T1 baseline

- Implements: TRN-INST, TRN-CPT, TRN-SFT, TRN-EXEC
- Implements: IAC-APPLY, EVL-TIERS without EVL-TIERS-4
- Implements: ENG-SPLIT without ENG-SPLIT-1 without ENG-SPLIT-2
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3

Defers: COR-AUG, TRN-TEACH, ENG-DETERM

## Status

The schema, the pairs builder, the train stack, the task runner, and the CI jobs
can land now. No decision blocks this plan. Decisions
[T2](../../spec/DECISIONS.md#t2), [T3](../../spec/DECISIONS.md#t3),
[T4](../../spec/DECISIONS.md#t4), [T6](../../spec/DECISIONS.md#t6), and
[T7](../../spec/DECISIONS.md#t7) shape it.

The prerequisites are done. The pipeline key sits in the CI secrets. Both
declared offers hold a probed quota, and the billing reads passed with both
keys. [The runbook](../../infra/persistent/RUNBOOK.md) records each one, and it
names two open human steps: the persistent apply of the pipeline-policy change,
and the infra-apply branch policy. Both steps gate the first campaign dispatch.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. This plan
excludes both: a FuguTTX plan lands each change.

EVL-TIERS-4 — the tier T2 suite in OpenBSD guests — waits for phase P5.

COR-AUG and TRN-TEACH wait for phase P4. The pairs builder reads an augmentation
input, and that input stays empty until the teacher campaign.

A thin `stx` harness command drives every llama.cpp call of the tier T1 sweep.
The harness stays the only caller of llama.cpp, per decision
[T7](../../spec/DECISIONS.md#t7) and ENG-SPLIT-4. The schema holds no offset
field, so the model produces no offset (ENG-SPLIT-3). The tokenizer and the
offset rules of ENG-SPLIT-1 and ENG-SPLIT-2 wait for the engine, in phase P6,
with ENG-DETERM.

IAC-APPLY stays partial after this plan. The plan lands the task runner, the
watchdog, and the train stack CI jobs. The other absent parts of IAC-APPLY-4
stay absent. These are the state encryption, the CI-webhook alert channel, the
push-to-main apply jobs, and the pull-request plan job. Also absent: the
persistent, dev, and image dispatch jobs, and the scheduled reinstall job. The
daily Audit Trail export stays absent too. The dev-host watchdog timer waits for
the dev host, in phase P5. Step 14 sets the IAC-APPLY note, and the note names
each absent part.

## Order of work

1. Define the annotation schema serialization and its llama.cpp GBNF grammar
   (ENG-SCHEMA-1, ENG-SCHEMA-2), in one committed file. The pairs builder, the
   sweep, and the future engine must read the same file. A test must prove that
   the grammar accepts each legal record, and that it rejects an illegal record.
   Add the thin `stx` harness command: a token list in, labels out, through
   llama.cpp under the grammar (ENG-SPLIT-3, ENG-SPLIT-4). A test must cover the
   command, with a stub in place of llama.cpp.
2. Extend `packages/stx-corpus` with a pairs builder (TRN-SFT-2): a token list
   in, schema labels out, from the train splits. The dev split is a score input,
   and it must not enter a pair (TRN-SFT-3). The builder also reads the
   augmentation input of TRN-SFT-1. A test must prove that no eval-lane sentence
   and no dev-split sentence enters a pair (COR-LANES-4, TRN-SFT-3).
3. Upload the training lane and the pairs to `stx-corpus`, and the eval lane to
   `stx-evalcorpus`. The train instance and the CI jobs read the buckets.
4. Grow `infra/train`: one GPU server, the root and the scratch volumes, and one
   routed IPv4 address. A variable selects the offer. H100-1-80G is the default,
   and L40S-1-48G is the budget escape (TRN-INST, decision T3). Build the tags
   from one map in `locals.tf`, per
   [the shared tags](../../infra/CLAUDE.md#tags).
5. Add `make infra-plan`, `infra-plan-ro`, `infra-up`, `infra-down`,
   `infra-price`, `infra-status`, `infra-cost`, and `infra-watchdog` to
   `mk/local.mk`, per
   [the shared task runner](../../infra/CLAUDE.md#task-runner). `infra-up` must
   read the live price first (TRN-INST-1), and it must run the forecast check. A
   forecast must not assume a run cheaper than one hour (TRN-BUDGET-1).
   `infra-status` must check the versioning of each bucket against
   COR-BUCKETS-2, and it must fail on a mismatch. A test must cover the stop
   decision of the forecast check and the versioning check.
6. Implement the watchdog. It must destroy the train stack in two cases only.
   The cases: the stack is idle per
   [the shared idle definition](../../infra/CLAUDE.md#spend-guardrails), or the
   time passes `stx:expires`. It must report, and must not destroy, a resource
   with no `stx:managed` tag. It must not touch a resource with the
   `stx:lifecycle=persistent` tag. A test must cover the destroy decision and
   the report decision.
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
   key carries the run identifier and the step number (COR-BUCKETS-3). A test
   must cover the claim and the heartbeat of the driver.
9. Run the campaign: the CPT rehearsal, then two SFT runs — one from the base
   model, and one from the CPT output. Score both runs on the dev split with the
   tier T0 scorer. The comparison decides TRN-CPT-2. When the CPT pass does not
   move the scores, drop it, and record why (TRN-CPT-3). The first forecast
   check is the pipeline-read probe. Record its result in the runbook.
10. Merge the chosen adapter into the base model. Convert the merged model to
    GGUF at Q8_0 (decision T2). Record the model hash. Upload the artifact to
    `stx-artifacts`.
11. Run the tier T1 baseline sweep over the eval lane. The harness command
    drives the GGUF under llama.cpp: the CPU, greedy decoding, and the grammar.
    The scorecard holds UPOS, lemma, and LAS per treebank. It also holds the
    llama.cpp version, the thread count, the model hash, the UD release tag, and
    the run identifier. The sweep writes the scorecard to `stx-artifacts`
    (EVL-TIERS-1). Write each measured baseline score into
    [evaluation.md](../../spec/evaluation.md#evl-tiers) as the tier T1 threshold
    (EVL-TIERS-5).
12. Wire the gated tier T1 sweep into CI, on the CPU (EVL-TIERS-3). The job runs
    on a manual dispatch, before a promotion.
13. Write the LEARNING entries. Record the quota state and its response time
    (TRN-INST-2). Record the live price against the table. Record the stack up
    and down, the teardown completeness, and the train key delivery. Record the
    watchdog and the claim protocol. Record Axolotl in Docker, the checkpoint
    sync, the CPT decision, and the SFT scores. Map each entry to its FuguTTX
    units, per [the rehearsal index](../../spec/LEARNING.md#lrn-map).
14. Set [STATUS.md](../../spec/STATUS.md): TRN-INST, TRN-CPT, TRN-SFT, TRN-EXEC,
    TRN-BUDGET, ENG-SCHEMA, ENG-SPLIT, and COR-BUCKETS per the campaign result.
    Trim the EVL-TIERS and LRN-DELIVER notes. Set the IAC-APPLY note: it must
    name each absent part. Set the code roots of training.md, engine.md, and
    infrastructure.md.

## The lane rule

The pairs builder must take treebank pairs from the train splits only
(TRN-SFT-3). Eval data must not enter training (COR-LANES-4, decision T6). The
sweep reads the eval lane at measurement time only. A sentence, a score, or an
error sample from the eval lane must not enter a training input.

## Open questions

- The CPT branch. TRN-CPT-2 has two outcomes, and this plan cannot state the
  result before the runs. When the pass moves the scores, `make train-cpt`
  stays. When it does not, the product drops the pass, and
  [training.md](../../spec/training.md#trn-cpt) changes in the same change.
- The threshold values. EVL-TIERS-5 forbids a guess in the specification. The
  implementation writes the measured values after the baseline run, in the same
  change as the scorecard.
