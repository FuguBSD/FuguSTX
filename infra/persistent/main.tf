# The current project: the one the Operator's credential targets. No
# UUID is hardcoded here; the project ID comes from SCW_DEFAULT_PROJECT_ID.
data "scaleway_account_project" "current" {}

# Three IAM applications split the credentials by blast radius. This
# stack declares each application and each policy, and it must not
# declare an API key: a human or CI creates each key out of band. The
# name follows the shared `<project>.<env>.<thing>` pattern; the pilot
# has one environment, `prod`.
resource "scaleway_iam_application" "pipeline" {
  name        = "stx.prod.pipeline"
  description = "Applies and destroys infra/dev, infra/train, and infra/image."
}

resource "scaleway_iam_application" "operator" {
  name        = "stx.prod.operator"
  description = "Applies infra/persistent, under human review."
}

resource "scaleway_iam_application" "train" {
  name        = "stx.prod.train"
  description = "Reads and writes Object Storage during one training campaign."
}

# The pipeline policy must not hold IAMManager, OrganizationManager, or
# ProjectManager. A rule holds permission sets of one scope type only,
# so the org-scoped sets get their own rule. IAMApplicationManager is
# there for one flow: at `make infra-up STACK=train`, CI mints the
# train key on the train application, and at down it deletes the key,
# per the shared train-credential rule. A probe on 2026-08-28 proved
# that the set covers api-key create and delete. IAC-APPLY-6 accepts
# the organization scope, because Scaleway offers no narrower one.
# BlockStorageFullAccess is there for the SBS root volume of the train
# server: InstancesFullAccess alone cannot write an SBS volume (probed
# 2026-08-28). SSHKeysFullAccess is there for the ephemeral campaign
# SSH key that the train stack declares.
resource "scaleway_iam_policy" "pipeline" {
  name           = "stx.prod.pipeline"
  description    = "Compute and Object Storage in this project, billing read, and the train key mint."
  application_id = scaleway_iam_application.pipeline.id

  rule {
    project_ids = [data.scaleway_account_project.current.id]
    permission_set_names = [
      "InstancesFullAccess",
      "BlockStorageFullAccess",
      "ElasticMetalFullAccess",
      "ObjectStorageFullAccess",
      "SSHKeysFullAccess",
    ]
  }

  rule {
    organization_id = scaleway_iam_application.pipeline.organization_id
    permission_set_names = [
      "BillingReadOnly",
      "IAMApplicationManager",
    ]
  }
}

# The operator policy adds the IAM, Object Storage, and billing
# administration that only infra/persistent needs. IAM and billing are
# products of the organization, so their permission sets sit in an
# organization-scoped rule.
resource "scaleway_iam_policy" "operator" {
  name           = "stx.prod.operator"
  description    = "Object Storage in this project, and IAM and billing administration."
  application_id = scaleway_iam_application.operator.id

  rule {
    project_ids = [data.scaleway_account_project.current.id]
    permission_set_names = [
      "ObjectStorageFullAccess",
      "ObjectStorageBucketPolicyFullAccess",
    ]
  }

  rule {
    organization_id = scaleway_iam_application.operator.organization_id
    permission_set_names = [
      "IAMApplicationManager",
      "IAMPolicyManager",
      "BillingManager",
    ]
  }
}

# The train policy permits Object Storage in the project, and nothing
# else. Each of its keys lives for one campaign, created by CI at
# `make infra-up STACK=train`, never by OpenTofu.
resource "scaleway_iam_policy" "train" {
  name           = "stx.prod.train"
  description    = "Object Storage only, in this project, for one training campaign."
  application_id = scaleway_iam_application.train.id

  rule {
    project_ids          = [data.scaleway_account_project.current.id]
    permission_set_names = ["ObjectStorageFullAccess"]
  }
}

# The state bucket that `backend.tf` names. `infra/bootstrap` creates it,
# with local state, before this stack's own first apply can run. This
# resource only lets this stack read its ID, to scope the bucket policy
# below to the named applications.
data "scaleway_object_bucket" "state" {
  name = "stx-tofu-state"
}

# The checkout agent application: a documented console-made exception
# (IAC-APPLY-5). It runs the plans and the delegated applies of this
# stack today, so the bucket policy below must name it with write
# access. An apply through this backend cuts its own key off from the
# state bucket otherwise.
data "scaleway_iam_application" "agent" {
  name = "stx.prod.claude"
}

