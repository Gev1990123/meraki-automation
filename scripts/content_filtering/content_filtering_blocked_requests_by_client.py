from collections import defaultdict
from datetime import datetime, timedelta

from meraki_utils.logger import log, set_log_callback
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.network import get_all_networks, get_network_events
from meraki_utils.helpers import write_csv

def run_blocked_request_report(csv_file, days=1, network_filter=None, output="blocked_requests_by_client.csv", debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🔄 Running blocked request report...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return []

    all_networks = get_all_networks(dashboard, org_id)
    if not all_networks:
        log("⚠️ No production networks found.")
        return []

    if network_filter:
        filter_value = network_filter.strip().upper()
        all_networks = [net for net in all_networks if filter_value in net['name'].upper()]
        log(f"🔍 Filtered networks using '{filter_value}': {len(all_networks)} found.")

    time_since = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    results = []

    for network in all_networks:
        network_name = network['name']
        network_id = network['id']
        product_types = network.get('productTypes', [])

        if 'appliance' not in product_types:
            log(f"⏭️ Skipping {network_name} (no appliance)")
            continue

        log(f"📡 Fetching events for {network_name}...")

        try:
            events = get_network_events(
                dashboard,
                network_id,
                product_type='appliance',
                starting_after=time_since,
                event_type='contentFilteringBlocked'
            )
        except Exception as e:
            log(f"❌ Error fetching events for {network_name}: {e}")
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

    success, results_message = write_csv(csv_file=csv_file, data=results, fieldnames = ['network', 'client', 'blocked_requests'])
    log(results_message)

    if success:
        summary = f"✅ Exported {len(results)} blocked requests."
        log(summary)

        return {
            "count": len(results),
            "summary": summary
        }

