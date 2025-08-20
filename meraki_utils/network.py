def get_network_name(dashboard, orgId):
    networks = dashboard.organizations.getOrganizationNetworks(orgId)
    networks_list = []
    for network in networks:
        networks_list.append({
            'name': network['name'],
            'id': network['id']
        })
    return networks_list

# Function to get the Network ID         
def get_network_id(dashboard, orgId, network_name):
    networks = dashboard.organizations.getOrganizationNetworks(orgId)
    for network in networks:
        if network['name'] == network_name:
            return network['id']
    return None

# Function to confirm if a network is already present
def is_network_present(dashboard, orgId, new_network_name):
    networks = dashboard.organizations.getOrganizationNetworks(orgId)
    for network in networks:
        if network['name'] == new_network_name:
            return True
    return False

# Function to confirm if a network is already present
def is_vlan_present(dashboard, networkId, vlan_name):
    vlans = dashboard.appliance.getNetworkApplianceVlans(networkId)
    for vlan in vlans:
        if vlan['name'] == vlan_name:
            return True
    return False

# Function to get all networks in an organization
def get_all_networks(dashboard, orgId, prod=False):
    try:
        networks = dashboard.organizations.getOrganizationNetworks(orgId)

        if prod == True:
            prod_networks = [network for network in networks if 'PROD' in network.get('name', '')]
            return prod_networks
        else:
            return networks
    except Exception as e:
        print(f"Error retrieving networks for organization {orgId}: {e}")
        return []
    
# Function to get all production networks in an organization
def get_all_prod_networks(dashboard, orgId):
    try:
        networks = dashboard.organizations.getOrganizationNetworks(orgId)
        prod_networks = [network for network in networks if 'PROD' in network.get('name', '')]
        return prod_networks
    except Exception as e:
        print(f"Error retrieving networks for organization {orgId}: {e}")
        return []
    
# Function to get all L3 Network Firewall Rules
def get_all_l3_firewall_rules(dashboard, networkId):
    try:
        rules = dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules(networkId)
        return rules
    except Exception as e:
        print(f"Error retrieving L3 firewall rules for network {networkId}: {e}")
        return []
    
# Function to get network events
def get_network_events(dashboard, networkId, product_type, starting_after=None, ending_before=None, event_type=None, total_pages="all", per_page=1000, additional_filters=None):
    try: 
        params = {
            "productType": product_type,
            "perPage": per_page,
            "totalPages": total_pages
        }

        if starting_after:
            params["startingAfter"] = starting_after
        if ending_before:
            params["endingBefore"] = ending_before
        if event_type:
            params["eventType"] = event_type
        if additional_filters and isinstance(additional_filters, dict):
            params.update(additional_filters)
        
        events = dashboard.networks.getNetworkEvents(networkId, **params)
        return events.get('events', [])
    
    except Exception as e:
        print(f"Error retrieving network events for network {networkId}: {e}")
        return []