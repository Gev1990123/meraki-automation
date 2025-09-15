import ipaddress
from meraki_utils.logger import log
from pathlib import Path
import csv

# Function Convert mbps to kbps
def convert_mbps_to_kbps(value):
    return value * 1000

# Function to get a users selection: 
def get_user_selection(item):
    selection = int(input("Enter the number of your choice: "))
    if 1 <= selection <= len(item):
        selected_item = item[selection - 1]
        return selected_item
    else:
        log("Invalid selection. Please try again.")
        return None

def display_list_for_user_selection(item, item_name):
    print(f'Please select a {item_name}: ')
    for i, item in enumerate(item, start=1):
        log(f'{i}. {item['name']}')

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
        with path.open(mode='a', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames)
            writer.writeheader()

            for object in data:
                writer.writerow(object)
        
        return True, f"✅ Successfully updated: {csv_file}"
    except Exception as e:
        return False, f"❌ Failed to write to file: {e}"
    
# Load CSV File
def load_csv(csv_file, fieldnames):
    objects = []
    try: 
        path = Path(csv_file)
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            log(f"Detected CSV Headers: {csv_reader.fieldnames}")

            missing_keys = []
            for i, row in enumerate(csv_reader, start=1):
                filtered_row = {}
                for key in fieldnames:
                    if key in row:
                        filtered_row[key] = row[key]
                    else:
                        missing_keys.append((i, key))
                objects.append(filtered_row)
            if missing_keys:
                log("Warning: missing fields detedted:")
                for row_num, key, in missing_keys:
                    log(f" - Row {row_num}: missing '{key}'")

    except Exception as e:
        log(f"Failed to load CSV: {e}")
    return objects


