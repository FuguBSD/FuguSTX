# Implementation register

This register is the one record of implementation state. One row exists for each
unit of the specification. A unit is one design element of one specification
document. The [conventions](index.md#conventions) define the unit IDs. Each row
describes the current state only. A row must not carry a plan name or a
reference to an earlier state. A note can carry the date of a recorded fact.

The learning register of [register.md](register.md) is a different document. It
records what each campaign teaches about the FuguTTX specification.

## States

| State   | Meaning                                                              |
| ------- | -------------------------------------------------------------------- |
| open    | No code implements the unit.                                         |
| partial | Code implements a part of the unit. The note names each absent part. |
| done    | Code implements the full unit. The note links the code or the tests. |
| n-a     | No code can implement the unit. It exists for citation only.         |

The "Done by" column names a phase of the [roadmap](ROADMAP.md), or "—" when no
phase applies.

## Units

| Unit                                         | State | Done by | Note                                   |
| -------------------------------------------- | ----- | ------- | -------------------------------------- |
| [ENG-SPLIT](engine.md#eng-split)             | open  | —       | —                                      |
| [ENG-SCHEMA](engine.md#eng-schema)           | open  | —       | —                                      |
| [ENG-DETERM](engine.md#eng-determ)           | open  | —       | —                                      |
| [ENG-CONTRACT](engine.md#eng-contract)       | open  | —       | —                                      |
| [ENG-IFACE](engine.md#eng-iface)             | open  | —       | —                                      |
| [ENG-LEXICON](engine.md#eng-lexicon)         | open  | —       | —                                      |
| [ENG-STE](engine.md#eng-ste)                 | open  | —       | —                                      |
| [COR-BUCKETS](corpus.md#cor-buckets)         | open  | —       | —                                      |
| [COR-LANES](corpus.md#cor-lanes)             | open  | —       | —                                      |
| [COR-AUG](corpus.md#cor-aug)                 | open  | —       | —                                      |
| [TRN-INST](training.md#trn-inst)             | open  | —       | —                                      |
| [TRN-CPT](training.md#trn-cpt)               | open  | —       | —                                      |
| [TRN-SFT](training.md#trn-sft)               | open  | —       | —                                      |
| [TRN-TEACH](training.md#trn-teach)           | open  | —       | —                                      |
| [TRN-EXEC](training.md#trn-exec)             | open  | —       | —                                      |
| [TRN-BUDGET](training.md#trn-budget)         | open  | —       | —                                      |
| [EVL-TIERS](evaluation.md#evl-tiers)         | open  | —       | —                                      |
| [EVL-SUITE](evaluation.md#evl-suite)         | open  | —       | —                                      |
| [IAC-APPLY](infrastructure.md#iac-apply)     | open  | —       | —                                      |
| [IAC-DEVHOST](infrastructure.md#iac-devhost) | open  | —       | —                                      |
| [IAC-IMAGE](infrastructure.md#iac-image)     | open  | —       | —                                      |
| [REG-DELIVER](register.md#reg-deliver)       | open  | —       | —                                      |
| [REG-MAP](register.md#reg-map)               | n-a   | —       | Citation only. The planned rehearsals. |
| [REG-SCOPE](register.md#reg-scope)           | n-a   | —       | Citation only. A constraint on claims. |
| [LIC-LIC](licensing.md#lic-lic)              | open  | —       | —                                      |
| [LIC-RELEASE](licensing.md#lic-release)      | open  | —       | —                                      |
| [RSK-ACC](risks.md#rsk-acc)                  | n-a   | —       | Citation only.                         |
| [RSK-DETERM](risks.md#rsk-determ)            | n-a   | —       | Citation only.                         |
| [RSK-FINDINGS](risks.md#rsk-findings)        | n-a   | —       | Citation only.                         |
| [RSK-SCOPE](risks.md#rsk-scope)              | n-a   | —       | Citation only.                         |
| [RSK-SEQ](risks.md#rsk-seq)                  | n-a   | —       | Citation only.                         |

## Update protocol

1. The change that implements a unit, or a part of a unit, sets the state of the
   unit in this register, in the same change.
2. A `partial` note names each absent rule or part.
3. A `done` note holds at least one relative link to code or to tests.

## Code roots

The drift gate maps each document to the code that implements it. No code
exists, so every value is "—". Set the roots when the layout lands.

| Document          | Roots |
| ----------------- | ----- |
| engine.md         | —     |
| corpus.md         | —     |
| training.md       | —     |
| evaluation.md     | —     |
| infrastructure.md | —     |
| register.md       | —     |
| licensing.md      | —     |
| risks.md          | —     |

## Retired IDs

| ID  |
| --- |
