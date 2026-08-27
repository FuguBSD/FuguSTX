# Infrastructure

FuguSTX runs on the shared FuguBSD infrastructure design.
[The applied instructions](#iac-apply) state the substitutions and the inherited
rules. [The dev host](#iac-devhost) states the host selection.
[The image stack](#iac-image) states the guest image build.

<a id="iac-apply"></a>

## The applied instructions

The synced [infra/CLAUDE.md](../infra/CLAUDE.md) holds the shared rules: naming,
layout, tags, state, credentials, spend guardrails, and teardown. FuguSTX
applies these rules first, so FuguTTX inherits tested rules
([T9](DECISIONS.md#t9)). Rehearses: the FuguTTX IAC family.

- **IAC-APPLY-1** — The project code must be `stx`, and the tag prefix must be
  `stx:`.
- **IAC-APPLY-2** — FuguSTX must have its own Scaleway Project, in the same
  Organization. The Project must carry the name `fugustx.prod`, from the
  repository name. Only a resource inside the Project takes the `stx` code of
  IAC-APPLY-1.
- **IAC-APPLY-3** — The budget must be EUR 300 per month, with alerts at 50, 75,
  and 100 percent.
- **IAC-APPLY-4** — Every other rule of the synced instructions must apply as
  written.
- **IAC-APPLY-5** — Three items must stay outside OpenTofu. A human must make
  each one by hand. The three are the `fugustx.prod` Scaleway Project, the
  `stx.prod.claude` agent application with its policy and its key, and the
  compute quotas. [The runbook](../infra/persistent/RUNBOOK.md) must hold the
  procedure that recreates each one.
- **IAC-APPLY-6** — The operator policy and the pipeline policy must hold an
  organization-scoped rule. Scaleway offers no project scope for the IAM
  managers, for `BillingManager`, or for `BillingReadOnly`. Each key therefore
  reaches every project of the shared Organization. Only the narrow permission
  sets of that rule are acceptable at organization scope.
- **IAC-APPLY-7** — Each principal that applies `infra/persistent` must hold the
  operator scope. The state-bucket policy must name each one. An agent
  application can be such a principal, as an exception to the smallest-scope
  rule of the synced instructions. Its key must expire after 7 days, and one
  checkout must hold that key.

<a id="iac-devhost"></a>

## The dev host

The FuguTTX KVM test decides the host type. Either result closes an open
question in the FuguTTX specification.
[The LEARNING entries](LEARNING.md#lrn-entries) hold the result of the test.
Rehearses: FuguTTX IAC-METAL, FuguTTX D9.

- **IAC-DEVHOST-1** — Before the first dev stack apply, the pilot must run the
  FuguTTX KVM test: one virtual instance, one hour.
- **IAC-DEVHOST-2** — The test must check `/dev/kvm`, and it must boot one
  OpenBSD guest with `fuguvm`.
- **IAC-DEVHOST-3** — If both checks pass, the dev host must be an ephemeral
  virtual instance, cycled around each session.
- **IAC-DEVHOST-4** — If a check fails, the dev host must be the smallest
  Elastic Metal offer. The offer must run two to four parallel guests.
- **IAC-DEVHOST-5** — [The LEARNING entries](LEARNING.md#lrn-entries) must
  record the result of the test.
- **IAC-DEVHOST-6** — The dev host offer must run the parallel guests of
  [the artifact suite](evaluation.md#evl-suite). A KVM result from one guest
  does not qualify an offer.

<a id="iac-image"></a>

## The image stack

The stack makes the OpenBSD guest image. The
[artifact suite](evaluation.md#evl-suite) boots its guests from this image.

- **IAC-IMAGE-1** — The stack must build the OpenBSD guest qcow2 with `fuguvm`
  and `autoinstall(8)`, exactly as FuguTTX IAC-IMAGE specifies.
