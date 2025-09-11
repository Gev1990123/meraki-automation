import sys
import os
import csv
from pathlib import Path
import logging
import argparse

# Add parent path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.logger import setup_logger
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.network import get_network_id, get_all_networks
from meraki_utils.content_filtering import content_filtering_get_current_settings

parser = argparse.ArgumentParser(description="Content Filtering Status Report in Meraki")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument("--output", default="content_filtering_status_report.csv", help="Output CSV file path")
parser.add_argument("--difference", action="store_true", help="Compare the content filtering to a predefined baseline")
parser.add_argument("--network", help="Filter networks by name substring (e.g., 'LON' for London networks only)")
args = parser.parse_args()

setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

def export_content_filtering_report_to_csv(data, output_path):
    fieldnames = ['network_name', 'network_id', 'blocked_categories', 'blocked_urls', 'allowed_urls']

    try:
        output_path = Path(__file__).resolve().parent.parent.parent / "output" / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        logger.info(f"Content filtering report saved to {output_path}")
    except Exception as e:
        logger.error(f"Error writing content filtering report: {e}")

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

def export_differences_to_csv(differences, output_path='content_filtering_differences.csv'):
    fieldnames = ['network_name', 'category_missing', 'category_extra', 'blocked_urls_missing', 'blocked_urls_extra', 'allowed_urls_missing', 'allowed_urls_extra']

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for diff in differences:
                writer.writerow({k: ', '.join(v) if isinstance(v, list) else v for k, v in diff.items()})
        logger.info(f"Differences exported to {output_path}")
    except Exception as e:
        logger.error(f"Failed to write differences CSV: {e}")


def run_content_filtering_report(output_filename="content_filtering_status_report.csv", network_filter=None, compare_to_baseline=False):
    org_id = get_organization_id(dashboard)
    if not org_id:
        raise Exception("Organization ID not found.")
    
    all_networks = get_all_networks(dashboard, org_id, prod=True)
    if not all_networks:
        return [], "No production networks found."
    
    if network_filter:
        filter_value = network_filter.strip().upper()
        all_networks = [net for net in all_networks if filter_value in net['name'].upper()]
    
    results = []
    
    for network in all_networks:
        network_name = network['name']
        network_id = network['id']

        try:
            settings = content_filtering_get_current_settings(dashboard, network_id)
        except Exception as e:
            logging.error(f"Error fetching settings for {network_name}: {e}")
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

    output_path = Path(__file__).resolve().parent.parent.parent / "output" / output_filename
    export_content_filtering_report_to_csv(results, output_path)

    if compare_to_baseline:

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
            output_diff_path = Path(__file__).resolve().parent.parent.parent / "output" / "content_filtering_differences.csv"
            export_differences_to_csv(differences, output_diff_path)
            return results, f"Differences saved to {output_diff_path}"
        else:
            return results, "All networks match the baseline."

    return results, f"Report saved to {output_path}"
