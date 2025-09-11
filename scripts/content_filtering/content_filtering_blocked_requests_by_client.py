import sys
import os
import csv
from pathlib import Path
import logging
from collections import defaultdict
from datetime import datetime, timedelta

# Add parent path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.logger import setup_logger
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.network import get_all_networks, get_network_events

logger = logging.getLogger(__name__)


def export_to_csv(data, output_path):
    fieldnames = ['network', 'client', 'blocked_requests']
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with output_path.open('w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"✅ Data successfully exported to {output_path.resolve()}")
    except Exception as e:
        logger.error(f"❌ Failed to export data to CSV: {e}")


def run_blocked_request_report(days=1, network_filter=None, output="blocked_requests_by_client.csv", debug=False):
    """
    Run the blocked content filtering report.

    Args:
        days (int): How many days back to check.
        network_filter (str): Optional substring to filter network names.
        output (str): Filename for output CSV.
        debug (bool): Enable debug logging.

    Returns:
        str: Message indicating result.
    """
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)

    org_id = get_organization_id(dashboard)
    if not org_id:
        logger.error("❌ Organization ID not found.")
        return "❌ Organization ID not found."

    all_networks = get_all_networks(dashboard, org_id)
    if not all_networks:
        logger.warning("⚠️ No production networks found.")
        return "⚠️ No production networks found."

    if network_filter:
        filter_value = network_filter.strip().upper()
        all_networks = [net for net in all_networks if filter_value in net['name'].upper()]
        logger.info(f"🔍 Filtered networks using '{filter_value}': {len(all_networks)} found.")

    time_since = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    results = []

    for network in all_networks:
        network_name = network['name']
        network_id = network['id']
        product_types = network.get('productTypes', [])

        if 'appliance' not in product_types:
            logger.debug(f"⏭️ Skipping {network_name} (no appliance)")
            continue

        logger.info(f"📡 Fetching events for {network_name}...")

        try:
            events = get_network_events(
                dashboard,
                network_id,
                product_type='appliance',
                starting_after=time_since,
                event_type='contentFilteringBlocked'
            )
        except Exception as e:
            logger.error(f"❌ Error fetching events for {network_name}: {e}")
            continue

        blocked_by_client = defaultdict(int)

        for event in events:
            client = event.get('clientMac') or event.get('clientIp') or "unknown"
            blocked_by_client[client] += 1

        for client, count in blocked_by_client.items():
            results.append({
                "network": network_name,
                "client": client,
                "blocked_requests": count
            })

    output_path = Path(__file__).resolve().parent.parent.parent / "output" / output

    if results:
        export_to_csv(results, output_path)
        return f"✅ Report generated: {output_path}"
    else:
        logger.info("📭 No blocked content filtering events found.")
        return "📭 No blocked content filtering events found."

