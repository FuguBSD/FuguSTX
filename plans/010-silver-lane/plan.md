# 010 — The silver lane

Gold has a cap. The permissive UD English train splits give 22123 pairs. The P4
teacher added 111 records in a 3.93-hour stack, at an acceptance rate of 0.0925.
Its judge compared two samples of one model. This plan builds a silver lane. The
teacher of decision T5 writes in-domain sentences at scale, and two
purpose-built UD parsers label each one. The judge admits a record only when
both parsers agree and the structural checks pass. The SFT pass then trains on
gold plus silver. Decision T5 names the two annotators and the judge, and this
plan builds them. The roadmap holds this work as phase P10.

- Defers: LIC-RELEASE
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: EVL-TIERS
- Defers: ENG-LEXICON
- Defers: IAC-APPLY

## Status

Two probes run first, with no GPU. One is the license and training-data probe of
each parser, and one is the accuracy probe of each parser on the dev split. The
dev split is a score input (TRN-SFT-3). A probe below the go rule stops the plan
before the lane exists.

Steps 3 to 7 and step 9 can land after the probes pass, each with its tests. The
judge then follows decision T5 with no wait on plan 009. Step 8 and its tests
wait on plan 009, because the pairs take the anchored serialization. The
campaign waits on the tolerance of plan 007.

TRN-TEACH, TRN-SFT, COR-AUG, COR-LANES, and LIC-LIC are done. The implementation
change edits the text of TRN-TEACH-4, and it appends rules to COR-AUG and
COR-LANES. It adds rows to the licensing table, and it sets the TRN-SFT note.
The units stay done, so this plan cites none of them under `Implements:`, per
the plans rule on a done unit.

LIC-RELEASE stays partial, and this plan cites it under `Defers:`. It extends
the provenance rule (LIC-RELEASE-3) to the silver records, and it applies the
non-commercial criterion of LIC-RELEASE-4 to each component it adds. The
attribution, the redistribution, and the release-level check (LIC-RELEASE-1,
LIC-RELEASE-2, LIC-RELEASE-4) stay absent until the release.

ENG-LEXICON stays open. The word table of the judge stays the interim source,
and the approved dictionary waits for a later plan.

## Decisions

This plan changes no decision. Decision T5 splits the teacher role. Qwen3-32B
writes the sentences, and two independent UD parsers label them. The judge
admits a record only when both agree and the structural checks pass. The current
judge compares two samples of Qwen3-32B, so it does not follow T5, and this plan
brings the judge in line.

Decision T5 requires the agreement of both parsers. This plan reads agreement as
agreement on every field of the record, after the normalization of the judge:
UPOS, lemma, head, deprel, and feats. Stage one records the disagreement rate
per field. If feats alone drives the rejects, the batch proposes a T5 wording
change, and a human decides.

Decision T6 holds. The lane rule stays absolute. The comparator of step 3 proves
zero overlap between the silver text and the eval lane before each upload.
Decision T1 holds. The licensing table of
[the licensing document](../../spec/licensing.md) gains a row for each parser
and for the silver records (LIC-LIC-1).

The learning maps to FuguTTX TRN-AUG and FuguTTX D4. The judge design decides
the yield, and a filter that measures consistency admits a tenth of the
proposals at best.

## The reason

From LEARNING batch 2 and the P4 records:

1. Check 1 of the judge rejected 149 to 160 of 200 proposals per batch. It
   compares two samples of Qwen3-32B at temperature 0.2 under two seeds. Greedy
   decoding passes it, and a stable wrong annotation passes it too.
2. The accepted records were 111, half a percent of the pairs, in a domain the
   eval treebanks do not cover. No effect on the tier T1 cells was possible.
3. A 32B general model is not a gold UD annotator. A purpose-built parser
   trained on the same treebanks reaches the high 0.80s LAS on these test splits
   with gold tokens. The student sits at 0.77.
