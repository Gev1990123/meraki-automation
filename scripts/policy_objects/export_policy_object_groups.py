import csv
from pathlib import Path
import logging

from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.policy_objects import get_all_policy_objects, get_all_policy_object_groups, get_policy_object_by_id
from meraki_utils.logger import setup_logger

def write_csv(csv_file, group_objects):
    try:
        path = Path(csv_file)
        with path.open(mode='w', newline='') as outfile:
            fieldnames = ['group_name', 'object_name', 'object_type', 'object_value']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for obj in group_objects:
                writer.writerow(obj)

        return True, f"✅ Successfully wrote policy object groups to: {csv_file}"
    except Exception as e:
        return False, f"❌ Failed to write to file: {e}"


def export_policy_object_groups(csv_file, debug=False, log_callback=None):
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)

    def log(msg, level="info"):
        if log_callback:
            log_callback(msg)
        getattr(logger, level)(msg)

    log("🚀 Starting export of policy object groups...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None

    try:
        group_objects = get_all_policy_object_groups(dashboard, org_id)
    except Exception as e:
        log(f"❌ Failed to fetch group objects: {e}")
        return

    current_objects = []

    for group in group_objects:
        groupName = group['name']
        object_ids = group.get('objectIds', [])

        for object_id in object_ids:
            try:
                obj = get_policy_object_by_id(dashboard, org_id, object_id)

                type = obj.get("type", "")
                if type == 'fqdn':
                    object_value = obj.get("fqdn", "")
                elif type == 'cidr':
                    object_value = obj.get("cidr", "")

                current_objects.append({
                    "group_name": groupName,
                    "object_name": obj.get("name", ""),
                    "object_type": type,
                    "object_value": object_value

                })
            except Exception as e:
                log(f"⚠️ Failed to fetch object '{object_id}' in group '{groupName}': {e}")


    success, result_message = write_csv(csv_file, current_objects)
    log(result_message)

    if success:
        summary = f"✅ Exported {len(current_objects)} policy object group members."
        log(summary)

        return {
            "count": len(current_objects),
            "summary": summary
        }
    else:
        return None

