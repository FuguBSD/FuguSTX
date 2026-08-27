# Learning

This document holds the learning of the pilot. It records what each campaign
teaches about the FuguTTX specification. An entry is a dated record of one
campaign, and it is not a design statement. The
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

<a id="lrn-map"></a>

## The planned rehearsals

Each row of the table is a planned rehearsal, and each campaign appends
findings. One row exists for each pilot component. "The shared instructions"
names the synced [infra/CLAUDE.md](../infra/CLAUDE.md).

| Pilot component                                | FuguTTX units rehearsed                             |
| ---------------------------------------------- | --------------------------------------------------- |
| H100 quota request and grant time              | FuguTTX IAC-TRAIN, FuguTTX IAC-PREREQ               |
| Live price read before apply                   | FuguTTX IAC-PREREQ, the shared instructions         |
| State backend, native lock, encryption         | The shared instructions                             |
| Three-application credential split             | The shared instructions, FuguTTX D9                 |
| Train key over SSH, expiry backstop            | The shared instructions                             |
| Watchdog, heartbeat, claim protocol            | The shared instructions                             |
| Train stack up/down, teardown completeness     | FuguTTX IAC-TRAIN, the shared instructions          |
| Checkpoint sync per epoch                      | FuguTTX IAC-DURA, FuguTTX TRN-EXEC                  |
| Axolotl in Docker on the GPU OS image          | FuguTTX TRN-EXEC, FuguTTX D3                        |
| CPT and SFT passes end to end                  | FuguTTX TRN-CPT, FuguTTX TRN-SFT, FuguTTX D4        |
| Qwen3-32B under vLLM, SSH tunnel, judge filter | FuguTTX TRN-AUG, FuguTTX D4                         |
| Corpus lanes and bucket policies               | FuguTTX IAC-PERSIST, FuguTTX D6                     |
| KVM test and dev host selection                | FuguTTX IAC-METAL, FuguTTX IAC-DEV, FuguTTX D9      |
| Guest image build with fuguvm and autoinstall  | FuguTTX IAC-IMAGE                                   |
| llama.cpp on OpenBSD, CPU only, determinism    | FuguTTX D2, and the FuguTTX inference specification |

<a id="lrn-entries"></a>

## The entries

Each entry records what one campaign taught, with the FuguTTX units it maps to,
per [the planned rehearsals](#lrn-map). The scope rules of
[the claims](#lrn-scope) apply to every entry.

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
