output "vpc_name" {
  value = google_compute_network.vpc_network.name
}

output "vm_external_ip" {
  value = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}

output "bucket_url" {
  value = "gs://${google_storage_bucket.secure_bucket.name}"
}
