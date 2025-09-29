import ipaddress
from meraki_utils.logger import log
from pathlib import Path
import csv
import re
import json

# Function Convert mbps to kbps
def convert_mbps_to_kbps(value):
    return value * 1000

# Function to get a users selection: 
def get_user_selection(item):
    try: 
        selection = int(input("Enter the number of your choice: "))
        if 1 <= selection <= len(item):
            selected_item = item[selection - 1]
            return selected_item
        else:
            log("Invalid selection. Please try again.")
            return None
    except ValueError:
        log("Invalid input. Please enter a number.")
        return None

def display_list_for_user_selection(item, item_name):
    print(f'Please select a {item_name}: ')
    for i, obj in enumerate(item, start=1):
        log(f'{i}. {obj['name']}')

# Function to confirm if a string contains letters
def contains_letters(object_ip):
    for char in str(object_ip):
        if char.isalpha():
            return 'fqdn'
    
    return 'cidr'

# Function to determine eithe object is FQDN or CIDR
def determine_object_type(object_ip):
    try:
        # Try parsing as an IP network (CIDR)
        ipaddress.ip_network(object_ip)
        return 'cidr'
    except ValueError:
        # If it fails, assume it a FQDN
        return 'fqdn'
    
# Write CSV File
def write_csv(csv_file, data, fieldnames):
    try: 
        path = Path(csv_file)
        with path.open(mode='w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames)
            writer.writeheader()

            for object in data:
                writer.writerow(object)
        
        return True, f"✅ Successfully ouput to: {csv_file}"
    except Exception as e:
        return False, f"❌ Failed to write to file: {e}"
    
# Append CSV File
def append_csv(csv_file, data, fieldnames):
    try: 
        path = Path(csv_file)
        file_exists = path.exists() and path.stat().st_size > 0

        with path.open(mode='a', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        return True, f"✅ Successfully updated: {csv_file}"
    except Exception as e:
        return False, f"❌ Failed to write to file: {e}"
    
# Load CSV File
def load_csv(csv_file, fieldnames):
    objects = []
    try: 
        path = Path(csv_file)

        if not path.exists():
            log("❌ CSV file does not exist.")
            return None

        with path.open(mode='r', newline='', encoding='latin-1') as file:
            csv_reader = csv.DictReader(file)

            log(f"Detected CSV Headers: {csv_reader.fieldnames}")

            missing_keys = []
            for i, row in enumerate(csv_reader, start=1):
                filtered_row = {}
                for key in fieldnames:
                    if key in row and row[key] is not None:
                        filtered_row[key] = row[key].strip()
                    else:
                        filtered_row[key] = ''
                if all(filtered_row[key] for key in fieldnames):
                    objects.append(filtered_row)
                else:
                    missing_keys.append((i, [key for key in fieldnames if not filtered_row.get(key)]))

            if missing_keys:
                log("⚠️ Warning: missing fields detected:")
                for row_num, keys in missing_keys:
                    for key in keys:
                        log(f" - Row {row_num}: missing '{key}'")

        log(f"✅ Loaded {len(objects)} valid rows from CSV.")
        return objects

    except Exception as e:
        log(f"❌ Exception while loading CSV: {e}")
        return None

# Load JSON File    
def load_json(json_file):
    try:
        path = Path(json_file)
        with open(json_file, mode='r', encoding='utf-8') as file: 
            data = json.load(file)

        return data, None
    
    except Exception as e:
        return [], str(e)

# Extract policy object group IDs
def extract_group_ids(cidr_field):
    if not cidr_field:
        return []
    return re.findall(r'GRP\((\d+)\)', cidr_field)