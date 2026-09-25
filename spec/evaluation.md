# Evaluation

Three tiers measure the engine. [The tiers](#evl-tiers) define the tier table
and the metrics. [The artifact suite](#evl-suite) defines the tier T2 checks.

<a id="evl-tiers"></a>

## The tiers

Evaluation promotes a model version, and a scorecard lands in
[the artifacts bucket](corpus.md#cor-buckets). This is the FuguTTX D5 pattern.
Three tiers make the evaluation:

| Tier    | Where                        | What                                                                                                                                              |
| ------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| tier T0 | CI, CPU, every commit        | Score script on the [dev split](corpus.md#cor-lanes): balanced accuracy and category agreement                                                    |
| tier T1 | CI, CPU                      | Promotion sweep against the [eval lane](corpus.md#cor-lanes), gated: the two dev metrics, plus the false-positive rate on the later-era human set |
| tier T2 | OpenBSD guests, under FuguVM | The [artifact suite](#evl-suite)                                                                                                                  |

The baseline scorecard in [the artifacts bucket](corpus.md#cor-buckets) holds
the pins, the counts, and the model hash. The first scorecard that yields a
metric fixes its tier T1 threshold (EVL-TIERS-5). The pilot bar of
[T13](DECISIONS.md#t13) sits in this document beside the thresholds
(EVL-TIERS-10). The table below defines the three metrics, and it names the tier
of each one:

| Metric              | Definition                                                                            | Direction | Tier   |
| ------------------- | ------------------------------------------------------------------------------------- | --------- | ------ |
| Balanced accuracy   | The mean of the recall on each verdict class, per segment                             | Higher    | T0, T1 |
| False-positive rate | The share of the segments of the later-era human set with a machine verdict           | Lower     | T1     |
| Category agreement  | The share of matching categories on the segments that both sides mark machine-written | Higher    | T0, T1 |

A promotion review compares the next scorecard against the baseline scorecard by
hand, and no job reads a threshold.

- **EVL-TIERS-1** — Each promotion must write a scorecard to the artifacts
  bucket.
- **EVL-TIERS-2** — CI must run tier T0 on the CPU, on every commit. The score
  script scores the dev split on balanced accuracy and category agreement.
- **EVL-TIERS-3** — CI must run tier T1 on the CPU. The gated promotion sweep
  runs against the eval lane, and it adds the false-positive rate on the
  later-era human set.
- **EVL-TIERS-4** — The artifact suite of tier T2 must run in OpenBSD guests
  under FuguVM.
- **EVL-TIERS-5** — The first scorecard that yields a metric fixes its tier T1
  threshold. A threshold in this document before that scorecard is a guess. The
  specification must not hold a guess.
- **EVL-TIERS-6** — The score script must compute each metric from the confusion
  counts, and the scorecard must hold the counts.
- **EVL-TIERS-7** — One command must read each scorecard of the artifacts bucket
  and print the scores. The command must not hold a threshold, because the
  promotion review stays a human act.
- **EVL-TIERS-8** — A scorecard key must take the form
  `runs/<run identifier>/scorecard-<name>.json`. This document holds the one
  definition of that form. Each component that writes such a key, or reads one,
  must follow it.
- **EVL-TIERS-9** — The first scorecard of a pair corpus must score the base
  model with no training pass. Each later scorecard must compare against it.
- **EVL-TIERS-10** — The operator must set the pilot bar of decision
  [T13](DECISIONS.md#t13) after the zero-training baseline run, and this
  document must hold it. A bar before that run is a guess.

<a id="evl-suite"></a>

## The artifact suite

The suite installs the shipped artifact into OpenBSD guests that FuguVM boots
from [the project image](infrastructure.md#iac-image). The artifact is `stx`,
llama.cpp, and the model. These are the mechanics of the FuguTTX agentic suite,
minus the agent ([T8](DECISIONS.md#t8)). The suite makes five checks. Rehearses:
FuguTTX IAC-DEV, FuguTTX IAC-IMAGE.

- **EVL-SUITE-1** — The artifact must build and run under
  `pledge("stdio rpath")` and unveil.
- **EVL-SUITE-2** — Two guests must produce byte-identical findings for the same
  input. A difference fails the [determinism contract](engine.md#eng-determ).
- **EVL-SUITE-3** — Guest scores must equal host scores on a sample.
- **EVL-SUITE-4** — The suite must measure and record cold start and throughput.
  These are measurements, not gates.
- **EVL-SUITE-5** — `fuguvm snapshot restore` must return each guest to base
  between runs.
