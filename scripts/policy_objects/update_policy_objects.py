import sys
import os
import csv
from pathlib import Path
import argparse
import logging

# Add parent path to import from meraki_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.logger import setup_logger
from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.policy_objects import get_policy_object_by_name

parser = argparse.ArgumentParser(description="Update Meraki policy object from a CSV file")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument("--update", choices=['name', 'value', 'both'], default='both',help="Choose what to update: name, value, or both (default: both)")
args = parser.parse_args()

setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

logger.info("Script Started")

def main():
    orgId = get_organization_id(dashboard)
    if not orgId:
        logger.error("Organization ID not found.")
        return

    csv_path = Path(__file__).resolve().parent.parent / "data" / "update_policy_objects.csv"
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return

    updated_count = 0
    skipped_count = 0

    with csv_path.open(mode='r') as file: 
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            old_name = row['old_name']
            new_name = row['new_name']
            value = row['value']

            try:
                object = get_policy_object_by_name(dashboard, orgId, objectName=old_name)
            except Exception as e:
                logger.error(f"Failed to retrieve object with ID {obj_id}: {e}")
                skipped_count += 1
                continue
            
            obj_id = object.get('id')

            if not obj_id:
                logger.error(f"Object ID not found for object named '{old_name}'. Skipping update.")
                skipped_count += 1
                continue

            update_payload = {}

            if args.update in ['name', 'both']:
                if new_name and new_name.strip():
                    update_payload['name'] = new_name.strip()
                else:
                    logger.warning(f"New name is empty for object ID {obj_id}. Skipping update.")

            if args.update in ['value', 'both']:
                if not value or not value.strip():
                    logger.warning(f"Value is empty for object ID {obj_id}. Skipping update.")
                else:
                    if object['type'] == 'cidr':
                        update_payload['cidr'] = value.strip()
                    elif object['type'] == 'fqdn':
                        update_payload['fqdn'] = value.strip()
                    else:
                        logger.warning(f"Unsupported object type '{object['type']}' for object ID {obj_id}. Skipping update.")
                        skipped_count += 1
                        continue

            if not update_payload:
                logger.info(f"No updates provided for object ID {obj_id}. Skipping.")
                continue

            try:
                dashboard.organizations.updateOrganizationPolicyObject(
                    organizationId=orgId,
                    policyObjectId=obj_id,
                    **update_payload
                )

                logger.info(f"Updated object ID {obj_id} with {update_payload}")
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update object {obj_id}: {e}")
                skipped_count += 1

    logger.info(f"\nSummary:\n✅ Updated: {updated_count}\n❌ Skipped/Failed: {skipped_count}")

if __name__ == "__main__":
    main()
