terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  backend "gcs" {
    # bucket はユーザー環境ごとに異なるため、terraform init 実行時に
    # -backend-config="bucket=<project>-tfstate" で指定する。
    prefix = "calendar-notifier"
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

locals {
  github_dispatch_url = "https://api.github.com/repos/${var.github_repository}/dispatches"
  github_headers = {
    "Authorization" = "Bearer ${var.github_pat}"
    "Accept"        = "application/vnd.github+json"
    "Content-Type"  = "application/json"
  }
}

resource "google_cloud_scheduler_job" "calendar_notifier_hourly" {
  name        = "calendar-notifier-hourly"
  description = "Trigger calendar_notifier.yml via repository_dispatch every hour"
  schedule    = "0 * * * *"
  time_zone   = "Etc/UTC"

  http_target {
    uri         = local.github_dispatch_url
    http_method = "POST"
    headers     = local.github_headers
    body        = base64encode(jsonencode({ event_type = "calendar-tick" }))
  }
}

resource "google_cloud_scheduler_job" "weekly_playground_suggester" {
  name        = "weekly-playground-suggester"
  description = "Trigger weekly_playground.yml via repository_dispatch every Friday"
  schedule    = "0 1 * * 5"
  time_zone   = "Etc/UTC"

  http_target {
    uri         = local.github_dispatch_url
    http_method = "POST"
    headers     = local.github_headers
    body        = base64encode(jsonencode({ event_type = "playground-tick" }))
  }
}
