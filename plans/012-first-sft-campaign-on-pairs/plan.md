# 012 — The first SFT campaign on the pair corpus

This plan trains the first model on the admitted pairs of phase P11, and it
lands `stx analyze` on the generated grammar. It writes the tier T0 score script
and the tier T1 sweep anew on that verb. The script runs on the dev split. The
sweep runs on the eval lane. The promotion review reads its scorecard against
the tier T1 thresholds of EVL-TIERS-5 and the bar of EVL-TIERS-10. Phase P11
sets the bar and two thresholds after its baseline run, and this plan sets the
category-agreement threshold. The bar then decides the pilot, per decision T13.
The roadmap holds this work as phase P12.

- Implements: TRN-SFT
- Implements: ENG-SCHEMA without ENG-SCHEMA-2 without ENG-SCHEMA-3 without
  ENG-SCHEMA-4 without ENG-SCHEMA-5 without ENG-SCHEMA-6 without ENG-SCHEMA-7
- Implements: ENG-IFACE without ENG-IFACE-2
- Implements: ENG-DETERM
- Implements: ENG-CONTRACT
- Implements: EVL-TIERS without EVL-TIERS-1 without EVL-TIERS-4 without
  EVL-TIERS-7 without EVL-TIERS-8 without EVL-TIERS-9 without EVL-TIERS-10
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: TRN-CPT
- Defers: TRN-TEACH
- Defers: TRN-EXEC
- Defers: COR-LANES
- Defers: IAC-APPLY
- Defers: EVL-SUITE

## Status

Every package waits on plan 011. Package 1 waits on its package 6, the lanes.
Package 2 waits on packages 1 and 4, on plan 006 packages 1 and 2, and on the
train stack apply. Package 3 waits on plan 011 package 2, the grammar, and it
can land with a fixture model before the pairs exist. Packages 4 to 6 wait in
order, and package 6 waits on the operator. Plan 007 step 1 lands before this
plan, and it moves every configuration to the recipe of decision T3. Package 2
runs that recipe. The other steps of plan 007 wait on this plan. The roadmap
holds this plan as phase P12.

Plan 011 packages 2 and 3 remove the treebank pipeline, and each package names
the files that leave. Among them are the `label` verb of `bin/stx`, `pairs.py`,
`score.py`, `t0.py`, the sweep of `t1.py`, and the workflow `t1.yml`. From plan
011 package 2 to this plan, `bin/stx` holds the `segment` verb only. `t1.py`
holds the scorecard record, the key form, the aggregate, and the hash. Packages
1, 4, and 5 write the pairs builder, the score script, and the sweep anew on
`stx analyze`. They change no old module, except for the `score` verb of
`scripts/train`.

Plan 006 packages 1 and 2 are the seed and the card rule, and package 2 waits on
those two packages only. It opens with the card. Plan 006 packages 3 to 7 land
after packages 1, 4, and 5, and they extend the new files with the instruments.
The instruments are the eval loss, the per-segment file, the paired bootstrap,
the parallel scoring, and the split and label inputs. Package 4 lands
EVL-TIERS-6, the confusion counts, and plan 006 adds the per-category counts and
the failure reasons on top. Package 5 writes the tier T1 scorecard. The
promotion review compares it against the thresholds, the bar, and the baseline
scorecard of phase P11 by hand. No job reads a threshold, per EVL-TIERS-7. Plan
006 package 5 implements the comparison half of EVL-TIERS-9, the paired
bootstrap. That package is not a wait. The new `t1.yml` of package 5 takes the
run identifier and the split as inputs, and plan 006 adds the rest.

TRN-SFT is open. This plan lands TRN-SFT-1 and TRN-SFT-2, the admitted pairs as
the input and the segments-in, findings-out format. It lands TRN-SFT-3, the
train-split rule: the dev split enters no pair.

