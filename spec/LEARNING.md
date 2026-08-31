# Learning

This document is the delivered ledger of the pilot. It receives one batch for
each campaign, and each batch cites the library pages that hold its evidence.
The working record is the library, the shared repository FuguBSD/Wiki, and it
holds every observation and every admitted claim.

The edited set lives downstream: a finding lands in FuguTTX `docs/research/`,
and a contradiction becomes a FuguTTX specification change. The
[implementation register](STATUS.md) is a different document, and it records
implementation state.

<a id="lrn-deliver"></a>

## The learning is a deliverable

The learning is the deliverable of G2, per decision [T11](DECISIONS.md#t11). Two
records split the work, and each rule below names the record it governs.

- **LRN-DELIVER-1** — Every campaign must end with one batch in this ledger. The
  batch maps the outcome of the campaign to FuguTTX specification units.
- **LRN-DELIVER-2** — A finding must land in the FuguTTX `docs/research/`
  directory.
- **LRN-DELIVER-3** — A finding that contradicts the FuguTTX specification must
  become a FuguTTX specification change, not a note.
- **LRN-DELIVER-4** — A batch must record one completed campaign, with its
  evidence: a probe, an apply, a run, or a measurement. Authoring work alone
  must not produce a batch.
- **LRN-DELIVER-5** — A batch that corrects an earlier claim must name the batch
  that it corrects. Do not edit the earlier batch.
- **LRN-DELIVER-6** — An observation must reach the library at capture time. The
  library is the working record, and a batch here is the delivered record.
- **LRN-DELIVER-7** — A batch must hold one section for each campaign, and each
  section must cite the library pages that hold its evidence. A batch must hold
  no per-entry prose: the library holds it.
- **LRN-DELIVER-8** — A claim that names a number, a cause, or a platform
  behavior must meet a verifier before it enters the library. Any other claim
  enters with no check.

<a id="lrn-map"></a>

## The library index

One row exists for each pilot component. A row names the FuguTTX units that the
component rehearses, and the library page that holds its claims. The library is
the repository FuguBSD/Wiki, and a page there is the one source of a claim: this
row only points. "The shared instructions" names the synced
[infra/CLAUDE.md](../infra/CLAUDE.md).

| Pilot component                                | FuguTTX units rehearsed                             | Library page                           |
| ---------------------------------------------- | --------------------------------------------------- | -------------------------------------- |
| H100 quota request and grant time              | FuguTTX IAC-TRAIN, FuguTTX IAC-PREREQ               | `Library-FuguSTX-quota`                |
| Live price read before apply                   | FuguTTX IAC-PREREQ, the shared instructions         | `Library-FuguSTX-price`                |
| Budget ownership in the shared Organization    | FuguTTX IAC-PREREQ, the shared instructions         | `Library-FuguSTX-budget`               |
| State backend, native lock, encryption         | The shared instructions                             | `Library-FuguSTX-state-backend`        |
| Three-application credential split             | The shared instructions, FuguTTX D9                 | `Library-FuguSTX-credentials`          |
| Operator network and key delivery              | The shared instructions, FuguTTX IAC-DEV            | `Library-FuguSTX-operator-network`     |
| Train key over SSH, expiry backstop            | The shared instructions                             | `Library-FuguSTX-ssh-delivery`         |
| Watchdog, heartbeat, claim protocol            | The shared instructions                             | `Library-FuguSTX-watchdog`             |
| Train stack up/down, teardown completeness     | FuguTTX IAC-TRAIN, the shared instructions          | `Library-FuguSTX-train-stack`          |
| Checkpoint sync per epoch                      | FuguTTX IAC-DURA, FuguTTX TRN-EXEC                  | `Library-FuguSTX-checkpoints`          |
| Axolotl in Docker on the GPU OS image          | FuguTTX TRN-EXEC, FuguTTX D3                        | `Library-FuguSTX-axolotl`              |
| CPT and SFT passes end to end                  | FuguTTX TRN-CPT, FuguTTX TRN-SFT, FuguTTX D4        | `Library-FuguSTX-passes`               |
| Promotion and the artifacts scorecard          | FuguTTX D5, FuguTTX TRN-EXEC                        | `Library-FuguSTX-promotion`            |
| Qwen3-32B under vLLM, SSH tunnel, judge filter | FuguTTX TRN-AUG, FuguTTX D4                         | `Library-FuguSTX-teacher-augmentation` |
| Corpus lanes and bucket policies               | FuguTTX IAC-PERSIST, FuguTTX D6                     | `Library-FuguSTX-corpus-buckets`       |
| KVM test and dev host selection                | FuguTTX IAC-METAL, FuguTTX IAC-DEV, FuguTTX D9      | `Library-FuguSTX-kvm-devhost`          |
| Guest image build with fuguvm and autoinstall  | FuguTTX IAC-IMAGE                                   | `Library-FuguSTX-guest-image`          |
| llama.cpp at a pinned build, CPU inference     | FuguTTX D2, and the FuguTTX inference specification | `Library-FuguSTX-llamacpp`             |
| llama.cpp on OpenBSD, determinism              | FuguTTX D2, and the FuguTTX inference specification | `Library-FuguSTX-openbsd-inference`    |

<a id="lrn-entries"></a>

## The delivered batches

Each batch records one campaign. It states the outcome, and it cites the library
pages that hold the evidence. A batch holds no per-entry prose (LRN-DELIVER-7).

### Batch 1 — the phase P3 campaigns, through 2026-08-29

The pilot rehearsed the FuguTTX production pipeline end to end at 0.6B, on the
same components, at real prices. The campaign promoted `sft-cpt`, and the tier
T1 sweep fixed the thresholds of [evaluation.md](evaluation.md).

Outcome by FuguTTX unit:

- **FuguTTX IAC-PREREQ, FuguTTX IAC-TRAIN** — Both declared offers hold a quota
  by default in this Organization, so a quota request measures nothing here. A
  recorded price goes stale, and only the pre-apply read counts. Evidence:
  `Library-FuguSTX-quota`, `Library-FuguSTX-price`, `Library-FuguSTX-budget`.
- **FuguTTX D9, the shared instructions** — A policy document is not a
  permission. An IAM rule holds permission sets of one scope type only, so a
  shared Organization cannot hold a per-project IAM administrator. Evidence:
  `Library-FuguSTX-credentials`, `Library-FuguSTX-state-backend`,
  `Library-FuguSTX-operator-network`.
- **FuguTTX IAC-TRAIN** — A correct boot takes 66 s and a teardown 39 s. A
  failed apply leaks adoptable state, and it bills until a teardown dispatch.
  Evidence: `Library-FuguSTX-train-stack`, `Library-FuguSTX-ssh-delivery`.
- **The shared instructions** — The claim protocol works on this platform, and
  the heartbeat survives a dropped session. A cron schedule is best effort, and
  the expiry tag carries the guarantee. Evidence: `Library-FuguSTX-watchdog`.
- **FuguTTX TRN-CPT, FuguTTX TRN-SFT, FuguTTX D4** — The CPT pass earns its
  place at 0.6B. The training cost is deterministic and measured. Evidence:
  `Library-FuguSTX-passes`, `Library-FuguSTX-axolotl`,
  `Library-FuguSTX-checkpoints`.
- **FuguTTX D2, FuguTTX D5, the FuguTTX inference specification** — A promote
  must not need the instance. A pin change needs a probe of each transport.
  Evidence: `Library-FuguSTX-promotion`, `Library-FuguSTX-llamacpp`.
- **FuguTTX IAC-PERSIST, FuguTTX D6** — A bucket policy is an allow list, and a
  per-bucket setting needs a per-bucket check. Evidence:
  `Library-FuguSTX-corpus-buckets`.
- **FuguTTX IAC-METAL, FuguTTX IAC-DEV** — Nested KVM works on the POP2 range.
  Evidence: `Library-FuguSTX-kvm-devhost`.

Not rehearsed: FuguTTX TRN-AUG, FuguTTX IAC-IMAGE, and llama.cpp on OpenBSD.

Delivery: LRN-DELIVER-2 and LRN-DELIVER-3 stay open for this batch. The findings
have not reached the FuguTTX `docs/research/` directory yet, and the
contradictions have not become FuguTTX specification changes yet.

### Batch 2 — the phase P4 teacher campaign, through 2026-08-31

The campaign ran the teacher augmentation end to end, on the run
`gh-33342320766`. The judge filter accepted 111 of 1200 proposed records, the
sft-aug pass trained on them, and the promote gate kept `sft-cpt`.

Outcome by FuguTTX unit:

- **FuguTTX TRN-AUG, FuguTTX D4** — The teacher proposed six batches of 200, and
  the filter accepted 111 of 1200, a rate of 0.0925 (per batch 0.055 to 0.135).
  Check 1, the agreement of the two seeded annotation passes, rejected 149 to
  160 records per batch. That gate rejects six times more than the other checks
  together. The other rejects per batch: tag 7 to 14, tree 7 to 15, word 4 to
  10, and count 0 to 1. The teacher repeats sentences across batch seeds at
  temperature 0.9. The rebuild deduplication therefore absorbed 12 of the 96
  accepted records of batches 2 to 6. An independent comparator, with a passed
  sensitivity test, found zero overlap between the 111 accepted sentences and
  the 4310 eval-lane records, verbatim and normalized. Evidence:
  `Library-FuguSTX-teacher-augmentation`.
- **FuguTTX TRN-AUG, the shared instructions** — The first serve on a fresh
  instance took near six minutes: a 72 s image pull, then 290 s to the health
  answer. The health answer alone confirms the FP8 fit. The driver starts the
  container detached, and no verb fetches a container log, so the CI path
  captures no GPU memory number. The container binds 127.0.0.1:8000 on the
  instance, and the teach client reaches the endpoint over the SSH tunnel. A
  driver log line prints the boot STX_RUN_ID, not the dispatching workflow run.
  Evidence: `Library-FuguSTX-teacher-augmentation`,
  `Library-FuguSTX-train-stack`.
- **FuguTTX TRN-SFT, FuguTTX D4** — The sft-aug pass trained on 22222 pairs: 464
  steps, train_runtime 813.5 s, and a loss from 2.881 to 0.0486. The tier T1
  sweep passed eight of nine cells, and the ewt lemma cell failed by 0.0003. The
  scores (UPOS/Lemma/LAS): ewt 0.9377/0.9506/0.7738, gum 0.9386/0.9569/0.7673,
  and pud 0.9543/0.9637/0.7848. Evidence: `Library-FuguSTX-passes`.
- **FuguTTX D5** — The promote gate blocked the promote on the one failed cell,
  and `sft-cpt` stays the promoted artifact. Evidence:
  `Library-FuguSTX-promotion`.
- **FuguTTX IAC-PREREQ** — The campaign compute cost EUR 11.27: 3.93 hours at
  EUR 2.8665 per hour, under the teacher-row estimate alone. Evidence:
  `Library-FuguSTX-price`, `Library-FuguSTX-budget`, `Library-FuguSTX-watchdog`.

Not rehearsed: FuguTTX IAC-IMAGE, and llama.cpp on OpenBSD.

Delivery: LRN-DELIVER-2 and LRN-DELIVER-3 stay open for this batch.

<a id="lrn-scope"></a>

## The scope of a claim

Each entry must scope every claim, because these FuguTTX risks stay open after
the pilot:

- The author-copyright eval lane, and its licensing handling. Every FuguSTX
  input carries [a permissive license](licensing.md#lic-lic).
- Training dynamics at 4B: multi-hour epochs, checkpoint sizes that stress the
  bucket rules, catastrophic forgetting, and replay mixes.
- Agentic traces: tool calls, rollouts against mutable guests, and the
  fabricated-observation risk. The guests of the pilot
  [verify an artifact](evaluation.md#evl-suite), and they never host an agent.
- RAG, variants, and personas.

A 0.6B result does not predict a 4B result. Each entry must say what a finding
is evidence for, and what it is not.