4. The compact taggers of the field train on silver data at scale. A 0.6B
   student on a few hundred thousand parser-labeled sentences approaches the
   parser it learns from.

[The accuracy risk](../../spec/risks.md#rsk-acc) names the stake: the gates
decide, not hope. [The scope leak risk](../../spec/risks.md#rsk-scope) names the
test. G1 needs the data, and the LEARNING row names the rehearsal.

## The design

- The sentence source. The teacher generates in-domain sentences: technical
  statements, step instructions, and ASD-STE100-style prose. A topic list
  rotates per call, to cut the duplicate rate of P4. The client sends eight
  requests at a time, and a normalized-text set drops each duplicate. The
  transport stays the SSH tunnel (TRN-TEACH-3), and the endpoint stays on
  localhost (TRN-TEACH-2).
- The annotators. Two UD parsers with a permissive license for the code and the
  English models, for example Stanza and Trankit. Each runs on the pre-tokenized
  forms of the teacher tokenizer. Both run on CI runners: the parsers need no
  GPU, and no instance runs during the labeling. A parser model must train on
  permissive train splits only. A model whose training set holds an eval-lane
  split carries eval labels in its weights. A model trained on a non-commercial
  document carries that restriction. The eval-lane splits are EWT test, GUM
  test, and PUD, and the plan excludes such a model.
- The judge. Check 1 becomes: both parsers agree on every field of every token,
  after normalization. Checks 2 and 3 stay: one root and a connected tree, the
  tag inventory, the record count, and the word table. The reject log keeps each
  reason and the disagreeing field (TRN-TEACH-5), and the rates enter LEARNING
  (TRN-TEACH-6).
- The comparator. An `overlap.py` module compares each silver sentence against
  the eval lane, verbatim and normalized, with a sensitivity test. The P4
  session ran such a check by hand, outside the repository, and this module
  makes it a step of the labeling verb.
- The lane. A silver record takes the lane shape with `source: silver`. Its tag
  names both parsers and their versions, and its sentence identifier carries the
  run identifier (COR-AUG-2). One thousand silver sentences stay out of every
  training file as a silver dev set. That set is a score input for the product
  domain, which no gold set covers.
- The verbs and the batches. `silver-write` runs the teacher on the instance
  through the tunnel, 5000 sentences per dispatch, and uploads the proposals
  under the run prefix in `stx-artifacts`. `silver-label` runs the annotators,
  the judge, and the comparator on the runner, one proposal batch per dispatch,
  with no instance. It uploads the accepted records under the run prefix in
  `stx-corpus`. The rejects and the report go under the run prefix in
  `stx-artifacts`, the convention of the P4 teach verb. Each dispatch fits the
  job timeout of `train.yml`, and the label verb reports the parser throughput.
- The mix. The pairs builder takes a `--silver` input in place of
  `--augmentation`, and a `--gold-repeat` count. The first campaign compares
  gold repeated twice against gold once, at 20000 silver records, three seeds
  per mix.
- The stages. Stage one: 21000 accepted records, 20000 for training and 1000 for
  the silver dev set, and one SFT comparison. Stage two runs only on a positive
  slope: 100000 accepted training records, with the silver dev set of stage one.
  Each stage uses two stacks: one for the teacher, and one for the SFT passes.
  The labeling runs between them with no instance.

## The experiment card

- Hypothesis H6: the agreement subset of the two parsers scores at least 0.85
  LAS on the ewt and gum dev splits. The agreement rate is at least 0.6. This is
  the go rule of the probe.
- Hypothesis H7: gold plus 20000 silver records raises the dev LAS of ewt and
  gum against the gold-only run of plan 009. The margin exceeds the tolerance.
  It raises the silver dev LAS by more.
- Prediction: H6 holds. H7 holds on the silver dev set, and on ewt and gum by a
  smaller margin, because the domain differs.
- Seeds: 11, 23, and 37.
- Stop rule: a probe below the go rule ends the plan before the campaign, and
  the batch records the parser scores. A stage one slope inside the tolerance
  ends the plan before stage two. The dispatches stop two hours before a lease
  expires, and `down` runs.

## Order of work

1. Probe the licenses and the training data. Record the license of the code and
   of the English models of each candidate parser in the licensing table. Record
   the treebanks, the splits, and the documents that each model trained on. A
   non-commercial license excludes the parser (LIC-RELEASE-4). An eval-lane
   split in the training set excludes the model (COR-LANES-4), and so does a
   non-commercial GUM document (COR-SOURCES-3).
2. Probe the accuracy. Run each parser on the ewt and gum dev splits with gold
   tokens. Score each output with `score.py`, and score the agreement subset.
   Record the per-parser and the agreement rates, and apply the go rule. A
   published model selected its checkpoint on these dev splits, so the probe
   reads an optimistic number, and the batch says so. Both probes run locally,
   and the results enter the library as observations. A probe below the go rule
   ends the plan here, and the batch records the parser scores.
3. Add `overlap.py`, the eval-lane comparator, with its sensitivity test.
   `test_overlap.py` covers the comparator and its sensitivity case.
4. Extend the generation client. A topic list, eight concurrent requests, the
   normalized duplicate set, and a progress line per thousand. The existing
   `--count` option sets the batch size. `test_teacher.py` covers the topic
   list, the concurrency, and the duplicate set.
5. Add the annotator step, a `silver.py` module. It reads the proposals, runs
   both parsers on the forms, and writes two annotation passes per sentence in
   the shape the judge reads. Add the parser packages to the workspace manifest
   and its lockfile as a `silver` dependency group. The label verb runs
   `uv run --locked --group silver`, so CI finds them. `test_silver.py` covers
   the step with two fake parsers.
6. Rewrite check 1 of `judge.py` per the design, and log the disagreeing field.
   Edit the text of TRN-TEACH-4 and the teacher prose of
   [the training document](../../spec/training.md) in the same change. Set the
   TRN-TEACH note in [the register](../../spec/STATUS.md). `test_judge.py`
   covers an agree and a disagree on each field.
7. Add the silver lane to `lanes.py` and the tag to the record shape. Hold out
   the silver dev set. `test_lanes.py` covers the silver source and the dev
   hold-out.
8. Add `--silver` and `--gold-repeat` to `pairs.py`, and the silver dev pairs as
   a second eval set. Add `sft-silver-2.yml` and `sft-silver-1.yml`, the two
   mixes, from the plan 009 winner. `test_pairs.py` covers both inputs.
9. Add the `silver-write` and `silver-label` verbs to `scripts/train` and to
   `train.yml`, per the design. The `teach` verb and action, `teacher.annotate`,
   the `--augmentation` input, and `train/sft-aug.yml` retire in the same
   change. Decision T5 does not sanction that path. The P4 accepted records stay
   in the corpus bucket as a record. `t/train.t` covers both new verbs, the two
   upload buckets, and the absence of the teach path.
10. Write the card. Stage one starts with the teacher stack. Read the price.
    Dispatch `up` with an eight-hour lease. Dispatch `teach-serve`. Dispatch
    seven `silver-write` batches. Dispatch `teach-stop`, then `down`. Dispatch
    seven `silver-label` batches on the runner, to 21000 accepted records. Then
    the SFT stack: dispatch `up` with an eight-hour lease. For each seed and
    mix, dispatch the `sft` action. Dispatch `gguf`, then `score`. Six passes.
    Dispatch `down`. Dispatch the tier T1 sweep and the dev sweep on the median
    dev seed of the better mix.
11. Analyze with the compare command of plan 006 against the plan 009 winner.
    Cover ewt, gum, pud, and the silver dev set, per metric and length bucket.
12. Stage two runs on a positive slope only. It repeats the two stacks: 34
    `silver-write` batches to 100000 accepted records, the labeling on the
    runner, and three seeds on the better mix. It ends with the same analysis,
    and with the tier T1 sweep and the dev sweep on the median dev seed. Promote
    when the candidate passes the promote rule of plan 006.
13. Update the specification. Append a rule to COR-AUG: a silver record must
    name each annotator and its version in its tag. Append a rule to COR-LANES.
    The training lane can hold a silver lane, and a silver dev set stays a score
    input. Edit the augmentation prose of
    [the corpus document](../../spec/corpus.md). Set the COR-AUG, COR-LANES,
    LIC-RELEASE, TRN-TEACH, and TRN-SFT notes in
    [the register](../../spec/STATUS.md). Name the two verbs and the two pairs
    inputs in the stage map of `train/RUNBOOK.md`. Take the `teach` verb out of
    it, and keep `teach-serve` and `teach-stop`.
14. Write LEARNING batch 6. The claims: the parser licenses and training sets,
    the parser and agreement accuracies, and the acceptance rate by reason and
    field at each stage. Then the duplicate rate, the teacher throughput at
    eight concurrent requests, and the parser throughput per batch. Then the
    paired effect of each mix and stage with its interval, and the silver dev
    scores. Add one row to [the library index](../../spec/LEARNING.md#lrn-map):
    the parser-labeled silver lane and the independent judge, on the page
    `Library-FuguSTX-silver-lane`. The row rehearses FuguTTX TRN-AUG and FuguTTX
    D4.

## The budget

Stage one needs about 37000 teacher sentences for 21000 accepted records at an
agreement rate of 0.6. The P4 generation calls returned 20 sentences each, so
that is about 1850 calls, 15 to 30 minutes at eight concurrent requests. The
teacher stack bills one hour, the minimum, with the serve and the up and down.
The parsers label 5 to 50 sentences per second on a CI runner. A 5000-sentence
batch therefore takes 2 to 20 minutes of runner time, with no instance, and
runner minutes are free for a public repository. On the SFT stack, three passes
on about 64000 pairs, gold twice plus silver, take about 45 minutes each. Three
passes on about 42000 pairs take about 30 minutes each. With a 2-minute
conversion and a 5-minute dev score each, the stack bills four to five hours.
Stage one: five to six GPU-hours, EUR 14 to 18. Stage two needs about 170000
sentences, about 8500 calls, one to three hours at eight concurrent requests,
and about 34 label batches. The teacher stack bills two to three hours. Three
SFT passes on 122000 to 144000 pairs take 80 to 95 minutes each, per the better
mix. The SFT stack bills about five hours. Stage two: seven to eight GPU-hours,
EUR 20 to 23. Each stack takes an eight-hour lease, and the stop rule keeps the
dispatches inside it. A forecast must not assume a run cheaper than one hour
(TRN-BUDGET-1). Both stages fit the teacher row of the compute budget table.

## Out of scope

- A second text source. The OpenBSD manual pages and the FuguBSD documents carry
  permissive licenses and the product domain. A later plan can add them through
  the same lane and comparator.
- An in-domain gold set. Two hundred hand-checked sentences can replace the
  silver dev proxy, and the open questions hold it.
- The approved dictionary (ENG-LEXICON), the reference client, and RAG.
- A change to the base model or the recipe.

## Open questions

- The parser pair. If one candidate fails a probe, a second choice runs the same
  probes. One parser alone gives no independence check, and the plan does not
  run with one.
- The mix ratio at stage two. Stage one measures gold twice against gold once,
  and stage two takes the better one.
- The domain gap. The tier T1 cells measure web, multi-genre, and news text, and
  the product targets technical prose. The silver dev set is the proxy, and a
  hand-checked in-domain set is the honest instrument.
- The feats field. Two parser models can differ in feats conventions, and the
  agreement rule covers feats per decision T5. Stage one records the
  disagreement rate per field, and the batch proposes a T5 change if feats alone
  drives the rejects.
