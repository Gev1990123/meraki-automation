import sys
import os
import csv
from pathlib import Path
import logging
import argparse

# Add parent path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import is_policy_object_present, get_policy_object_id
from meraki_utils.helpers import contains_letters
from meraki_utils.logger import setup_logger

parser = argparse.ArgumentParser(description="Create Meraki policy object from a CSV file")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)


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

def main():
    orgId = get_organization_id(dashboard)
    if not orgId:
        print("Organization ID not found.")
        return
    
    csv_path = Path(__file__).resolve().parent.parent / "data" / "policy_objects.csv"
    if not csv_path.exists():
        print(f"CSV file not found at {csv_path}")
        return

    objects = load_csv(csv_path)
    new_objects = []
    existing_objects = []

    for obj in objects:
        name = obj['name']
        ip = obj['ip']

        if not is_policy_object_present(dashboard, orgId, name, ip):
            print(f"➕ Creating policy object: {name} ({ip})")
            object_type = contains_letters(ip)
            try:
                if object_type == 'cidr':
                    response = dashboard.organizations.createOrganizationPolicyObject(orgId, name=name, category='network', type='cidr', cidr=ip)
                elif object_type == 'fqdn':
                    response = dashboard.organizations.createOrganizationPolicyObject(orgId, name=name, category='network', type='fqdn', fqdn=ip)
                else:
                    print(f"❌ Unsupported IP format for {name}: {ip}")
                    continue
                
                new_objects.append(response['id'])
            except Exception as e:
                print(f"❌ Error creating object {name}: {e}")
        else:
            print(f"✅ Object {name} already exists.")
            obj_id = get_policy_object_id(dashboard, orgId, name, ip)
            existing_objects.append(obj_id)

    print("\nSummary:")
    print(f"Newly created objects: {len(new_objects)}")
    print(f"Existing objects: {len(existing_objects)}")
  
if __name__ == "__main__":
    main()