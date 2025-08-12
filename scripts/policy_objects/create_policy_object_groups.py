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
from meraki_utils.policy_objects import is_policy_object_groups_present
from meraki_utils.logger import setup_logger

# CLI arguments
parser = argparse.ArgumentParser(description="Create Meraki policy object groups from a CSV file")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument("--csv_file", default="create_group_policy_objects.csv", help="CSV filename in /data directory")
args = parser.parse_args()

# Setup logging
setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)


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


def main():
    org_id = get_organization_id(dashboard)
    if not org_id:
        logger.error("❌ Organization ID not found.")
        return

    csv_path = Path(__file__).resolve().parent.parent.parent / "data" / args.csv_file
    if not csv_path.exists():
        logger.error(f"❌ CSV file not found: {csv_path}")
        return

    groups = load_csv(csv_path)

    created_count = 0
    skipped_count = 0

    for group in groups:
        name = group['name']
        category = group['category']

        if is_policy_object_groups_present(dashboard, org_id, name):
            logger.info(f"✅ Object group '{name}' already exists. Skipping.")
            skipped_count += 1
            continue

        logger.info(f"➕ Creating policy object group: '{name}'")

        try:
            dashboard.organizations.createOrganizationPolicyObjectsGroup(
                organizationId=org_id,
                name=name,
                category=category
            )
            logger.info(f"✅ Created policy object group: '{name}'")
            created_count += 1
        except Exception as e:
            logger.error(f"❌ Error creating object group '{name}': {e}")
            skipped_count += 1

    logger.info(f"\n📋 Summary:\n  ➕ Created: {created_count}\n  ⏭️ Skipped (already exists or failed): {skipped_count}")


if __name__ == "__main__":
    main()
