locals {
  code = "stx"

  # One tag map builds every tag shape, per the shared tag rule. An
  # instance resource takes the list shape.
  tags = {
    "${local.code}:stack"     = "train"
    "${local.code}:managed"   = "true"
    "${local.code}:lifecycle" = "ephemeral"
    "${local.code}:run-id"    = var.run_id
    "${local.code}:expires"   = var.expires
  }
  tag_list = [for key, value in local.tags : "${key}=${value}"]

  # The scratch sizes follow the offer, per the FuguTTX train stack
  # table: 3000 GB on the H100, 1600 GB on the L40S.
  scratch_size_gb = {
    "H100-1-80G" = 3000
    "L40S-1-48G" = 1600
  }
}
