# 012 — The first SFT campaign on the pair corpus

This plan trains the first model on the admitted pairs of phase P11, and it
lands `stx analyze` on the generated grammar. It writes the tier T0 score script
and the tier T1 sweep anew on that verb. The script runs on the dev split. The
sweep runs on the eval lane, against the tier T1 thresholds of EVL-TIERS-5 and
the bar of EVL-TIERS-10. Phase P11 sets the bar and two thresholds after its
baseline run, and this plan sets the category-agreement threshold. The bar then
decides the pilot, per decision T13. The roadmap holds this work as phase P12.

- Implements: TRN-SFT
- Implements: ENG-IFACE without ENG-IFACE-2
- Implements: ENG-DETERM
- Implements: ENG-CONTRACT
- Implements: EVL-TIERS without EVL-TIERS-1 without EVL-TIERS-4 without
  EVL-TIERS-7 without EVL-TIERS-8 without EVL-TIERS-9 without EVL-TIERS-10
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: TRN-CPT
- Defers: TRN-TEACH
- Defers: IAC-APPLY
- Defers: EVL-SUITE

## Status

Every package waits on plan 011. Package 1 waits on its package 6, the lanes.
Package 2 waits on package 1 and on the train stack apply. Package 3 waits on
plan 011 package 2, the grammar, and it can land with a fixture model before the
pairs exist. Packages 4 to 6 wait in order, and package 6 waits on the operator.
Plan 007 step 1 lands before this plan, and it moves every configuration to the
recipe of decision T3. Package 2 runs that recipe. The other steps of plan 007
wait on this plan. Plan 006 lands the instruments of the scorecard. They are the
seed, the eval loss, the confusion counts, the failure kinds, the per-segment
file, and the paired bootstrap. This plan lands the metrics of the same
scorecard. The roadmap holds this plan as phase P12.

Plan 011 packages 2 and 3 remove the treebank pipeline, and each package names
the files that leave. Among them are the `label` verb of `bin/stx`, `pairs.py`,
`score.py`, `t0.py`, the sweep of `t1.py`, and the workflow `t1.yml`. From plan
011 package 2 to this plan, `bin/stx` holds the `segment` verb only. `t1.py`
holds the scorecard record, the key form, the aggregate, and the hash. Packages
1, 4, and 5 write the pairs builder, the score script, and the sweep anew on
`stx analyze`. They change no old module.

TRN-SFT is open. This plan lands TRN-SFT-1 and TRN-SFT-2, the admitted pairs as
the input and the segments-in, findings-out format. It lands TRN-SFT-3, the
train-split rule: the dev split enters no pair.

ENG-IFACE, ENG-DETERM, and ENG-CONTRACT are open. This plan lands `stx analyze`
(ENG-IFACE-1), and the offsets and the model hash on each record (ENG-DETERM-1).
It lands the same-bytes guarantee (ENG-DETERM-2), and the engine-independent
output (ENG-CONTRACT-1, ENG-CONTRACT-2). The daemon of ENG-IFACE-2 waits.

EVL-TIERS stays partial. This plan lands the two dev metrics of EVL-TIERS-2 from
the confusion counts of EVL-TIERS-6. It lands the tier T1 sweep on the eval
lane, with the false-positive rate on the later-era human-only set
(EVL-TIERS-3). The old score script and the old sweep scored a treebank, and
they leave in plan 011. This plan writes both anew on the `analyze` output and
the eval lane. After the baseline run of plan 011, the operator sets the bar
(EVL-TIERS-10) and two tier T1 thresholds. Those are balanced accuracy and the
false-positive rate, the two numbers that the baseline yields. Plan 011 package
8 writes them, and this plan runs against them. The baseline gives no category,
so it yields no category-agreement threshold. EVL-TIERS-5 lands here for that
threshold only. The operator sets it from the first scorecard with categories,
and package 6 writes it. The tier T2 suite of EVL-TIERS-4 waits for phase P5.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. A FuguTTX plan
lands each change.

TRN-CPT is open. Plan 007 decides the CPT pass, and this plan starts from the
base model. TRN-TEACH is the judge of plan 011. This plan runs no generator and
no judge, and it reads the admitted pairs. IAC-APPLY stays partial. The campaign
dispatches the train stack, and this plan implements no rule of the unit.
EVL-SUITE is open, and phase P5 holds it.

TRN-EXEC is done, and this plan changes no rule of it. `make train-sft` and the
promote verb are existing capabilities, so this plan does not cite the unit.

## Decisions

