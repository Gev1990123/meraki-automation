import csv
from pathlib import Path
import logging

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import is_policy_object_groups_present, get_policy_object_group_by_name
from meraki_utils.logger import setup_logger

def load_csv(file_path):
    groups = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            groups.append({
                'name': row['name'].strip(),
            })
    return groups


def delete_group_policy_objects(csv_file, debug=False, log_callback=None):
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)

    def log(msg, level="info"):
        if log_callback:
            log_callback(msg)
        getattr(logger, level)(msg)

    log("🚀 Starting policy object groups deletion...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None

    csv_path = Path(csv_file)
    if not csv_path.exists():
        log(f"❌ CSV file not found: {csv_path}")
        return None

    groups = load_csv(csv_path)

    deleted_count = 0
    skipped_count = 0

    for group in groups:
        name = group['name']

        if not is_policy_object_groups_present(dashboard, org_id, name):
            log(f"⏭️ Object group '{name}' not found. Skipping.")
            skipped_count += 1
            continue

        log(f"➕ Deleting policy object group: '{name}'")

        try: 
            exisiting_group = get_policy_object_group_by_name(dashboard, org_id, name)
            groupId = exisiting_group['id']
        except Exception as e:
            log(f"❌ Error locating object group ID for group name: '{name}': {e}")
            skipped_count += 1
            continue

        try:
            dashboard.organizations.deleteOrganizationPolicyObjectsGroup(
                org_id,
                groupId)
            log(f"✅ Deleted policy object group: '{name}'")
            deleted_count += 1
        except Exception as e:
            log(f"❌ Error deleting object group '{name}': {e}")
            skipped_count += 1

    summary = f"\n📋 Summary:\n  ➕ Deleted: {deleted_count}\n  ⏭️ Skipped (already exists or failed): {skipped_count}"
    log(summary)

    return{
        "deleted": deleted_count,
        "skipped": skipped_count,
        "total": deleted_count + skipped_count,
        "summary": summary
    }



