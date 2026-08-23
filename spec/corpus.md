# Corpus

<a id="cor-buckets"></a>

## The buckets

Four buckets hold the data of the pilot. The set mirrors the FuguTTX bucket set.
Rehearses: FuguTTX IAC-PERSIST, FuguTTX D6.

- **COR-BUCKETS-1** — The project must use four buckets: `stx-corpus`,
  `stx-evalcorpus`, `stx-checkpoints`, and `stx-artifacts`.
- **COR-BUCKETS-2** — Each bucket must apply the same versioning and lifecycle
  rules as the FuguTTX bucket set.

<a id="cor-lanes"></a>

## The lanes

Two lanes split the corpus ([T6](DECISIONS.md#t6)). Contamination drives the
lane rule here, and author copyright drives it in FuguTTX D6. The mechanics are
identical, so the rehearsal is faithful.

- **COR-LANES-1** — The training lane must hold the train and dev splits of UD
  English EWT and GUM (CC-BY-SA).
- **COR-LANES-2** — The training lane must also hold a prose lane for
  [the CPT rehearsal](training.md#trn-cpt): public-domain and CC-BY grammar
  prose.
- **COR-LANES-3** — The eval lane must hold the UD test splits, plus PUD.
- **COR-LANES-4** — The lane rule is absolute: eval data must not enter
  training.

<a id="cor-aug"></a>

## Augmentation

The augmentation set holds teacher-generated technical and instructional
sentences, with proposed annotations.

- **COR-AUG-1** — A record must enter the training lane only through
  [the judge filter](training.md#trn-teach).
- **COR-AUG-2** — Each record must carry a provenance tag.
