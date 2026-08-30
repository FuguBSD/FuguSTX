# Campaign runbook

This runbook holds a map, not a design. It maps each shared stage name of the
workspace observer set to the verb of this project. It names the stages this
project omits, and it names the file that holds each answer.

Three files own the content. This runbook points at them, and it does not
restate them.

| File                          | Owns                                                         |
| ----------------------------- | ------------------------------------------------------------ |
| `train/config.env`            | The campaign pins and the shared names (TRN-EXEC-2).         |
| `infra/persistent/RUNBOOK.md` | The offer probe, the manual platform steps, the human steps. |
| `spec/`                       | Every design fact, the promote rule, the threshold policy.   |

## The stage map

The campaign dispatches through `.github/workflows/train.yml`, with
`gh workflow run train.yml -f action=<verb>`. The twelve `make infra-*` verbs
come from the synced `infra/CLAUDE.md`, and they are the same in every project.

| Stage      | Verb of this project                                                         | Where                         |
| ---------- | ---------------------------------------------------------------------------- | ----------------------------- |
| `infra`    | `up`, and the twelve `make infra-*` targets                                  | `train.yml`, `mk/`            |
| `corpus`   | `teach-serve`, `teach`, `teach-stop`, and the bucket sync of `CORPUS_BUCKET` | `train.yml`, `spec/corpus.md` |
| `train`    | `cpt`, `merge-cpt`, `sft-base`, `sft-cpt`, `sft-aug`                         | `train.yml`                   |
| `evaluate` | `score`, and the tier T1 sweep                                               | `train.yml`, `t1.yml`         |
| `promote`  | `promote`                                                                    | `train.yml`                   |
| `teardown` | `down`                                                                       | `train.yml`                   |

## What this project omits

This project omits no stage. It runs a CPT pass, and it has a promote step.

## The answers

- **The campaign pins.** `train/config.env`. It holds each image pin, the base
  model, and each bucket name. Confirm each pin before a campaign.
- **The offer probe and each manual platform step.**
  `infra/persistent/RUNBOOK.md`.
- **The promote rule.** TRN-EXEC-5 of `spec/training.md`. Promote copies the
  GGUF.
- **The threshold policy.** `spec/evaluation.md`. A baseline run fixes the
  thresholds.
- **The lease.** The `hours` input of `train.yml` sets the `stx:expires` tag.
  The watchdog reads it.

## The rules that the observer set adds

- Export this project's `.env` before any command that reaches Scaleway. The
  `env` block of the workspace checkout shadows every project key (Workspace
  D-05). Without the export, `tofu` bills the wrong Scaleway Project.
- State the clone and the git HEAD that each step read. A stale clone does not
  fail loudly.
- A campaign observation goes to the learning library at capture time. The
  ledger in `spec/LEARNING.md` receives one batch for each campaign.
