# VPC + Subnet
resource "google_compute_network" "vpc_network" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${var.vpc_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.self_link
}

# Firewall Rule
resource "google_compute_firewall" "default" {
  name    = "allow-ssh-internal"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["10.0.0.0/24"]
}

# GCE VM
resource "google_compute_instance" "vm_instance" {
  name         = var.vm_name
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.vpc_network.self_link
    subnetwork = google_compute_subnetwork.subnet.self_link
    access_config {} # Public IP
  }

  labels = {
    sentinel = "true"
    secure   = "yes"
  }

  tags = ["secure-vm"]
}

# GCS Bucket (Encrypted + Versioned)
resource "google_storage_bucket" "secure_bucket" {
  name     = var.bucket_name
  location = var.region

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true

  encryption {
    default_kms_key_name = google_kms_crypto_key.key.id
  }
}

# KMS Key
resource "google_kms_key_ring" "key_ring" {
  name     = "sentinel-keyring"
  location = var.region
}

resource "google_kms_crypto_key" "key" {
  name     = "sentinel-key"
  key_ring = google_kms_key_ring.key_ring.id
}

# Fetch project number dynamically for service account
data "google_project" "project" {
  project_id = var.project_id
}

# Allow GCS to use the KMS key
resource "google_kms_crypto_key_iam_binding" "allow_gcs_usage" {
  crypto_key_id = google_kms_crypto_key.key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"

  members = [
    "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
  ]
}
