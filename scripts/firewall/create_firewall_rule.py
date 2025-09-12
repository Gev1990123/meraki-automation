from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import get_policy_object_by_id, get_all_policy_object_groups
from meraki_utils.firewall import firewall_get_l3_rules, firewall_l3_rule_exists
from meraki_utils.network import get_all_prod_networks
from meraki_utils.site_codes import get_site_info_from_network
from meraki_utils.logger import log, set_log_callback

def get_policy_object_groups_for_dropdown(log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

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

def create_firewall_rule(comment, policy, protocol, src, src_port, dst, dst_port, rule_position, enable_syslog=False, dry_run=False,  debug=False, log_callback=False):
    if log_callback:
        set_log_callback(log_callback)
    
    log("Creating Firewall Rules")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return []
    
    networks = get_all_prod_networks(dashboard, org_id)

    success_networks = []
    skipped_networks = []
    error_networks = []

    for network in networks:
        network_name = network.get('name')
        if network_name == "AUKS-L-MX-PROD":
            log(f"Not continuing with {network_name}, as it's in Azure")
            skipped_networks.append(network_name)
            continue

        networkId = network.get('id')
        current_l3_rules = firewall_get_l3_rules(dashboard, networkId).get('rules', [])
        current_l3_rules = [rule for rule in current_l3_rules if rule.get('comment', '').strip() != 'Default rule']

        site = get_site_info_from_network(network_name)
        if not site:
            log(f"⚠️ Unknown site code for network: {network_name}")
            skipped_networks.append(network_name)
            continue

        site_code = site["site_code"]
        src_group_names = [group.format(site_code=site_code) for group in src]

        src_group_ids = []
        for group in src_group_names:
            group_id = get_policy_object_by_id(dashboard, org_id, group)
            if group_id:
                src_group_ids.append(f'GRP({group_id})')
            else:
                log(f"❌ Source group not found: {group}")

        dest_group_ids = []
        for group in dst:
            group_id = get_policy_object_by_id(dashboard, org_id, group)
            if group_id:
                dest_group_ids.append(f'GRP({group_id})')
            else:
                log(f"❌ Destination group not found: {group}")

        if not src_group_ids or not dest_group_ids:
            log(f"❌ Skipping {network_name} due to missing group IDs")
            skipped_networks.append(network_name)
            continue

        src_cidr = ",".join(src_group_ids)
        dest_cidr = ",".join(dest_group_ids)

        new_rule = {
            "comment": comment,
            "policy": policy,
            "protocol": protocol,
            "destPort": dst_port,
            "destCidr": dest_cidr,
            "srcPort": src_port,
            "srcCidr": src_cidr,
            "syslogEnabled": enable_syslog
        }

        if not firewall_l3_rule_exists(new_rule, current_l3_rules):
            insert_index = max(0, min(rule_position - 1, len(current_l3_rules)))
            updated_rules = current_l3_rules[:insert_index] + [new_rule] + current_l3_rules[insert_index:]

            if dry_run:
                log(f"[Dry Run] Would add rule to {network_name} at position {rule_position}")
                log(f"[Dry Run] Rule: {new_rule}")
                success_networks.append(network_name)
            else:
                try:
                    dashboard.appliance.updateNetworkApplianceFirewallL3FirewallRules(networkId, rules=updated_rules)
                    log(f"✅ Rule added to {network_name}")
                    success_networks.append(network_name)
                except Exception as e:
                    log(f"❌ Failed to update rules for {network_name}: {e}")
                    error_networks.append(network_name)
        else:
            log(f"✅ Rule already exists in {network_name}, skipping update.")
            skipped_networks.append(network_name)

    return True, {
        "success": success_networks,
        "skipped": skipped_networks,
        "error": error_networks
    }
