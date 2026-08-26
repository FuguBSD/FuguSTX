# 001 — The corpus pipeline and the tier T0 score script

Implements: COR-LANES, COR-SOURCES, COR-CONLLU, EVL-TIERS without EVL-TIERS-1,
EVL-TIERS-3, EVL-TIERS-4, EVL-TIERS-5

Defers: COR-BUCKETS, COR-AUG

## Scope

This plan builds the local data pipeline of roadmap phase P1. The pipeline
fetches the UD treebanks, reads CoNLL-U files into training pairs, and splits
the corpus into the training lane and the eval lane. This plan also builds the
tier T0 score script. No cloud resource exists in this phase. The pipeline
writes to a local directory, not to a Scaleway bucket.

## How the pipeline lands

1. Add a fetch step. It pulls each treebank file at the pinned `r2.18` tag, per
   COR-SOURCES-1 and COR-SOURCES-2. It records the tag in the pipeline output.
2. Add a GUM license filter. It reads the GUM license file, and it excludes each
   document with a non-commercial license, per COR-SOURCES-3.
3. Add the prose lane fetch. It pulls the three named Gutenberg books, per
   COR-SOURCES-4. It strips the Project Gutenberg header and footer from each
   book, per COR-SOURCES-5.
4. Add a CoNLL-U reader. It applies each rule of COR-CONLLU:
   - It takes sentence text from `# text`.
   - It expands a multiword range line and excludes it from label targets.
   - It strips the DEPS column and each decimal ID line.
   - It strips the GUM extra payload.
   - It keeps a literal underscore FORM.
5. Add a lane split step. It places the EWT and GUM train and dev splits, plus
   the prose lane, in the training lane, per COR-LANES-1 and COR-LANES-2. It
   places the UD test splits and PUD in the eval lane, per COR-LANES-3. A test
   asserts that no eval-lane record leaks into the training lane, per the
   absolute rule of COR-LANES-4.
6. Write each lane to a local directory. This step defers COR-BUCKETS: no
   Scaleway bucket exists in phase P1, so the pipeline must not assume one.

## How the tier T0 score script lands

1. Add a score script. It scores the dev split of the training lane on UPOS,
   lemma, and LAS, per EVL-TIERS-2.
2. Add a comparison test against the UD tools scorer `eval.py`, per EVL-TIERS-6.
   The test must show matching scores on a fixture split.
3. Add a CI job. It runs the score script on the CPU, on every commit, per
   EVL-TIERS-2. The job needs no Scaleway resource: it runs in the existing CI
   runner.

This plan excludes EVL-TIERS-1, because a promotion scorecard needs the
artifacts bucket, which phase P2 creates. It excludes EVL-TIERS-3, because the
gated promotion sweep needs the eval lane thresholds that phase P3 fixes. It
excludes EVL-TIERS-4, because the artifact suite needs the OpenBSD guest and
image stack of phase P5. It excludes EVL-TIERS-5, because the first baseline run
of phase P3 fixes the tier T1 thresholds.

## Status

The full corpus pipeline and the tier T0 score script can land now. Both run
locally, and neither needs a Scaleway resource.

COR-BUCKETS waits on phase P2, which creates the four buckets under
[IAC-APPLY](../../spec/infrastructure.md#iac-apply). This plan writes lane
output to a local directory as a placeholder, not to a bucket path.

COR-AUG waits on phase P4, which runs the teacher campaign and the judge filter
of [TRN-TEACH](../../spec/training.md#trn-teach). No augmented record can exist
before that campaign runs.

EVL-TIERS-1 and EVL-TIERS-3 wait on phase P2 for the artifacts bucket. Both also
wait on phase P3 for the baseline run that fixes the tier T1 thresholds
(EVL-TIERS-5). EVL-TIERS-4 waits on phase P5 for the image stack and the OpenBSD
guest fleet.

No open question blocks this plan.
