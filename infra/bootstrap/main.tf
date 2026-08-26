# The state bucket that every stack's backend.tf names. Versioning is
# on, and a noncurrent version expires after 30 days.
resource "scaleway_object_bucket" "state" {
  name          = "stx-tofu-state"
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}
