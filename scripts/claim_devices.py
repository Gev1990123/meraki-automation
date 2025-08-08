import sys
import os
import csv
from pathlib import Path

# Add parent path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.network import is_network_present, get_network_id


def claim_network_device(serial, networkId):
    try:
        response = dashboard.networks.claimNetworkDevices(networkId, serials=[serial])
        return response
    except Exception as e:
        print(f"❌ Failed to claim device {serial} to network {networkId}: {e}")
        return None

def main():
    orgId = get_organization_id(dashboard)
    if not orgId:
        print("Organization ID not found.")
        return
    
    data_path = Path(__file__).resolve().parent.parent / "data" / "device_serials.csv"
    with data_path.open(mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            network_name = row['network_name']
            serial = row['serial_number']

            if is_network_present(dashboard, orgId, network_name):
                networkId = get_network_id(dashboard, orgId, network_name)
                if networkId:
                    claim_network_device(serial, networkId)
                    print(f'Network device with serial {serial} has been claimed to {network_name}')
                else:
                    print(f'Network ID for {network_name} not found')
            else:
                print(f'Network {network_name} not present')

if __name__ == "__main__":
    main()
