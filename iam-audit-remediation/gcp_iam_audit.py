import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load .env environment
load_dotenv()

# === Safe Credential Path Handling ===
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Fallback if env is missing or invalid
if not creds_path or not os.path.exists(creds_path):
    fallback_path = os.path.join(os.path.dirname(__file__), "credentials", "gcp-audit-sa.json")
    if os.path.exists(fallback_path):
        creds_path = fallback_path
    else:
        raise FileNotFoundError(f"❌ GCP service account file not found at: {creds_path or fallback_path}")

# Load credentials
credentials = service_account.Credentials.from_service_account_file(creds_path)
project_id = credentials.project_id
iam_service = build("iam", "v1", credentials=credentials)
cloudresourcemanager = build("cloudresourcemanager", "v1", credentials=credentials)

# === IAM Audit Entry ===
def audit_gcp_iam():
    print("[*] Starting GCP IAM audit...")
    report = {
        "overprivileged_accounts": [],
        "custom_roles_with_wildcards": [],
        "broad_scope_bindings": [],
        "stale_service_accounts": [],
        "inactive_users_guess": []
    }

    # 1️⃣ IAM Policy Bindings
    policy = cloudresourcemanager.projects().getIamPolicy(
        resource=project_id, body={}
    ).execute()

    for binding in policy.get("bindings", []):
        role = binding["role"]
        members = binding.get("members", [])

        if role in ["roles/owner", "roles/editor", "roles/resourcemanager.organizationAdmin"]:
            for member in members:
                report["overprivileged_accounts"].append({
                    "member": member,
                    "role": role
                })

        for member in members:
            if "*" in member:
                report["broad_scope_bindings"].append({
                    "role": role,
                    "member": member
                })

    # 2️⃣ Custom Roles with Wildcard Permissions
    roles = iam_service.projects().roles().list(parent=f"projects/{project_id}").execute()
    for role in roles.get("roles", []):
        permissions = role.get("includedPermissions", [])
        wildcard_perms = [p for p in permissions if "*" in p]
        if wildcard_perms:
            report["custom_roles_with_wildcards"].append({
                "role": role["name"],
                "wild_permissions": wildcard_perms
            })

    # 3️⃣ Stale Service Account Keys
    service_accounts = iam_service.projects().serviceAccounts().list(
        name=f"projects/{project_id}"
    ).execute()

    for sa in service_accounts.get("accounts", []):
        keys = iam_service.projects().serviceAccounts().keys().list(
            name=sa["name"]
        ).execute()
        for key in keys.get("keys", []):
            created = datetime.strptime(key["validAfterTime"], "%Y-%m-%dT%H:%M:%SZ")
            if (datetime.utcnow() - created).days > 90:
                report["stale_service_accounts"].append({
                    "service_account": sa["email"],
                    "key_id": key["name"].split("/")[-1],
                    "key_age_days": (datetime.utcnow() - created).days
                })

    print("[+] GCP IAM audit complete.")
    return report

# === Optional Logging-Only Remediation ===
def remediate_gcp(report):
    print("[*] GCP IAM remediation review (recommendation only):")

    for user in report["overprivileged_accounts"]:
        print(f"[!] Overprivileged: {user['member']} has role {user['role']}")

    for role in report["custom_roles_with_wildcards"]:
        print(f"[!] Custom role {role['role']} has wildcard perms: {role['wild_permissions']}")

    for item in report["broad_scope_bindings"]:
        print(f"[!] Broad scope: {item['member']} bound to {item['role']}")

    for stale in report["stale_service_accounts"]:
        print(f"[!] Stale SA key: {stale['service_account']} key {stale['key_id']} is {stale['key_age_days']} days old")

    print("[+] GCP remediation logging complete (no changes applied)")