ENG-IFACE, ENG-DETERM, and ENG-CONTRACT are open. This plan lands `stx analyze`
(ENG-IFACE-1), and the offsets and the model hash on each record (ENG-DETERM-1).
It lands the same-bytes guarantee (ENG-DETERM-2), and the engine-independent
output (ENG-CONTRACT-1, ENG-CONTRACT-2). The daemon of ENG-IFACE-2 waits.

ENG-SCHEMA is open. Plan 011 package 2 lands ENG-SCHEMA-2 to ENG-SCHEMA-7, and
it leaves ENG-SCHEMA-1 to this phase. Package 3 lands ENG-SCHEMA-1: the
`analyze` verb runs the model under the generated grammar. That package sets the
ENG-SCHEMA row of the register in the same change.

EVL-TIERS stays partial. This plan lands the confusion counts (EVL-TIERS-6) and
the two dev metrics of EVL-TIERS-2 from them. It lands the tier T1 sweep on the
eval lane, with the false-positive rate on the later-era human-only set
(EVL-TIERS-3). The old score script and the old sweep scored a treebank, and
they leave in plan 011. This plan writes both anew on the `analyze` output and
the eval lane. After the baseline run of plan 011, the operator sets the bar
(EVL-TIERS-10) and two tier T1 thresholds. Those are balanced accuracy and the
false-positive rate, the two numbers that the baseline yields. Plan 011 package
8 writes them. The promotion review of package 6 reads the tier T1 scorecard
against them. The baseline gives no category, so it yields no category-agreement
threshold. EVL-TIERS-5 lands here for that threshold only. The operator sets it
from the first scorecard with categories, and package 6 writes it. The tier T2
suite of EVL-TIERS-4 waits for phase P5.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. A FuguTTX plan
lands each change.

TRN-CPT is open. Plan 007 decides the CPT pass, and this plan starts from the
base model. TRN-TEACH is the judge of plan 011. This plan runs no generator and
no judge, and it reads the admitted pairs. IAC-APPLY stays partial. The campaign
dispatches the train stack, and this plan implements no rule of the unit.
EVL-SUITE is open, and phase P5 holds it. COR-LANES is open, and plan 011
package 6 lands every rule of it. Package 1 adds the pair write to the
`upload.py` of that package, under the lane rule (COR-LANES-4). It implements no
rule of the unit, so this plan cites the unit under `Defers:`.

TRN-EXEC is done, and this plan changes no rule of it. `make train-sft` and the
promote verb are existing capabilities. Package 4 changes the `score` verb of
`scripts/train`, and the verb implements no rule of the unit. This plan
therefore cites the unit under `Defers:`.

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
   package 6, and plan 006 package 3 waits on it. Write a new `pairs.py` for the
   admitted pairs of the training lane. The old module left in plan 011
   package 2. One example per document: the segments of the document in, and one
   grammar-constrained finding per segment out. A human segment carries the
   verdict human and the category `none`. A mirror segment carries the verdict
   machine and its alignment label. The builder reads the train split only, and
   it writes the dev split to `pairs-dev.jsonl` as the eval set of plan 006
   (TRN-SFT-3). Add the pair write to the `upload.py` of plan 011 package 6. The
   old write left in plan 011 package 2. The write puts `pairs.jsonl` and
   `pairs-dev.jsonl` in `stx-corpus` before the run of package 2, under the lane
   rule (COR-LANES-4, COR-BUCKETS-1). Both files come from the training lane,
   and no eval file touches `stx-corpus`. The card of package 2 records the
   class balance: the share of human segments, of machine segments, and of each
   category. Tests: a new `test_pairs.py` covers the example shape on a fixture
   pair, the label map, and the split rule. `test_upload.py` covers the bucket
   of both files.
