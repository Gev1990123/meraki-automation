from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.policy_objects import get_all_policy_objects
from meraki_utils.logger import log, set_log_callback
from meraki_utils.helpers import write_csv

def export_policy_objects(csv_file, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🚀 Starting export of policy object groups...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None
    
    current_objects = []

    try:
        policy_objects = get_all_policy_objects(dashboard, org_id)
    except Exception as e:
        log(f"❌ Failed to fetch policy objects: {e}")
        return

    for obj in policy_objects:
        if obj['type'] == 'fqdn': 
            current_objects.append({
                'id': obj['id'],
                'name': obj['name'],
                'type': obj['type'],
                'value': obj['fqdn']
            })
        elif obj['type'] == 'cidr':
            current_objects.append({
                'id': obj['id'],
                'name': obj['name'],
                'type': obj['type'],
                'value': obj['cidr']
            })
    
    success, result_message = write_csv(csv_file=csv_file, data=current_objects, fieldnames=['id', 'type', 'name', 'value'])
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