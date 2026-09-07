# 007 — The noise floor and the CPT decision

One campaign runs the recipe of decision T3 at 0.6B, bf16 with a LoRA adapter,
plus flash attention for the packing. It runs three seeds from the base model
and three from the CPT merge, one seed for each pair of runs. The spread across
seeds is the noise floor of the pilot. The paired difference decides TRN-CPT-2
by a rule that the experiment card states before the first dispatch. The seed
spread on the eval split sets the tolerance of the tier T1 review. The roadmap
holds this work as phase P7, with plan 006.

- Implements: EVL-TIERS without EVL-TIERS-4
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: IAC-APPLY

## Status

The configuration change can land after plan 006 merges. The campaign waits on
plan 006: the seed input, the eval loss, the per-field scorecard, and the paired
bootstrap.

No decision blocks the campaign. Decision T3 sets bf16 for a model that fits the
GPU with its optimizer states, and the four configurations of this plan follow
it. Decision T4 names a seeded, paired comparison against the noise floor as the
test of the CPT pass. TRN-CPT-3 says LEARNING records why when the product drops
the pass. This plan runs that test. The text of T4 can change after the result,
with human approval, and the Decisions section holds the wording for each
outcome.

TRN-CPT, TRN-SFT, and TRN-EXEC are done, and this plan cites none of them under
`Implements:`, per the plans rule on a done unit. The implementation change
edits the text of TRN-CPT-2 per the result and appends one rule to TRN-EXEC. The
units stay done.

EVL-TIERS stays partial. This plan implements the tolerance of EVL-TIERS-5, and
the tier T2 suite (EVL-TIERS-4) waits for phase P5.

## Decisions

Decision T3 holds, and this plan brings the configurations in line with it.
`train/cpt.yml`, `train/sft-base.yml`, `train/sft-cpt.yml`, and
`train/sft-aug.yml` load the base in 4-bit with a rank-32 adapter. A 0.6B model
fits the GPU in bf16 with its optimizer states. The four files move to bf16 with
a LoRA adapter, and the P3 recipe stays a record. The configuration of the
promoted `sft-cpt` artifact stays in the history at commit 022961a, with its
scorecard. TRN-EXEC-2 governs a run, and no run of the P3 recipe happens after
this change. Flash attention joins the configurations for the packing, and it is
a TRN-EXEC rule, not a part of T3.

The decision rule of the card has two outcomes: the pass stays, or the product
drops it. The campaign proposes one of two texts for decision T4, and the
outcome picks one. A human approves the text before the implementation change
lands. A decision describes the current state only, so neither text narrates the
campaign, and LEARNING holds the measurement.

On the drop outcome, T4 becomes: "T4 — Method: SFT from the base model.
`make train-cpt` rehearses the FuguTTX CPT verb, and its output does not enter a
promoted model. LEARNING holds the seeded measurement behind this decision."
TRN-CPT-2 then reads: the promoted model must train from the base model, not
from a CPT merge. Both edits land with the first promote that replaces
`sft-cpt`, in plan 008 or later. The specification and the promoted artifact
then agree in every change, and LEARNING holds the result until then.

On the stay outcome, T4 keeps its text, and TRN-CPT-2 keeps its text. LEARNING
records the measured effect and its interval.

No other decision changes. The seeds of this plan are the control of plan 008.

## The reason

The P3 comparison keeps the CPT pass on one run each side. The CPT pass ran 8
optimizer steps at a learning rate of 0.00002 over about 260000 tokens, so its
weight delta is near zero. The run logs of 33204307208 and 33205452689 hold the
loss lines of `sft-base` and `sft-cpt`. The first logged losses read 2.85
against 2.87, and the last 0.051 against 0.050, so the curves are near
identical. The library page records 0.187 against 0.185 for the same passes, the
`train_loss` summary values. Batch 3 records, with a verifier, that the summary
value is the mean over training. Yet `sft-cpt` scored 0.0237 LAS higher on the
ewt dev split, and it failed 47 sentences against 80. A near-zero perturbation
of the base moved the outcome by two points. That is the size of the noise, not
the size of a CPT effect. Nothing in the record separates the two readings.
Three seeds a side do.

The P3 recipe cannot run again at 0.6B. Decision T3 reserves a 4-bit load for a
model that does not fit the GPU in bf16. The seeds therefore run on the T3
recipe, and the P3 and P4 single runs stay the QLoRA reference. A single run
against a seed spread is a weaker comparison than seeds against seeds, and the
batch says so.

