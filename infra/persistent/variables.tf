variable "budget_amount_eur" {
  description = "The monthly budget, in euros. IAC-APPLY-3 sets it to 300."
  type        = number
  default     = 300
}

variable "budget_alert_emails" {
  description = "The email addresses that a budget alert notifies."
  type        = list(string)
}

variable "budget_alert_webhook_urls" {
  description = "The CI webhook URLs that a budget alert notifies."
  type        = list(string)
  default     = []
}
