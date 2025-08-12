import sys
import os
import socket
import csv
import logging
import argparse
from collections import defaultdict
from pathlib import Path

# Add parent path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import get_all_policy_objects
from meraki_utils.logger import setup_logger

# CLI arguments
parser = argparse.ArgumentParser(description="Find duplicate Meraki policy objects by resolved IP")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

# Setup logging
setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

def resolve_fqdn(fqdn):
    try:
        return socket.gethostbyname_ex(fqdn)[2]
    except socket.gaierror:
        logger.warning(f"⚠️ Could not resolve FQDN: {fqdn}")
        return []

def main():
    org_id = get_organization_id(dashboard)
    if not org_id:
        logger.error("❌ Organization ID not found.")
        return

    try:
        objects = get_all_policy_objects(dashboard, org_id)
    except Exception as e:
        logger.error(f"❌ Failed to fetch policy objects: {e}")
        return

    ip_to_objects = defaultdict(list)
    duplicate_rows = []

    for obj in objects:
        name = obj.get("name")
        obj_type = obj.get("type")
        value = None

        if obj_type == 'cidr':
            value = obj.get("cidr")
        elif obj_type == 'fqdn':
            value = obj.get("fqdn")

        if not value:
            continue

        if obj_type == 'fqdn' and '*' in value:
            logger.warning(f"⚠️ Wildcard FQDN '{value}' cannot be resolved via DNS. Skipping.")
            continue

        resolved_ips = []
        if obj_type == 'fqdn':
            resolved_ips = resolve_fqdn(value)
        elif obj_type in ['ip', 'cidr']:
            resolved_ips = [value]

        for ip in resolved_ips:
            ip_to_objects[ip].append({
                "object_name": name,
                "object_type": obj_type,
                "object_value": value,
                "resolved_ip": ip
            })

    # Output duplicates to CSV
    for ip, entries in ip_to_objects.items():
        if len(entries) > 1:
            for entry in entries:
                duplicate_rows.append(entry)

    if not duplicate_rows:
        logger.info("✅ No duplicates found.")
        return

    output_path = Path(__file__).resolve().parent.parent.parent / "output"
    output_path.mkdir(exist_ok=True)
    output_file = output_path / "duplicate_policy_objects.csv"

    with output_file.open("w", newline='') as csvfile:
        fieldnames = ["object_name", "object_type", "object_value", "resolved_ip"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(duplicate_rows)

    logger.info(f"✅ Duplicates exported to: {output_file}")

if __name__ == "__main__":
    main()