This plan changes no decision. Decision T2 pins the engine: llama.cpp on the
CPU, greedy decoding, one GGUF at Q8_0, and the three pins. Packages 3 and 5
follow it. Decision T3 sets the recipe, and plan 007 step 1 moves every
configuration to it before this plan. Package 2 follows it. Decision T4 names
one CPT rehearsal pass before the SFT pass, and a seeded, paired comparison
against the noise floor decides that pass. Plan 007 runs the comparison on the
instruments of plan 006. This plan runs one SFT pass from the base model, the
refinement of the baseline that decision T13 names. It makes no CPT decision.
Decision T13 fixes the gate: the tier T1 sweep against the bar decides the
pilot, and below the bar the operator decides. Package 6 follows it.

## The reason

Sentence-level labels need a trained head. The research summary of 2026-09-24 on
the tells of machine prose finds that every zero-shot method scores a document.
A tagger over per-token features localizes at the sentence level, and no
zero-shot method does. A perplexity contrast at sub-1B scale is weak at the
sentence level. The baseline of phase P11 scores each segment through one cut on
that contrast, in the shape of every later scorecard. It gives no category. The
engine reports one finding per segment with a category, so the pilot needs the
trained head.

The SFT pass on the pairs is the bet of decision T12. The model learns the tells
from aligned pairs, and the grammar constrains the output to the registry. The
tier T1 sweep against the bar is the measurement of that bet, and one pass at
0.6B costs single-digit euros. A pass that clears the bar commits the pilot to
the method. A pass below the bar gives the operator a measured reason to change
the method before FuguTTX pays full price.

## Order of work

Each package sets the register row of its unit in the same change.

1. **The SFT pairs.** TRN-SFT-1, TRN-SFT-2, and TRN-SFT-3. Waits on plan 011
   package 6. Write a new `pairs.py` for the admitted pairs of the training
   lane. The old module left in plan 011 package 2. One example per document:
   the segments of the document in, and one grammar-constrained finding per
   segment out. A human segment carries the verdict human and the category
   `none`. A mirror segment carries the verdict machine and its alignment label.
   The builder reads the train split only, and it writes the dev split to
   `pairs-dev.jsonl` as the eval set of plan 006 (TRN-SFT-3). The card records
   the class balance: the share of human segments, of machine segments, and of
   each category. Tests: a new `test_pairs.py` covers the example shape on a
   fixture pair, the label map, and the split rule.
2. **The configuration and the run.** TRN-SFT, on the `make train-sft` verb of
   TRN-EXEC-3. Waits on package 1, on plan 007 step 1, and on the train stack
   apply. `train/sft-base.yml` holds the recipe of decision T3 after plan 007
   step 1. It takes the finding task: the dataset of package 1, the eval set,
   and the seed of plan 006. Read the live price (TRN-INST-1), and dispatch
   `up`. Then dispatch the `sft` action with `sft-base` on the H100, then
   `gguf`. The gguf step uploads the artifact to the checkpoint bucket, and
   `down` follows. The run log holds the eval loss lines. No new test: plan 006
   covers the dispatch, the seed, and the label.
3. **`stx analyze`.** ENG-IFACE-1, ENG-DETERM-1, ENG-DETERM-2, ENG-CONTRACT-1,
   and ENG-CONTRACT-2. Waits on plan 011 package 2 for the grammar, and the
   harness lands with a fixture model before the pairs exist. Add an `analyze`
   verb to `bin/stx`, beside the `segment` verb of plan 011. The `label` verb of
   the earlier format left in plan 011 package 2. The `analyze` verb segments
   the text with the segmenter of plan 011. It calls llama.cpp once per document
   with the generated grammar, and it emits one JSON finding per segment. Each
   finding holds the byte offsets of the harness segmenter, the verdict, the
   category, and the model hash (ENG-DETERM-1). The output names no model
   internal: no token, no logit, and no prompt (ENG-CONTRACT-1). A purpose-built
   engine can then replace the model without a client change (ENG-CONTRACT-2).
   The verb reads the grammar from the generated copy under `share/`. Tests:
   `t/stx.t` covers the finding shape and the offsets against a fixture
   llama.cpp command. A determinism test runs the verb twice on one input under
   the pins of decision T2. It compares the outputs byte for byte
   (ENG-DETERM-2).
