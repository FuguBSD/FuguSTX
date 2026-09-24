# 006 — Instrument the training loop

Every configuration of the record ran once. No record says how much a re-run of
one configuration moves a score, so a comparison of two single runs is
unreadable. This plan adds the instruments that make one comparison on the pair
corpus readable. They are a seed in each run, an eval loss during training, and
a scorecard with the confusion counts. They are also a failure reason per
malformed record, a paired bootstrap against the zero-training baseline,
parallel dev scoring, and the experiment card. No training run is part of this
plan.

- Implements: EVL-TIERS without EVL-TIERS-4 without EVL-TIERS-5 without
  EVL-TIERS-10
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Extends: TRN-EXEC
- Defers: ENG-SPLIT
- Defers: IAC-APPLY
- Defers: TRN-SFT

## Status

Packages 1 and 2 land now: the run dispatch by name with a seed, and the
experiment card. Each one lands with its tests and its register note. No
decision blocks them, and no GPU run is part of them. Packages 3 to 7 wait on
phase P11, the pair corpus. Each one reads the dev split, the labels, or the
zero-training baseline scorecard of that phase. Plan 007 waits on this plan and
on phase P12. It compares seeded runs through the scorecard that this plan
defines. The roadmap holds this plan as a part of phase P7.

EVL-TIERS stays partial. The tier T2 suite (EVL-TIERS-4) waits for phase P5.
EVL-TIERS-5 and EVL-TIERS-10 wait on the baseline run, in phases P11 and P12.
This plan lands the comparison of each later scorecard against the baseline
(EVL-TIERS-9), and phase P11 lands the baseline scorecard.

TRN-EXEC is done, and the implementation appends one rule to it. A run must
record its seed in the run log and in each scorecard. The unit stays done, so
this plan cites it under `Extends:`.

TRN-SFT is partial. This plan adds a seed and an eval set to each SFT
configuration, and it implements no rule of the unit. The admitted pairs and the
format of TRN-SFT-1 and TRN-SFT-2 land in phase P12.

ENG-SPLIT and IAC-APPLY stay partial. The `kind` field touches the harness, and
the workflow inputs touch the dispatch jobs. Neither implements a rule of those
units.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. A FuguTTX plan
lands each change.

## Decisions

This plan changes no decision. Decision T2 fixes the pins of the tier T1 sweep,
and the sweep keeps them. Decision T4 names a seeded, paired comparison against
the noise floor as the test of the CPT pass. Decision T13 names the
zero-training baseline as the comparison point of every scorecard, and this plan
pairs each run against it. Plan 007 runs the comparison of T4 with the
instruments of this plan.

## The reason

Six facts of the record make every comparison so far unreadable:

1. Every configuration ran once. No `train/*.yml` sets a seed, and no run
   repeats a configuration.
2. No SFT configuration names an eval set, and the run log shows
   `val_set_size: 0.0`. No eval loss exists. The first signal about
   generalization arrives with the dev score, after a pass ends.
3. The scorecard holds no confusion count and no per-category count. It cannot
   say which verdict class or which tell category fails, and it holds no
   breakdown by segment length.
4. The sweep counts a malformed reply and drops the reason that the harness
   returns. A malformed reply scores every segment of its record wrong, and no
   record says why it failed.
5. The promotion review compares one scorecard against one scorecard, with no
   interval. Nothing separates a re-run difference from an effect. Plan 007
   separates the two.
6. The dev score runs one record at a time. It takes longer than the pass it
   scores.

