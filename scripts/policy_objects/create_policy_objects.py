import csv
from pathlib import Path
import logging

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import is_policy_object_present, get_policy_object_id
from meraki_utils.helpers import contains_letters
from meraki_utils.logger import setup_logger

def load_csv(file_path):
    objects = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            objects.append({
                'name': row['name'],
                'ip': row['ip']
            })
    return objects

def create_policy_objects(csv_file, debug=False, log_callback=None):
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)

    def log(msg, level="info"):
        if log_callback:
            log_callback(msg)
        getattr(logger, level)(msg)

    log("🚀 Starting policy objects creation...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        log(f"❌ CSV file not found: {csv_path}")
        return None

    objects = load_csv(csv_path)

    new_objects = []
    existing_objects = []

    for obj in objects:
        name = obj['name']
        ip = obj['ip']

        if not is_policy_object_present(dashboard, org_id, name, ip):
            log(f"➕ Creating policy object: {name} ({ip})")
            object_type = contains_letters(ip)
            try:
                if object_type == 'cidr':
                    response = dashboard.organizations.createOrganizationPolicyObject(org_id, name=name, category='network', type='cidr', cidr=ip)
                elif object_type == 'fqdn':
                    response = dashboard.organizations.createOrganizationPolicyObject(org_id, name=name, category='network', type='fqdn', fqdn=ip)
                else:
                    log(f"❌ Unsupported IP format for {name}: {ip}")
                    continue
                
                new_objects.append(response['id'])
            except Exception as e:
                log(f"❌ Error creating object {name}: {e}")
        else:
            log(f"✅ Object {name} already exists.")
            obj_id = get_policy_object_id(dashboard, org_id, name, ip)
            existing_objects.append(obj_id)

    summary = f"\n📋 Summary:\n  ➕ Newly Created: {len(new_objects)}\n  ⏭️ Exisiting Objects: {len(existing_objects)}"
    log(summary)

    return {
        "newly_created": new_objects,
        "exisiting_objects": existing_objects,
        "summary": summary
    }
  