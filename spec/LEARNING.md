# Learning

This document is the evidence ledger of the pilot. It records what each
completed rehearsal teaches about the FuguTTX specification. An entry is a
dated, append-only record with its evidence, and it is not a design statement.
[The rehearsal index](#lrn-map) points from each pilot component to its entries.
The edited set lives downstream: a finding lands in FuguTTX `docs/research/`,
and a contradiction becomes a FuguTTX specification change. The
[implementation register](STATUS.md) is a different document, and it records
implementation state.

<a id="lrn-deliver"></a>

## The learning is a deliverable

The learning is the deliverable of G2, per decision [T11](DECISIONS.md#t11).

- **LRN-DELIVER-1** — Every campaign must end with a LEARNING entry that maps
  its outcome to FuguTTX specification units.
- **LRN-DELIVER-2** — A finding must land in the FuguTTX `docs/research/`
  directory.
- **LRN-DELIVER-3** — A finding that contradicts the FuguTTX specification must
  become a FuguTTX specification change, not a note.
- **LRN-DELIVER-4** — An entry must record one completed rehearsal, with its
  evidence: a probe, an apply, a run, or a measurement. Authoring work alone
  must not produce an entry.
- **LRN-DELIVER-5** — An entry that corrects an earlier claim must name the
  entry that it corrects. Do not edit the earlier entry.

<a id="lrn-map"></a>

## The rehearsal index

One row exists for each pilot component. A row names the FuguTTX units that the
component rehearses, and the dated entries that hold its findings. An entry is
the one source of a finding: a row only points. "The shared instructions" names
the synced [infra/CLAUDE.md](../infra/CLAUDE.md).

| Pilot component                                | FuguTTX units rehearsed                             | Entries                |
| ---------------------------------------------- | --------------------------------------------------- | ---------------------- |
| H100 quota request and grant time              | FuguTTX IAC-TRAIN, FuguTTX IAC-PREREQ               | 2026-08-25             |
| Live price read before apply                   | FuguTTX IAC-PREREQ, the shared instructions         | —                      |
| Budget ownership in the shared Organization    | FuguTTX IAC-PREREQ, the shared instructions         | 2026-08-26             |
| State backend, native lock, encryption         | The shared instructions                             | 2026-08-26             |
| Three-application credential split             | The shared instructions, FuguTTX D9                 | 2026-08-25, 2026-08-26 |
| Operator network and key delivery              | The shared instructions, FuguTTX IAC-DEV            | 2026-08-26             |
| Train key over SSH, expiry backstop            | The shared instructions                             | —                      |
| Watchdog, heartbeat, claim protocol            | The shared instructions                             | —                      |
| Train stack up/down, teardown completeness     | FuguTTX IAC-TRAIN, the shared instructions          | —                      |
| Checkpoint sync per epoch                      | FuguTTX IAC-DURA, FuguTTX TRN-EXEC                  | —                      |
| Axolotl in Docker on the GPU OS image          | FuguTTX TRN-EXEC, FuguTTX D3                        | —                      |
| CPT and SFT passes end to end                  | FuguTTX TRN-CPT, FuguTTX TRN-SFT, FuguTTX D4        | —                      |
| Qwen3-32B under vLLM, SSH tunnel, judge filter | FuguTTX TRN-AUG, FuguTTX D4                         | —                      |
| Corpus lanes and bucket policies               | FuguTTX IAC-PERSIST, FuguTTX D6                     | 2026-08-26             |
| KVM test and dev host selection                | FuguTTX IAC-METAL, FuguTTX IAC-DEV, FuguTTX D9      | 2026-08-26             |
| Guest image build with fuguvm and autoinstall  | FuguTTX IAC-IMAGE                                   | —                      |
| llama.cpp on OpenBSD, CPU only, determinism    | FuguTTX D2, and the FuguTTX inference specification | —                      |

<a id="lrn-entries"></a>

## The entries

Each entry records what one rehearsal taught, with the FuguTTX units it maps to,
per [the rehearsal index](#lrn-map). The scope rules of [the claims](#lrn-scope)
apply to every entry.

### 2026-08-25 — The credential and quota probes

- **Quota by default.** A probe created and deleted one H100-1-80G server in
  `fr-par-2`, with no support request. The grant existed already, so a quota
  request has nothing to measure in this Organization. The useful procedure is a
  probe of each declared offer before a campaign, and
  [training.md](training.md#trn-inst) now states it. The same correction is a
  candidate for the FuguTTX quota prerequisite, per LRN-DELIVER-3. Scope: this
  proves the H100-1-80G offer, in this Organization, on this date. It proves no
  other offer: the L40S-1-48G quota stays unproven. Maps to: FuguTTX IAC-TRAIN,
  FuguTTX IAC-PREREQ.
- **Credential scope drift.** The agent key creates every dev, train, and image
  resource type. The platform denies the same key `billing consumption list`,
  although its policy states the operator scope. A policy document is not a
  permission: only a platform response proves authorization, as the shared
  verification rule states. [The runbook](../infra/persistent/RUNBOOK.md)
  records the probe, and the next persistent apply confirms the policy rules.
  Scope: one Organization, one policy set, one day. Maps to: the shared
  instructions, FuguTTX D9.

### 2026-08-26 — The persistent stack and the KVM test

- **State backend.** The state bucket with `use_lockfile = true` worked on the
  first init and on every apply. One trap: `tofu init -backend=false` still
  demands the backend credential in a checkout that applied the stack, so the
  validate gate needs its own `TF_DATA_DIR`. Maps to: the shared instructions.
- **Credential split.** The three applications and their policies applied. The
  shared instructions do not state one Scaleway constraint: one IAM rule holds
  permission sets of one scope type only. A policy that mixes project sets with
  `BillingReadOnly` or the IAM managers needs two rules. The second rule takes
  organization scope, so a shared Organization cannot hold a per-project IAM
  administrator. [IAC-APPLY-6](infrastructure.md#iac-apply) states the accepted
  design. Maps to: the shared instructions, FuguTTX D9.
- **Corpus buckets.** The four buckets applied with the multipart lifecycle
  rule. One trap: a bucket policy is an allow list. The principal that runs the
  apply must name itself. An unnamed principal cuts its own key off from the
  state bucket. A second trap: the versioning setting differs per bucket in the
  FuguTTX set, and the checkpoint bucket keeps it off. A per-bucket rule needs a
  per-bucket check, because `tofu validate` reads no value. A third trap: S3
  suspends versioning, and it never removes versioning. A bucket that starts
  with versioning on can never return to the unversioned state, so the correct
  setting must land at creation. Maps to: FuguTTX IAC-PERSIST, FuguTTX D6.
- **Budget.** `scaleway_billing_budget` is a resource of the Organization, not
  of a Project. Every FuguBSD project shares one Organization, so a second
  project's persistent stack collides on the same budget. The organization must
  decide budget ownership before a second apply. Maps to: FuguTTX IAC-PREREQ,
  the shared instructions.
- **Operator network.** The operator's corporate proxy resets SSH and plain HTTP
  to an IP it cannot categorize, so a workstation cannot reach a fresh instance
  directly. A presigned-URL relay through the artifacts bucket works, because
  the S3 endpoint is an allowed domain. A key-delivery step that assumes
  workstation SSH must run from CI instead. Maps to: the shared instructions,
  FuguTTX IAC-DEV.
- **KVM test.** Both checks passed on a POP2-2C-8G virtual instance in
  `fr-par-2`. `/dev/kvm` exists, with vmx on each vCPU. `fuguvm up` installed
  and booted one OpenBSD 7.8 guest in 5.5 minutes, and guest SSH answered. The
  dev host is an ephemeral virtual instance, per IAC-DEVHOST-3. Scope: this
  proves nested KVM on the POP2 range today. It proves nothing about an other
  instance range, and it is not a platform guarantee. Maps to: FuguTTX
  IAC-METAL, FuguTTX IAC-DEV, FuguTTX D9.

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
