# Corpus

<a id="cor-buckets"></a>

## The buckets

Four buckets hold the data of the pilot. The set mirrors the FuguTTX bucket set.
Rehearses: FuguTTX IAC-PERSIST, FuguTTX D6.

- **COR-BUCKETS-1** — The project must use four buckets: `stx-corpus`,
  `stx-evalcorpus`, `stx-checkpoints`, and `stx-artifacts`.
- **COR-BUCKETS-2** — Versioning must be on for `stx-corpus`, `stx-evalcorpus`,
  and `stx-artifacts`. `stx-checkpoints` must hold no version, because a
  checkpoint is large and Scaleway bills each version. Object Storage suspends
  versioning, and it never removes versioning.
- **COR-BUCKETS-3** — A checkpoint key must carry the run identifier and the
  step number. No version protects an overwrite on `stx-checkpoints`.

<a id="cor-lanes"></a>

## The lanes

Two lanes split the corpus ([T6](DECISIONS.md#t6)). Contamination drives the
lane rule here, and author copyright drives it in FuguTTX D6. The mechanics are
identical, so the rehearsal is faithful.

- **COR-LANES-1** — The training lane must hold the train and dev splits of
  [the pair corpus](#cor-pairs), filtered per [the sources](#cor-sources).
- **COR-LANES-2** — The training lane must also hold a prose lane for
  [the CPT rehearsal](training.md#trn-cpt): the human side of the train split.
- **COR-LANES-3** — The eval lane must hold the test split of the pair corpus,
  plus a human-only set from an era after every training document.
- **COR-LANES-4** — The lane rule is absolute: eval data must not enter
  training.
- **COR-LANES-5** — A split must divide by document, never by segment, so no
  pair spans two splits.

<a id="cor-sources"></a>

## The sources

A source is a version-controlled tree of human-written technical prose under a
permissive license, with a commit date on each document. The table shows the
sources at the time of publication. Confirm each source before a campaign.

| Source                     | Access                                                                                             | License              | Note                                   |
| -------------------------- | -------------------------------------------------------------------------------------------------- | -------------------- | -------------------------------------- |
| OpenBSD `src` manual pages | `https://cvsweb.openbsd.org/checkout/src/<path>?rev=<tag>`, at a release tag such as `OPENBSD_3_0` | BSD or ISC, per file | The GitHub mirror holds no release tag |

- **COR-SOURCES-1** — The pipeline must pin each source to one tag, and it must
  record the tag.
- **COR-SOURCES-2** — The pipeline must fetch each document, and the source
  files that it describes, from the tree at the pinned tag.
- **COR-SOURCES-3** — The pipeline must exclude each document whose license
  header is not permissive, per [LIC-RELEASE-4](licensing.md#lic-release).
- **COR-SOURCES-4** — The prose lane must hold the human side of the train split
  only.
- **COR-SOURCES-5** — The pipeline must strip the version-control id lines and
  the license comment block from each document. They leak the era and the
  source.
- **COR-SOURCES-6** — The pipeline must exclude a document with no provable
  license. It must not default to including the document.

<a id="cor-pairs"></a>

## The pair corpus

A pair is one human document and one mirror of the same facts. The alignment
labels each segment of the pair, and the labels are the training targets.
[The judge filter](training.md#trn-teach) admits each pair.

- **COR-PAIRS-1** — A pair must hold one human document and one mirror, written
  from the same facts at the same source tag.
- **COR-PAIRS-2** — The generator input must hold the facts and the structure of
  the document. It must not hold a sentence of the human prose.
- **COR-PAIRS-3** — A human document must enter a pair only when it passes the
  memorization check of the judge filter.
- **COR-PAIRS-4** — The alignment must label each segment of the pair against
  its counterpart, with a label from the tell inventory of
  [the finding schema](engine.md#eng-schema). The labeler and the mechanical
  check of [the judge filter](training.md#trn-teach) produce the label.
- **COR-PAIRS-5** — Each pair must carry its provenance: the source tag, the
  generator identity and version, the seed, the prompt hash, and the inventory
  version.
- **COR-PAIRS-6** — The human documents must span more than one era and each
  register that the engine checks. The label is then authorship, not era or
  register.
- **COR-PAIRS-7** — A split must not hold the mirrors of one generator only.
