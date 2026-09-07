# 008 — The training recipe

Plan 007 moves the configurations to the recipe of decision T3, bf16 with a LoRA
adapter, plus flash attention for the packing. Two recipe questions stay open.
Does a full fine-tune beat the adapter at 0.6B, and which epoch count and
learning rate fit the eval loss curve? This plan tests a bf16 full fine-tune
against the plan 007 seeds, three seeds each, and then tunes the winner. The
roadmap holds this work as phase P8.

- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: EVL-TIERS
- Defers: IAC-APPLY

## Status

The driver change and its tests can land after plan 006 merges. The `sft-full`
configuration lands after plan 007, because its base model follows the T4
result. The campaign waits on the noise floor and the tolerance of plan 007.

No decision blocks this plan. Decision T3 sets bf16 for a 0.6B model, and both
recipes of this plan are bf16.

TRN-EXEC and TRN-SFT are done. The implementation change appends one rule to
TRN-EXEC, and both units stay done. This plan therefore cites neither one under
`Implements:`, per the plans rule on a done unit.

EVL-TIERS stays partial, and this plan changes no gate. The first candidate that
passes the promote rule of plan 006 promotes through the existing verb.

## Decisions

This plan changes no decision. Decision T3 sets the precision and the adapter by
model size. A model that fits the GPU in bf16 with its optimizer states trains
in bf16, as a full fine-tune or as a bf16 adapter. Plan 007 moves the four
configurations to a bf16 adapter, and this plan adds the full fine-tune beside
them. Decision T1 keeps the 0.6B base. Decision T4 follows the result of
plan 007. The control and the full fine-tune start from the base model or from
the CPT merge, per that result.

The learning maps to FuguTTX D3. A 4B model in bf16 with a LoRA adapter fits an
80 GB card with room. QLoRA at 4B is therefore a memory decision too. The
FuguTTX change is a LRN-DELIVER-3 item.

## The reason

Three facts from the P3 and P4 run logs shaped decision T3, and two recipe
questions remain after it:

1. `trainable params: 20,185,088 || all params: 616,235,008`. A full bf16
   fine-tune of the base needs about 10 GB for the weights, the gradients, and
   the optimizer states. The card holds 80 GB. A rank-64 adapter moves about 40
   million parameters. Whether the full fine-tune beats the adapter at this size
   is an open measurement.
2. Axolotl warned at every P3 and P4 SFT start: `sample_packing` without an
   attention backend does not handle cross-sample decontamination. The run logs
   of 33204307208, 33205452689, and 33350914761 hold the warning. Plan 007 sets
   flash attention, and the warning must be absent from its logs.
3. The logged loss fell from about 2.9 to about 0.065 at the end of the first
   epoch. It reached about 0.05 at the end of the second. All three P3 and P4
   passes show it. The dev LAS stayed at 0.75 to 0.77. The model fits the pairs
   it has. The eval loss of plan 006 shows where the second epoch stops paying,
   and this plan reads it.

## The experiment card

- Hypothesis H2: the bf16 full fine-tune beats the bf16 adapter seeds of plan
  007 on dev LAS. The margin exceeds the tolerance on ewt and gum.
- Hypothesis H3: the eval loss reaches its minimum inside the second epoch, and
  a third epoch adds nothing above the tolerance.
- Prediction: H2 holds by a small margin, and H3 holds.
- Seeds: 11, 23, and 37, the seeds of plan 007. The control is the plan 007 set
  that the T4 result names, with no new run.
- Stop rule: an out-of-memory failure gets one configuration change, half the
  micro batch and double the accumulation steps, committed before the retry
  (TRN-EXEC-2). A second failure drops the recipe from the campaign. The
  dispatches stop two hours before the lease expires, and `down` runs.

## Order of work

1. Add `train/sft-full.yml`. The settings are no adapter, learning rate 0.00002,
   warmup 3 percent, and a cosine schedule. It keeps `flash_attention: true`,
   sample packing, `bf16: true`, gradient checkpointing, the seed key, and the
   eval set of plan 006. Its base model follows the T4 result of plan 007.
