# The offer variable of decision T3: H100-1-80G is the default, and
# L40S-1-48G is the budget escape (TRN-INST).
variable "instance_type" {
  type    = string
  default = "H100-1-80G"

  validation {
    condition     = contains(["H100-1-80G", "L40S-1-48G"], var.instance_type)
    error_message = "The offer must be H100-1-80G or L40S-1-48G (decision T3)."
  }
}

# The campaign run identifier. The stx:run-id tag ties each resource to
# one CI run, and the checkpoint keys carry it (COR-BUCKETS-3).
variable "run_id" {
  type = string
}

# The hard end of the lease, in UTC RFC 3339. The watchdog destroys the
# stack when the time passes this tag.
variable "expires" {
  type = string

  validation {
    condition     = can(regex("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", var.expires))
    error_message = "The expiry must be UTC RFC 3339, for example 2026-08-28T18:00:00Z."
  }
}

# The public key of the campaign SSH keypair. Cloud-init writes it, so
# no IAM SSH key resource is needed. A public key in user_data is safe:
# user_data is readable through the instance API, and the private key
# never leaves the CI secret.
variable "ssh_public_key" {
  type = string
}

# The published Axolotl CUDA Docker image (TRN-EXEC-1). The value comes
# from train/config.env, the one source of the campaign pins.
variable "axolotl_image" {
  type = string
}
