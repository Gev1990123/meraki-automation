import socket
import csv
import logging
from collections import defaultdict
from pathlib import Path

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import get_all_policy_objects
from meraki_utils.logger import setup_logger

def resolve_fqdn(fqdn, log):
    try:
        return socket.gethostbyname_ex(fqdn)[2]
    except socket.gaierror:
        log(f"⚠️ Could not resolve FQDN: {fqdn}")
        return []
    
def write_csv(csv_file, group_objects):
    try:
        path = Path(csv_file)
        with path.open(mode='w', newline='') as outfile:
            fieldnames = ['object_name', 'object_type', 'object_value', 'resolved_ip']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for obj in group_objects:
                writer.writerow(obj)

        return True, f"✅ Successfully wrote policy object groups to: {csv_file}"
    except Exception as e:
        return False, f"❌ Failed to write to file: {e}"

def find_duplicate_policy_objects(csv_file, debug=False, log_callback=None):
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)

    def log(msg, level="info"):
        if log_callback:
            log_callback(msg)
        getattr(logger, level)(msg)

    log("🚀 Finding duplicate policy objects...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None
    
    try:
        objects = get_all_policy_objects(dashboard, org_id)
    except Exception as e:
        log(f"❌ Failed to fetch policy objects: {e}")
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
            log(f"⚠️ Wildcard FQDN '{value}' cannot be resolved via DNS. Skipping.")
            continue

        resolved_ips = []
        if obj_type == 'fqdn':
            resolved_ips = resolve_fqdn(value, log)
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
        log("✅ No duplicates found.")
        return
    
    success, result_message = write_csv(csv_file, duplicate_rows)
    log(result_message)

    if success: 
        summary = f"Number of duplicate policy objects {len(duplicate_rows)}."
        log(summary)

        return {
            "count": len(duplicate_rows),
            "summary": summary
        }
    else:
        return None