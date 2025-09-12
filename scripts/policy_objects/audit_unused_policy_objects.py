import re
from pathlib import Path
import csv

from meraki_utils.logger import log, set_log_callback
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import (
    get_all_policy_objects,
    get_all_policy_object_groups,
    get_object_ids_from_group_id,
)
from meraki_utils.network import get_all_networks, get_all_l3_firewall_rules

def extract_group_ids(cidr_field):
    if not cidr_field:
        return []
    return re.findall(r'GRP\((\d+)\)', cidr_field)


def write_csv(csv_file, group_objects):
    try:
        path = Path(csv_file)
        with path.open(mode='w', newline='') as outfile:
            fieldnames = ['id', 'name', 'type', 'value']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for obj in group_objects:
                writer.writerow(obj)

        return True, f"✅ Successfully wrote policy object groups to: {csv_file}"
    except Exception as e:
        return False, f"❌ Failed to write to file: {e}"


def audit_unused_policy_objects(csv_file, log_callback=None, debug=False):
    if log_callback:
        set_log_callback(log_callback)

    log("Running audit on unsued policy objects")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return []
    
    all_policy_objects = get_all_policy_objects(dashboard, org_id)
    if not all_policy_objects:
        log("No policy objects found")
        return []
    
    all_object_dict = {obj['id']: obj for obj in all_policy_objects}
    log(f"Total policy objects found: {len(all_object_dict)}")

    all_groups = get_all_policy_object_groups(dashboard, org_id)
    if not all_groups:
        log("No policy object groups found")
        return []
    
    log(f"Total policy object groups found: {len(all_groups)}")

    all_networks = get_all_networks(dashboard, org_id, prod=True)
    if not all_networks:
        log("⚠️ No production networks found.")
        return []

    log(f"Total networks found: {len(all_networks)}")

    all_rules = []
    for network in all_networks:
        network_id = network['id']

        try:
            rules_resp = get_all_l3_firewall_rules(dashboard, network_id)
            rules = rules_resp.get('rules', [])
            log(f"Fetched {len(rules)} firewall rules from network {network['name']} ({network_id})")
            all_rules.extend(rules)
        except Exception as e:
            log(f"Failed to get firewall rules for network {network['name']} ({network_id}): {e}")

        log(f"Total firewall rules aggregated: {len(all_rules)}")

    # Extract referenced group IDs
    used_group_ids = set()
    for rule in all_rules:
        used_group_ids.update(extract_group_ids(rule.get('srcCidr', '')))
        used_group_ids.update(extract_group_ids(rule.get('destCidr', '')))
    
    log(f"Total unique group IDs referenced in firewall rules: {len(used_group_ids)}")

    used_object_ids = set()
    for group_id in used_group_ids:
        try:
            group = get_object_ids_from_group_id(dashboard, org_id, group_id)
            object_ids = group.get('objectIds', [])
            used_object_ids.update(object_ids)
        except Exception as e:
            log(f"Failed to get object IDs from group {group_id}: {e}")

    for group in all_groups:
        used_object_ids.update(group.get('objectIds', []))

    log(f"Total unique policy object IDs used in groups: {len(used_object_ids)}")

    # Determine unused policy objects
    unused_object_ids = set(all_object_dict.keys()) - used_object_ids
    log(f"Total unused policy objects found: {len(unused_object_ids)}")

    unused_objects = [all_object_dict[obj_id] for obj_id in unused_object_ids]

    # Write to CSV

    for obj in unused_objects:
        if obj['type'] == 'cidr':
            value = obj.get('cidr', '')
        elif obj['type'] == 'fqdn':
            value = obj.get('fqdn', '')
        else:
            value = ''
        obj['value'] = value
 
    success, result_message = write_csv(csv_file, unused_objects)
    log(result_message)

    if success: 
        summary = f"Located {len(unused_objects)} unsed policy objects"
        log(summary)

        return {
            "count": len(unused_objects),
            "summary": summary
        }