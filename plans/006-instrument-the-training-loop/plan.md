# 006 — Instrument the training loop

The two campaigns compared single runs at the fourth decimal. The promote gate
blocked `sft-aug` on one lemma cell by 0.0003. No record says how much a re-run
of one configuration moves a cell. This plan adds the instruments that make a
comparison readable. They are a seed in each run, an eval loss during training,
and a per-field scorecard with failure reasons. They are also a paired bootstrap
against the promoted model, parallel dev scoring, and the experiment card. No
training run is part of this plan.

- Implements: EVL-TIERS without EVL-TIERS-4
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: ENG-SPLIT
- Defers: IAC-APPLY

## Status

Everything in this plan can land now. No decision blocks it, and no GPU run is
part of it. Plans 007 to 010 wait on this plan. Each one compares seeded runs
through the scorecard that this plan defines. The roadmap holds the phases P7 to
P10 of the capability track, and this plan lands P7 with plan 007.

EVL-TIERS stays partial. The tier T2 suite (EVL-TIERS-4) waits for phase P5.

TRN-SFT and TRN-EXEC are done. The implementation change appends one rule to
TRN-EXEC and edits the text of TRN-SFT-3. Both units stay done, so this plan
cites neither one under `Implements:`, per the plans rule on a done unit.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. A FuguTTX plan
lands each change.

## Decisions

This plan changes no decision. Decision T2 fixes the pins of the tier T1 sweep,
and the sweep keeps them. Decision T4 names a seeded, paired comparison against
the noise floor as the test of the CPT pass. Plan 007 runs that test with the
instruments of this plan.

## The reason

Six facts from the P3 and P4 records make every comparison so far unreadable:

1. Every configuration ran once. No `train/*.yml` sets a seed, and no run
   repeats a configuration.
2. No SFT configuration names an eval set, and the run log shows
   `val_set_size: 0.0`. No eval loss exists. The first signal about
   generalization arrives with the dev score, thirty minutes after a pass ends.
3. The scorecard holds three rates: UPOS, lemma, and LAS. It cannot say whether
   the head or the label fails, and it holds no breakdown by sentence length.
4. The sweep counts a failed sentence and drops the reason that the harness
   returns. Between half a percent and four percent of the sentences fail, by
   model and treebank, and each one scores every token wrong.
5. The tier T1 thresholds are the cells of one run. The `sft-aug` sweep missed
   one cell by 0.0003, about 0.2 standard errors of one cell at 25000 tokens.
   The CPT comparison of P3 moved LAS by 0.0237 on the ewt dev split, after 8
   optimizer steps at a low learning rate. Either a re-run moves a cell by about
   two points, or the CPT pass did. Plan 007 separates the two.
6. The dev score runs one sentence at a time. It takes twice as long as the pass
   it scores.

