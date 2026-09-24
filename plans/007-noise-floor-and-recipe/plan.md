# 007 — The noise floor, the CPT decision, and the recipe

One campaign after phase P12 runs the recipe of decision T3: bf16 with a LoRA
adapter, plus flash attention for the packing. It runs three seeds per arm. The
spread across the seeds is the noise floor of the pilot. The paired difference
of three seeds from the base and three from the CPT merge decides TRN-CPT-2.
Then the full fine-tune runs against the adapter, and the epoch count and the
learning rate follow. The comparison point of every arm is the zero-training
baseline of EVL-TIERS-9. The seed spread on the eval split sets the tolerance of
the tier T1 review. The roadmap holds this work as phase P7, with plan 006.

- Implements: TRN-CPT
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Extends: TRN-EXEC
- Defers: EVL-TIERS
- Defers: TRN-SFT
- Defers: IAC-APPLY

## Status

Step 1 lands after package 1 of plan 006: a configuration change with no
training run. It moves every configuration to the recipe of decision T3 before
phase P12. The first SFT campaign on the pair corpus then runs that recipe. Plan
006 edits the same files: its package 1 adds the `seed` key, and its package 3
adds the eval set. Step 1 changes the precision, the adapter, and the attention
backend. It also appends the rule that binds every configuration to decision T3.
`train/sft-aug.yml` loads the base in 4-bit, and it leaves `train/` under
package 1 of plan 006. Step 1 therefore waits on that package, and this plan
does not change the file. Every other step waits on phase P11, the pair corpus,
and on phase P12, the first SFT campaign on it. The campaign also waits on the
instruments of plan 006: the seed input, the eval loss, the scorecard counts,
and the paired bootstrap.

No decision blocks the campaign. Decision T3 sets bf16 for a model that fits the
GPU with its optimizer states, and every configuration of this plan follows it.
Decision T4 names a seeded, paired comparison against the noise floor as the
test of the CPT pass. This plan runs that test. Decision T13 names the
zero-training baseline as the comparison point, and each arm of this plan pairs
against it.

TRN-CPT is open. The campaign runs the pass on the prose lane (TRN-CPT-1),
applies the drop rule (TRN-CPT-2), and records the reason (TRN-CPT-3).

TRN-EXEC is done, and the implementation appends two rules to it. A
configuration must name its attention backend, and sample packing must run on a
packing-capable backend. The precision and the adapter of a configuration must
follow decision T3. The unit stays done, so this plan cites it under `Extends:`.

TRN-SFT is open, and phase P12 lands its rules. This plan adds SFT
configurations and runs SFT passes, and it implements no rule of the unit.

EVL-TIERS stays partial. This plan reads the scorecards and writes the measured
tolerance beside the thresholds of the evaluation document. It implements no
rule of the unit, and the tier T2 suite (EVL-TIERS-4) waits for phase P5.

IAC-APPLY stays partial. The campaign dispatches the train stack, and it
implements no rule of the unit.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. A FuguTTX plan
lands each change.

## Decisions

Decision T3 holds, and this plan brings the configurations in line with it.
`train/cpt.yml`, `train/sft-base.yml`, and `train/sft-cpt.yml` load the base in
4-bit with a rank-32 adapter. A 0.6B model fits the GPU in bf16 with its
optimizer states. The three files move to bf16 with a LoRA adapter, and the full
fine-tune joins them as `train/sft-full.yml`. Flash attention joins the
configurations for the packing, and it is a TRN-EXEC rule, not a part of T3.

The decision rule of the card has two outcomes: the pass stays, or the product
drops it. Decision T4 holds both outcomes, so no decision text changes. On the
drop outcome, the change that records the result removes `train/sft-cpt.yml`.
The SFT arms of the recipe then start from the base model. It also edits the
TRN-SFT prose that says the SFT pass follows the CPT rehearsal, and it sets the
TRN-CPT note. On the stay outcome, `train/sft-cpt.yml` stays, and the SFT arms
start from the CPT merge. LEARNING records the measured effect and its interval
in both cases (TRN-CPT-3).

The learning maps to FuguTTX D3. A 4B model in bf16 with a LoRA adapter fits an
80 GB card with room. QLoRA at 4B is therefore a memory decision too. The
FuguTTX change is a LRN-DELIVER-3 item.

No other decision changes.

## The reason

Three seeds a side separate an effect from a re-run difference, and one run a
side cannot. The CPT pass runs one epoch at a low learning rate (TRN-CPT-1), so
its weight delta is small. A small perturbation of the base moves a score by an
amount that only a seed spread can bound. Nothing in a single run separates that
movement from a CPT effect.

