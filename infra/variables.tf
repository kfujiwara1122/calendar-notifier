variable "gcp_project_id" {
  description = "GCP project ID that hosts the Cloud Scheduler jobs"
  type        = string
}

variable "gcp_region" {
  description = "GCP region for the Cloud Scheduler jobs"
  type        = string
  default     = "asia-northeast1"
}

variable "github_repository" {
  description = "GitHub repository in owner/repo form that receives the repository_dispatch events"
  type        = string
  default     = "kfujiwara1122/calendar-notifier"
}

variable "github_pat" {
  description = "Fine-grained GitHub PAT (Contents: Read and write) used to call the repository_dispatch API"
  type        = string
  sensitive   = true
}