4. **The metrics and tier T0.** EVL-TIERS-2 and EVL-TIERS-6. Waits on package 3.
   Write a new `score.py` and a new `t0.py` on the `analyze` output. The old
   modules scored the treebank, and they left in plan 011 package 3. The new
   ones derive the two dev metrics of
   [the evaluation document](../../spec/evaluation.md#evl-tiers) from the
   confusion counts. They are balanced accuracy, and category agreement on the
   segments that both sides mark machine-written. The scorecard holds the
   counts, and plan 006 widens them per category and per length bucket. The
   baseline scorecard of plan 011 follows the same form. The tier T0 job of
   `check.yml` returns with `t0.py`. It runs the score script on the dev split
   on every commit, on the CPU (EVL-TIERS-2). Tests: a new `test_score.py` and a
   new `test_t0.py` cover the two dev metrics from fixture counts. They also
   cover a self-score of a fixture at balanced accuracy 1.
5. **The tier T1 sweep.** EVL-TIERS-3. Waits on packages 2 and 4. Write the
   sweep anew in `t1.py`, and write a new workflow `t1.yml`. The old sweep
   scored the treebank, and it left in plan 011 package 2 with the old workflow.
   `t1.py` keeps the scorecard record, the key form, the aggregate, and the
   hash, and the new sweep uses them. The workflow runs the gated sweep on the
   CPU, against the eval lane (COR-LANES-3). That lane holds the test split and
   the later-era human-only set of the late release. The sweep reads the GGUF of
   package 2 from the checkpoint bucket, and it runs `stx analyze` under the
   pins of decision T2. It scores the two dev metrics on the test split. It adds
   the false-positive rate on the later-era human-only set, from the confusion
   counts of that set (EVL-TIERS-3). It writes the scorecard under the key form
   of EVL-TIERS-8. The baseline scorecard of plan 011 holds the same shape. It
   gives one verdict per segment, through one cut chosen on the dev split. It
   scores balanced accuracy on the test split and the false-positive rate on the
   later-era human-only set. It records category agreement as not applicable,
   and it holds the confusion counts. The aggregate pairs the two scorecards
   through the paired bootstrap of plan 006, on balanced accuracy and the
   false-positive rate (EVL-TIERS-9). Category agreement has no baseline value,
   so the aggregate reports it with no delta. The section-level AUROC and the
   true-positive rates of the baseline are extra measurements, and the aggregate
   pairs nothing against them. The promotion review reads the scores against the
   thresholds of EVL-TIERS-5 by hand, and no job reads a threshold
   (EVL-TIERS-7). Tests: a new `test_t1.py` covers the eval lane input, the
   `analyze` call, the false-positive rate from fixture counts, and the
   scorecard key.
6. **The decision and the batch.** Decision T13, EVL-TIERS-5, the promote verb
   of TRN-EXEC-5, and LRN-DELIVER. Waits on package 5 and on the operator. The
   tier T1 scorecard of package 5 is the first scorecard with categories. The
   operator sets the category-agreement threshold from it. This package writes
   the threshold into
   [the evaluation document](../../spec/evaluation.md#evl-tiers), and it sets
   the EVL-TIERS row of the register (EVL-TIERS-5). The operator reads the tier
   T1 scorecard against the bar of EVL-TIERS-10. Above the bar, `promote` copies
   the GGUF from the checkpoint bucket to the artifacts bucket, with the hash
   gate against the dev scorecard. The pilot then commits to the method. Below
   the bar, the operator decides, LEARNING records why, and the register records
   the state. In both cases the batch delivers the tier T0 and tier T1 numbers,
   and the delta against the baseline with its interval. It delivers the class
   balance and the eval loss curve too. Each numeric claim meets the verifier
   (LRN-DELIVER-8). Add one row to
   [the library index](../../spec/LEARNING.md#lrn-map): the first SFT pass on
   the pair corpus, on the page `Library-FuguSTX-pair-sft`. The row rehearses
   FuguTTX TRN-SFT, FuguTTX D4, and FuguTTX D5. Name the `analyze` verb in the
   stage map of `train/RUNBOOK.md`.

## The budget

One SFT pass at 0.6B costs 1 to 2 GPU-hours on the H100-1-80G, EUR 3 to 6 at the
price read 2026-08-28. The compute budget table of
[the training document](../../spec/training.md#trn-budget) holds the row. The
lease holds the pass, the conversion, and the dev score. A forecast must not
assume a run cheaper than one hour (TRN-BUDGET-1). The sweep, the tier T0
script, and the tests run on the CPU, on the CI runners.

## Out of scope

- The CPT decision. Plan 007 runs the seeded comparison of decision T4.
- The recipe arms: the full fine-tune, the epoch count, and the learning rate.
  Plan 007 holds them.
- The tier T2 suite. Phase P5 holds it.
- The daemon of ENG-IFACE-2.
- A change to the registry or to the judge. Plan 011 holds both.

## Open questions

- The example window. One document per example keeps the section context, and
  one section per example gives more examples with a shorter window. The token
  length of a rendered page against the context of the pass decides, and the
  card records the choice.
- The class balance. The human side is about half of the segments, and the
  mirror side spreads over the categories. When a category holds few segments,
  category agreement is noise there, and the batch says so.
- A mirror segment labeled `none`. Its verdict is machine and its category is
  `none`, so the model learns that a machine segment can carry no tell. The open
  choice is whether the target keeps the machine verdict, or the segment leaves
  the loss. The card fixes it, and the false-positive rate of the tier T1 sweep
  shows the cost.
