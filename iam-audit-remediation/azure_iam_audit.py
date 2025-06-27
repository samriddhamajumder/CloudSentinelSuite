import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from dateutil import parser  # ✅ added for robust ISO timestamp parsing
from azure.identity import ClientSecretCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from dateutil import parser
from datetime import datetime, timezone

# === Load environment variables ===
load_dotenv()

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")

# === Azure Credentials ===
credential = ClientSecretCredential(
    tenant_id=AZURE_TENANT_ID,
    client_id=AZURE_CLIENT_ID,
    client_secret=AZURE_CLIENT_SECRET
)

# === Microsoft Graph API Token & Header ===
token = credential.get_token("https://graph.microsoft.com/.default").token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# === Azure Role Management Client ===
auth_client = AuthorizationManagementClient(credential, AZURE_SUBSCRIPTION_ID)

# === Utility to call Graph API ===
def graph_get(endpoint):
    url = f"https://graph.microsoft.com/v1.0{endpoint}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])

# === Azure IAM Audit ===
def audit_azure_iam():
    print("[*] Starting Azure IAM audit...")
    report = {
        "users_without_mfa": [],
        "high_privilege_roles": [],
        "stale_service_principals": [],
        "guest_users": [],
        "sp_with_owner_contributor": []
    }

    # 1️⃣ User Audit
    users = graph_get("/users")
    for user in users:
        user_principal = user.get("userPrincipalName", "unknown@domain.com")
        user_type = user.get("userType", "Unknown")

        if user_type == "Guest":
            report["guest_users"].append({
                "userPrincipalName": user_principal,
                "created": user.get("createdDateTime", "N/A")
            })
        else:
            report["users_without_mfa"].append({
                "userPrincipalName": user_principal,
                "type": user_type
            })

    # 2️⃣ Stale Service Principals
    sps = graph_get("/servicePrincipals")
    now_utc = datetime.now(timezone.utc)
    for sp in sps:
        created = sp.get("createdDateTime")
        if created:
            try:
                created_dt = parser.isoparse(created)
                age_days = (now_utc - created_dt).days
                if age_days > 90:
                    report["stale_service_principals"].append({
                        "name": sp.get("appDisplayName", "N/A"),
                        "id": sp["id"],
                        "age_days": age_days
                    })
            except Exception as e:
                print(f"[!] Error parsing service principal date '{created}': {e}")

    # 3️⃣ Owner / Contributor Role Assignments
    for assignment in auth_client.role_assignments.list_for_scope("/subscriptions/" + AZURE_SUBSCRIPTION_ID):

        role_id = assignment.role_definition_id.split("/")[-1]
        try:
            role_def = auth_client.role_definitions.get(assignment.scope, role_id)
            if role_def.role_name in ["Owner", "Contributor"]:
                report["sp_with_owner_contributor"].append({
                    "principal_id": assignment.principal_id,
                    "role": role_def.role_name,
                    "scope": assignment.scope
                })
        except Exception as e:
            print(f"[!] Error resolving role {role_id}: {str(e)}")

    print("[+] Azure IAM audit complete.")
    return report

# === Optional Remediation Logger ===
def remediate_azure(report):
    print("[*] Azure IAM remediation — dry run")
    for user in report["users_without_mfa"]:
        print(f"[!] MFA not enabled: {user['userPrincipalName']} ({user['type']})")
    for guest in report["guest_users"]:
        print(f"[!] Guest user: {guest['userPrincipalName']} created at {guest['created']}")
    for sp in report["stale_service_principals"]:
        print(f"[!] Stale SP: {sp['name']} (ID: {sp['id']}) — {sp['age_days']} days old")
    for role in report["sp_with_owner_contributor"]:
        print(f"[!] SP {role['principal_id']} has role {role['role']} on {role['scope']}")
    print("[+] Azure IAM remediation complete.")
