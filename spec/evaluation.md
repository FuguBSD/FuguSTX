# Evaluation

Three tiers measure the engine. [The tiers](#evl-tiers) define the tier table
and the thresholds. [The artifact suite](#evl-suite) defines the tier T2 checks.

<a id="evl-tiers"></a>

## The tiers

Evaluation promotes a model version, and a scorecard lands in
[the artifacts bucket](corpus.md#cor-buckets). This is the FuguTTX D5 pattern.
Three tiers make the evaluation:

| Tier    | Where                        | What                                                                   |
| ------- | ---------------------------- | ---------------------------------------------------------------------- |
| tier T0 | CI, CPU, every commit        | Score script on the [dev split](corpus.md#cor-lanes): UPOS, lemma, LAS |
| tier T1 | CI, CPU                      | Promotion sweep against the [eval lane](corpus.md#cor-lanes), gated    |
| tier T2 | OpenBSD guests, under FuguVM | The [artifact suite](#evl-suite)                                       |

- **EVL-TIERS-1** — Each promotion must write a scorecard to the artifacts
  bucket.
- **EVL-TIERS-2** — CI must run tier T0 on the CPU, on every commit. The score
  script scores the dev split on UPOS, lemma, and LAS.
- **EVL-TIERS-3** — CI must run tier T1 on the CPU. The gated promotion sweep
  runs against the eval lane.
- **EVL-TIERS-4** — The artifact suite of tier T2 must run in OpenBSD guests
  under FuguVM.
- **EVL-TIERS-5** — The first baseline run fixes each tier T1 threshold. A
  threshold in this document before that run is a guess. The specification must
  not hold a guess.

<a id="evl-suite"></a>

## The artifact suite

The suite installs the shipped artifact into OpenBSD guests that FuguVM boots
from [the project image](infrastructure.md#iac-image). The artifact is `stx`,
llama.cpp, and the model. These are the mechanics of the FuguTTX agentic suite,
minus the agent ([T8](DECISIONS.md#t8)). The suite makes five checks. Rehearses:
FuguTTX IAC-DEV, FuguTTX IAC-IMAGE.

- **EVL-SUITE-1** — The artifact must build and run under
  `pledge("stdio rpath")` and unveil.
- **EVL-SUITE-2** — Two guests must produce byte-identical annotations for the
  same input. A difference fails the
  [determinism contract](engine.md#eng-determ).
- **EVL-SUITE-3** — Guest scores must equal host scores on a sample.
- **EVL-SUITE-4** — The suite must measure and record cold start and throughput.
  These are measurements, not gates.
- **EVL-SUITE-5** — `fuguvm snapshot restore` must return each guest to base
  between runs.
