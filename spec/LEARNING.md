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

| Pilot component                                | FuguTTX units rehearsed                             | Entries                            |
| ---------------------------------------------- | --------------------------------------------------- | ---------------------------------- |
| H100 quota request and grant time              | FuguTTX IAC-TRAIN, FuguTTX IAC-PREREQ               | 2026-08-25, 2026-08-28             |
| Live price read before apply                   | FuguTTX IAC-PREREQ, the shared instructions         | 2026-08-28                         |
| Budget ownership in the shared Organization    | FuguTTX IAC-PREREQ, the shared instructions         | 2026-08-26                         |
| State backend, native lock, encryption         | The shared instructions                             | 2026-08-26                         |
| Three-application credential split             | The shared instructions, FuguTTX D9                 | 2026-08-25, 2026-08-26, 2026-08-28 |
| Operator network and key delivery              | The shared instructions, FuguTTX IAC-DEV            | 2026-08-26                         |
| Train key over SSH, expiry backstop            | The shared instructions                             | 2026-08-28, 2026-08-29             |
| Watchdog, heartbeat, claim protocol            | The shared instructions                             | 2026-08-28, 2026-08-29             |
| Train stack up/down, teardown completeness     | FuguTTX IAC-TRAIN, the shared instructions          | 2026-08-28, 2026-08-29             |
| Checkpoint sync per epoch                      | FuguTTX IAC-DURA, FuguTTX TRN-EXEC                  | 2026-08-28, 2026-08-29             |
| Axolotl in Docker on the GPU OS image          | FuguTTX TRN-EXEC, FuguTTX D3                        | 2026-08-28                         |
| CPT and SFT passes end to end                  | FuguTTX TRN-CPT, FuguTTX TRN-SFT, FuguTTX D4        | 2026-08-28                         |
| Promotion and the artifacts scorecard          | FuguTTX D5, FuguTTX TRN-EXEC                        | 2026-08-29                         |
| Qwen3-32B under vLLM, SSH tunnel, judge filter | FuguTTX TRN-AUG, FuguTTX D4                         | —                                  |
| Corpus lanes and bucket policies               | FuguTTX IAC-PERSIST, FuguTTX D6                     | 2026-08-26                         |
| KVM test and dev host selection                | FuguTTX IAC-METAL, FuguTTX IAC-DEV, FuguTTX D9      | 2026-08-26                         |
| Guest image build with fuguvm and autoinstall  | FuguTTX IAC-IMAGE                                   | —                                  |
| llama.cpp at a pinned build, CPU inference     | FuguTTX D2, and the FuguTTX inference specification | 2026-08-28, 2026-08-29             |
| llama.cpp on OpenBSD, determinism              | FuguTTX D2, and the FuguTTX inference specification | —                                  |

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

### 2026-08-28 — The campaign prerequisites

- **L40S quota by default.** A probe created and deleted one L40S-1-48G server
  in `fr-par-2`, with no support request. Both declared offers of the train
  stack now hold a proven quota. Scope: this Organization, this date. Maps to:
  FuguTTX IAC-TRAIN, FuguTTX IAC-PREREQ.
