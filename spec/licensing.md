# Licensing and release

Every FuguSTX component ships under a permissive license. This document names
the license of each component, and it states the release rules.

<a id="lic-lic"></a>

## The licenses

Decision [T1](DECISIONS.md#t1) sets the base model, and
[the corpus sources](corpus.md#cor-sources) name the data sources. The table
names the license of each component.

| Component                                | License                            |
| ---------------------------------------- | ---------------------------------- |
| The harness and all tooling              | ISC                                |
| The base model                           | Apache 2.0                         |
| The teacher model                        | Apache 2.0                         |
| The training data, treebank EWT          | CC BY-SA 4.0                       |
| The training data, treebank GUM          | Public domain, CC-BY, and CC-BY-SA |
| The training data, prose                 | Public domain and CC-BY            |
| The training data, accepted augmentation | Apache 2.0                         |
| The judge word table, from the treebanks | CC BY-SA 4.0                       |
| The eval data, UD test splits and PUD    | CC BY-SA                           |

The GUM row names the licenses after the exclusion of the non-commercial
documents (corpus COR-SOURCES-3). The word table derives from the train splits
of UD_English-EWT and UD_English-GUM, and
[the corpus sources](corpus.md#cor-sources) hold the attribution of both
treebanks. The accepted augmentation records come from the teacher of decision
[T5](DECISIONS.md#t5), and each record carries a provenance tag through
[the judge filter](training.md#trn-teach) (LIC-RELEASE-3).

- **LIC-LIC-1** — Each component must carry the license that the table names.

<a id="lic-release"></a>

## Release integrity

These rules keep the release permissive, from the data to the weights.

- **LIC-RELEASE-1** — The released model must carry attribution.
- **LIC-RELEASE-2** — Anyone can redistribute the released model, commercially
  included.
- **LIC-RELEASE-3** — A teacher output must inherit
  [the training lane](corpus.md#cor-lanes) and its
  [provenance tags](corpus.md#cor-aug).
- **LIC-RELEASE-4** — A component must not carry a non-commercial restriction.
