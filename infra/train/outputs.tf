output "public_ip" {
  description = "The routed IPv4 address of the train instance."
  value       = scaleway_instance_ip.train.address
}

output "server_id" {
  description = "The instance identifier, for the runbook."
  value       = scaleway_instance_server.train.id
}

output "run_id" {
  description = "The campaign run identifier of the stx:run-id tag."
  value       = var.run_id
}

output "expires" {
  description = "The hard end of the lease, from the stx:expires tag."
  value       = var.expires
}
