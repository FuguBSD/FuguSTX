# The persistent stack runbook

This stack needs the Operator key
([the shared instructions](../CLAUDE.md#credentials)). An agent must not run
these steps. `scw account project list` and `scw iam api-key list` fail with
"insufficient permissions" under the Agent key of this checkout, by design.

Only `make infra-fmt-check`, `make infra-validate`, and `make infra-check` exist
today. Neither needs a credential. Every other command below is a direct `tofu`
call. This repository has not yet added the rest of
[the shared task runner](../CLAUDE.md#task-runner): no stack held a resource to
run it against, before this change.

## Before the first apply

A human completes each step once, in order:

1. Create the `stx` Scaleway Project in the shared Organization.
2. Ask Scaleway Support for a quota of 1 for each compute offer that
   `infra/dev`, `infra/train`, and `infra/image` will declare, in `fr-par-2`.
3. Hold the Operator key: `SCW_ACCESS_KEY`, `SCW_SECRET_KEY`,
   `SCW_DEFAULT_PROJECT_ID`, and `SCW_DEFAULT_ORGANIZATION_ID`, scoped to the
   `stx` Project.
4. Run `make infra-bootstrap`. It creates the `stx-tofu-state` bucket that every
   stack's `backend.tf` names, with versioning on and a 30-day
   noncurrent-version expiration rule. `infra/bootstrap` keeps local state, on
   purpose: no remote bucket can back its own creation.

## The first apply

```sh
export SCW_ACCESS_KEY=...
export SCW_SECRET_KEY=...
export SCW_DEFAULT_PROJECT_ID=...
export SCW_DEFAULT_ORGANIZATION_ID=...

cd infra/persistent
tofu init
tofu plan -var 'budget_alert_emails=["ops@example.invalid"]'
tofu apply -var 'budget_alert_emails=["ops@example.invalid"]'
```

Review the plan before the apply. The apply creates the three IAM applications,
their policies, the four corpus buckets, the state-bucket policy, and the EUR
300 budget with its three alerts (IAC-APPLY-3).

It creates no API key. Create the Pipeline and Operator keys by hand, on their
application, per [the shared instructions](../CLAUDE.md#credentials).

It sends each alert to email only. Pass
`-var 'budget_alert_webhook_urls=["https://..."]'` to add the CI webhook
channel, once that endpoint exists.

**A shared-Organization risk:** `scaleway_billing_budget` is a resource of the
Organization, not of a Project. The FuguBSD Organization holds every project's
Project, so a second project's `infra/persistent` that applies this same pattern
will collide with this one, on the same budget. Resolve this org-wide, before a
second project's persistent stack applies its budget.

## After the apply

1. Run the KVM test of [IAC-DEVHOST](../../spec/infrastructure.md#iac-devhost):
   one virtual instance, one hour, in `infra/dev`.
2. Write the first register entries, per
   [REG-MAP](../../spec/register.md#reg-map).
3. Set `spec/STATUS.md`: move IAC-APPLY, IAC-DEVHOST, COR-BUCKETS, and
   REG-DELIVER to `done`. Add a note to each entry that links the applied
   resources, or the register entries.
