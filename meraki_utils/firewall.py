# Function to get application categories id
def firewall_get_application_categories(dashboard, networkId, category_name):
    try:
        response = dashboard.appliance.getNetworkApplianceFirewallL7FirewallRulesApplicationCategories(networkId)
               
        if isinstance(response, dict) and 'applicationCategories' in response:
            categories = response['applicationCategories']
            print(categories)

        for app_category in categories:
            if app_category['name'].lower() == category_name.lower():
                return app_category
        print(f"Category '{category_name}' not found.")
        return None
    except Exception as e:
        print(f"Error retrieving application categories: {e}")
        return None
    
# Function to get L3 Firewall Rules
def firewall_get_l3_rules(dashboard, networkId):
    l3_firewall_rules = dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules(networkId)
    return l3_firewall_rules

# Function to check if a L3 firewall rule exisits.
def firewall_l3_rule_exists(new_rule, existing_rules):
    for rule in existing_rules:
        if isinstance(rule, dict) and all(
            rule.get(k) == new_rule.get(k)
            for k in ['comment', 'policy', 'protocol', 'destPort', 'destCidr', 'srcPort', 'srcCidr', 'syslogEnabled']
            ):
            return True
    return False

# Function to get L3 Firewall Rules
def firewall_get_l3_rules(dashboard, networkId):
    l3_firewall_rules = dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules(networkId)
    return l3_firewall_rules

# Function to check if a L3 firewall rule exisits.
def firewall_l3_rule_exists(new_rule, existing_rules):
    for rule in existing_rules:
        if isinstance(rule, dict) and all(
            rule.get(k) == new_rule.get(k)
            for k in ['comment', 'policy', 'protocol', 'destPort', 'destCidr', 'srcPort', 'srcCidr', 'syslogEnabled']
            ):
            return True
    return False
