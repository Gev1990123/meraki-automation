import sys
import os
import csv
from pathlib import Path
import logging
import argparse

# Add parent path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.policy_objects import get_all_policy_objects
from meraki_utils.logger import setup_logger

parser = argparse.ArgumentParser(description="Export Meraki policy objects")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

# Setup logging
setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

def main():
    orgId = get_organization_id(dashboard)
    if not orgId:
        print("Organization ID not found.")
        return
    
    current_objects = []

    try:
        policy_objects = get_all_policy_objects(dashboard, orgId)
    except Exception as e:
        print(f"❌ Failed to fetch policy objects: {e}")
        return

    for obj in policy_objects:
        if obj['type'] == 'fqdn': 
            current_objects.append({
                'id': obj['id'],
                'name': obj['name'],
                'type': obj['type'],
                'value': obj['fqdn']
            })
        elif obj['type'] == 'cidr':
            current_objects.append({
                'id': obj['id'],
                'name': obj['name'],
                'type': obj['type'],
                'value': obj['cidr']
            })

    output_path = Path(__file__).resolve().parent.parent.parent / "output" / "policy_objects_output.csv"


    with output_path.open(mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name", "type", "value"])
        writer.writeheader()
        writer.writerows(current_objects)

    print(f"✅ Exported {len(current_objects)} policy objects to {output_path}")

if __name__ == "__main__":
    main()