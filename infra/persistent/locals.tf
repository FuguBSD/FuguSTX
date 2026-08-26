locals {
  code = "stx"

  # This stack's own resources are never ephemeral: the watchdog must
  # never touch a `<code>:lifecycle=persistent` resource.
  common_tags = {
    "${local.code}:stack"     = "persistent"
    "${local.code}:managed"   = "true"
    "${local.code}:lifecycle" = "persistent"
  }
}
