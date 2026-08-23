# Licensing and release

Every FuguSTX component ships under a permissive license. This document names
the license of each component, and it states the release rules.

<a id="lic-lic"></a>

## The licenses

Decision [T1](DECISIONS.md#t1) sets the base model, and
[the corpus lanes](corpus.md#cor-lanes) set the data sources. The table names
the license of each component.

| Component                                  | License                 |
| ------------------------------------------ | ----------------------- |
| The harness and all tooling                | ISC                     |
| The base model                             | Apache 2.0              |
| The training data, treebanks (UD EWT, GUM) | CC-BY-SA                |
| The training data, prose                   | Public domain and CC-BY |

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
