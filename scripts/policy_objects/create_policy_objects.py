from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import is_policy_object_present, get_policy_object_id
from meraki_utils.helpers import contains_letters
from meraki_utils.logger import log, set_log_callback
from meraki_utils.helpers import load_csv

def create_policy_objects(csv_file, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🚀 Starting policy objects creation...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None

    objects = load_csv(csv_file=csv_file, fieldnames=['name', 'ip'])

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
  