[The misleading findings risk](../../spec/risks.md#rsk-findings) names the
consequence. A gate that reads noise as signal blocks a real gain about as often
as it admits one.

## Order of work

1. Dispatch a pass by name. Replace the per-configuration actions of `train.yml`
   with one `sft` action. The `name` input of `train.yml` and of `t1.yml` is
   free text, and the choice lists of both workflows retire. Each workflow
   passes the name, the seed, and the label to the shell through the
   environment. No step keeps an inline expression of a free-text input. The
   `offer` choice list stays inline, because a choice list is not free text. The
   shell checks each value against `[\w.-]+`.
   `make train-sft NAME=<name> SEED=<seed>` runs `scripts/train sft` with both
   values, and the `sft` job calls that target (TRN-EXEC-3). The `SFT_FROM`
   variable retires.
2. Seed every SFT run. Add a `seed` key to each `train/*.yml`. Add a `seed`
   input to `train.yml` and to `t1.yml`. For an `sft` run, the driver passes the
   seed as a configuration override. It sets `output_dir` to the configured path
   plus `-s<seed>`. TRN-EXEC-2 holds: the file names the default, and the run
   log names the value. The `gguf`, `score`, and `promote` verbs take the seed
   too. They derive each path and the scorecard label from the name and the
   seed, for example `sft-base-s11`. The `score` and `promote` verbs also take a
   `--label`. For the promote verb, the label selects the three fixed copies, so
   they come from one sweep. The verb checks the `model_hash` of the copied
   scorecard against the promoted GGUF, so a wrong label cannot install the
   baseline of another model. The hash gate of TRN-EXEC-5 keeps the dev
   scorecard of the name and the seed. A run on the file default takes no
   suffix, and its label is the name alone, so the P3 and P4 artifacts stay
   reachable. A run with a `seed` input takes the suffix. The `cpt` and
   `merge-cpt` verbs take no seed, and they keep their fixed paths. A stack runs
   one CPT pass, and `sft-cpt.yml` reads `/scratch/outputs/cpt-merged`. Append a
   rule to TRN-EXEC: a run must record its seed in the run log and in each
   scorecard.
3. Add an eval loss. The pairs builder writes `pairs-dev.jsonl` from the dev
   split, beside `pairs.jsonl`. `upload.py` puts it in `stx-corpus`. Each SFT
   configuration names it under `test_datasets`, with two evaluations per epoch.
   The run log then holds an `eval_loss` line each half epoch. Edit the text of
   TRN-SFT-3. A dev pair is a score input, and the trainer can compute a loss on
   it. It must not enter a training file. The eval lane stays out of every file
   (COR-LANES-4).
4. Widen the scorecard. `t1.py` counts three more matches per token: the head
   alone, the deprel alone, and the feats field. It also counts each match in
   four length buckets: 1 to 10 tokens, 11 to 20, 21 to 40, and 41 and more.
   `scores()` derives a rate for each count. `score.py` gains the same counts,
   so the scorer agreement test covers each new rate. EVL-TIERS-6 keeps its
   three rates against the UD scorer. `cards.py` prints the new columns behind a
   `--fields` flag, so the default table keeps its width. Append a rule to
   EVL-TIERS. A scorecard must hold the rate of each output field, and a
   breakdown by sentence length.
5. Keep the failure reason. `bin/stx label` adds a `kind` field to each error
   reply: `count`, `fields`, `head`, `cutoff`, or `empty`. The server transport
   reads the stop reason of the reply for `cutoff`. The exec transport marks an
   output at the token cap with too few records as `cutoff`. `t1.py` counts
   failures by kind. It writes each failed sentence with its reply to a failure
   file beside the scorecard. Append a rule to EVL-TIERS. A sweep must record
   each failed sentence with the reason.
6. Write per-sentence results and the paired bootstrap. The sweep writes a
   per-sentence file: one row per sentence, with the token count and the match
   counts. The per-sentence file and the failure file take the name of their
   scorecard, with `sentences-` or `failures-` in place of `scorecard-`. The GPU
   score therefore writes `sentences-dev-<label>.jsonl`, and the CPU dev sweep
   writes `sentences-cpu-dev-<label>.jsonl`, so the two never collide. The
   promote verb copies three files of the promoted model to fixed keys:
   `promoted/scorecard-t1.json`, `promoted/sentences-t1.jsonl`, and
   `promoted/sentences-cpu-dev.jsonl`. The dev copy is optional. The verb copies
   it when the CPU dev sweep of the model exists, and it skips it otherwise. The
   aggregate job reads the fixed per-sentence file of its split, pairs the rows
   on the sentence identifier, and resamples the sentences 10000 times. The
   scorecard gains a `delta` block per treebank and metric: the mean difference
   and the 95 percent interval. When the fixed file of the split is absent, the
   card holds no `delta` block and says so. A `compare` command of `cards.py`
   computes the same interval between any two per-sentence files. A candidate
   can therefore pair against an unpromoted control, and a silver dev set
   against its own baseline. Edit the text of EVL-TIERS-8. A scorecard key takes
   the run form, and the copy of the promoted model takes the fixed `promoted/`
   form. Append a rule to EVL-TIERS with the name form of the per-sentence file
   and the failure file. `cards.py` lists the `promoted/` prefix beside `runs/`,
   so one command still reads each scorecard (EVL-TIERS-7). It prints the
   interval and makes no decision.
7. Reword the threshold policy in
   [the evaluation document](../../spec/evaluation.md). The table shows the
   scorecard of the promoted model, and the review reads the paired interval
   against it. The promote rule has two conditions. On every treebank and
   metric, the interval excludes a loss larger than the tolerance. On at least
   one treebank, the LAS interval lies above zero. Edit the text of EVL-TIERS-5.
   The promoted scorecard holds the baseline of each cell, and the table shows
   it with the tolerance. A value before a measurement is a guess, and the
   document must not hold one. The tolerance column stays empty until plan 007
   measures the seed spread.
8. Score in parallel. `train-driver serve` starts `llama-server` with eight
   slots and continuous batching. It scales the context to eight times 8192
   tokens, so each slot keeps the 4096-token output cap of the harness. `t1.py`
   runs eight `stx label` workers over interleaved record subsets and merges the
   counts. The tier T1 sweep on the CPU keeps one worker and four threads per
   shard, because decision T2 pins that path. The dev scorecard keeps
   `device: gpu`.
9. Add a `split` input and a `label` input to `t1.yml`. The split is `dev` or
   `eval`, and the label defaults to the name plus the seed. The dev sweep
   fetches `training.jsonl` from `stx-corpus`, and the eval sweep keeps
   `eval.jsonl` from `stx-evalcorpus`. A dev sweep is not tier T1, which
   EVL-TIERS-3 defines on the eval lane. Its aggregate key is
   `scorecard-cpu-dev-<label>.json`, so it never overwrites the eval aggregate
   of the same run and label. A dev sweep on the CPU shards costs no GPU minute.
10. Add the experiment card. Append a rule to LRN-DELIVER. A campaign must open
    with one card as its first observation in the library, before the first
    dispatch (decision T11). The card must name the hypothesis, and the
    predicted direction and size of the effect. It must name the smallest effect
    that the sweep can detect, the seeds, and the stop rule. The card is an
    observation of the library, and the closing batch cites it.
11. Add the tests. `test_t1.py` covers the new counts, the kinds, the buckets,
    and the per-sentence file. It also covers the worker split, the count merge,
    and the bootstrap on a fixture pair. `test_cards.py` covers the columns, the
    delta block, and the compare command. `test_pairs.py` covers the dev pairs
    file. The harness test under `t/` covers the `kind` field.
    `t/train-driver.t` covers the seed override, the output suffix, and the
    eight-slot serve. `t/train.t` covers the `sft` verb, the seed input, the
    label, the seedless form, and the free-text name check. A new
    `t/workflows.t` covers the environment rule of both workflows, because the
    `t/ci` files are synced copies of the org pack.
12. Set [the register](../../spec/STATUS.md). The EVL-TIERS note names the new
    files and the dev sweep. The TRN-EXEC note names the seed, the TRN-SFT note
    names the dev pairs file, and the LRN-DELIVER note names the card. Name the
    `sft` action and the `seed`, `split`, and `label` inputs in the stage map of
    `train/RUNBOOK.md`. Update the promote and threshold answers of the runbook
    to the promote rule and the promoted baseline.
13. Verify on the promoted `sft-cpt` artifact, with no seed. Run the eval sweep
    first, with the label `sft-cpt-verify`. Its aggregate must equal the tier T1
    table of the evaluation document cell for cell on the same runner class. The
    CPU pins hold there (decision T2). A difference on another runner CPU is a
    T2 finding for the batch, not a defect of this plan. The label keeps the
    baseline card of run gh-33203797910 intact. Then run the dev sweep with the
    same label. Compare its rates with the GPU dev scorecard of run
    gh-33203797910. That scorecard came from one server slot, so the difference
    is the single-slot GPU against CPU number, and the batch records it. Then
    run the promote verb again for the same run and name, with the label
    `sft-cpt-verify`. The hash gate reads the dev scorecard of `sft-cpt`, which
    exists from P3. The three fixed keys then exist, and the `delta` block
    appears on the next sweep. The dev card must show the head rate, the deprel
    rate, the length buckets, and the failure kinds. That card is the first
    diagnostic deliverable of the capability track.

## The budget

No GPU run. The sweeps and the tests run on the CI runners of a public
repository.

## Out of scope

- A training run, and a tolerance number. Plan 007 measures both.
- A change to the recipe, the output format, or the data. Plans 007 to 010.
- LRN-DELIVER-2 and LRN-DELIVER-3, which change the FuguTTX repository.
- A plot, or a report page.

## Open questions

- The `test_datasets` key of the pinned Axolotl image. The image tag in
  `train/config.env` fixes the schema, and the first run confirms the key name
  and the log line.
- The parallel dev score and GPU numerics. A batched kernel can change a greedy
  pick at a near tie. The dev card is a comparison input, not a T2 pin, and the
  tier T1 sweep keeps one slot per shard. Plan 007 scores one GGUF with eight
  slots and on the CPU shards, and the batch records the difference.
- The bootstrap seed and the resample count. The plan fixes both in the
  aggregate code, so a re-run of the aggregate gives one interval.
