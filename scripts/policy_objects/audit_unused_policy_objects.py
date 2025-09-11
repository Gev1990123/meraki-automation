# audit_logic.py
import os
import csv
import logging
import re
from pathlib import Path

from meraki_utils.logger import setup_logger
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import (
    get_all_policy_objects,
    get_all_policy_object_groups,
    get_object_ids_from_group_id,
)
from meraki_utils.network import get_all_networks, get_all_l3_firewall_rules

logger = logging.getLogger(__name__)

def extract_group_ids(cidr_field):
    if not cidr_field:
        return []
    return re.findall(r'GRP\((\d+)\)', cidr_field)


def audit_unused_policy_objects(log_callback=None, debug=False):
    try:
        setup_logger(debug=debug)
        logger = logging.getLogger(__name__)

        org_id = get_organization_id(dashboard)
        if not org_id:
            logger.error("❌ Organization ID not found.")
            return "❌ Organization ID not found."
    
        all_policy_objects = get_all_policy_objects(dashboard, org_id)
        all_object_dict = {obj['id']: obj for obj in all_policy_objects}
        logger.info(f"Total policy objects found: {len(all_object_dict)}")

        all_groups = get_all_policy_object_groups(dashboard, org_id)
        logger.info(f"Total policy object groups found: {len(all_groups)}")

        networks = get_all_networks(dashboard, org_id)
        logger.info(f"Total networks found: {len(networks)}")

        all_rules = []
        for network in networks:
            network_id = network['id']

            try:
                rules_resp = get_all_l3_firewall_rules(dashboard, network_id)
                rules = rules_resp.get('rules', [])
                logger.info(f"Fetched {len(rules)} firewall rules from network {network['name']} ({network_id})")
                all_rules.extend(rules)
            except Exception as e:
                logger.warning(f"Failed to get firewall rules for network {network['name']} ({network_id}): {e}")

        logger.info(f"Total firewall rules aggregated: {len(all_rules)}")

        # Extract referenced group IDs
        used_group_ids = set()
        for rule in all_rules:
            used_group_ids.update(extract_group_ids(rule.get('srcCidr', '')))
            used_group_ids.update(extract_group_ids(rule.get('destCidr', '')))
        logger.info(f"Total unique group IDs referenced in firewall rules: {len(used_group_ids)}")

        used_object_ids = set()
        for group_id in used_group_ids:
            try:
                group = get_object_ids_from_group_id(dashboard, org_id, group_id)
                object_ids = group.get('objectIds', [])
                used_object_ids.update(object_ids)
            except Exception as e:
                logger.warning(f"Failed to get object IDs from group {group_id}: {e}")

        for group in all_groups:
            used_object_ids.update(group.get('objectIds', []))

        logger.info(f"Total unique policy object IDs used in groups: {len(used_object_ids)}")

        # Determine unused policy objects
        unused_object_ids = set(all_object_dict.keys()) - used_object_ids
        logger.info(f"Total unused policy objects found: {len(unused_object_ids)}")

        unused_objects = [all_object_dict[obj_id] for obj_id in unused_object_ids]

        # Write to CSV
        output_path = Path(__file__).resolve().parent.parent / "output" / "unused_policy_objects.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open('w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'type', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for obj in unused_objects:
                value = obj.get('cidr') if obj['type'] == 'cidr' else obj.get('fqdn', '')
                writer.writerow({
                    'id': obj['id'],
                    'name': obj['name'],
                    'type': obj['type'],
                    'value': value
                })

        logger.info(f"✅ Unused policy objects exported to {output_path}")
        return output_path

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return None