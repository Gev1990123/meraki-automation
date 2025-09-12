from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.network import get_network_id, get_all_networks
from meraki_utils.content_filtering import content_filtering_get_current_settings
from meraki_utils.logger import log, set_log_callback
from meraki_utils.helpers import write_csv

def compare_to_baseline(results, baseline):
    differences = []

    def parse_set(s):
        return set(item.strip() for item in s.split(',') if item.strip())
    
    for network in results:
        diffs = {
            'network_name': network['network_name'],
            'category_missing': sorted(list(baseline['blocked_categories'] - parse_set(network['blocked_categories']))),
            'category_extra': sorted(list(parse_set(network['blocked_categories']) - baseline['blocked_categories'])),
            'blocked_urls_missing': sorted(list(baseline['blocked_urls'] - parse_set(network['blocked_urls']))),
            'blocked_urls_extra': sorted(list(parse_set(network['blocked_urls']) - baseline['blocked_urls'])),
            'allowed_urls_missing': sorted(list(baseline['allowed_urls'] - parse_set(network['allowed_urls']))),
            'allowed_urls_extra': sorted(list(parse_set(network['allowed_urls']) - baseline['allowed_urls'])),
        }
        differences.append(diffs)

    return differences

def run_content_filtering_report(csv_file, network_filter=None, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)
    
    log("🔄 Running content status report...") 

    
    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return []
    
        
    all_networks = get_all_networks(dashboard, org_id, prod=True)
    if not all_networks:
        log("⚠️ No production networks found.")
        return []
    
    if network_filter:
        filter_value = network_filter.strip().upper()
        all_networks = [net for net in all_networks if filter_value in net['name'].upper()]
        log(f"🔍 Filtered networks using '{filter_value}': {len(all_networks)} found.")

    results = []
    
    for network in all_networks:
        network_name = network['name']
        network_id = network['id']

        if network_name == "AUKS-L-MX-PROD":
            continue

        try:
            settings = content_filtering_get_current_settings(dashboard, network_id)
        except Exception as e:
            log(f"Error fetching settings for {network_name}: {e}")
            continue

        blocked_categories = ', '.join(cat['name'] for cat in settings.get('blockedUrlCategories', []) if 'name' in cat)
        blocked_urls = ', '.join(settings.get('blockedUrlPatterns', []))
        allowed_urls = ', '.join(settings.get('allowedUrlPatterns', []))

        results.append({
            'network_name': network_name,
            'network_id': network_id,
            'blocked_categories': blocked_categories,
            'blocked_urls': blocked_urls,
            'allowed_urls': allowed_urls
        })

    baseline_config = {
        "blocked_categories": {
            "Adult", "Games", "Hate Speech", "Illegal Activities", "Illegal Drugs", "Gambling", "Hacking", "Pornography", 
            "Non-sexual Nudity", "Child Abuse Content", "Alcohol", "Tobacco", "Illegal Downloads", "Paranormal", "Cannabis",
            "Cryptocurrency", "Cryptomining", "Terrorism and Violent Extremism", "Malware Sites", "Spyware and Adware", "Phishing", 
            "Botnets", "Spam", "Exploits", "High Risk Sites and Locations", "Bogon", "Ebanking Fraud", "Indicators of Compromise (IOC)", 
            "TOR exit Nodes", "Cryptojacking", "Malicious Sites"
        },
        "blocked_urls": {
            "deepdip2.com", "lifechangestrust.org.uk", "web.archive.org"
        },
        "allowed_urls": {
            "tnlcommunityfund.org.uk"
        }
    }        

    differences = compare_to_baseline(results, baseline_config)

    if differences:
        success, results_message = write_csv(csv_file=csv_file, data=differences, fieldnames = ['network_name', 'category_missing', 'category_extra', 
                          'blocked_urls_missing', 'blocked_urls_extra', 
                          'allowed_urls_missing', 'allowed_urls_extra'])
        log(results_message)

        if success:
            summary = f"Exported {len(differences)} number of differences"
            log(summary)

            return {
                "count": len(differences),
                "summary": summary
            }
        
    return {
        "count": 0,
        "summary": "No deviations found from the baseline."
    }

