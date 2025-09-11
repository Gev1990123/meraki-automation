import logging
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import get_policy_object_by_id
from meraki_utils.firewall import firewall_get_l3_rules, firewall_l3_rule_exists
from meraki_utils.network import get_all_prod_networks
from meraki_utils.site_codes import get_site_info_from_network
from meraki_utils.logger import setup_logger

def create_firewall_rule(
    comment="Azure VPN Connectivity-IntToInt-Any-001",
    policy="allow",
    protocol="Any",
    src_port="Any",
    dest_port="Any",
    enable_syslog=False,
    rule_position=2,
    dry_run=False,
    debug=False,
):
    """
    Add a Layer 3 firewall rule to all production networks (except one excluded network).
    Returns tuple: (success_flag: bool, details: dict or error message)
    """
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)
    
    orgId = get_organization_id(dashboard)
    if not orgId:
        logger.error("Organisation ID not found.")
        return False, "Organisation ID not found"
    
    networks = get_all_prod_networks(dashboard, orgId)

    dst_groups = ['NETWORK Internal TNLCF CIDR']
    src_groups = ['AVPN Internal Clients CIDR']

    success_networks = []
    skipped_networks = []
    error_networks = []

    for network in networks:
        network_name = network.get('name')
        if network_name == "AUKS-L-MX-PROD":
            logger.warning(f"Not continuing with {network_name}, as it's in Azure")
            skipped_networks.append(network_name)
            continue

        networkId = network.get('id')
        current_l3_rules = firewall_get_l3_rules(dashboard, networkId).get('rules', [])
        current_l3_rules = [rule for rule in current_l3_rules if rule.get('comment', '').strip() != 'Default rule']

        site = get_site_info_from_network(network_name)
        if not site:
            logger.warning(f"⚠️ Unknown site code for network: {network_name}")
            skipped_networks.append(network_name)
            continue

        site_code = site["site_code"]
        src_group_names = [group.format(site_code=site_code) for group in src_groups]

        src_group_ids = []
        for group in src_group_names:
            group_id = get_policy_object_by_id(dashboard, orgId, group)
            if group_id:
                src_group_ids.append(f'GRP({group_id})')
            else:
                logger.error(f"❌ Source group not found: {group}")

        dest_group_ids = []
        for group in dst_groups:
            group_id = get_policy_object_by_id(dashboard, orgId, group)
            if group_id:
                dest_group_ids.append(f'GRP({group_id})')
            else:
                logger.error(f"❌ Destination group not found: {group}")

        if not src_group_ids or not dest_group_ids:
            logger.error(f"❌ Skipping {network_name} due to missing group IDs")
            skipped_networks.append(network_name)
            continue

        src_cidr = ",".join(src_group_ids)
        dest_cidr = ",".join(dest_group_ids)

        new_rule = {
            "comment": comment,
            "policy": policy,
            "protocol": protocol,
            "destPort": dest_port,
            "destCidr": dest_cidr,
            "srcPort": src_port,
            "srcCidr": src_cidr,
            "syslogEnabled": enable_syslog
        }

        if not firewall_l3_rule_exists(new_rule, current_l3_rules):
            insert_index = max(0, min(rule_position - 1, len(current_l3_rules)))
            updated_rules = current_l3_rules[:insert_index] + [new_rule] + current_l3_rules[insert_index:]

            if dry_run:
                logger.info(f"[Dry Run] Would add rule to {network_name} at position {rule_position}")
                logger.debug(f"[Dry Run] Rule: {new_rule}")
                success_networks.append(network_name)
            else:
                try:
                    dashboard.appliance.updateNetworkApplianceFirewallL3FirewallRules(networkId, rules=updated_rules)
                    logger.info(f"✅ Rule added to {network_name}")
                    success_networks.append(network_name)
                except Exception as e:
                    logger.error(f"❌ Failed to update rules for {network_name}: {e}")
                    error_networks.append(network_name)
        else:
            logger.info(f"✅ Rule already exists in {network_name}, skipping update.")
            skipped_networks.append(network_name)

    return True, {
        "success": success_networks,
        "skipped": skipped_networks,
        "error": error_networks
    }
