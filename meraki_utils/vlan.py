# Function to get all vlans within a network ID
def get_vlans(dashboard, networkId):
    vlans = dashboard.appliance.getNetworkApplianceVlans(networkId)
    vlan_list = []
    for vlan in vlans:
        vlan_list.append({
            'name': vlan['name'],
            'id': vlan['id'],
            'subnet': vlan['subnet'],
            'applianceip': vlan['applianceIp']
        })
    return vlan_list

# Function to Get VLAN settings from a network Appliance
# Returns the enabled status of VLANs for the network
def get_vlan_status(dashboard, networkId):
    vlan_status = dashboard.appliance.getNetworkApplianceVlansSettings(networkId)
    return vlan_status

# Function to get the VLAN ID by name
def get_network_appliance_vlanid(dashboard, networkId, vlan_name):
    vlans = dashboard.appliance.getNetworkApplianceVlans(networkId)
    for vlan in vlans: 
        if vlan['name'] == vlan_name:
            vlan_id = vlan['id']
            return vlan_id
        
