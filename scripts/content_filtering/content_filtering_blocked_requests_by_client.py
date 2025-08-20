import sys
import os
import csv
from pathlib import Path
import logging
import re
import argparse
from collections import defaultdict
from datetime import datetime, timedelta

# Add parent path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.logger import setup_logger
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.network import get_all_networks, get_network_events

parser = argparse.ArgumentParser(description="Report on blocked content filtering requests by client.")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument("--output", default="blocked_requests_by_client.csv", help="Output CSV file path")
parser.add_argument("--days", type=int, default=1, help="How many days back to check")
parser.add_argument("--network", help="Filter networks by substring (e.g. 'LON')")
args = parser.parse_args()

setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

def export_to_csv(data, output_path):
    fieldnames = ['network', 'client', 'blocked_requests']
    output_path = Path(output_path)
    try:
        with output_path.open('w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Data successfully exported to {output_path.resolve()}")
    except Exception as e:
        logger.error(f"Failed to export data to CSV: {e}")


def main():
    org_id = get_organization_id(dashboard)
    if not org_id:
        logger.error("Organization ID not found.")
        return
    
    all_networks = get_all_networks(dashboard, org_id)
    if not all_networks:
        logger.warning("No production networks found.")
        return
    
    if args.network:
        filter_value = args.network.strip().upper()
        all_networks = [net for net in all_networks if filter_value in net['name'].upper()]
        logger.info(f"Filtered networks using --networks '{filter_value}': {len(all_networks)} found.")

    time_since = (datetime.utcnow() - timedelta(days=args.days)).isoformat() + "Z"
    results = []
    
    for network in all_networks:
        network_name = network['name']
        network_id = network['id']
        product_types = network.get('productTypes', [])

        if 'appliance' not in product_types:
            logger.info(f"Skipping {network_name} (no appliance)")
            continue

        logger.info(f"Fetching events for {network_name}...")

        events = get_network_events(dashboard, network_id, product_type='appliance', starting_after=time_since, event_type='contentFilteringBlocked')
        
        blocked_by_client = defaultdict(int)

        for event in events:
            client = event.get('clientMac') or event.get('clientIp') or "unknown"
            blocked_by_client[client] += 1

        if results:
            export_to_csv(results, args.ouput)
        else:
            logger.info("No blocked content filtering events found.")


if __name__ == "__main__":
    main()