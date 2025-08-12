import sys
import os
import csv
from pathlib import Path
import argparse
import logging
import time

# Add parent path to import from meraki_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.logger import setup_logger
from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.policy_objects import get_policy_object_by_name

parser = argparse.ArgumentParser(description="Delete Meraki policy object from a CSV file")
parser.add_argument("--csv_file", type=str, default="delete_policy_objects.csv", help="CSV filename in /data directory")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

logger.info("Script Started")

def main():
    orgId = get_organization_id(dashboard)
    if not orgId:
        logger.error("Organization ID not found.")
        return

    csv_path = Path(__file__).resolve().parent.parent.parent / "data" / args.csv_file
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return

    deleted_count = 0
    skipped_count = 0

    deleted_policy_objects = []

    with csv_path.open(mode='r') as file: 
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            name = row['name']
            if not name:
                logger.warning("Empty name found in CSV, skipping row.")
                skipped_count += 1
                continue

            try:
                obj = get_policy_object_by_name(dashboard, orgId, objectName=name)
            except Exception as e:
                logger.error(f"Failed to retrieve object named {name}: {e}")
                skipped_count += 1
                continue

            if obj is None:
                logger.error(f"Policy object named '{name}' not found. Skipping deletion.")
                skipped_count += 1
                continue
            
            obj_id = obj['id']
            obj_type = obj['type']

            if obj_type == 'fqdn':
                value = obj['fqdn']
            elif obj_type == 'cidr':
                value = obj['cidr']

            if not obj_id:
                logger.error(f"Object ID not found for object named '{name}'. Skipping update.")
                skipped_count += 1
                continue
            
            try:
                dashboard.organizations.deleteOrganizationPolicyObject(orgId, obj_id)
                logger.info(f"Deleted policy object '{name}' with ID {obj_id}")
                deleted_policy_objects.append({
                    'name': obj['name'],
                    'type': obj['type'],
                    'value': value,
                    })
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete object with ID {obj_id}: {e}")
                skipped_count += 1
                continue
        
    

    output_csv_path = Path(__file__).resolve().parent.parent.parent / "output" / "deleted_policy_objects_log.csv"
    try: 
        file_exists = output_csv_path.exists()

        with output_csv_path.open(mode='a', newline='') as outfile:
            fieldnames = ['name', 'type', 'value']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()

            for obj in deleted_policy_objects:
                writer.writerow(obj)

        logger.info(f"Deleted policy objects logged to {output_csv_path}")
    except Exception as e:
        logger.error(f"Failed to write deleted policy objects to CSV: {e}")

    logger.info(f"Summary: Deleted {deleted_count} objects, skipped {skipped_count}")

if __name__ == "__main__":
    main()
