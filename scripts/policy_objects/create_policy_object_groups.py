import csv
from pathlib import Path
import logging

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import is_policy_object_groups_present
from meraki_utils.logger import log, set_log_callback

def load_csv(file_path):
    groups = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            groups.append({
                'name': row['name'].strip(),
                'category': row.get('category', 'NetworkObjectGroup').strip(),
            })
    return groups


def create_policy_object_groups(csv_file, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🚀 Starting policy object group creation...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None

    csv_path = Path(csv_file)
    if not csv_path.exists():
        log(f"❌ CSV file not found: {csv_path}")
        return None

    groups = load_csv(csv_path)

    created_count = 0
    skipped_count = 0

    for group in groups:
        name = group['name']
        category = group['category']

        if is_policy_object_groups_present(dashboard, org_id, name):
            log(f"✅ Object group '{name}' already exists. Skipping.")
            skipped_count += 1
            continue

        log(f"➕ Creating policy object group: '{name}'")

        try:
            dashboard.organizations.createOrganizationPolicyObjectsGroup(
                organizationId=org_id,
                name=name,
                category=category
            )
            log(f"✅ Created policy object group: '{name}'")
            created_count += 1
        except Exception as e:
            log(f"❌ Error creating object group '{name}': {e}")
            skipped_count += 1

    summary = f"\n📋 Summary:\n  ➕ Created: {created_count}\n  ⏭️ Skipped: {skipped_count}"
    log(summary)
    return {
        "created": created_count,
        "skipped": skipped_count,
        "total": created_count + skipped_count,
        "summary": summary
    }