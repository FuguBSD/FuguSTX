# Roadmap

The work proceeds in phases. Each phase ends with a measurement and an entry in
[the learning](LEARNING.md#lrn-deliver), which is the FuguTTX D10 pattern. No
phase starts cloud spend before P2. Every phase is days, not weeks, because the
model is small. This scale mitigates [the sequencing risk](risks.md#rsk-seq).

| Phase | Scope                                                                                                                                                                                                                                                                |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P0    | The repository, this specification as `spec/`, and the org sync pack.                                                                                                                                                                                                |
| P1    | The [data pipeline](corpus.md#cor-lanes) and the [tier T0](evaluation.md#evl-tiers) score script. Local only: no cloud resource exists.                                                                                                                              |
| P2    | The [persistent stack](infrastructure.md#iac-apply), the credential split, the state backend, and the [KVM test](infrastructure.md#iac-devhost). First LEARNING entries.                                                                                             |
| P3    | The first [SFT campaign](training.md#trn-sft) on the H100. The baseline scorecard fixes the tier T1 gates.                                                                                                                                                           |
| P4    | The teacher campaign and the [judge filter](training.md#trn-teach).                                                                                                                                                                                                  |
| P5    | The [image stack](infrastructure.md#iac-image), the dev host, and the tier T2 [artifact suite](evaluation.md#evl-suite).                                                                                                                                             |
| P6    | Withdrawn by decision T12: the `stx-ste` reference client beside the regex `ste-lint`.                                                                                                                                                                               |
| P7    | The training-loop instruments, the seeded noise floor on the recipe of decision T3, the CPT decision, and the recipe: the full fine-tune against the adapter, the epoch count, and the learning rate.                                                                |
| P8    | Folded into P7.                                                                                                                                                                                                                                                      |
| P9    | Withdrawn by decision T12: the anchored output format of the analyzer.                                                                                                                                                                                               |
| P10   | Withdrawn by decision T12: the silver lane of parser-labeled sentences.                                                                                                                                                                                              |
| P11   | The pair corpus: the sources at pinned tags, the memorization check, the two generators, the judge filter, and the zero-training baseline of decision T13. The baseline run fixes the tier T1 thresholds that it yields, and the operator sets the T13 bar after it. |
| P12   | The first SFT campaign on the pair corpus, against the tier T1 thresholds and the bar of phase P11. The T13 bar decides the pilot.                                                                                                                                   |
| P13   | `stx analyze` against one FuguBSD repository beside the regex `ste-lint`, and the later-era human set measurement.                                                                                                                                                   |

P11 precedes every later training phase. P7 runs on the pair corpus after P12.
P5 is independent, and a phase of it can interleave with the others.
