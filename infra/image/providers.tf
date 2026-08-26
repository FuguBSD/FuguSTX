# The provider takes its region, its zone, and its credential from the
# environment. It must not set access_key, secret_key, or project_id.
provider "scaleway" {
  region = "fr-par"
  zone   = "fr-par-2"
}
