import csv
from pathlib import Path

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import is_policy_object_groups_present, get_policy_object_group_by_name, get_policy_object_by_name, get_all_policy_object_groups
from meraki_utils.logger import log, set_log_callback

def load_csv(file_path):
    objects = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            name = row.get('name', '').strip()
            if name:
                    objects.append({'name': name})
    return objects

def get_policy_object_groups_for_dropdown(log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🔄 Fetching policy object groups...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return []

    try:
        groups = get_all_policy_object_groups(dashboard, org_id)
        log(f"✅ Retrieved {len(groups)} policy object groups.")
        return groups
    except Exception as e:
        log(f"❌ Failed to fetch from Meraki API: {e}")
        return []

def update_policy_objects_in_group(csv_file, policy_object_group, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🚀 Starting update.. ")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        log(f"❌ CSV file not found: {csv_path}")
        return None

    objects = load_csv(csv_path)

    try:
        group = get_policy_object_group_by_name(dashboard, org_id, group_name=policy_object_group)
    except Exception as e:
        log(f"❌ Failed to fetch group '{policy_object_group}': {e}")
        return

    groupId = group['id']
    existing_object_ids = set(group.get('objectIds', []))

    created_count = 0
    skipped_count = 0

    for obj in objects:
        try:
            pol_object = get_policy_object_by_name(dashboard, org_id, obj['name'])
            if pol_object is None:
                log(f"❌ Policy object not found: '{obj['name']}'")
                skipped_count += 1
                continue

            pol_object_id = pol_object['id']

            if pol_object_id in existing_object_ids:
                log(f"⏭️ Object '{obj['name']}' already in group. Skipping.")
                skipped_count += 1
                continue

            existing_object_ids.add(pol_object_id)
            created_count +=1
            log(f"➕ Added object '{obj['name']}' to group update list.")

        except Exception as e:
            log(f"Failed to retrieve object with name {obj['name']}: {e}")
            skipped_count +=1
            continue

    if not existing_object_ids:
        log("🚫 No valid policy objects to update the group with. Nothing to do.")
        return
    
    log(f"📦 Updating group with object IDs: {list(existing_object_ids)}")

    try:
        dashboard.organizations.updateOrganizationPolicyObjectsGroup(
            org_id, groupId,
            objectIds=list(existing_object_ids)
        )
        log(f"✅ Updated group '{policy_object_group}' with new objects.")
    except Exception as e:
        log(f"❌ Failed to update group: {e}")

    summary = f"\n📋 Summary:\n  ➕ Created: {created_count}\n  ⏭️ Skipped (already exists or failed): {skipped_count}"
    log(summary)

    return {
        "summary": summary,
        "created": created_count,
        "skipped": skipped_count
    }

