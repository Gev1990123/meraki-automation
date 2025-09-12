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
            objects.append({
                'name': row['name']
            })
    return objects

def delete_policy_objects(csv_file, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🚀 Starting policy objects deletion...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None

    csv_path = Path(csv_file)
    if not csv_path.exists():
        log(f"❌ CSV file not found: {csv_path}")
        return None
    
    objects = load_csv(csv_path)

    deleted_count = 0
    skipped_count = 0

    deleted_policy_objects = []

    for object in objects:
        name = object['name']
        if not name:
            log("Empty name found in CSV, skipping row.")
            skipped_count += 1
            continue

        try:
            obj = get_policy_object_by_name(dashboard, org_id, objectName=name)
        except Exception as e:
            log(f"Failed to retrieve object named {name}: {e}")
            skipped_count += 1
            continue

        if obj is None:
                log(f"Policy object named '{name}' not found. Skipping deletion.")
                skipped_count += 1
                continue
            
        obj_id = obj['id']
        obj_type = obj['type']

        if obj_type == 'fqdn':
            value = obj['fqdn']
        elif obj_type == 'cidr':
            value = obj['cidr']

        if not obj_id:
            log(f"Object ID not found for object named '{name}'. Skipping update.")
            skipped_count += 1
            continue
            
        try:
            dashboard.organizations.deleteOrganizationPolicyObject(org_id, obj_id)
            log(f"Deleted policy object '{name}' with ID {obj_id}")
            deleted_policy_objects.append({
                'name': obj['name'],
                'type': obj['type'],
                'value': value,
                })
            deleted_count += 1
        except Exception as e:
            log(f"Failed to delete object with ID {obj_id}: {e}")
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

        log(f"Deleted policy objects logged to {output_csv_path}")
    except Exception as e:
        log(f"Failed to write deleted policy objects to CSV: {e}")

    summary = f"\n📋 Summary:\n  deleted: {deleted_count}\n Skipped Objects: {skipped_count}"
    log(summary)

    return {
        "deleted": deleted_policy_objects,
        "skipped_count": skipped_count,
        "summary": summary 
    }