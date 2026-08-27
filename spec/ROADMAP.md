# Roadmap

The work proceeds in phases. Each phase ends with a measurement and an entry in
[the learning](LEARNING.md#lrn-deliver), which is the FuguTTX D10 pattern. No
phase starts cloud spend before P2. Every phase is days, not weeks, because the
model is small. This scale mitigates [the sequencing risk](risks.md#rsk-seq).

| Phase | Scope                                                                                                                                                                    |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| P0    | The repository, this specification as `spec/`, and the org sync pack.                                                                                                    |
| P1    | The [data pipeline](corpus.md#cor-lanes) and the [tier T0](evaluation.md#evl-tiers) score script. Local only: no cloud resource exists.                                  |
| P2    | The [persistent stack](infrastructure.md#iac-apply), the credential split, the state backend, and the [KVM test](infrastructure.md#iac-devhost). First LEARNING entries. |
| P3    | The first [SFT campaign](training.md#trn-sft) on the H100. The baseline scorecard fixes the tier T1 gates.                                                               |
| P4    | The teacher campaign and the [judge filter](training.md#trn-teach).                                                                                                      |
| P5    | The [image stack](infrastructure.md#iac-image), the dev host, and the tier T2 [artifact suite](evaluation.md#evl-suite).                                                 |
| P6    | [`stx-ste`](engine.md#eng-ste), run against one FuguBSD repository beside the regex `ste-lint`.                                                                          |
