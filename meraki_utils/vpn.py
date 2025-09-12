from meraki_utils.logger import log

# Funtion to get the current mode of Site-to-Site VPN
def get_vpn_type(dashboard, networkId):
    site_to_siteVPN_config = dashboard.appliance.getNetworkApplianceVpnSiteToSiteVpn(networkId)
    mode = site_to_siteVPN_config['mode']
    return mode

# Function to confirm if local subnet is present
def is_s2s_localSubnet_present(dashboard, orgId, networkId, addressPrefix):
    response = dashboard.appliance.getNetworkApplianceVpnSiteToSiteVpn(networkId)

    if not response['subnets']:
        return False

    for subnet in response['subnets']:
        if subnet['localSubnet'] == addressPrefix:
            return True
        
    return False

# Function to get the site to site mode
def get_s2s_mode(dashboard, networkId):
    response = dashboard.appliance.getNetworkApplianceVpnSiteToSiteVpn(networkId)
    return response['mode']
