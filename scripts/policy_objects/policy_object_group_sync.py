import sys
import os
import csv
from pathlib import Path
import argparse
import logging

# Add parent path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.logger import setup_logger
from meraki_utils.config import dashboard
from meraki_utils.functions import (
    get_organization_id,
    is_policy_object_present,
    is_policy_object_groups_present,
    get_policy_object_group,
    get_policy_object_id,
    get_object_ids_from_group_id,
    contains_letters
)

parser = argparse.ArgumentParser(description="Create or update Meraki policy objects and groups")
parser.add_argument("--group_name", type=str, required=True, help="Name of the policy object group to create or update")
parser.add_argument("--csv_file", type=str, default="policy_objects_create.csv", help="CSV filename in the /data directory")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

logger.info("Script Started")

def load_policy_objects_from_csv(csv_path):
    objects = []
    with csv_path.open(mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            objects.append({
                'name': row['name'],
                'ip': row['ip']
            })
    return objects

def create_or_get_policy_object(dashboard, org_id, name, ip):
    if not is_policy_object_present(dashboard, org_id, name, ip):
        logger.info(f"➕ Creating policy object: {name} ({ip})")
        category = "network"
        obj_type = contains_letters(ip)
        if obj_type == "cidr":
            res = dashboard.organizations.createOrganizationPolicyObject(
                org_id, name=name, category=category, type=obj_type, cidr=ip
            )
        elif obj_type == "fqdn":
            res = dashboard.organizations.createOrganizationPolicyObject(
                org_id, name=name, category=category, type=obj_type, fqdn=ip
            )
        else:
            logger.error(f"⚠️ Unknown object type for {ip}")
            return None
        return res['id']
    else:
        logger.info(f"✅ Object already exists: {name} ({ip})")
        return get_policy_object_id(dashboard, org_id, name, ip)

def main():
    org_id = get_organization_id(dashboard)
    if not org_id:
        logger.error("❌ Organisation ID not found.")
        return

    # --- Load objects ---
    csv_path = Path(__file__).resolve().parent.parent / "data" / args.csv_file
    if not csv_path.exists():
        logger.error(f"❌ CSV file not found: {csv_path}")
        return
    policy_objects = load_policy_objects_from_csv(csv_path)

    # --- Create or fetch object IDs ---
    all_object_ids = []
    for obj in policy_objects:
        obj_id = create_or_get_policy_object(dashboard, org_id, obj['name'], obj['ip'])
        if obj_id:
            all_object_ids.append(obj_id)

    # --- Policy Object Group Name ---
    group_name = args.group_name

    if not is_policy_object_groups_present(dashboard, org_id, group_name):
        logger.info(f"➕ Creating policy object group: {group_name}")
        dashboard.organizations.createOrganizationPolicyObjectsGroup(
            org_id, name=group_name, category="NetworkObjectGroup"
        )
    else:
        logger.info(f"✅ Policy Object Group already exists: {group_name}")
    # --- Add missing objects to the group ---
    group_id = get_policy_object_group(dashboard, org_id, group_name)
    current_group = get_object_ids_from_group_id(dashboard, org_id, group_id)
    current_ids = set(current_group.get("objectIds", []))

    combined_ids = list(current_ids.union(all_object_ids))

    logger.info(f"🛠 Updating group '{group_name}' with {len(combined_ids)} total object(s)...")

    dashboard.organizations.updateOrganizationPolicyObjectsGroup(
        org_id, group_id, objectIds=combined_ids
    )

    logger.info(f"✅ Policy Object Group updated successfully")
if __name__ == "__main__":
    main()
