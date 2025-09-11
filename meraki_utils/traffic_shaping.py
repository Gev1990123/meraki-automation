# Function to get the current settings of uplink bandwidth
def traffic_shaping_get_uplink_bandwidth(dashboard, networkId):
    return dashboard.appliance.getNetworkApplianceTrafficShapingUplinkBandwidth(networkId)

# Function to get the ID of a custom perfermance class
def traffic_shaping_get_custom_performance_class_id(dashboard, networkId, name):
    try:
        cp_classes = dashboard.appliance.getNetworkApplianceTrafficShapingCustomPerformanceClasses(networkId)
        for cp_class in cp_classes:
            if cp_class['name'].lower() == name.lower():
                return cp_class.get('customPerformanceClassId',[])
        return None
    except Exception as e:
        print(f"Error retrieving custom performance classes: {e}")
        return None
    
# Function to get the settings of a custom performance class by ID
def traffic_shaping_get_custom_performance_class_settings(dashboard, networkId, cp_class_id):
    return dashboard.appliance.getNetworkApplianceTrafficShapingCustomPerformanceClass(networkId, cp_class_id)

# Function to get the current custom performance classes, and confirm it is present: 
def traffic_shaping_get_custom_performance_class_status(dashboard, networkId, cp_class_name):
    try:
        cp_classes = dashboard.appliance.getNetworkApplianceTrafficShapingCustomPerformanceClasses(networkId)
        for cp_class in cp_classes:
            if cp_class['name'].lower() == cp_class_name.lower():
                return True
        return False
    except Exception as e:
        print(f"Error retrieving custom performance classes: {e}")
        return False
    
# Function to get the settings of the uplink selection
def traffic_shaping_get_uplink_selection_status(dashboard, networkId):
    return dashboard.appliance.getNetworkApplianceTrafficShapingUplinkSelection(networkId)


