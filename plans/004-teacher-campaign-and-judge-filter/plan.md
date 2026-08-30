# 004 — The teacher campaign and the judge filter

This plan lands phase P4 of [the roadmap](../../spec/ROADMAP.md): the teacher
proposes, and a verifier disposes ([T5](../../spec/DECISIONS.md#t5)).

- Implements: TRN-TEACH
- Implements: COR-AUG
- Implements: ENG-LEXICON without ENG-LEXICON-2
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: EVL-TIERS
- Defers: IAC-APPLY

## Status

The generation client, the judge filter, the lexicon, and the CI wiring can land
now. No decision blocks this plan. Decisions [T2](../../spec/DECISIONS.md#t2),
[T5](../../spec/DECISIONS.md#t5), and [T6](../../spec/DECISIONS.md#t6) shape it.

The campaign runs on the existing train stack, with the current CI secrets. The
secrets move in [the runbook](../../infra/persistent/RUNBOOK.md) is a human
step, and it blocks nothing here.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. This plan
excludes both: a FuguTTX plan lands each change.

ENG-LEXICON-2 marks the dictionary status in the engine output. The engine
arrives in phase P6, so this plan excludes that rule. The filter needs
ENG-LEXICON-1 only.

EVL-TIERS stays partial. The campaign runs the tier T1 sweep as a measurement,
and the tier T2 suite (EVL-TIERS-4) waits for phase P5.

IAC-APPLY stays partial. This plan adds the teach actions to the existing
dispatch job. Every other absent IAC-APPLY item waits for a later plan.

## Order of work

1. Pin the teacher in `train/config.env`: a `VLLM_IMAGE` tag and a
   `TEACHER_MODEL` name, each from a dated read (decision T5). The open
   questions hold the precision choice.
2. Build the lexicon from the training lane: each word, with its observed UPOS
   set (ENG-LEXICON-1). The build lands in `packages/stx-corpus`, and the
   committed file lands in `share/`. Record the lexicon source in
   [engine.md](../../spec/engine.md#eng-lexicon) in the same change.
3. Add the generation client to `packages/stx-corpus`. The client prompts the
   teacher for technical and instructional sentences. It runs two annotation
   passes for each sentence, against the localhost endpoint.
4. Add the judge filter to `packages/stx-corpus` (TRN-TEACH-4). Check 1: the two
   passes agree. Check 2: the tree has one root, fully connected. Check 3: every
   tag is in the inventory of `share/annotation.gbnf`, and the lexicon check
   passes. The filter must log each rejected record with its reason
   (TRN-TEACH-5). An accepted record takes the lane JSONL shape, with a
   provenance tag (COR-AUG-2). A test covers an accept and each reject reason.
5. Add the transport verbs to `scripts/train`. `teach-serve` starts vLLM on the
   instance, in Docker, bound to 127.0.0.1 (TRN-TEACH-1, TRN-TEACH-2). `teach`
   opens an SSH tunnel with keepalives, runs the client and the filter, and
   uploads the outputs (TRN-TEACH-3). The NAT entry of
   [the LEARNING](../../spec/LEARNING.md#lrn-entries) forces the keepalives. Add
   `make train-teach`, and add both actions to the `train.yml` choice list.
6. Upload the accepted records, the reject log, and the rate report under one
   run prefix in `stx-corpus`. The accepted file is the `--augmentation` input
   of the pairs builder (COR-AUG-1), and the reader exists.
7. Add `train/sft-aug.yml`: the SFT pass from the CPT merge, on the treebank
   pairs plus the accepted records (TRN-SFT-1). Add `sft-aug` to the `train.yml`
   and `t1.yml` choice lists. The `t1.yml` `name` input is a fixed choice list,
   so `sft-aug` needs the list change.
8. Run the campaign: up, teach-serve, teach, sft-aug, gguf, score, the tier T1
   sweep, down. Compare the scorecard against
   [the thresholds](../../spec/evaluation.md#evl-tiers) by hand. Promote only on
   a pass, and the promote verb needs no instance. A sweep below a threshold
   blocks the promote step only: the batch still lands.
9. Write LEARNING batch 2: the filter design, the agreement rate, the rejection
   rates, the vLLM serve facts, and the tunnel behavior (TRN-TEACH-6). Each
   numeric claim meets the verifier (LRN-DELIVER-8). The library page is
   `Library-FuguSTX-teacher-augmentation`, per
   [the map](../../spec/LEARNING.md#lrn-map).
10. Set [STATUS.md](../../spec/STATUS.md): TRN-TEACH and COR-AUG per the
    campaign result, and ENG-LEXICON partial, with ENG-LEXICON-2 named absent.
    Trim the LRN-DELIVER note.

## The filter gate

A record enters the training lane only through the filter (COR-AUG-1). The eval
lane stays out of the campaign (COR-LANES-4): a few-shot example in a teacher
prompt must come from the train splits only. No eval sentence, no eval score
sample, and no eval error sample can enter a prompt or a pair.

## The budget

The teacher row of [the compute budget](../../spec/training.md#trn-budget)
prices the campaign at 5–15 GPU-hours (EUR 14–43). The augmented SFT pass adds
one run (EUR 3–6). A forecast must not assume a run cheaper than one hour
(TRN-BUDGET-1).

## Open questions

- The teacher precision. Qwen3-32B at BF16 holds near 65 GB of weights, so the
  KV cache gets thin headroom on 80 GB. The official FP8 checkpoint is the
  default choice. The first serve confirms the fit, before generation at scale.
- The independence of check 1. Greedy decoding twice returns one output, and the
  agreement check measures nothing. The implementation sets the sampling of the
  two passes, and LEARNING records the choice (TRN-TEACH-6).
- The acceptance volume. No target count exists for the accepted records. The
  campaign measures the acceptance rate first, and the budget bounds the spend.
- The client dictionary. The ASD-STE100 dictionary carries a license, and
  [LIC-LIC](../../spec/licensing.md#lic-lic) stays open. The filter lexicon
  derives from the training lane, and phase P6 decides the client dictionary.
