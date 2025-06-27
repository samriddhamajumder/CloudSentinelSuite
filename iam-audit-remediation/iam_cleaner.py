import json
import os
import yaml
from datetime import datetime
from aws_iam_audit import audit_aws_iam, remediate_aws
from azure_iam_audit import audit_azure_iam, remediate_azure
from gcp_iam_audit import audit_gcp_iam, remediate_gcp
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

REMEDIATE = config["global"].get("enable_remediation", False)
LOG_DIR = config["global"].get("log_directory", "logs/")
BASE_OUTPUT = config["global"].get("report_file", "audit_report_template.json")

# Ensure log folder exists
os.makedirs(LOG_DIR, exist_ok=True)

def run_audit():
    print("🔐 [*] Starting Multi-Cloud IAM Audit...")

    try:
        all_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "aws": audit_aws_iam(),
            "azure": audit_azure_iam(),
            "gcp": audit_gcp_iam()
        }

        # Save main audit report
        with open(BASE_OUTPUT, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"✅ Audit report saved to: {BASE_OUTPUT}")

        # Save timestamped log
        timestamped_path = os.path.join(
            LOG_DIR, f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(timestamped_path, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"📝 Log archived to: {timestamped_path}")

        # Optional remediation step
        if REMEDIATE:
            print("⚠️ [!] Starting Remediation Phase...")
            remediate_aws(all_results["aws"])
            remediate_azure(all_results["azure"])
            remediate_gcp(all_results["gcp"])
            print("✅ Remediation Completed")

    except Exception as e:
        print(f"❌ ERROR: IAM audit failed — {e}")

if __name__ == "__main__":
    run_audit()
