# 004 — The teacher campaign and the judge filter

This plan lands phase P4 of [the roadmap](../../spec/ROADMAP.md): the teacher
proposes, and a verifier disposes ([T5](../../spec/DECISIONS.md#t5)).

- Implements: TRN-TEACH
- Implements: COR-AUG
- Implements: LIC-LIC
- Implements: LIC-RELEASE without LIC-RELEASE-1 without LIC-RELEASE-2 without
  LIC-RELEASE-4
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: ENG-LEXICON
- Defers: EVL-TIERS
- Defers: IAC-APPLY

## Status

The generation client, the judge filter, the word table, and the CI wiring can
land now. No decision blocks this plan. Decisions
[T2](../../spec/DECISIONS.md#t2), [T5](../../spec/DECISIONS.md#t5), and
[T6](../../spec/DECISIONS.md#t6) shape it.

The campaign runs on the existing train stack, with the current CI secrets.
[The runbook](../../infra/persistent/RUNBOOK.md) holds one human step, the move
of the CI secrets, and that step blocks nothing here.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. This plan
excludes both: a FuguTTX plan lands each change.

The filter needs a lexicon input for its check 3. The plan builds an interim
word table from the train splits, and the table is not the approved dictionary
of ENG-LEXICON-1. The unit stays open, so this plan defers it. Step 4 amends
check 3 of training.md, so TRN-TEACH stays fully implementable here. Phase P6
decides the client dictionary. Step 2 adds the licensing row of the table, and
step 10 sets the LIC-LIC state.

TRN-SFT and TRN-EXEC are done, and both rows stay done, so the citation block
excludes both, per [the transient rule](../CLAUDE.md). Step 10 refreshes both
notes. The `sft-aug` pass runs through the existing `make train-sft`: the
`SFT_FROM` variable selects the start point, and `train/sft-aug.yml` is one more
run configuration (TRN-EXEC-2). The accepted records reach the pass through the
existing reader (TRN-SFT-1). The teach verbs follow the `gguf` and `promote`
pattern: `scripts/train` verbs with no make target, outside the training runs of
TRN-EXEC-3.

EVL-TIERS stays partial. The campaign runs the tier T1 sweep as a measurement,
and the tier T2 suite (EVL-TIERS-4) waits for phase P5.

IAC-APPLY stays partial. This plan adds the teach actions to the existing
dispatch job. Every other absent IAC-APPLY item waits for a later plan.

## Order of work

1. Pin the teacher in `train/config.env`: a `VLLM_IMAGE` tag and a
   `TEACHER_MODEL` name, each from a dated read (decision T5). The open
   questions hold the precision choice.
2. Build the interim word table from the train splits: each word, with its
   observed UPOS set. The dev split is a score input, and it must not shape the
   table. The committed table and its builder land in `packages/stx-corpus`, and
   a test covers the builder. The test proves that no dev-split entry shapes the
   table. Add the table row to [licensing.md](../../spec/licensing.md#lic-lic)
   with its treebank attribution, in the same change. The engine lexicon of
   [ENG-LEXICON](../../spec/engine.md#eng-lexicon) waits for phase P6.
3. Add the generation client to `packages/stx-corpus`. The client prompts the
   teacher for technical and instructional sentences. It runs two annotation
   passes for each sentence, against the localhost endpoint. A test runs the
   client against a stub endpoint. The test proves that no eval-lane and no
   dev-split sentence enters a prompt.
4. Add the judge filter to `packages/stx-corpus` (TRN-TEACH-4). Check 1: the two
   passes agree. Check 2: the tree has one root, fully connected. Check 3: every
   tag is in the inventory of `share/annotation.gbnf`, and the word-table check
   passes. The filter must log each rejected record with its reason
   (TRN-TEACH-5). An accepted record takes the lane JSONL shape, with a
   provenance tag (COR-AUG-2). A test covers an accept and each reject reason.
   The word-table check constrains a known word only: a known word must carry an
   allowed UPOS, and an unknown word passes. Amend the judge-filter prose of
   [training.md](../../spec/training.md#trn-teach) in the same change: check 3
   runs on the word table. The amendment names the table source and the
   known-word rule. Record the prompt rule there too: a few-shot example comes
   from the train splits only.
5. Add the transport verbs to `scripts/train`. `teach-serve` starts vLLM on the
   instance, in Docker, bound to 127.0.0.1 (TRN-TEACH-1, TRN-TEACH-2).
   `teach-stop` stops the container, and it must run before a training pass: the
   teacher holds the GPU memory that Axolotl needs. `teach` opens an SSH tunnel
   with keepalives, runs the client and the filter, and uploads the outputs
   (TRN-TEACH-3). The `teach` verb claims the stack, and it writes the
   heartbeat, as the train driver does: the watchdog destroys a stack with a
   stale heartbeat. The keepalives follow the library page
   `Library-FuguSTX-ssh-delivery`: the runner NAT kills a quiet SSH stream. The
   `teach` verb runs one bounded batch for each dispatch, under the six-hour job
   limit. A run prefix makes the batches resumable. The verbs follow the `gguf`
   pattern: no make target. Amend TRN-TEACH-3 in the same change: the generation
   client reaches the endpoint over the tunnel. Add the three actions to the
   `train.yml` choice list. Update the stage map of `train/RUNBOOK.md` in the
   same change. `t/train.t` covers the new verbs.
6. Upload the accepted records to `stx-corpus`, under a run prefix. Upload the
   reject log and the rate report to `stx-artifacts`, under the same prefix. A
   rejected record must not reach the corpus bucket (COR-AUG-1). Rebuild the
   pairs with the `--augmentation` input; the reader exists. Upload the
   augmented pairs to `stx-corpus`. Add the licensing row of the accepted
   records, with the teacher license, in the same change.
7. Add `train/sft-aug.yml`: the SFT pass from the merged CPT base, on the
   treebank pairs plus the accepted records (TRN-SFT-1). Add the `sft-aug` verb
   to `scripts/train`, its driver step, and its job step in `train.yml`. The job
   runs `make train-sft SFT_FROM=aug`, per TRN-EXEC-3. Add `sft-aug` to the
   `action` list, each `train.yml` `name` list, and the `t1.yml` list. Extend
   `t1.yml`: the sweep must read a candidate GGUF from `stx-checkpoints`, so it
   runs before a promote. Update the stage map of `train/RUNBOOK.md` in the same
   change. `t/train.t` covers the new verb.
8. Run the campaign: up, teach-serve, teach, teach-stop, cpt, merge-cpt,
   sft-aug, gguf, score, down. The `sft-aug` pass needs the merged CPT base on
   the instance, and no verb restores it, so the campaign re-runs `cpt` and
   `merge-cpt`. Run the tier T1 sweep after the down: the sweep needs no
   instance. Compare the scorecard against
   [the thresholds](../../spec/evaluation.md#evl-tiers) by hand. Promote only on
   a pass, and the promote verb needs no instance. A sweep below a threshold
   blocks the promote step only: the batch still lands.
9. Write LEARNING batch 2: the filter design, the rates, the vLLM serve facts,
   and the tunnel behavior (TRN-TEACH-6). A claim that names a number, a cause,
   or a platform behavior meets the verifier (LRN-DELIVER-8). The library page
   is `Library-FuguSTX-teacher-augmentation`, per
   [the map](../../spec/LEARNING.md#lrn-map).
10. Split the [STATUS.md](../../spec/STATUS.md) updates across the two changes.
    The change of steps 1 to 7 sets LIC-LIC and LIC-RELEASE, and it refreshes
    the TRN-EXEC, TRN-SFT, and EVL-TIERS notes. The closing change sets
    TRN-TEACH and COR-AUG per the campaign result, and it trims the LRN-DELIVER
    note.

## The filter gate

A record enters the training lane only through the filter (COR-AUG-1). The eval
lane stays out of the campaign (COR-LANES-4): a few-shot example in a teacher
prompt must come from the train splits only. An eval sentence, an eval score
sample, or an eval error sample must not enter a prompt or a pair.

## The budget

The teacher row of [the compute budget](../../spec/training.md#trn-budget)
prices the campaign at 5–15 GPU-hours (EUR 14–43). The augmented SFT pass adds
one run (EUR 3–6). A CPT re-run, when the merged base is absent, adds one more
(EUR 3–6). A forecast must not assume a run cheaper than one hour
(TRN-BUDGET-1).

## Open questions

- The teacher precision. Qwen3-32B at BF16 holds near 65 GB of weights, so the
  KV cache gets thin headroom on 80 GB. The official FP8 checkpoint is the
  default choice. The first serve confirms the fit, before generation at scale.
  The implementation records the served checkpoint in training.md, in the same
  change.
- The independence of check 1. Greedy decoding twice returns one output, and the
  agreement check measures nothing. The implementation sets the sampling of the
  two passes, and it records the choice in training.md, in the same change.
  LEARNING records the measured effect (TRN-TEACH-6).
- The acceptance volume. No target count exists for the accepted records. The
  campaign measures the acceptance rate first, and the budget bounds the spend.
- The client dictionary. The ASD-STE100 dictionary carries a license, and the
  [licensing table](../../spec/licensing.md#lic-lic) holds no row for it yet.
  The filter table derives from the train splits, and phase P6 decides the
  client dictionary.
