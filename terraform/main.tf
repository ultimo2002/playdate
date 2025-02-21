# Providers instellen
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}


provider "kubernetes" {
  host                   = digitalocean_kubernetes_cluster.my_cluster.endpoint
  token                  = digitalocean_kubernetes_cluster.my_cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(digitalocean_kubernetes_cluster.my_cluster.kube_config[0].cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = digitalocean_kubernetes_cluster.my_cluster.endpoint
    token                  = digitalocean_kubernetes_cluster.my_cluster.kube_config[0].token
    cluster_ca_certificate = base64decode(digitalocean_kubernetes_cluster.my_cluster.kube_config[0].cluster_ca_certificate)
  }
}

# Kubernetes-cluster aanmaken

resource "digitalocean_kubernetes_cluster" "my_cluster" {
  name    = var.cluster_name
  region  = var.region
  version = var.do_version

  node_pool {
    name       = "webapi-compleet"
    size       = "s-1vcpu-2gb"
    node_count = var.node_count
  }
}

# Namespaces
resource "kubernetes_namespace" "app_namespace" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_namespace" "monitoring_namespace" {
  metadata {
    name = var.monitoring_namespace
  }
}


resource "kubernetes_secret" "docker_registry" {
  metadata {
    name      = "docker-registry"
    namespace = kubernetes_namespace.app_namespace.metadata[0].name
  }
  type = "kubernetes.io/dockerconfigjson"

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "registry.digitalocean.com" = {
          "username" = var.docker_username
          "password" = var.docker_auth_token
          "auth"     = base64encode("${var.docker_username}:${var.do_token}")
        }
      }
    })
  }
}

# PersistentVolumeClaim voor PostgreSQL
resource "kubernetes_persistent_volume_claim" "postgres_pvc" {
  metadata {
    name      = "postgres-pvc"
    namespace = var.namespace
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}

# PostgreSQL Deployment
resource "kubernetes_deployment" "postgres" {
  metadata {
    name      = "postgres"
    namespace = var.namespace
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "postgres"
      }
    }
    template {
      metadata {
        labels = {
          app = "postgres"
        }
      }
      spec {
        container {
          name  = "postgres"
          image = "postgres:16"
          env {
            name  = "POSTGRES_DB"
            value = var.db_name
          }
          env {
            name  = "POSTGRES_USER"
            value = var.db_user
          }
          env {
            name  = "POSTGRES_PASSWORD"
            value = var.db_password
          }
          env {
            name  = "PGDATA"
            value = "/var/lib/postgresql/data/pgdata" # PGDATA instellen
          }
          volume_mount {
            name       = "postgres-storage"
            mount_path = "/var/lib/postgresql/data"
          }
        }
        volume {
          name = "postgres-storage"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.postgres_pvc.metadata[0].name
          }
        }
      }
    }
  }
}

# PostgreSQL Service
resource "kubernetes_service" "postgres" {
  metadata {
    name      = "postgres"
    namespace = var.namespace
  }
  spec {
    selector = {
      app = "postgres"
    }
    port {
      port        = 5432
      target_port = 5432
    }
    type = "LoadBalancer"
  }
}

resource "kubernetes_config_map" "grafana_dashboard" {
  metadata {
    name      = "fastapi-cluster-dashboard"
    namespace = kubernetes_namespace.monitoring_namespace.metadata[0].name
    labels = {
      grafana_dashboard = "1"
    }
  }

  data = {
 #   "fastapi-cluster-dashboard.json" = file("${path.module}/grafana/dashboards/fastapi-cluster-dashboard.json")
  }
}


# Helm Release: Prometheus
resource "helm_release" "prometheus" {
  chart      = "kube-prometheus-stack"
  name       = "prometheus"
  namespace  = kubernetes_namespace.monitoring_namespace.metadata[0].name
  repository = "https://prometheus-community.github.io/helm-charts"
  version    = "56.3.0"
  #values = [file("${path.module}/values.yaml")]

  set {
    name  = "podSecurityPolicy.enabled"
    value = true
  }

  set {
    name  = "server.persistentVolume.enabled"
    value = false
  }
}


# Website Deployment binnen het Kubernetes-cluster

resource "kubernetes_deployment" "website" {
  metadata {
    name      = "website"
    namespace = var.namespace
  }
  spec {
    replicas = 2
    selector {
      match_labels = {
        app = "website"
      }
    }
    template {
      metadata {
        labels = {
          app = "website"
        }
      }
      spec {
        image_pull_secrets {
          name = kubernetes_secret.docker_registry.metadata[0].name
        }
        container {
          name  = "website"
          image = var.website_image
          image_pull_policy = "Always"
          port {
            container_port = 8000
          }
          env {
            name  = "URL_DATABASE"
            value = "postgresql://${var.db_user}:${var.db_password}@postgres.${var.namespace}.svc.cluster.local:5432/${var.db_name}"
          }
        }
          image_pull_secrets {
          name = "docker_registry"
        }
      }
    }
  }
}


resource "kubernetes_service" "webapi-loadbalancer" {
  metadata {
    name      = "webapi-loadbalancer"
    namespace = kubernetes_namespace.app_namespace.metadata[0].name
  }

  spec {
    selector = {
      app = "website" # Match labels van je deployment
    }

    port {
      protocol    = "TCP"
      port        = 80       # Externe poort
      target_port = 8000     # Poort waar je app luistert
    }

    type = "LoadBalancer"
  }
}