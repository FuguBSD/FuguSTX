# 002 — Persistent stack, credential split, state backend, and KVM test

Implements: IAC-APPLY, IAC-DEVHOST, COR-BUCKETS, REG-DELIVER without
REG-DELIVER-2

Defers: IAC-IMAGE

## Status

The persistent stack and the KVM test can land now. No decision blocks this
plan.

Three prerequisites wait on a human, before the first apply:

- A human creates the `stx` Scaleway Project in the shared Organization.
- A human asks Scaleway Support for the quotas of `infra/persistent` and of the
  KVM test instance, in `fr-par-2`.
- A human sets the EUR 300 monthly budget and its three alerts, and holds the
  Operator key.

REG-DELIVER-2 sends a finding to the FuguTTX `docs/research/` directory. That
directory lives in the FuguTTX repository, so this plan excludes it: a FuguTTX
plan lands that change.

IAC-IMAGE — the guest image stack — waits for phase P5. This plan touches the
`infra/image` root only to create the empty stack skeleton, per
[the shared layout](../../infra/CLAUDE.md#layout). It does not apply the stack.

## Order of work

1. Bootstrap the state bucket with `make infra-bootstrap`, by hand, once.
2. Add `infra/persistent`: the three IAM applications and their policies, the
   four corpus buckets, the budget, and the alerts. Apply it with the Operator
   key, under human review.
3. Add the empty `infra/dev`, `infra/train`, and `infra/image` root modules.
   Give each module `versions.tf`, `backend.tf`, `providers.tf`, `variables.tf`,
   `outputs.tf`, and `locals.tf`, per
   [the shared layout](../../infra/CLAUDE.md#layout).
4. Wire `make infra-fmt-check`, `make infra-validate`, and `make infra-check`
   into `make check`.
5. Run the KVM test from `infra/dev`: one virtual instance, for one hour. Check
   `/dev/kvm`, and boot one OpenBSD guest under `fuguvm`.
6. Record the KVM test result. Set the dev host type of `infra/dev` accordingly.
   Choose an ephemeral virtual instance, or the smallest Elastic Metal offer
   with two to four parallel guests.
7. Write the first register entries: the state backend, the credential split,
   the corpus buckets, and the KVM test result. Map each entry to its FuguTTX
   units, per [REG-MAP](../../spec/register.md#reg-map).
8. Set STATUS.md: IAC-APPLY, IAC-DEVHOST, COR-BUCKETS, and REG-DELIVER move to
   `done`. Add a note to each entry that links the code or the register entries.

## Bucket policy note

COR-BUCKETS-1 names the four buckets. This plan creates them in
`infra/persistent`, with the versioning and the lifecycle rules of
[the shared instructions](../../infra/CLAUDE.md#buckets), per COR-BUCKETS-2. The
corpus lanes and the license lane of `corpus.md` stay out of scope. They read
and write objects, and they do not change the bucket stack.

## Open question

The KVM test result decides the dev host type. This plan cannot state the result
before the test runs. It states both branches, IAC-DEVHOST-3 and IAC-DEVHOST-4.
The register entry of step 7 records which branch applies.
