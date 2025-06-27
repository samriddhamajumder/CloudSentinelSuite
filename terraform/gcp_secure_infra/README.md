# GCP Secure Infra – Cloud Sentinel Suite

This Terraform module provisions secure foundational infrastructure in GCP:
- VPC with subnet and firewall rules
- GCE instance with tags/labels
- GCS bucket with versioning and KMS encryption
- KMS key for encryption
- IAM bindings and logging integration (coming next)

## Usage

```bash
terraform init
terraform plan -var="project_id=your-project-id"
terraform apply -var="project_id=your-project-id"


---

## ✅ Next Add-ons (Optional)
- ✅ `log_sink.tf` — forward logs to BigQuery or Sentinel  
- ✅ `iam.tf` — bind roles (e.g., `roles/logging.logWriter`, `roles/storage.admin`)  
- 🔐 Secure service account usage  
- 🔁 Add `backend.tf` to store state in GCS

---

Ready to proceed with:
- Full IAM policies + secure service account setup?
- Or Sentinel integration (log sink to BigQuery or Pub/Sub)?

Let me know which submodule you want next inside `gcp_secure_infra/` or if you'd like me to generate the full Terraform files to drop in directly.