The tier T1 review needs the same number. A tolerance under the seed spread
blocks a real gain about as often as it admits one. A tolerance far above the
spread admits a loss.
[The misleading findings risk](../../spec/risks.md#rsk-findings) applies to the
4B target too. A run there costs hours, so the pilot fixes the method here.

Two recipe questions stay open after the noise floor. Does a full fine-tune beat
the adapter at 0.6B, and which epoch count and learning rate fit the eval loss
curve? A full bf16 fine-tune of the base needs about 10 GB for the weights, the
gradients, and the optimizer states. The card holds 80 GB. A rank-64 adapter
moves about 40 million parameters, and whether the full fine-tune beats it at
this size is an open measurement. The eval loss of plan 006 shows where the
second epoch stops paying, and this plan reads it. Axolotl warns at each start
of a packed run without an attention backend. The run logs of this campaign must
hold no such warning.

## The experiment card

The observer writes the card as the first observation of the campaign in the
library, per the LRN-DELIVER rule of plan 006. It states each decision rule
before the first dispatch.

- Hypothesis H1: the CPT pass moves the dev balanced accuracy by more than the
  seed spread of the base recipe.
- Prediction: no. The expected paired difference sits inside the spread.
- Hypothesis H2: the bf16 full fine-tune beats the bf16 adapter on dev balanced
  accuracy, by more than the tolerance.
- Hypothesis H3: the eval loss reaches its minimum inside the second epoch, and
  a third epoch adds nothing above the tolerance.
- Prediction: H2 holds by a small margin, and H3 holds.
- Seeds: 11, 23, and 37, one for each arm.
- The comparison point: the zero-training baseline scorecard of phase P11
  (EVL-TIERS-9), through the paired bootstrap of plan 006.
- The decision rule for TRN-CPT-2: the pass stays only when three conditions
  hold. Every one of the three paired differences on the dev split improves
  balanced accuracy and category agreement. None of the three raises the
  false-positive rate of the tier T1 sweep on the eval split. The mean
  difference exceeds two standard deviations of the base seeds on both. In every
  other case the product drops the pass.
- The recipe rule: the full fine-tune wins when its paired interval against the
  adapter seeds lies above zero on balanced accuracy. The eval loss picks the
  epoch count, and the dev balanced accuracy picks the learning rate.
- The tolerance rule: for each metric, two standard deviations of the eval-split
  scores across the three base seeds, rounded up to 0.001.
- Stop rule: a failed run repeats once. A second failure ends the campaign with
  the runs that completed, and the batch records the count. An out-of-memory
  failure gets one configuration change: half the micro batch and double the
  accumulation steps, landed before the retry (TRN-EXEC-2). The dispatches stop
  two hours before the lease expires, and `down` runs.

## Order of work

1. Move the configurations to the T3 recipe with flash attention. Lands after
   package 1 of plan 006. The settings are `load_in_4bit: false`,
   `adapter: lora`, `lora_r: 64`, `lora_alpha: 128`, and
   `flash_attention: true`. `cpt.yml` keeps its completion dataset, and it takes
   no eval set. Sample packing stays. Add `train/sft-full.yml` as a copy of
   `train/sft-base.yml`. It takes no adapter, learning rate 0.00002, warmup 3
   percent, and a cosine schedule. Replace the SFT row of the compute budget
   table with the T3 recipe. Add a row for the full fine-tune. Append two rules
   to TRN-EXEC. A configuration must name its attention backend, and sample
   packing must run on a packing-capable backend. The precision and the adapter
   of a configuration must follow decision T3.
2. Teach the driver a run with no adapter. `cmd_merge` reads the `adapter` key
   of the configuration, and it copies the output as the merged model when the
   key is absent. The `gguf` verb of `scripts/train` then converts the merged
   model. The `sft` action of plan 006 takes the configuration name, so no list
   changes.
3. Write the card. Read the price first (TRN-INST-1). Dispatch `up` with an
   eight-hour lease.
4. Dispatch `cpt` once and `merge-cpt` once. The run log must show no packing
   warning. The merge is the base of the three CPT seeds. The CPT pass takes the
   seed 11 in its own configuration.
5. For each seed, dispatch the `sft` action with `sft-base`, then `gguf`, then
   `score` on the dev split. Repeat the three with `sft-cpt`. Eighteen
   dispatches. Each scorecard carries its seed and label, for example
   `sft-cpt-s23`.
6. Dispatch `down`. Dispatch the tier T1 sweep on each of the six GGUF files, on
   the eval split. Dispatch the dev sweep of plan 006 on the same six. The
   counts and the failure kinds then exist on the CPU pins too.
7. Analyze the noise floor. For each metric and split: the six scores, and the
   mean and the standard deviation per side. Then the three paired differences,
   and the interval of each pair against the baseline, from the compare command
   of plan 006. Compare the eight-slot GPU dev card and the CPU dev card of one
   GGUF. That is the numerics question of plan 006.
8. Apply the tolerance rule. Write the tolerance beside the tier T1 thresholds
   of [the evaluation document](../../spec/evaluation.md). The promotion review
   reads it by hand, and no job reads it (EVL-TIERS-7).
9. Apply the decision rule. On the drop outcome, remove `train/sft-cpt.yml`,
   edit the TRN-SFT prose, and set the TRN-CPT note. On the stay outcome, set
   the TRN-CPT note with the measured effect. In both cases, LEARNING records
   why (TRN-CPT-3), and the SFT arms of step 10 take the start point of the
   outcome.
10. Run the precision phase. Read the price, and dispatch `up` with a ten-hour
    lease. For each seed, dispatch the `sft` action with `sft-full`, then `gguf`
    and `score`. Three runs. The control is the seed set of the outcome of step
    9, with no new run.
11. Add one configuration file per tuning arm, from the winner of the precision
    phase. The arms are a three-epoch run, the learning rate at half, and the
    learning rate at double, for example `sft-full-e3.yml`,
    `sft-full-lr-half.yml`, and `sft-full-lr-double.yml`. Every configuration
    lives in the repository (TRN-EXEC-2). The eval loss curves of the precision
    phase show the two-epoch shape.
12. Run the tuning phase, three seeds per arm. Nine runs. The eval loss picks
    the epoch count, and the dev balanced accuracy picks the rate.
13. Dispatch `down`. Dispatch the tier T1 sweep on the median dev seed of the
    winner of each phase. The median seed keeps the interval free of a selection
    gain. Dispatch the dev sweep of plan 006 on the same seed.
14. Analyze the recipe. Read each arm against the baseline and against the
    control, with the compare command of plan 006. Read each metric against the
    tolerance of step 8.
15. Promote the tuned winner when its tier T1 scorecard clears the bar of
    EVL-TIERS-10 and the promotion review admits it. The promote verb needs no
    instance (TRN-EXEC-5). Below the bar, the operator decides, and LEARNING
    records why (decision T13).
16. Update [the training document](../../spec/training.md). Put the measured
    minutes of each recipe into the compute budget table. Name each
    configuration in the stage map of `train/RUNBOOK.md`. Set the TRN-EXEC note
    for the two rules, and set the TRN-CPT note in
    [the register](../../spec/STATUS.md).
17. Write the LEARNING batch. The claims: the seed spread per metric and split,
    and the paired CPT effect with its interval. Then the peak memory and the
    minutes of each recipe, and the paired effect of the full fine-tune against
    the adapter. Then the eval loss curve by epoch, and the learning rate
    bracket. Then the failure kinds, the per-category counts, and the GPU
    against CPU dev difference. Each numeric claim meets the verifier
    (LRN-DELIVER-8). Add two rows to
    [the library index](../../spec/LEARNING.md#lrn-map). One row is seeded
    replication and the noise floor, on the page `Library-FuguSTX-noise-floor`.
    The other row is precision and adapter at 0.6B, on the page
    `Library-FuguSTX-recipe`. The rows rehearse FuguTTX D3, FuguTTX D4, FuguTTX
    TRN-EXEC, and the FuguTTX evaluation specification. The scope note says what
    the 0.6B spread predicts about 4B: the method, not the number.

## The budget

The noise floor lease holds six SFT runs, six conversions, and six dev scores,
plus the CPT pass and the merge. The recipe lease holds twelve SFT runs with
their conversions and dev scores. A bf16 adapter pass at 0.6B ran near 15
minutes on the retired corpus, and the phase P12 record replaces that number. A
conversion takes about 2 minutes, and a dev score about 5 minutes with the eight
slots of plan 006. Seven to eleven hours on the H100-1-80G at EUR 2.8665 per
hour, read 2026-08-28: EUR 20 to 32. The two leases are the cap, not the
estimate, and the stop rule keeps the dispatches inside them. A forecast must
not assume a run cheaper than one hour (TRN-BUDGET-1). The tier T1 sweeps and
the dev sweeps run on CI runners.

## Out of scope

- The output format, and the data. Phase P11 holds the data, and the finding
  schema holds the format.
- A larger base model. Decision T1 stands, and the accepted cost table fixes the
  artifact near 0.6 GB.
- The L40S. A 0.6B bf16 run fits it, and the price row exists, but the plan
  keeps one offer so the numbers compare.
- A second adapter rank. Rank 64 is the guess for bf16, and the batch says
  whether the spread leaves room for a rank-128 arm.

## Open questions

- Three seeds or five. Five seeds give a better spread at about EUR 6 more per
  arm, and the card fixes the count before dispatch.
- The CPT pass under a seed. The pass is deterministic under one seed, and its
  delta is small, so one merge serves all three CPT seeds. A reader who wants
  the CPT seed spread adds two passes and two merges, at about ten minutes.
- The tolerance shape. Two standard deviations of three samples is a rough
  estimate. The paired bootstrap interval is the finer instrument, and the
  review reads both.
- The learning rate of the full fine-tune. 0.00002 is the starting guess, and
  the tuning phase brackets it.
- The Q8_0 export of a full fine-tune. The convert path is the same, and the
  first `gguf` run confirms the tensor count.
- G2 fidelity. FuguTTX trains adapters. The batch records both recipes, so the
  FuguTTX choice has a measured pair to read.
