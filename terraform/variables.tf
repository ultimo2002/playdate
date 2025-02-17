variable "do_token" {
 type = string
 description = "DigitalOcean API token"
  sensitive   = true
}
variable "do_version" {
  type = string
  description = "DigitalOcean version"
}
# images
variable "website_image" {
  default = "registry.digitalocean.com/timots/fast-api:latest"
}
# Kubernetes Cluster Configuration
variable "cluster_name" {
  description = "The name of the Kubernetes cluster"
  type        = string
}

variable "region" {
  description = "The region for the Kubernetes cluster"
  type        = string
}

variable "node_count" {
  description = "The number of nodes in the Kubernetes cluster"
  type        = number
}

# Kubernetes Namespaces
variable "namespace" {
  description = "The namespace for the application"
  type        = string
}

variable "monitoring_namespace" {
  description = "The namespace for monitoring tools"
  type        = string
}

# Docker Registry Credentials
variable "docker_server" {
  description = "Docker registry server URL"
  type        = string
}

variable "docker_auth_token" {
  default = ""
  sensitive   = true
}

variable "docker_username" {
  description = "Docker registry username"
  type        = string
  sensitive   = true
}

variable "docker_email" {
  description = "Docker registry email"
  type        = string
  sensitive   = true
}

# PostgreSQL Database Configuration
variable "db_name" {
  description = "Database name for PostgreSQL"
  type        = string
}

variable "db_user" {
  description = "Database user for PostgreSQL"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password for PostgreSQL"
  type        = string
  sensitive   = true
}