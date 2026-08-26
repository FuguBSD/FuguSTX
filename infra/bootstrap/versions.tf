# This root keeps local state, on purpose: it creates the bucket that
# every other stack's remote state needs. See infra/persistent/RUNBOOK.md.
terraform {
  required_version = ">= 1.11.0"

  required_providers {
    scaleway = {
      source  = "scaleway/scaleway"
      version = "~> 2.80"
    }
  }
}