2. **The configuration and the run.** TRN-SFT, on the `make train-sft` verb of
   TRN-EXEC-3. Waits on packages 1 and 4, on plan 007 step 1, and on plan 006
   packages 1 and 2. The run waits on the train stack apply too.
   `train/sft-base.yml` holds the recipe of decision T3 after plan 007 step 1.
   It takes the finding task: the dataset of package 1 and the seed of plan 006
   package 1. The eval set of plan 006 package 3 joins the configuration when
   that package lands. Open the campaign with the experiment card, per the
   LRN-DELIVER rule of plan 006 package 2. The card comes before the first
   dispatch. It states the hypothesis, the class balance, the example window,
   the `none` rule, the stop rule, and the compute budget. Read the live price
   (TRN-INST-1), and dispatch `up`. Then dispatch the `sft` action with
   `sft-base` on the H100, then `gguf`, then `score`, then `down`. The gguf step
   uploads the artifact to the checkpoint bucket. The `score` verb of package 4
   writes the dev scorecard inside the lease. The run log holds the eval loss
   lines when the eval set is in place. No new test: plan 006 covers the
   dispatch, the seed, and the label.
3. **`stx analyze`.** ENG-SCHEMA-1, ENG-IFACE-1, ENG-DETERM-1, ENG-DETERM-2,
   ENG-CONTRACT-1, and ENG-CONTRACT-2. Waits on plan 011 package 2 for the
   grammar, and the harness lands with a fixture model before the pairs exist.
   Add an `analyze` verb to `bin/stx`, beside the `segment` verb of plan 011.
   The `label` verb of the earlier format left in plan 011 package 2. The
   `analyze` verb segments the text with the segmenter of plan 011. It calls
   llama.cpp once per document with the generated grammar (ENG-SCHEMA-1), and it
   emits one JSON finding per segment. The package sets the ENG-SCHEMA row of
   the register in the same change. Each finding holds the byte offsets of the
   harness segmenter, the verdict, the category, and the model hash
   (ENG-DETERM-1). The output names no model internal: no token, no logit, and
   no prompt (ENG-CONTRACT-1). A purpose-built engine can then replace the model
   without a client change (ENG-CONTRACT-2). The verb reads the grammar from the
   generated copy under `share/`. Tests: `t/stx.t` covers the finding shape and
   the offsets against a fixture llama.cpp command. A determinism test runs the
   verb twice on one input under the pins of decision T2. It compares the
   outputs byte for byte (ENG-DETERM-2).
