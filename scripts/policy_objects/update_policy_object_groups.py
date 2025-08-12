import sys
import os
import csv
from pathlib import Path
import logging
import argparse

# Add parent path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import is_policy_object_groups_present, get_policy_object_group_by_name, get_policy_object_by_name
from meraki_utils.logger import setup_logger

# CLI arguments
parser = argparse.ArgumentParser(description="Update Meraki policy object groups from a CSV file")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument("--csv_file", default="update_group_policy_objects.csv", help="CSV filename in /data directory")
parser.add_argument("--policy_object_group", help="A current policy object group name")
args = parser.parse_args()

# Setup logging
setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)


def load_csv(file_path):
    objects = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            name = row.get('name', '').strip()
            if name:
                    objects.append({'name': name})
    return objects


def main():
    org_id = get_organization_id(dashboard)
    if not org_id:
        logger.error("❌ Organization ID not found.")
        return

    csv_path = Path(__file__).resolve().parent.parent.parent / "data" / args.csv_file
    if not csv_path.exists():
        logger.error(f"❌ CSV file not found: {csv_path}")
        return

    objects = load_csv(csv_path)

    try:
        group = get_policy_object_group_by_name(dashboard, org_id, group_name=args.policy_object_group)
    except Exception as e:
        logger.error(f"❌ Failed to fetch group '{args.policy_object_group}': {e}")
        return

    groupId = group['id']
    groupName = group['name']
    existing_object_ids = set(group.get('objectIds', []))

    created_count = 0
    skipped_count = 0

    for obj in objects:
        try:
            pol_object = get_policy_object_by_name(dashboard, org_id, obj['name'])
            if pol_object is None:
                logger.error(f"❌ Policy object not found: '{obj['name']}'")
                skipped_count += 1
                continue

            pol_object_id = pol_object['id']

            if pol_object_id in existing_object_ids:
                logger.info(f"⏭️ Object '{obj['name']}' already in group. Skipping.")
                skipped_count += 1
                continue

            existing_object_ids.add(pol_object_id)
            created_count +=1
            logger.info(f"➕ Added object '{obj['name']}' to group update list.")

        except Exception as e:
            logger.error(f"Failed to retrieve object with name {obj['name']}: {e}")
            skipped_count +=1
            continue

    if not existing_object_ids:
        logger.error("🚫 No valid policy objects to update the group with. Nothing to do.")
        return
    
    logger.debug(f"📦 Updating group with object IDs: {list(existing_object_ids)}")

    try:
        dashboard.organizations.updateOrganizationPolicyObjectsGroup(
            org_id, groupId,
            objectIds=list(existing_object_ids)
        )
        logger.info(f"✅ Updated group '{args.policy_object_group}' with new objects.")
    except Exception as e:
        logger.error(f"❌ Failed to update group: {e}")

    logger.info(f"\n📋 Summary:\n  ➕ Created: {created_count}\n  ⏭️ Skipped (already exists or failed): {skipped_count}")


if __name__ == "__main__":
    main()