[The misleading findings risk](../../spec/risks.md#rsk-findings) names the
consequence. A gate that reads noise as signal blocks a real gain about as often
as it admits one.

## Order of work

1. Dispatch a run by name, and seed every run. Lands now. Replace the
   per-configuration actions of `train.yml` with one `sft` action. The `name`
   input of `train.yml` and of `t1.yml` is free text, and the choice lists of
   both workflows retire. Each workflow passes the name, the seed, and the label
   to the shell through the environment. No step keeps an inline expression of a
   free-text input. The `offer` choice list stays inline, because a choice list
   is not free text. The shell checks each value against `[\w.-]+`.
   `make train-sft NAME=<name> SEED=<seed>` runs `scripts/train sft` with both
   values, and the `sft` job calls that target (TRN-EXEC-3). The `SFT_FROM`
   variable retires. A configuration with no lane in the corpus leaves `train/`
   in the same change. Add a `seed` key to each `train/*.yml`, and a `seed`
   input to `train.yml` and to `t1.yml`. For an `sft` run, the driver passes the
   seed as a configuration override, and it sets `output_dir` to the configured
   path plus `-s<seed>`. TRN-EXEC-2 holds: the file names the default, and the
   run log names the value. The file default applies when the input is empty,
   and the label carries the seed in every case. The `gguf`, `score`, and
   `promote` verbs take the seed too. They derive each path and the scorecard
   label from the name and the seed, for example `sft-base-s11`. The `score` and
   `promote` verbs also take a `--label`. The hash gate of TRN-EXEC-5 keeps the
   dev scorecard of the name and the seed. The `cpt` and `merge-cpt` verbs take
   no seed, and they keep their fixed paths. A stack runs one CPT pass, and
   `sft-cpt.yml` reads `/scratch/outputs/cpt-merged`. Append a rule to TRN-EXEC.
   A run must record its seed in the run log and in each scorecard.
   `t/train-driver.t` covers the seed override and the output suffix.
   `t/train.t` covers the `sft` verb, the seed input, the label, and the
   free-text name check. A new `t/workflows.t` covers the environment rule of
   both workflows, because the `t/ci` files are synced copies of the org pack.
   Name the `sft` action and the `seed` input in the stage map of
   `train/RUNBOOK.md`. Set the TRN-EXEC note of
   [the register](../../spec/STATUS.md): it names the seed.
2. Add the experiment card. Lands now. Append a rule to LRN-DELIVER. A campaign
   must open with one card as its first observation in the library, before the
   first dispatch (decision T11). The card must name the hypothesis, and the
   predicted direction and size of the effect. It must name the smallest effect
   that the sweep can detect, the seeds, and the stop rule. It must name the
   comparison point: the zero-training baseline scorecard (EVL-TIERS-9). The
   card is an observation of the library, and the closing batch cites it. Set
   the LRN-DELIVER note of the register: it names the card.
3. Add an eval loss. Waits on phase P11. `pairs.py` writes the SFT examples of
   the dev split to `pairs-dev.jsonl`, beside `pairs.jsonl`. `upload.py` puts it
   in `stx-corpus`. Each SFT configuration names it under `test_datasets`, with
   two evaluations per epoch. The run log then holds an `eval_loss` line each
   half epoch. The dev split stays a score input (TRN-SFT-3): the trainer reads
   `pairs-dev.jsonl` for the loss only, and no dev example enters `pairs.jsonl`.
   The eval lane stays out of every file (COR-LANES-4).
4. Widen the scorecard. Waits on phase P11. The score script and the sweep count
   each segment into the confusion counts of EVL-TIERS-6. A count is one verdict
   of the model against one label, per verdict class. A second count is the
   category match on each segment that both sides mark machine-written. The
   script also counts each match per tell category. It keeps each count in four
   length buckets: 1 to 10 tokens, 11 to 20, 21 to 40, and 41 and more.
   `scores()` derives each metric from the counts. The dev split gives balanced
   accuracy and category agreement (EVL-TIERS-2), and the eval lane adds the
   false-positive rate on its human set (EVL-TIERS-3). `score.py` and `t0.py`
   derive the same counts, so the tier T0 script and the sweep agree. `cards.py`
   prints the per-category columns and the buckets behind a `--fields` flag, so
   the default table keeps its width. Keep the failure reason. `bin/stx` adds a
   `kind` field to each error reply, with a schema-shaped kind: `count`,
   `category`, `cutoff`, or `empty`. The server transport reads the stop reason
   of the reply for `cutoff`. The exec transport marks an output at the token
   cap with too few records as `cutoff`. The sweep counts failures by kind, and
   it writes each malformed record with its reply to a failure file beside the
   scorecard. Append a rule to EVL-TIERS. A scorecard must hold the per-category
   counts and a breakdown by segment length. Append a second rule. A sweep must
   record each malformed record with the reason.
5. Write per-segment results and the paired bootstrap. Waits on phase P11. The
   sweep writes a per-segment file: one row per segment, with the token count,
   the label, the verdict, and the category. The per-segment file and the
   failure file take the name of their scorecard, with `segments-` or
   `failures-` in place of `scorecard-`. The GPU score therefore writes
   `segments-dev-<label>.jsonl`, and the CPU dev sweep writes
   `segments-cpu-dev-<label>.jsonl`, so the two never collide. The baseline
   scorer of phase P11 feeds the same score script, so it writes the per-segment
   file too. The aggregate job takes a `baseline` input, and the default in
   `t1.yml` is the label of the zero-training baseline scorecard (EVL-TIERS-9).
   It reads the per-segment file of that label for the same split. It pairs the
   rows on the segment identifier, and it resamples the segments 10000 times.
   The scorecard gains a `delta` block per metric: the mean difference and the
   95 percent interval. When the baseline file of the split is absent, the card
   holds no `delta` block and says so. A `compare` command of `cards.py`
   computes the same interval between any two per-segment files. A candidate can
   therefore pair against any control. Append a rule to EVL-TIERS with the name
   form of the per-segment file and the failure file. `cards.py` prints the
   interval and makes no decision (EVL-TIERS-7).
6. Score in parallel. Waits on phase P11. `train-driver serve` starts
   `llama-server` with eight slots and continuous batching. It scales the
   context to eight times 8192 tokens, so each slot keeps the 4096-token output
   cap of the harness. `t1.py` runs eight `bin/stx` workers over interleaved
   record subsets and merges the counts. The tier T1 sweep on the CPU keeps one
   worker and four threads per shard, because decision T2 pins that path. The
   dev scorecard keeps `device: gpu`. Add a `split` input and a `label` input to
   `t1.yml`. The split is `dev` or `eval`, and the label defaults to the name
   plus the seed. The dev sweep fetches the dev split of the training lane from
   `stx-corpus` (COR-LANES-1). The eval sweep keeps the eval lane from
   `stx-evalcorpus` (COR-LANES-3). The labels of each split come from the
   alignment of the pair corpus (COR-PAIRS-4). A dev sweep is not tier T1, which
   EVL-TIERS-3 defines on the eval lane. Its aggregate key is
   `scorecard-cpu-dev-<label>.json`, so it never overwrites the eval aggregate
   of the same run and label. A dev sweep on the CPU shards costs no GPU minute.
7. Add the tests, set the register, and verify. Waits on phase P11. `test_t1.py`
   covers the confusion counts, the false-positive rate, the per-category
   counts, the kinds, the buckets, and the per-segment file. It also covers the
   worker split, the count merge, and the bootstrap on a fixture pair.
   `test_score.py` and `test_t0.py` cover the two dev metrics from the counts.
   `test_cards.py` covers the columns, the `delta` block, and the `compare`
   command. `test_pairs.py` covers the dev examples file. `t/stx.t` covers the
   `kind` field. `t/train-driver.t` covers the eight-slot serve. Set the
   EVL-TIERS note of the register: it names the counts, the new files, and the
   dev sweep. Name the `split` and `label` inputs in the stage map of
   `train/RUNBOOK.md`. Update the promote and threshold answers of the runbook
   to the baseline comparison of EVL-TIERS-9. Verify against a pair-corpus
   scorecard. Re-run the zero-training baseline scorer of phase P11 through the
   widened score script, under its own label. Its counts must equal the counts
   of the baseline scorecard, and its metrics must equal the baseline metrics.
   The run also gives the baseline its per-segment file. Then run the aggregate
   of a later scorecard against that label, or the baseline against itself when
   no later scorecard exists. A self-pairing must show a zero mean difference
   and an interval of zero width. The dev card must show the per-category
   counts, the length buckets, and the failure kinds. That card is the first
   diagnostic deliverable of the capability track.

## The budget

No GPU run. The sweeps and the tests run on the CI runners of a public
repository.

## Out of scope

- A training run, and a tolerance number. Plan 007 measures both.
- The zero-training baseline run, and the thresholds and the bar that follow it.
  Phases P11 and P12 hold them.
- A change to the recipe, the output format, or the data. Plan 007 holds the
  recipe, and phase P11 holds the data.
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
- The per-segment file of the zero-training baseline. The baseline is a
  perplexity contrast (decision T13), and phase P11 lands its scorer before
  package 5. The re-run of package 7 gives it the per-segment file. When the
  scorer holds its own writer, package 5 moves that writer into the score script
  first.