The tier T1 review needs the same number. A tolerance under the seed spread
blocks a real gain about as often as it admits one. A tolerance far above the
spread admits a loss.
[The misleading findings risk](../../spec/risks.md#rsk-findings) applies to the
4B target too. A run there costs hours, so the pilot fixes the method here.

## The experiment card

The observer writes the card as the first observation of the campaign in the
library, per the LRN-DELIVER rule of plan 006.

- Hypothesis H1: the CPT pass moves the dev LAS of ewt and gum by more than the
  seed spread of the base recipe.
- Prediction: no. The expected paired difference sits inside the spread.
- Seeds: 11, 23, and 37, one for each pair of runs.
- The decision rule for TRN-CPT-2: the pass stays only when two conditions hold.
  Every one of the three paired differences is positive on both treebanks. The
  mean difference exceeds two standard deviations of the base seeds on both. In
  every other case the product drops the pass.
- The tolerance rule: for each metric and treebank, two standard deviations of
  the eval-split scores across the three base seeds, rounded up to 0.001. The
  eval split covers pud, which has no dev split.
- Stop rule: a failed run repeats once. A second failure ends the campaign with
  the runs that completed, and the batch records the count. The dispatches stop
  two hours before the lease expires, and `down` runs.

## Order of work

1. Move the four configurations to the T3 recipe with flash attention. The
   settings are `load_in_4bit: false`, `adapter: lora`, `lora_r: 64`,
   `lora_alpha: 128`, `flash_attention: true`, and the seed key. The three SFT
   configurations also take the eval set of plan 006. `cpt.yml` trains a
   completion dataset on the prose lane, and it takes no eval set. Sample
   packing stays, and the first run log must show no packing warning. Replace
   the SFT row of the compute budget table with the T3 recipe in the same
   change. The P3 estimate stays in the row until step 10. Append a rule to
   TRN-EXEC. A configuration must name its attention backend, and sample packing
   must run on a packing-capable backend.
2. Write the card.
3. Read the price first (TRN-INST-1). Dispatch `up` with an eight-hour lease.
4. Dispatch `cpt` once and `merge-cpt` once. The merge is the base of the three
   CPT seeds. The CPT pass takes the seed 11 in its own configuration.
5. For each seed, dispatch the `sft` action with `sft-base`. Dispatch `gguf`,
   then `score` on the dev split. Repeat the three with `sft-cpt`. Eighteen
   dispatches. Each scorecard carries its seed and label, for example
   `sft-cpt-s23`.
6. Dispatch `down`. The remaining steps need no instance.
7. Dispatch the tier T1 sweep on each of the six GGUF files, on the eval split.
   Dispatch the dev sweep of plan 006 on the same six. The per-field card and
   the failure kinds then exist on the CPU pins too.
8. Analyze. For each treebank, metric, and split: the six scores, and the mean
   and the standard deviation per side. Then the three paired differences, and
   the interval of each pair from the compare command of plan 006. Compare the
   P3 and P4 single-run scorecards against the seed spread of the T3 recipe, as
   the QLoRA reference. Compare the eight-slot GPU dev card and the CPU dev card
   of one GGUF. That is the numerics question of plan 006.
9. Apply the tolerance rule. Write the tolerance column into the tier T1 table
   of [the evaluation document](../../spec/evaluation.md). The promote rule of
   plan 006 reads the tolerance from that table.
10. Apply the decision rule. Propose the T4 text to the user. On approval, the
    edit of T4 and TRN-CPT-2 waits for the first promote that replaces
    `sft-cpt`. That change sets the TRN-CPT note in
    [the register](../../spec/STATUS.md). On the drop outcome, point
    `train/sft-aug.yml` at the base model. `train/sft-cpt.yml` leaves with the
    T4 edit, in the change that promotes a model from the base. Edit the TRN-SFT
    prose that says the SFT pass follows the CPT rehearsal. Set the TRN-SFT
    note. Set the TRN-EXEC note for the attention rule. Put the measured minutes
    into the SFT row of the compute budget table. Name the recipe in the stage
    map of `train/RUNBOOK.md`.
11. Write LEARNING batch 3. The claims: the seed spread per metric, treebank,
    and split, and the paired CPT effect with its interval. Then the QLoRA
    reference comparison, the failure kinds, the per-field rates, and the GPU
    against CPU dev difference. Each numeric claim meets the verifier
    (LRN-DELIVER-8). Add one row to
    [the library index](../../spec/LEARNING.md#lrn-map): seeded replication and
    the noise floor, on the page `Library-FuguSTX-noise-floor`. The row
    rehearses FuguTTX D4 and the FuguTTX evaluation specification. The scope
    note says what the 0.6B spread predicts about 4B: the method, not the
    number.
12. Promote nothing. The tolerance and the interval exist after this plan, and
    plan 008 runs the first candidate through them.

## The budget

Six SFT runs, six conversions, and six dev scores, plus the CPT pass, the merge,
the up, and the down. A bf16 adapter pass at 0.6B runs near the 15 minutes of
the P3 pass. A conversion takes about 2 minutes, and a dev score about 5 minutes
with the eight slots of plan 006. Three to five hours on the H100-1-80G at EUR
2.8665 per hour, read 2026-08-28: EUR 9 to 15. The eight-hour lease is the cap,
not the estimate, and the stop rule keeps the dispatches inside it. A forecast
must not assume a run cheaper than one hour (TRN-BUDGET-1). The tier T1 sweeps
and the dev sweeps run on CI runners.

## Out of scope

- The full fine-tune, the output format, and the data. Plans 008 to 010.
- A run of `sft-aug`. The configuration moves to the T3 recipe with the others,
  and no run uses it here. The 111 records are half a percent of the pairs, and
  the plan measures noise, not augmentation.
- A promote.

## Open questions

- Three seeds or five. Five seeds give a better spread at about EUR 6 more, and
  the card fixes the count before dispatch.
- The CPT pass under a seed. The pass is deterministic under one seed, and its
  delta is near zero, so one merge serves all three CPT seeds. A reader who
  wants the CPT seed spread adds two passes and two merges, at about ten
  minutes.
- The tolerance shape. Two standard deviations of three samples is a rough
  estimate. The paired bootstrap interval is the finer instrument, and the
  review reads both.
- The adapter rank. 64 is the guess for bf16. Plan 008 can test a second rank.
