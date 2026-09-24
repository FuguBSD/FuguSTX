# Licensing and release

Every FuguSTX component ships under a permissive license. This document names
the license of each component, and it states the release rules.

<a id="lic-lic"></a>

## The licenses

Decision [T1](DECISIONS.md#t1) sets the base model, and
[the corpus sources](corpus.md#cor-sources) name the data sources. The table
names the license of each component.

| Component                   | License                                                         |
| --------------------------- | --------------------------------------------------------------- |
| The harness and all tooling | ISC                                                             |
| The base model              | Apache 2.0                                                      |
| The Qwen3-32B generator     | Apache 2.0                                                      |
| The human documents         | The permissive license of each source file                      |
| The mirrors                 | ISC, and the terms of each generator must permit redistribution |
| The later-era human set     | The permissive license of each source file                      |

Each human document carries the license of its source file, and
[the corpus sources](corpus.md#cor-sources) hold the attribution of each source.
Each mirror comes from a generator of decision [T5](DECISIONS.md#t5), and it
carries [its provenance](corpus.md#cor-pairs) (COR-PAIRS-5) through
[the judge filter](training.md#trn-teach) (LIC-RELEASE-3).

- **LIC-LIC-1** — Each component must carry the license that the table names.
- **LIC-LIC-2** — The campaign must admit a generator only when its terms permit
  redistribution of its outputs, commercially included.

<a id="lic-release"></a>

## Release integrity

These rules keep the release permissive, from the data to the weights.

- **LIC-RELEASE-1** — The released model must carry attribution.
- **LIC-RELEASE-2** — Anyone can redistribute the released model, commercially
  included.
- **LIC-RELEASE-3** — A generator output must inherit
  [the training lane](corpus.md#cor-lanes) and its
  [provenance tags](corpus.md#cor-pairs).
- **LIC-RELEASE-4** — A component must not carry a non-commercial restriction.
