# The persistent stack runbook

This stack is applied. The state lives in the `stx-tofu-state` bucket, which
`infra/bootstrap` created with local state.
[The LEARNING entries](../../spec/LEARNING.md#lrn-entries) record what the first
apply taught, and the constraints it found.
[IAC-APPLY-5](../../spec/infrastructure.md#iac-apply) lists the console-made
exceptions.

## The prerequisites

Complete each step in this order, after a total loss. Steps 1 to 3 are the
console-made exceptions of IAC-APPLY-5. A human makes each one by hand, because
no stack declares it.

1. The `fugustx.prod` Scaleway Project, in the shared Organization.
2. The compute quotas. Ask Scaleway Support for a quota of 1 for each compute
   offer that `infra/dev`, `infra/train`, and `infra/image` declare, in
   `fr-par-2`. Record each granted quota here. A live probe on 2026-08-25
   created and deleted one H100-1-80G server, so that quota exists. A live probe
   on 2026-08-28 created and deleted one L40S-1-48G server, so that quota
   exists. Every other quota stays unproven.
3. The `stx.prod.claude` agent application, with its policy and its key. The
   policy takes the operator scope, per IAC-APPLY-7. Give the key a 7-day
   expiry, and hold it in one HOME profile only. The CI apply retires this
   application.
4. The `stx-tofu-state` bucket. Run `make infra-bootstrap`. `infra/bootstrap`
   declares the bucket, with versioning on and a 30-day noncurrent-version
   expiration rule. That stack keeps local state, on purpose: no remote bucket
   can back its own creation.

## Credentials

A change to this stack needs a key with the rights of the `stx.prod.operator`
policy ([the shared instructions](../CLAUDE.md#credentials)). The stack declares
no API key. Create a key by hand, on the application that needs it:

```sh
scw iam api-key create application-id=<id> expires-at=<date>
```

Put the key pair in a HOME profile of its own, per the
[shared instructions](../CLAUDE.md#credentials), and name the profile on each
command:

```sh
SCW_PROFILE=<profile> AWS_PROFILE=<profile> tofu plan ...
```

The default project of the profile must name the `fugustx.prod` Project. The
`data "scaleway_account_project" "current"` source reads it, and every IAM
policy scopes to it. A wrong value retargets the whole stack.

[The LEARNING entries](../../spec/LEARNING.md#lrn-entries) record each key and
delegation probe. The console-made policy of the `stx.prod.claude` application
carries the name `stx.prod.full`, and it holds `BillingManager` at organization
scope.

## The campaign credentials, set 2026-08-28

The pipeline key `SCWA09NTBHDBCBNASZAQ` exists on `stx.prod.pipeline`. It
expires 2026-11-26. Its `default-project-id` names `fugustx.prod`: the platform
defaults a new key to the organization default project, and the Object Storage
calls of the key then target the wrong project. Pass `default-project-id` on
each `scw iam api-key create`.

The FuguBSD/FuguSTX repository holds the CI secrets `SCW_ACCESS_KEY`,
`SCW_SECRET_KEY`, and `STX_TRAIN_SSH_KEY`, and the variables
`SCW_DEFAULT_PROJECT_ID` and `SCW_DEFAULT_ORGANIZATION_ID`. The campaign SSH key
is an ed25519 pair with the fingerprint
`SHA256:3ZFZ5Zdzq51On4VmSX/IF2y0bY1I1ESx6HwxWjK25gI`. The train stack registers
its public half as an IAM SSH key, and the key agent of the image installs it on
root at boot; only the CI secret holds the private half.

The pipeline policy holds `IAMApplicationManager` (the CI up job mints the train
key), `BlockStorageFullAccess` (an SBS root volume writes through the Block
Storage API), and `SSHKeysFullAccess` (the train stack registers the campaign
key as an IAM resource).

One human step stays open:

1. The `infra-apply` environment exists with a main-only deployment branch
   policy, and it holds the two variables. Move the three secrets into it. Until
   then, the repository scope serves the same workflows.

The price table of [training.md](../../spec/training.md#trn-inst) holds the
2026-08-28 price read.

## A change to the stack

```sh
cd infra/persistent
tofu init
tofu plan -var 'budget_alert_emails=["ops@example.invalid"]'
tofu apply -var 'budget_alert_emails=["ops@example.invalid"]'
```

Pass the true alert address in place of the placeholder. Review the plan before
the apply. Pass `-var 'budget_alert_webhook_urls=["https://..."]'` to add the CI
webhook alert channel, once that endpoint exists.

The state-bucket policy is an allow list. It names the pipeline, the operator,
and the agent application. Keep the applying principal named, per
[the LEARNING entry](../../spec/LEARNING.md#lrn-entries).

## Recovery

A crashed apply can leave a stale lock, and a console-made resource can sit
outside the state. Confirm the situation first, then:

```sh
tofu force-unlock <lock-id>          # the failed apply printed the ID
tofu import <address> <resource-id>  # adopt a resource into the state
```

Two failures need a human with console rights, because no key in the tree can
repair them:

- **The allow-list lockout.** A bucket policy that drops the applying principal
  cuts that key off from the state bucket. Every later `tofu` call then fails
  with an access error. Correct the policy in the console, and name the
  principal again.
- **A deleted agent application.** The stack reads `stx.prod.claude` through a
  data source, so a delete blocks every plan, apply, and destroy. Recreate the
  application with step 3, or remove the data source and its policy statement.
