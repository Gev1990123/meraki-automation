#Function to get the current mode of the Intrusion detection and prevention
def ipds_get_mode(dashboard, networkId):
    try:
        response = dashboard.appliance.getNetworkApplianceSecurityIntrusion(networkId)
        return response.get('mode')
    except Exception as e:
        print(f"Error retrieving IPDS mode for network {networkId}: {e}")
        return None
    
#Function to get the current ruleset of the Intrusion detection and prevention
def ipds_get_ruleset(dashboard, networkId):
    try:
        response = dashboard.appliance.getNetworkApplianceSecurityIntrusion(networkId)
        return response.get('idsRulesets')
    except Exception as e:
        print(f"Error retrieving IPDS mode for network {networkId}: {e}")
        return None
    
#Function to get current IPDS settings
def ipds_get_current_settings(dashboard, networkId):
    return dashboard.appliance.getNetworkApplianceSecurityIntrusion(networkId)

    