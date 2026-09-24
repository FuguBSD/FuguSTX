# 011 — The pair corpus and the zero-training baseline

This plan builds the pair corpus of decision T12, and it admits each pair
through the judge of decision T5. Then it runs the zero-training baseline of
decision T13 on the admitted pairs. The phase ends with a baseline scorecard,
the bar and the tier T1 thresholds, and the LEARNING batch of the campaign. No
training pass is part of this plan. The roadmap holds this work as phase P11.

- Implements: ENG-SPLIT
- Implements: ENG-SCHEMA without ENG-SCHEMA-1
- Implements: COR-SOURCES
- Implements: COR-LANES
- Implements: COR-PAIRS
- Implements: TRN-TEACH
- Implements: TRN-BUDGET
- Implements: LIC-LIC
- Implements: LIC-RELEASE without LIC-RELEASE-1 without LIC-RELEASE-2 without
  LIC-RELEASE-4
- Implements: EVL-TIERS without EVL-TIERS-2 without EVL-TIERS-3 without
  EVL-TIERS-4 without EVL-TIERS-6
- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: TRN-SFT
- Defers: TRN-CPT
- Defers: IAC-APPLY

## Status

Packages 1 to 3 land now, and the Claude path of package 4 lands with them. No
decision blocks them, and no cloud resource is part of them. The Qwen3 path of
package 4 waits on the train stack apply. Packages 5 to 8 wait in order, and
package 8 waits on the operator too. Plan 006 packages 3 to 7 wait on this plan:
they read the dev split, the labels, and the baseline scorecard. Plan 007 waits
on this plan through phase P12. The roadmap holds this plan as phase P11.

ENG-SPLIT is partial. ENG-SPLIT-3 and ENG-SPLIT-4 hold: the schema holds no
offset field, and the harness is the only caller of llama.cpp. This plan lands
ENG-SPLIT-1 and ENG-SPLIT-2, the Perl segmenter and its offsets.

ENG-SCHEMA is open. This plan lands ENG-SCHEMA-2 to ENG-SCHEMA-7: the segment
record, the repair map, the registry, its version, and the generated copies.
ENG-SCHEMA-1 waits for `stx analyze` in phase P12, which runs the model under
the generated grammar.

COR-SOURCES, COR-PAIRS, and COR-LANES are open, and this plan lands every rule
of each.

TRN-TEACH is partial. TRN-TEACH-1 to TRN-TEACH-3 hold: the vLLM service, the
localhost bind, and the tunnel. This plan lands TRN-TEACH-4 to TRN-TEACH-10. The
batch of package 8 is the record of TRN-TEACH-6 for the pair filter. The card of
package 5 states each judge threshold and bound (TRN-TEACH-10). Package 8 writes
each value into the training document after the campaign.

TRN-BUDGET is partial, and this plan lands TRN-BUDGET-2, the call and token
record of the second generator. LIC-LIC is partial, and this plan lands
LIC-LIC-2, the terms check of each generator.

LIC-RELEASE is open. This plan lands LIC-RELEASE-3: each admitted record
inherits the training lane and the provenance tags. LIC-RELEASE-1,
LIC-RELEASE-2, and LIC-RELEASE-4 concern a released model, and no release is
part of this plan.

EVL-TIERS stays partial. EVL-TIERS-1, EVL-TIERS-7, and EVL-TIERS-8 hold: the
scorecard write, the scorecard reader, and the key form. This plan lands the
baseline scorecard of EVL-TIERS-9, and plan 006 lands the comparison half of the
same rule. After the baseline run, the operator sets the tier T1 thresholds of
EVL-TIERS-5 and the bar of EVL-TIERS-10. Package 8 writes them. The tier T0
score of EVL-TIERS-2, the tier T1 sweep of EVL-TIERS-3, and the counts of
EVL-TIERS-6 land in phase P12. The tier T2 suite of EVL-TIERS-4 waits for phase
P5.

