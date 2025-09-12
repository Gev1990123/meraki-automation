from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.policy_objects import get_all_policy_objects, get_all_policy_object_groups, get_policy_object_by_id
from meraki_utils.logger import log, set_log_callback
from meraki_utils.helpers import write_csv

def export_policy_object_groups(csv_file, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

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


    success, result_message = write_csv(csv_file=csv_file, data=current_objects, fieldnames=['group_name', 'object_name', 'object_type', 'object_value'])
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