2. Teach the driver a run with no adapter. `cmd_merge` reads the `adapter` key
   of the configuration, and it copies the output as the merged model when the
   key is absent. The `gguf` verb of `scripts/train` then converts the merged
   model. The `sft` action of plan 006 takes the configuration name, so no list
   changes.
3. Write the card. Read the price. Dispatch `up` with a ten-hour lease.
4. Run the precision phase. For each seed, dispatch the `sft` action with
   `sft-full`, then `gguf` and `score`. Three runs.
5. Add one configuration file per tuning arm, from the winner of the precision
   phase. The arms are a three-epoch run, the learning rate at half, and the
   learning rate at double, for example `sft-full-e3.yml`,
   `sft-full-lr-half.yml`, and `sft-full-lr-double.yml`. Every configuration
   lives in the repository (TRN-EXEC-2). The eval loss curves of the precision
   phase show the two-epoch shape.
6. Run the tuning phase, three seeds per arm. Nine runs. The eval loss picks the
   epoch count, and the dev LAS picks the rate.
7. Dispatch `down`. Dispatch the tier T1 sweep on the median dev seed of the
   winner of each phase. The median seed keeps the promote interval free of a
   selection gain. Dispatch the dev sweep of plan 006 on the same seed, so the
   promote verb finds its dev copy.
8. Analyze against the control with the compare command of plan 006. Read each
   treebank and metric against the tolerance of plan 007.
9. Promote the tuned winner when it passes the promote rule of plan 006. The
   promote verb needs no instance (TRN-EXEC-5). On the drop outcome of plan 007,
   this promote carries the T4 and TRN-CPT-2 edits.
10. Update [the training document](../../spec/training.md). Append one rule to
    TRN-EXEC: the precision and the adapter of a configuration must follow
    decision T3. Add the full fine-tune to the compute budget table with its
    measured minutes. Name each configuration in the stage map of
    `train/RUNBOOK.md`. Set the TRN-EXEC note in
    [the register](../../spec/STATUS.md).
11. Write LEARNING batch 4. The claims: the peak memory and the minutes of each
    recipe. Then the paired effect of the full fine-tune against the adapter,
    with its interval. Then the eval loss curve by epoch, and the learning rate
    bracket. Add one row to [the library index](../../spec/LEARNING.md#lrn-map):
    precision and adapter at 0.6B, on the page `Library-FuguSTX-recipe`. The row
    rehearses FuguTTX D3 and FuguTTX TRN-EXEC.

## The budget

Twelve runs. A bf16 pass at 0.6B runs near the 15 minutes of the P3 pass. Each
run adds a 2-minute conversion and a 5-minute dev score with the eight slots of
plan 006. Four to six hours on the H100-1-80G: EUR 12 to 18 at the 2026-08-28
price. The ten-hour lease is the cap, and the stop rule keeps the dispatches
inside it. A forecast must not assume a run cheaper than one hour
(TRN-BUDGET-1).

## Out of scope

- The output format, and the data. Plans 009 and 010.
- A larger base model. Decision T1 stands, and the accepted cost table fixes the
  artifact near 0.6 GB.
- The L40S. A 0.6B bf16 run fits it, and the price row exists, but the plan
  keeps one offer so the numbers compare.

## Open questions

- The learning rate of the full fine-tune. 0.00002 is the starting guess, and
  the tuning phase brackets it.
- A second adapter rank. Plan 007 fixes rank 64. A rank of 128 costs one more
  run per seed, and the batch of plan 007 says whether the spread leaves room.
- The Q8_0 export of a full fine-tune. The convert path is the same, and the
  first `gguf` run confirms the tensor count.
- G2 fidelity. FuguTTX trains adapters. The batch records both recipes, so the
  FuguTTX choice has a measured pair to read.
