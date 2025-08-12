import sys
import os
import csv
from pathlib import Path
import logging
import argparse

# Add parent path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.policy_objects import get_all_policy_objects, get_all_policy_object_groups, get_policy_object_by_id
from meraki_utils.logger import setup_logger

parser = argparse.ArgumentParser(description="Export Meraki Policy Object Groups")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

# Setup logging
setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

def main():
    orgId = get_organization_id(dashboard)
    if not orgId:
        print("Organization ID not found.")
        return

    try:
        group_objects = get_all_policy_object_groups(dashboard, orgId)
    except Exception as e:
        print(f"❌ Failed to fetch group objects: {e}")
        return

    current_objects = []

    for group in group_objects:
        groupId = group['id']
        groupName = group['name']
        objectIds = group.get('objectIds', [])

        for objectId in objectIds:
            try:
                obj = get_policy_object_by_id(dashboard, orgId, objectId)
                current_objects.append({
                    "group_name": groupName,
                    "object_name": obj.get("name", ""),
                    "object_type": obj.get("type", ""),
                    "object_value": obj.get("value", ""),

                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch object '{objectId}' in group '{groupName}': {e}")



    output_path = Path(__file__).resolve().parent.parent.parent / "output" / "policy_group_objects_output.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["group_name", "object_name", "object_type", "object_value"])
        writer.writeheader()
        writer.writerows(current_objects)

    logger.info(f"✅ Exported {len(current_objects)} policy object group members to {output_path}")

if __name__ == "__main__":
    main()