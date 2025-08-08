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

