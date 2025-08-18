import sys
import os
import csv
from pathlib import Path
import logging
import re
import argparse

# Add parent path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from meraki_utils.logger import setup_logger
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.policy_objects import (
    get_all_policy_objects,
    get_all_policy_object_groups,
    get_object_ids_from_group_id,
)

parser = argparse.ArgumentParser(description="Validate policy objects and groups in Meraki")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument("--output", default="policy_object_validation.csv", help="Output CSV file path")
args = parser.parse_args()

setup_logger(debug=args.debug)
logger = logging.getLogger(__name__)

NAMING_REGEX = re.compile(r"^([A-Z]{2,})_([A-Za-z0-9\s\-]+)-(\d{2,3})$")
seen_names = set()


def validate_policy_object(policy_object_name):
    errors = []
    lower_name = policy_object_name.lower()

    if lower_name in seen_names:
        errors.append("Duplicate Name")
    else:
        seen_names.add(lower_name)

    if not NAMING_REGEX.match(policy_object_name):
        errors.append("Invalid naming fromat")

    return errors

def export_results_to_csv(results, output_path):
    with open(output_path, mode="w", newline="") as csvfile:
        fieldnames = ["name", "status", "errors"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in results:
            writer.writerow(row)

    logger.info(f"Results exported to {output_path}")


#def validate_policy_object_group():
#    xx


def main():
    org_id = get_organization_id(dashboard)
    if not org_id:
        logger.error("Organization ID not found.")
        return
    
    all_policy_objects = get_all_policy_objects(dashboard, org_id)

    if not all_policy_objects:
        logger.info(f"No policy objects found!")
        return

    results = []

    for policy_object in all_policy_objects:
        name = policy_object.get('name')
        if not name:
            logger.warning("Unnamed policy object found.")
            continue

        errors = validate_policy_object(name)

        result = {
            "name": name,
            "status": "valid" if not errors else "invalid",
            "errors": "; ".join(errors) if errors else ""
        }
        results.append(result)

        for error in errors:
            logger.error(f"{name} - {error}")

    csv_path = Path(__file__).resolve().parent.parent.parent / "output" / args.output
    export_results_to_csv(results, csv_path)

if __name__ == "__main__":
    main()
