import ipaddress

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
        print("Invalid selection. Please try again.")
        return None

def display_list_for_user_selection(item, item_name):
    print(f'Please select a {item_name}: ')
    for i, item in enumerate(item, start=1):
        print(f'{i}. {item['name']}')

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