# Only the pipeline, the operator, and the agent application read or
# write the state bucket: a bucket policy is an allow list, per the
# shared rule.
resource "scaleway_object_bucket_policy" "state" {
  bucket = data.scaleway_object_bucket.state.name
  policy = jsonencode({
    Version = "2023-04-17"
    Id      = "stx-tofu-state-policy"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:*"]
        Principal = {
          SCW = [
            "application_id:${scaleway_iam_application.pipeline.id}",
            "application_id:${scaleway_iam_application.operator.id}",
            "application_id:${data.scaleway_iam_application.agent.id}",
          ]
        }
        Resource = [
          data.scaleway_object_bucket.state.name,
          "${data.scaleway_object_bucket.state.name}/*",
        ]
      },
    ]
  })
}

# COR-BUCKETS-1: the four buckets of the pilot. The literal names come
# from corpus.md; they carry no `<suffix>` segment, because the consumer
# specification states the exact bucket set, per the shared naming rule.
resource "scaleway_object_bucket" "corpus" {
  name          = "stx-corpus"
  tags          = local.common_tags
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled                                = true
    abort_incomplete_multipart_upload_days = 1
  }
}

resource "scaleway_object_bucket" "evalcorpus" {
  name          = "stx-evalcorpus"
  tags          = local.common_tags
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled                                = true
    abort_incomplete_multipart_upload_days = 1
  }
}

resource "scaleway_object_bucket" "checkpoints" {
  name          = "stx-checkpoints"
  tags          = local.common_tags
  force_destroy = false

  # COR-BUCKETS-2 keeps versioning off on the checkpoint bucket: a
  # checkpoint is large, and each version bills. The live bucket is
  # suspended, not unversioned, because Object Storage never removes
  # versioning once it starts.
  versioning {
    enabled = false
  }

  lifecycle_rule {
    enabled                                = true
    abort_incomplete_multipart_upload_days = 1
  }
}

resource "scaleway_object_bucket" "artifacts" {
  name          = "stx-artifacts"
  tags          = local.common_tags
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled                                = true
    abort_incomplete_multipart_upload_days = 1
  }
}

# IAC-APPLY-3: EUR 300 per month, with alerts at 50, 75, and 100 percent.
resource "scaleway_billing_budget" "monthly" {
  consumption_limit = var.budget_amount_eur * 100
  enabled           = true
}

resource "scaleway_billing_budget_alert" "at_50_percent" {
  budget_id = scaleway_billing_budget.monthly.id
  threshold = 50
}

resource "scaleway_billing_budget_alert" "at_75_percent" {
  budget_id = scaleway_billing_budget.monthly.id
  threshold = 75
}

resource "scaleway_billing_budget_alert" "at_100_percent" {
  budget_id = scaleway_billing_budget.monthly.id
  threshold = 100
}

resource "scaleway_billing_budget_alert_notification" "at_50_percent" {
  budget_alert_id = scaleway_billing_budget_alert.at_50_percent.id
  email_addresses = var.budget_alert_emails
}

resource "scaleway_billing_budget_alert_notification" "at_75_percent" {
  budget_alert_id = scaleway_billing_budget_alert.at_75_percent.id
  email_addresses = var.budget_alert_emails
}

resource "scaleway_billing_budget_alert_notification" "at_100_percent" {
  budget_alert_id = scaleway_billing_budget_alert.at_100_percent.id
  email_addresses = var.budget_alert_emails
}

# Alerts go to email and to a CI webhook. A notification resource holds
# exactly one channel, so the webhook channel is a second resource per
# alert, created only when a webhook URL is configured.
resource "scaleway_billing_budget_alert_notification" "at_50_percent_webhook" {
  count           = length(var.budget_alert_webhook_urls) > 0 ? 1 : 0
  budget_alert_id = scaleway_billing_budget_alert.at_50_percent.id
  webhook_urls    = var.budget_alert_webhook_urls
}

resource "scaleway_billing_budget_alert_notification" "at_75_percent_webhook" {
  count           = length(var.budget_alert_webhook_urls) > 0 ? 1 : 0
  budget_alert_id = scaleway_billing_budget_alert.at_75_percent.id
  webhook_urls    = var.budget_alert_webhook_urls
}

resource "scaleway_billing_budget_alert_notification" "at_100_percent_webhook" {
  count           = length(var.budget_alert_webhook_urls) > 0 ? 1 : 0
  budget_alert_id = scaleway_billing_budget_alert.at_100_percent.id
  webhook_urls    = var.budget_alert_webhook_urls
}
