# The train stack: one GPU server, the root and the scratch volumes,
# and one routed IPv4 address (TRN-INST, decision T3). The stack is
# ephemeral: `make infra-up STACK=train` starts billing, and
# `make infra-down STACK=train` stops it. Down means destroyed.

# The GPU OS image, resolved by marketplace label, never by UUID. The
# image supplies the NVIDIA driver, Docker, and the NVIDIA container
# toolkit.
data "scaleway_marketplace_image" "gpu_os" {
  label         = "ubuntu_noble_gpu_os_13_nvidia"
  instance_type = var.instance_type
}

# Scaleway bills a reserved IPv4, attached or not. The destroy must
# remove it, per the shared teardown rule.
resource "scaleway_instance_ip" "train" {
  type = "routed_ipv4"
  tags = local.tag_list
}

# OpenTofu must declare the scratch volume: the platform attaches
# scratch storage automatically only through the console and the CLI.
# Scratch NVMe is ephemeral at deletion, so a destroy loses no durable
# data.
resource "scaleway_instance_volume" "scratch" {
  name       = "stx.prod.train-scratch"
  type       = "scratch"
  size_in_gb = local.scratch_size_gb[var.instance_type]
  tags       = local.tag_list
}

resource "scaleway_instance_server" "train" {
  name  = "stx.prod.train"
  type  = var.instance_type
  image = data.scaleway_marketplace_image.gpu_os.id
  tags  = local.tag_list
  ip_id = scaleway_instance_ip.train.id

  root_volume {
    volume_type = "sbs_volume"
    size_in_gb  = 125
    sbs_iops    = 5000
  }

  additional_volume_ids = [scaleway_instance_volume.scratch.id]

  # Cloud-init must not receive a credential: user_data is readable
  # through the instance API. CI delivers the train key over SSH after
  # boot, per the shared train-credential rule. The cloud-init must
  # not run a distribution upgrade: a package upgrade on a GPU OS
  # image breaks the NVIDIA driver.
  user_data = {
    cloud-init = templatefile("${path.module}/cloud-init.yaml.tftpl", {
      ssh_public_key = var.ssh_public_key
      axolotl_image  = var.axolotl_image
    })
  }
}
