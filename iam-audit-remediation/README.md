# 🔐 IAM Audit & Auto-Remediation Engine — Cloud Sentinel Suite

This module provides a **multi-cloud IAM audit and remediation engine** that supports **AWS**, **Azure**, and **GCP**, using Python SDKs and JSON reports. It detects security misconfigurations, logs findings, and (optionally) remediates common identity risks.

---

## 🌍 Supported Cloud Platforms

| Cloud | Audits | Remediation |
|-------|--------|-------------|
| AWS   | ✅ Inactive keys, MFA, wildcard roles, inline policies | ✅ Disable keys, log warnings |
| Azure | ✅ Global admins, guests, stale SAs, no MFA | ⚠ Log only |
| GCP   | ✅ Wildcard roles, overprivileged users, stale SA keys | ⚠ Log only |

---

## 📂 Folder Structure

iam-audit-remediation/
├── aws_iam_audit.py # AWS IAM audit/remediation
├── azure_iam_audit.py # Azure IAM audit/logging
├── gcp_iam_audit.py # GCP IAM audit/logging
├── iam_cleaner.py # Orchestrator
├── audit_report_template.json # Sample output format
├── config.yaml # Optional audit thresholds
├── .env # Env vars (Azure/GCP creds)
├── credentials/
│ └── gcp-audit-sa.json # GCP service account key
└── logs/
└── ... # Timestamped audit logs

yaml
Copy
Edit