- **The train-key mint needs an IAM permission.** The shared instructions say
  that CI creates the train key at `make infra-up STACK=train`, with the
  pipeline credential. They do not say that the pipeline policy then needs an
  IAM write. A probe proved that `IAMApplicationManager` covers api-key create
  and delete on an application, so the pipeline policy takes that set in its
  organization-scoped rule. The set also mints keys on the operator application.
  [IAC-APPLY-6](infrastructure.md#iac-apply) accepts that trade at organization
  scope. The gap is a candidate correction for the shared instructions, per
  LRN-DELIVER-3. Maps to: the shared instructions, FuguTTX D9.
- **A minted key defaults to the wrong project.** `scw iam api-key create`
  without `default-project-id` binds the key to the organization default
  project, and the Object Storage calls of the key then target that project.
  Every mint must pass `default-project-id`. Maps to: the shared instructions,
  FuguTTX D9.
- **The agent billing read passes.** This entry corrects the credential scope
  drift claim of the 2026-08-25 entry: a consumption read with the agent key
  passed on 2026-08-28, and the pipeline key read the same data. The 2026-08-25
  denial did not reproduce, so the drift is closed without a policy change.
  Scope: one read per key, one day. Maps to: the shared instructions, FuguTTX
  D9.
- **The live price moved.** The price read gave EUR 2.8665 per hour for the
  H100-1-80G, against EUR 2.73 in the earlier table, and EUR 1.4699 for the
  L40S-1-48G. A recorded price goes stale in weeks: only the pre-apply read
  counts. Maps to: FuguTTX IAC-PREREQ, the shared instructions.
- **The lanes and the pairs are in the buckets.** The upload wrote 32,516
  training-lane records, 22,123 SFT pairs, and 7,009 prose paragraphs to
  `stx-corpus`. The eval lane holds 4,310 sentences in `stx-evalcorpus`. The
  keys are flat, and a manifest records the `r2.18` tag. Maps to: FuguTTX
  IAC-PERSIST, FuguTTX D6.
- **The conditional write holds.** A probe wrote one object with
  `If-None-Match: *`: the first PUT gave 200, and the second gave 412. The
  delete gave 204, and a read after it gave 404. The claim protocol of the
  shared instructions works on this platform. Maps to: the shared instructions,
  FuguTTX TRN-EXEC.

### 2026-08-28 — The first SFT campaign (run gh-33203797910)

- **The GPU OS image needs the SBS variant.** The default marketplace image
  resolves an l_ssd snapshot, and a server create on an SBS root volume fails:
  "requested volume type does not match the snapshot type, use 'l_ssd' instead"
  (run 33200578308). `image_type = "instance_sbs"` on the data source fixes it
  (`cb94371`). Scope: label `ubuntu_noble_gpu_os_13_nvidia`, fr-par-2, provider
  v2.81.0. Maps to: FuguTTX IAC-TRAIN.
- **An SBS root volume needs a Block Storage permission.** `InstancesFullAccess`
  alone gave "insufficient permissions: write volume" at server create (run
  33200948479). The pipeline policy needs `BlockStorageFullAccess` (`fd5db81`).
  Maps to: the shared instructions, FuguTTX D9.
- **Root key delivery goes through IAM, not cloud-init.** Two probes left root
  without the key: the SSH wait loop burned ~11 minutes of "Permission denied
  (publickey)" each time (runs 33201226106 and 33202448810). The key agent of
  the image writes `/root/.ssh/authorized_keys` from the registered project
  keys, and it overrides cloud-init. The fix registers
  `scaleway_iam_ssh_key.campaign` before the boot, and it grants the pipeline
  `SSHKeysFullAccess` (`0a12801`). A cloud-init template fix also needs a fresh
  boot: user_data applies at first boot only, so each retry costs a down/up
  cycle. Caution: the first fix (`9363eee`, a cloud-init `users:` block) matched
  the symptom, not the mechanism, and the error came back unchanged. Maps to:
  the shared instructions, FuguTTX IAC-TRAIN, FuguTTX D9.
- **A correct boot is fast, and a teardown is faster.** The good `up` ran 66 s
  end to end: server create 20 s, boot to SSH ~30 s, then the key mint and
  delivery ("up: run gh-33203797910 on 151.115.147.162 expires at
  2026-08-28T23:25:37Z"). Each teardown ran 30–47 s, with a constant 18 s server
  destroy, the key delete, and the claim release. The lease clock starts at
  dispatch, not at boot. Maps to: FuguTTX IAC-TRAIN.
- **A failed apply leaks adoptable state.** Attempt 1 created the IP and the
  scratch volume before the server create failed; attempt 2 adopted and retagged
  both ("Plan: 1 to add, 2 to change, 0 to destroy"). A half-up stack bills
  until a `down` dispatch; the watchdog is not the cleanup path (see the
  watchdog-reap entry of 2026-08-29). Maps to: the shared instructions, FuguTTX
  IAC-TRAIN.
- **Training cost at 0.6B, measured.** CPT, one epoch over 7,009 prose
  paragraphs: 8 optimizer steps, 18.8 s train time, final loss 5.97, a 2m01s
  job. Each SFT pass ran two epochs over 22,123 pairs: 464 steps, ~813 s, 1.48e4
  tokens/s per GPU. The final losses: 0.187 (base) and 0.185 (cpt), at 29.66 GiB
  peak memory. The two SFT wall clocks differ by 0.5 s: the cost is
  deterministic. GGUF conversion: ~90 s. Dev scoring: 28–31 min per model. The
  full matrix used ~2 h of the 4-hour lease, retries included. Scope:
  Qwen3-0.6B-Base with LoRA on one H100-1-80G; this predicts no 4B number. Maps
  to: FuguTTX TRN-CPT, FuguTTX TRN-SFT, FuguTTX TRN-EXEC, FuguTTX D4.
- **The CPT pass stays (TRN-CPT-2).** `sft-cpt` beats `sft-base` on every dev
  metric — ewt LAS 0.7725 versus 0.7488, gum LAS 0.7652 versus 0.7555 — and cuts
  the parse failures (ewt 80→47, gum 25→19). The campaign promotes `sft-cpt`,
  and training.md keeps the CPT pass. Scope: one run, dev split, 0.6B, UD r2.18,
  llama b10666. Maps to: FuguTTX TRN-CPT, FuguTTX D4.
- **Axolotl in Docker and the checkpoint sync work.** Cloud-init pre-pulls the
  Axolotl image (`main-20260827-py3.12-cu130-2.12.1`) during the SSH wait, and
  the AWS bundled installer supplies awscli, which Ubuntu Noble does not
  package. Each pass synced its checkpoints to Object Storage (checkpoint-232
  and checkpoint-464 per SFT pass; the bucket listing confirms both). A clean
  CPT run doubles as the cloud-init probe. Maps to: FuguTTX TRN-EXEC, FuguTTX
  D3, FuguTTX IAC-DURA.
- **ghcr publishes llama.cpp tags with gaps.** The pinned `full-b10665` never
  existed (docker exit 125); the tags jump b10644 → b10666 across 11,004 tags,
  and the unauthenticated first registry page truncates at b5350. Pin a tag only
  after a paginated registry probe (`ceb0f5c`). Maps to: FuguTTX TRN-EXEC.
- **q8_0 conversion works on Qwen3 directly.** The feared fallback (f16, then
  `llama-quantize`) never ran: the converter wrote `torch.bfloat16 --> Q8_0`, a
  633 MB artifact at 174 MB/s. Maps to: FuguTTX D2, the FuguTTX inference
  specification.
- **The runner NAT kills a silent SSH stream at ten minutes.** Dev scoring emits
  nothing while it runs; the stream broke 9m46s after the last output
  ("client_loop: send disconnect: Broken pipe", run 33207137344). Keepalives fix
  it (`ServerAliveInterval=30`, `ServerAliveCountMax=10`, `4d0baf6`). A dead
  scoring session also leaves its `stx-llama` container behind, so `serve`
  sweeps it first. Every quiet remote step needs both. Maps to: the shared
  instructions, FuguTTX TRN-EXEC.
- **The heartbeat and the claim survive a dropped session.** Each remote step
  starts its own idempotent writer; after the broken pipe the claim held, and
  the retry ran on the same stack three minutes later. The watchdog never
  threatened the stack. Maps to: the shared instructions.
- **The forecast gate works.** The gate printed "forecast: go: EUR 1.23 consumed
  plus EUR 11.47 forecast stays under the EUR 300.00 budget" before the good
  boot, at the live price of EUR 2.8665 per hour. Boot friction cost about EUR
  3, and the whole campaign cost about EUR 21. Maps to: FuguTTX IAC-PREREQ, the
  shared instructions.

### 2026-08-29 — The watchdog reap

- **GitHub cron is best effort, measured.** The watchdog declares a 30-minute
  cron; between 18:00 and 02:00 UTC only 2 of 16 slots fired, 7 and 18 minutes
  late. The expired stack lived 2 h 23 m past `stx:expires` (~EUR 6.8 of idle
  H100) before the reap (run 33227369925: "the time passes stx:expires"). The
  tag backstop carried the guarantee, exactly as the workflow comment predicts.
  Dispatch `down` at the end of the work; the schedule alone is best effort.
  Scope: sixteen slots of one night, in one repository; the skip rate can differ
  elsewhere. Maps to: the shared instructions, FuguTTX IAC-TRAIN.
- **Teardown completeness holds under the watchdog.** The reap destroyed all
  four resources (server, scratch volume, IAM key, IP) in 39 s, deleted the
  train keys, released the claim, and printed "the destroy is confirmed: no
  train server remains". Maps to: FuguTTX IAC-TRAIN, the shared instructions.

### 2026-08-29 — The stackless promote and the tier T1 baseline

- **A promote must not need the instance.** The scratch volume dies with the
  stack, and an SSH promote path dies with it. The GGUF survives, because the
  gguf step uploads it to the checkpoint bucket at once. `scripts/train promote`
  now copies it to the artifacts bucket on the runner, and the dev scorecard
  `model_hash` gates the copy (TRN-EXEC-5). The promote of `sft-cpt` ran
  stackless (run 33240656338), and the hash matched. Maps to: FuguTTX TRN-EXEC,
  FuguTTX D5.
- **llama.cpp split its CLI, and the pin crossed the split.** At b10666,
  `llama-cli` is a chat tool: it rejects `-no-cnv`, and its chat template would
  wrap the raw prompt. The raw one-shot tool is now `llama-completion`, and the
  end marker arrives as " [end of text]" with a leading space. The first sweep
  dispatch failed on all twelve shards in under a minute at zero GPU cost (run
  33240741185); a local probe with the promoted GGUF proved the fix. The server
  transport never sees the flag, so the dev scoring missed the break: each
  transport needs its own probe after a pin change. Maps to: FuguTTX D2, FuguTTX
  TRN-EXEC, the FuguTTX inference specification.
- **The tier T1 baseline ran on free CPU shards.** Twelve CI shards swept the
  4,310-sentence eval lane in 71 minutes wall clock (run 33241110946). Each
  shard ran 36–71 minutes on four threads, with no GPU and no instance. The
  aggregate scorecard: ewt LAS 0.7719, UPOS 0.9354, lemma 0.9509, 46 failures;
  gum LAS 0.7647, UPOS 0.9310, lemma 0.9492, 24 failures; pud LAS 0.7817, UPOS
  0.9515, lemma 0.9613, 6 failures. The ewt and gum eval scores sit within 0.001
  of the dev scores (LAS 0.7719 versus 0.7725, and 0.7647 versus 0.7652). The
  dev split therefore predicted the eval lane on the shared treebanks; pud has
  no dev split. evaluation.md holds each value as the tier T1 threshold
  (EVL-TIERS-5). Scope: one model, 0.6B at Q8_0, UD r2.18, llama b10666, greedy
  CPU decoding. Maps to: FuguTTX D2, FuguTTX D5, the FuguTTX inference
  specification.

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
