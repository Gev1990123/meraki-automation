from meraki_utils.config import dashboard
from meraki_utils.functions import get_organization_id
from meraki_utils.network import get_network_clients, get_all_prod_networks, get_network_id
from meraki_utils.logger import log, set_log_callback
from meraki_utils.helpers import write_csv

def network_client_stats(csv_file, network_name, timespan=2678400, high_usage_detection=False, usage_threshold_mb=500, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🚀 Starting network client analysis...")

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return None

    clients = []

    try:
        all_networks = get_all_prod_networks(dashboard, org_id)      
        if network_name == 'All':
            networks = all_networks
        else:
            matching = next((n for n in all_networks if n.get('name') == network_name), None)
            if not matching:
                log(f"❌ Network '{network_name}' not found.")
                return None
            networks = [matching]
    except Exception as e:
        log(f"❌ Failed to fetch networks: {e}")
        return

    for network in networks:
        networkId = network['id']
        network_clients = get_network_clients(dashboard, networkId, timespan=timespan)
        for network_client in network_clients:
            usage = network_client.get('usage', {})
            if isinstance(usage, dict):
                usage_sent = usage.get('sent', 0)
                usage_recv = usage.get('recv', 0)
                usage_total = usage.get('total', 0)
            else:
                usage_sent = usage_recv = usage_total = 0

            avg_daily_usage_mb = None


            if high_usage_detection:
                high_usage_detected = False
                analysis_days = max(timespan / 86400, 1)
                avg_daily_usage_bytes = usage_total / analysis_days
                avg_daily_usage_mb = round(avg_daily_usage_bytes / 1e6, 2)

                if avg_daily_usage_mb > usage_threshold_mb:
                    high_usage_detected = True
                    log(f"🚨 High usage client: {network_client.get('description', 'Unknown')} "
                        f"- {avg_daily_usage_mb:.2f} MB/day over last {int(analysis_days)} days")


            client_data = {
                'Network': network['name'],
                'Hostname': network_client.get('description', 'Unknown'),
                'MAC Address': network_client.get('mac'),
                'IP Address': network_client.get('ip'),
                'First Seen': network_client.get('firstSeen'),
                'Last Seen': network_client.get('lastSeen'),
                'Manufacturer': network_client.get('manufacturer'),
                'Connection Type': network_client.get('recentDeviceConnection'),
                'VLAN': network_client.get('vlan'),
                'Usage Sent (KB)': usage_sent,
                'Usage Recviced (KB)': usage_recv,
                'Usage Total (KB)': usage_total,
                'Status': network_client.get('status')
                }
        
            if high_usage_detection:
                client_data['Avg Daily Usage (MB)'] = avg_daily_usage_mb
                if high_usage_detected == True:
                    client_data['High Usage Detected'] = True
                else:
                    client_data['High Usage Detected'] = False

            clients.append(client_data)

    fieldnames = ['Network', 'Hostname', 'MAC Address', 'IP Address', 'First Seen', 'Last Seen', 'Manufacturer', 'Connection Type', 'VLAN', 'Usage Sent (KB)', 'Usage Recviced (KB)', 'Usage Total (KB)', 'Status']
    
    if high_usage_detection:
        fieldnames += ['Avg Daily Usage (MB)', 'High Usage Detected']
            
    success, result_message = write_csv(csv_file=csv_file, data=clients, fieldnames=fieldnames)
    log(result_message)

    if success:
        summary = f"Exported {len(clients)} network clients"
        log(summary)

        return {
            "count": len(clients),
            "summary": summary
        }

    else:
        return None