LRN-DELIVER-2 and LRN-DELIVER-3 change the FuguTTX repository. A FuguTTX plan
lands each change.

TRN-SFT and TRN-CPT stay open. The lanes of this plan are their inputs, and no
training pass runs here. IAC-APPLY stays partial. The Qwen3 path dispatches the
train stack, an existing capability, and this plan implements no rule of the
unit.

## Decisions

This plan changes no decision. Decision T5 fixes the two generator families, the
cross-family labeler with two seeded passes, and the four checks of the judge.
Packages 4 and 5 follow it. Decision T12 fixes the pair as the training unit,
and the generator input as facts and structure with no human prose. It also
fixes the tell inventory as a versioned registry with a generated grammar.
Packages 2, 3, and 4 follow it. Decision T13 fixes the zero-training baseline
before the first SFT pass, and the bar after the baseline run. Packages 7 and 8
follow it.

## The reason

Decision T12 rests on the mirror probe of 2026-09-24, and
[batch 3](../../spec/LEARNING.md#lrn-entries) of the learning record holds it.
Three facts of that probe shape this plan. A famous page returns from the
generator memory. A mirror from a structure skeleton plus the source code
rebuilds a memorized page. Surface lexical markers do not separate a human page
from its mirror; the differences are completeness, rationale sentences, and
invented facts.

Three risks follow from those facts.
[The memorization risk](../../spec/risks.md#rsk-mem): a memorized page gives a
pair with human text on both sides, and that pair is label noise. The recall
probe of package 5 drops such a page before it enters a pair (COR-PAIRS-3).
[The confound risk](../../spec/risks.md#rsk-confound): a corpus of one era and
one generator teaches the model era or generator identity. Three eras, two
generator families in each split, and the later-era human set of the eval lane
mitigate. [The generator drift risk](../../spec/risks.md#rsk-drift): the tells
of the next model generation differ. The registry version of package 2 and the
provenance of each pair let the corpus regenerate under a new inventory without
a schema change.

The research summary of 2026-09-24 on the tells of machine prose supports the
shape of the registry. Syntactic tells such as participial clauses and
nominalization persist across model sizes and families. Lexical tells decay
within one to two years, and the marker set rotates with each flagship model.
The registry therefore carries a level per row, and the `vocabulary` row names a
versioned word list as its evidence. A later audit can retire the lexical level
and leave the other levels in place.

The same summary weighs the zero-training baseline. A perplexity contrast
between a base model and its instruct sibling separates human text from machine
text at the document level. A sub-1B pair reaches near chance at the sentence
level. No study measured a sub-1B pair on English technical prose, and technical
prose has low perplexity by nature. Package 7 therefore scores at section
granularity of at least 100 tokens, and it reports the per-segment number for
information only. A memorized page scores machine-side under any perplexity
method, so the baseline runs on the admitted pairs only.

## Order of work

Each package sets the register row of its unit in the same change.

1. **The segmenter.** ENG-SPLIT-1 and ENG-SPLIT-2. Lands now. Add a `segment`
   verb to `bin/stx`. It reads text on standard input, and it writes one JSON
   record per sentence with the start and end byte offsets. The harness
   segmenter computes every offset, and the split is deterministic. The Python
   pipeline calls `stx segment` for every segmentation, so the corpus and the
   engine segment alike. Tests: `t/stx.t` covers the verb on fixtures with
   multi-byte characters and on rendered manual text. A test compares the
   offsets of each sentence against the bytes of the fixture.
2. **The registry and its generated copies.** ENG-SCHEMA-2 to ENG-SCHEMA-7.
   Lands now. Add `share/tells.tsv` at inventory version 1, with the columns of
   ENG-SCHEMA-5: id, level, repair, since, retired, description, and evidence.
   The row order is the precedence order for a segment that shows more than one
   tell. The seed rows are `none` (keep, the reserved id), `invented-fact`
   (content, verify), `addition` (content, delete), and `elaboration` (content,
   compress). Then `participial-tail` (syntactic, rewrite), `nominalization`
   (syntactic, rewrite), `triad` (structural, rewrite), `contrast-frame`
   (structural, rewrite), and `vocabulary` (lexical, rewrite). The evidence of
   `vocabulary` is a versioned word list under `share/`. Add a generator script
   that reads the registry and writes the grammar file and the alignment label
   list. The grammar record per segment holds the verdict, human or machine, and
   the category (ENG-SCHEMA-2). Each category maps to one repair action of the
   closed set (ENG-SCHEMA-3). A retired row stays in the registry and leaves the
   grammar (ENG-SCHEMA-6), and `none` is the only reserved id (ENG-SCHEMA-7).
   The old grammar `share/annotation.gbnf` leaves `share/` in this package, and
   the schema and grammar modules of the corpus package read the generated
   grammar. The label verb of `bin/stx` leaves with the file in the same change,
   and its subtests of `t/stx.t` leave with it. Tests: a test compares each
   committed copy byte for byte with a fresh generation from the registry
   (ENG-SCHEMA-4). A second test checks each id, each level, each repair action,
   and the evidence of each active row.
3. **The sources.** COR-SOURCES-1, COR-SOURCES-2, COR-SOURCES-3, COR-SOURCES-5,
   and COR-SOURCES-6. Lands now, and the fetch step needs the network. Rewrite
   `fetch.py` against the source table of
   [the corpus document](../../spec/corpus.md#cor-sources). The pipeline fetches
   each page from the OpenBSD tree through the cvsweb checkout URL at a pinned
   release tag. It records the tag (COR-SOURCES-1). It fetches the source files
   that each page describes at the same tag (COR-SOURCES-2). A page list per era
   names the pages: an early release, a middle release, and a late release. The
   late release serves the later-era human-only set of package 6. The list
   prefers a native page, one with no NetBSD id line. The license filter reads
   the header of each page and of each source file. It excludes a page whose
   license is not permissive (COR-SOURCES-3), and it excludes a page with no
   provable license (COR-SOURCES-6). The pipeline strips the version-control id
   lines and the license comment block from each page (COR-SOURCES-5). It
   renders each page, and later each mirror, with `mandoc -T markdown` before
   segmentation. Both sides then share one format, and the format matches the
   target register. The first cut is about two hundred admitted pairs, and the
   page list holds pages above that count for the rejection rate. Tests:
   `test_fetch.py` covers the URL form, the tag record, the license filter, and
   the strip, on fixture pages and a fixture license block.
4. **The generators.** TRN-TEACH-7, TRN-BUDGET-2, and LIC-LIC-2, over the held
   TRN-TEACH-1 to TRN-TEACH-3. The Claude path lands now, and the Qwen3 path
   waits on the train stack apply. The generator input is a structure skeleton
   of the page plus its source files, and it holds no sentence of the human
   prose (COR-PAIRS-2). Each generator writes one mirror per page, so a page
   yields up to two pairs. The Qwen3-32B path runs under vLLM on the train
   instance with the mirror prompt, through `teach-serve` and the tunnel of
   `scripts/train`. The second path runs Claude Opus through a headless
   `claude -p` session under a dedicated configuration directory (TRN-TEACH-7).
   The session loads no setting source and no tool, and it runs in an empty
   working directory. The output arrives on standard output, and the client
   reads the call and the token counts from the JSON result. The client records
   both counts per campaign, and the experiment card states the call budget
   before the first call (TRN-BUDGET-2). Check the terms of each generator
   (LIC-LIC-2). Admit a generator only when its terms permit redistribution of
   its outputs, commercially included. Record the check in the license table of
   [the licensing document](../../spec/licensing.md#lic-lic). Tests:
   `test_teacher.py` covers the prompt shape against a fixture page and the
   profile flags of the client call. It also covers the count record from a
   fixture JSON result.
5. **The judge filter.** TRN-TEACH-4, TRN-TEACH-5, TRN-TEACH-8, TRN-TEACH-9,
   COR-PAIRS-1 to COR-PAIRS-5, and LIC-RELEASE-3. Waits on package 4. Rewrite
   `judge.py` around the four checks of
   [the training document](../../spec/training.md#trn-teach). First, the
   memorization probe: per page and per generator, the client asks the generator
   for the page from its name and section alone. The 8-gram containment of the
   answer against the original stays under the threshold, or the page leaves the
   corpus (COR-PAIRS-3). Second, the containment of the mirror: the 8-gram
   containment of the mirror against the original stays under the threshold.
   Third, the structure match: the section skeleton of the mirror equals the
   skeleton of the page. The segment count ratio stays within the bound, and
   `mandoc -T lint` passes on the mirror. Fourth, the labels: a labeler of the
   other model family sees the segmented page and the segmented mirror, both
   numbered. It returns the counterpart index of each mirror segment, or none,
   and a label from the registry. Two passes with distinct seeds run, and the
   judge drops the target of a segment whose passes disagree (TRN-TEACH-8,
   TRN-TEACH-9). The judge rejects a pair whose share of dropped segments
   exceeds the bound. Then the mechanical check per category. `none` needs
   overlap with the counterpart above the bound, and `addition` needs no
   counterpart. `elaboration` needs a counterpart and a longer segment.
   `invented-fact` needs the content words of the quoted span absent from the
   source files. The judge admits a pair only when the four checks pass
   (TRN-TEACH-4), and it logs each rejected pair with its reason (TRN-TEACH-5).
   Each threshold and each bound is a parameter of the run in this package. The
   experiment card states each value before the first admission (TRN-TEACH-10).
   Package 8 writes each value into the training document after the campaign. An
   admitted pair holds the page and the mirror at one source tag (COR-PAIRS-1).
   It carries its provenance: the source tag, the generator identity and
   version, the seed, the prompt hash, and the inventory version (COR-PAIRS-5).
   The admitted record takes the training lane shape with those tags
   (LIC-RELEASE-3). Tests: `test_judge.py` covers each check on fixture pairs,
   one rejection per reason, the agreement drop, and the provenance fields.
6. **The lanes and the splits.** COR-LANES-1 to COR-LANES-5, COR-PAIRS-6, and
   COR-PAIRS-7. Waits on package 5. Rewrite `lanes.py` and `upload.py` for the
   pairs. The split divides the admitted pairs by document: 80 percent train, 10
   percent dev, and 10 percent test. No pair spans two splits, and the two pairs
   of one page sit in one split (COR-LANES-5). Each split holds the mirrors of
   both generator families (COR-PAIRS-7). The documents of each split span the
   three eras, and the manual page is the one register of the pilot
   (COR-PAIRS-6). The training lane holds the train and dev splits
   (COR-LANES-1). The prose lane holds the human side of the train split only
   (COR-LANES-2). The eval lane holds the test split plus the later-era
   human-only set of the late release (COR-LANES-3). `upload.py` puts the
   training lane and the prose lane in `stx-corpus`, and the eval lane in
   `stx-evalcorpus`. The lane rule is absolute: no eval file touches
   `stx-corpus` (COR-LANES-4). Tests: `test_lanes.py` covers the split by
   document, the family balance, the era span, and the refusal of an eval
   record. `test_upload.py` covers the bucket of each lane.
7. **The zero-training baseline.** EVL-TIERS-9, per decision T13. Waits on
   package 6. Add a baseline scorer to the corpus package. It scores a
   perplexity contrast between the Qwen3-0.6B base release and its instruct
   release. It scores the admitted pairs of the dev split and of the eval lane,
   one scorecard per split. The unit of the score is a section of at least 100
   tokens, and the scorer merges a short section with the next one. It reports
   the AUROC, and the true-positive rate at the false-positive rates 0.10 and
   0.01. It reports the per-segment result for information. It runs on the CPU.
   The scorecard holds the pins, the counts per verdict class, and the hash of
   each model. The score script of plan 006 can then pair a later scorecard
   against it. The scorecard goes to the artifacts bucket under the key form of
   EVL-TIERS-8, with the label `baseline`. Tests: `test_baseline.py` covers the
   section merge, the contrast score on fixture log-probability files, the AUROC
   and the rates, and the scorecard key.
8. **The bar, the thresholds, and the LEARNING batch.** EVL-TIERS-5,
   EVL-TIERS-10, TRN-TEACH-6, TRN-TEACH-10, and LRN-DELIVER. Waits on package 7
   and on the operator. The operator reads the baseline scorecard and the
   rejection log. Then the operator sets the pilot bar and each tier T1
   threshold. This package writes the bar and the tier T1 thresholds into
   [the evaluation document](../../spec/evaluation.md#evl-tiers) (EVL-TIERS-5,
   EVL-TIERS-10). It writes each judge threshold and bound of the card into
   [the training document](../../spec/training.md#trn-teach) (TRN-TEACH-10). It
   sets each register row, and the EVL-TIERS note names the baseline label. It
   delivers the batch: the memorization rate per era and per generator, the
   labeler agreement rate, each rejection rate, and the baseline numbers. Each
   numeric claim meets the verifier (LRN-DELIVER-8), and the batch cites the
   library pages (LRN-DELIVER-7). Add two rows to
   [the library index](../../spec/LEARNING.md#lrn-map). One row is the pair
   corpus and the judge filter, on the page `Library-FuguSTX-pair-corpus`. The
   other row is the zero-training baseline, on the page
   `Library-FuguSTX-baseline`. The rows rehearse FuguTTX TRN-AUG, FuguTTX D4,
   and FuguTTX D5. Name the `segment` verb and the baseline scorer in the stage
   map of `train/RUNBOOK.md`.

## The budget

The generator campaign row of
[the training document](../../spec/training.md#trn-budget) prices the Qwen3-32B
path. It is 5 to 15 GPU-hours on the H100-1-80G, EUR 14 to 43 at the price read
2026-08-28. The labeler passes and the recall probes of the Qwen3-32B side run
on the same instance, inside that lease. Read the live price before the apply
(TRN-INST-1). A forecast must not assume a run cheaper than one hour
(TRN-BUDGET-1).

The Claude path costs no instance. Its budget is a call count: about two hundred
pages, times one mirror, one recall probe, and two label passes on the Qwen3-32B
mirrors. That is near 800 calls before rejections and retries. No price attaches
to the calls: the session is subscription-billed, and the record is the call and
the token count (TRN-BUDGET-2). The baseline run and the tests run on the CPU,
on the CI runners or the operator machine.

## Out of scope

- Any training pass. Phase P12 holds the first SFT pass on the pairs, and plan
  007 holds the recipe.
- The tier T0 score and the tier T1 sweep on the three metrics. Phase P12 holds
  them.
- `stx analyze`. Phase P12 holds it, on the grammar of package 2.
- The tier T2 suite. Phase P5 holds it.

## Open questions

- The later-era human set and memorization. A late page can sit in the training
  set of a generator too, and a memorized page scores machine-side under a
  perplexity method. The recall probe of package 5 runs on the late pages as
  well, and the batch records the rate. A high rate moves the false-positive
  number of the baseline, and the operator reads the bar with that rate in view.
- The labeler of the Qwen3-32B mirrors. Claude Opus is the default, and a
  smaller Claude model cuts the call cost. The agreement rate of the two passes
  decides, and the card fixes the model before the first call.
- The mechanical check of `invented-fact`. Content words absent from the source
  files is a coarse test. A paraphrase of a source fact passes it, and a fact
  from a header comment fails it. The rejection log shows the miss rate, and the
  batch records it.
- The first-cut size against the memorization rate. Batch 3 saw the famous pages
  in the generator memory and the early-deleted page outside it. When the early
  era loses most pages to the probe, the page list grows, or the early era moves
  to a less famous set.
