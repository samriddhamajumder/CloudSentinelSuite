import boto3
from datetime import datetime, timezone

# AWS IAM client
iam = boto3.client('iam')
MAX_KEY_AGE_DAYS = 90

def audit_aws_iam():
    """
    Performs a complete IAM audit on AWS.
    Returns a structured report dictionary.
    """
    report = {
        "inactive_keys": [],
        "users_without_mfa": [],
        "wildcard_policies": [],
        "unused_users": [],
        "inline_policies": []
    }

    print("[*] Starting AWS IAM Audit...")
    users = iam.list_users()['Users']
    for user in users:
        username = user['UserName']
        
        # ✅ 1. Inactive access keys
        keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
        for key in keys:
            key_age = (datetime.now(timezone.utc) - key['CreateDate']).days
            if key_age > MAX_KEY_AGE_DAYS:
                report["inactive_keys"].append({
                    "user": username,
                    "access_key_id": key['AccessKeyId'],
                    "age_days": key_age
                })

        # ✅ 2. Users without MFA
        mfa = iam.list_mfa_devices(UserName=username)
        if len(mfa['MFADevices']) == 0:
            report["users_without_mfa"].append(username)

        # ✅ 3. Unused IAM Users
        try:
            last_used = iam.get_user(UserName=username)['User'].get('PasswordLastUsed')
            if not last_used or (datetime.now(timezone.utc) - last_used).days > 90:
                report["unused_users"].append({
                    "user": username,
                    "last_used": str(last_used)
                })
        except:
            # Possibly API-only user
            report["unused_users"].append({
                "user": username,
                "last_used": None
            })

        # ✅ 4. Inline policies on users
        inline_policies = iam.list_user_policies(UserName=username)
        if inline_policies['PolicyNames']:
            report["inline_policies"].append({
                "user": username,
                "policies": inline_policies['PolicyNames']
            })

    # ✅ 5. Wildcard permissions in role policies
    roles = iam.list_roles()['Roles']
    for role in roles:
        role_name = role['RoleName']
        attached = iam.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
        for policy in attached:
            try:
                policy_version = iam.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
                policy_doc = iam.get_policy_version(
                    PolicyArn=policy['PolicyArn'],
                    VersionId=policy_version
                )['PolicyVersion']['Document']
                statements = policy_doc['Statement']
                if not isinstance(statements, list):
                    statements = [statements]
                for stmt in statements:
                    if stmt['Effect'] == 'Allow' and stmt['Action'] == '*' and stmt['Resource'] == '*':
                        report["wildcard_policies"].append({
                            "role": role_name,
                            "policy": policy['PolicyName'],
                            "arn": policy['PolicyArn']
                        })
            except Exception as e:
                print(f"[!] Error checking policy {policy['PolicyName']}: {e}")

    print("[+] AWS IAM Audit completed.")
    return report

def remediate_aws(report):
    """
    Performs auto-remediation actions based on audit report.
    """
    print("[*] Starting AWS IAM remediation...")

    # 🚫 Disable old access keys
    for key_data in report["inactive_keys"]:
        try:
            print(f"[!] Disabling old access key {key_data['access_key_id']} for user {key_data['user']}")
            iam.update_access_key(
                UserName=key_data["user"],
                AccessKeyId=key_data["access_key_id"],
                Status='Inactive'
            )
        except Exception as e:
            print(f"[X] Failed to disable key: {e}")

    # ❗ Inline policies (alert only)
    for inline in report["inline_policies"]:
        print(f"[!] User {inline['user']} has inline policies: {inline['policies']} (manual review)")

    # ❗ Wildcard policies in roles (alert only)
    for wildcard in report["wildcard_policies"]:
        print(f"[!] Role {wildcard['role']} has wildcard permissions in policy {wildcard['policy']} (manual review)")

    # 🚨 Users without MFA (log only)
    for user in report["users_without_mfa"]:
        print(f"[!] User {user} has no MFA enabled")

    # 💤 Unused users (log only)
    for user_data in report["unused_users"]:
        print(f"[!] Unused user: {user_data['user']}, last used: {user_data['last_used']}")

    print("[+] AWS IAM remediation complete.")