4. **The metrics and tier T0.** EVL-TIERS-2 and EVL-TIERS-6. Waits on package 3,
   and plan 006 package 4 waits on it. Write a new `score.py` and a new `t0.py`
   on the `analyze` output. The old modules scored the treebank, and they left
   in plan 011 package 3. The new ones derive the two dev metrics of
   [the evaluation document](../../spec/evaluation.md#evl-tiers) from the
   confusion counts (EVL-TIERS-6). They are balanced accuracy, and category
   agreement on the segments that both sides mark machine-written. The scorecard
   holds the counts, and plan 006 widens them per category and per length
   bucket. The baseline scorecard of plan 011 follows the same form. The tier T0
   job of `check.yml` returns with `t0.py`. It runs the score script on the dev
   split on every commit, on the CPU (EVL-TIERS-2). Change the `score` verb of
   `scripts/train`. The verb keeps its present shape: a dispatch on the train
   instance through `train-driver serve`, inside the lease. Plan 006 package 6
   and plan 007 step 5 assume that shape. The verb runs the new `t0.py` against
   the GGUF of the run. It writes the dev scorecard to the artifacts bucket
   under the run identifier, in the key form of EVL-TIERS-8. That write is the
   existing capability of EVL-TIERS-1. Package 2 dispatches the verb after
   `gguf`, and package 6 promotes against its scorecard. Tests: a new
   `test_score.py` and a new `test_t0.py` cover the two dev metrics from fixture
   counts. They also cover a self-score of a fixture at balanced accuracy 1.
   `t/train.t` covers the `score` verb and its scorecard key.
5. **The tier T1 sweep.** EVL-TIERS-3. Waits on packages 2 and 4, and plan 006
   packages 4 to 7 wait on it. Write the sweep anew in `t1.py`, and write a new
   workflow `t1.yml`. The workflow takes the run identifier and the split as
   inputs, and plan 006 adds the rest. The old sweep scored the treebank, and it
   left in plan 011 package 2 with the old workflow. `t1.py` keeps the scorecard
   record, the key form, the aggregate, and the hash, and the new sweep uses
   them. The workflow runs the gated sweep on the CPU, against the eval lane
   (COR-LANES-3). That lane holds the test split and the later-era human-only
   set of the late release. The sweep reads the GGUF of package 2 from the
   checkpoint bucket, and it runs `stx analyze` under the pins of decision T2.
   It scores the two dev metrics on the test split. It adds the false-positive
   rate on the later-era human-only set, from the confusion counts of that set
   (EVL-TIERS-3). It writes the scorecard under the key form of EVL-TIERS-8. The
   baseline scorecard of plan 011 holds the same shape. It gives one verdict per
   segment, through one cut chosen on the dev split. It scores balanced accuracy
   on the test split and the false-positive rate on the later-era human-only
   set. It records category agreement as not applicable, and it holds the
   confusion counts. The promotion review reads the tier T1 scorecard beside the
   baseline scorecard of phase P11, by hand. Plan 006 package 5 implements the
   comparison half of EVL-TIERS-9, the paired bootstrap. That package is not a
   wait. The baseline holds no category-agreement value. Its section-level AUROC
   and its true-positive rates are extra measurements, and the review pairs
   nothing against them. The review reads the scores against the thresholds of
   EVL-TIERS-5 by hand, and no job reads a threshold (EVL-TIERS-7). Tests: a new
   `test_t1.py` covers the eval lane input, the `analyze` call, the
   false-positive rate from fixture counts, and the scorecard key.
6. **The decision and the batch.** Decision T13, EVL-TIERS-5, the promote verb
   of TRN-EXEC-5, and LRN-DELIVER. Waits on package 5 and on the operator. The
   tier T1 scorecard of package 5 is the first scorecard with categories. The
   operator sets the category-agreement threshold from it. This package writes
   the threshold into
   [the evaluation document](../../spec/evaluation.md#evl-tiers), and it sets
   the EVL-TIERS row of the register (EVL-TIERS-5). The operator reads the tier
   T1 scorecard against the bar of EVL-TIERS-10. Above the bar, `promote` copies
   the GGUF from the checkpoint bucket to the artifacts bucket. The hash gate
   reads the dev scorecard of package 4 (TRN-EXEC-5). The pilot then commits to
   the method. Below the bar, the operator decides, LEARNING records why, and
   the register records the state. In both cases the batch delivers the tier T0
   and tier T1 numbers, and the delta against the baseline. It delivers the
   class balance too, and the eval loss curve when the run log holds it. Each
   numeric claim meets the verifier (LRN-DELIVER-8). Add one row to
   [the library index](../../spec/LEARNING.md#lrn-map): the first SFT pass on
   the pair corpus, on the page `Library-FuguSTX-pair-sft`. The row rehearses
   FuguTTX TRN-SFT, FuguTTX D4, and FuguTTX D5. Name the `analyze` verb in the
   stage map of `train/RUNBOOK.md`.

## The budget

One SFT pass at 0.6B costs 1 to 2 GPU-hours on the H100-1-80G, EUR 3 to 6 at the
price read 2026-08-28. The compute budget table of
[the training document](../../spec/training.md#trn-budget) holds the row. The
lease holds the pass, the conversion, and the dev score. The conversion and the
dev score take minutes at this scale. A forecast must not assume a run cheaper
than one hour (TRN-BUDGET-1). The sweep, the tier T0 script, and the tests run
on the CPU, on the CI runners.

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
  card of package 2 records the choice.
- The class balance. The human side is about half of the segments, and the
  mirror side spreads over the categories. When a category holds few segments,
  category agreement is noise there, and the batch says so.
- A mirror segment labeled `none`. Its verdict is machine and its category is
  `none`, so the model learns that a machine segment can carry no tell. The open
  choice is whether the target keeps the machine verdict, or the segment leaves
  the loss. The card of package 2 fixes it, and the false-positive rate of the
  tier T1 sweep shows the cost.
