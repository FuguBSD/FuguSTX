# The backend takes its credential from the environment: never a key
# here. `make infra-bootstrap` creates the state bucket, once, by hand.
terraform {
  backend "s3" {
    bucket = "stx-tofu-state"
    key    = "dev.tfstate"
    region = "fr-par"

    endpoints = {
      s3 = "https://s3.fr-par.scw.cloud"
    }

    use_path_style = true
    use_lockfile   = true

    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
  }
}
