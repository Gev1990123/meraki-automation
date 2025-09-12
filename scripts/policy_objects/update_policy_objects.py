import csv
from pathlib import Path

from meraki_utils.logger import log, set_log_callback
from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.policy_objects import get_policy_object_by_name

def load_csv(file_path):
    objects = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            old_name = (row.get('old_name') or '').strip()
            new_name = (row.get('new_name') or '').strip()
            value = (row.get('value') or '').strip()
            
            
            objects.append({
                'old_name': old_name,
                'new_name': new_name,
                'value': value
            })
            
    return objects


def update_policy_objects(csv_file, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🚀 Starting update of policy objects...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        log(f"❌ CSV file not found: {csv_path}")
        return None

    updated_count = 0
    skipped_count = 0

    objects = load_csv(csv_file)

    for obj in objects:
        old_name = obj['old_name']
        new_name = obj['new_name']
        value = obj['value']

        try:
            object = get_policy_object_by_name(dashboard, org_id, objectName=old_name)
        except Exception as e:
            log(f"Failed to retrieve object with name {old_name}: {e}")
            skipped_count += 1
            continue
            
        obj_id = object.get('id')

        if not obj_id:
            log(f"Object ID not found for object named '{old_name}'. Skipping update.")
            skipped_count += 1
            continue

        update_payload = {}

        if new_name and new_name.strip():
                update_payload['name'] = new_name.strip()
        else:
            log(f"New name is empty for object ID {obj_id}. Skipping update.")

        if not value or not value.strip():
            log(f"Value is empty for object ID {obj_id}. Skipping update.")
        else:
            if object['type'] == 'cidr':
                update_payload['cidr'] = value.strip()
            elif object['type'] == 'fqdn':
                update_payload['fqdn'] = value.strip()
            else:
                log(f"Unsupported object type '{object['type']}' for object ID {obj_id}. Skipping update.")
                skipped_count += 1
                continue

        if not update_payload:
            logger.info(f"No updates provided for object ID {obj_id}. Skipping.")
            skipped_count += 1
            continue

        try:
            dashboard.organizations.updateOrganizationPolicyObject(
                organizationId=org_id,
                policyObjectId=obj_id,
                **update_payload
            )

            log(f"Updated object ID {obj_id} with {update_payload}")
            updated_count += 1
        except Exception as e:
            log(f"Failed to update object {obj_id}: {e}")
            skipped_count += 1

    summary = (f"\nSummary:\n✅ Updated: {updated_count}\n❌ Skipped/Failed: {skipped_count}")
    log(summary)

    return {
        "summary": summary,
        "updated_count": updated_count,
        "skipped_count": skipped_count
    }


