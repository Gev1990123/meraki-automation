# Function to get the ID of a content filtering category
def content_filtering_category_get_id(dashboard, networkId, category):
    try:
        response = dashboard.appliance.getNetworkApplianceContentFilteringCategories(networkId)
        categories = response.get('categories',[])
        for item in categories:
            if item.get('name').lower() == category.lower():
                return item.get('id')
        return None
    except Exception as e:
        print(f"Error retrieving content filtering categories: {e}")
        return None
    
# Function to get the current blocked categories and confirm if already is blocked. 
def content_filtering_category_status(dashboard, networkId, categoryId):
    try:
        response = dashboard.appliance.getNetworkApplianceContentFiltering(networkId)
        blockedUrlCategories = response.get('blockedUrlCategories',[])

        for category in blockedUrlCategories:
            if category.get('id') == categoryId:
                return True
        return False
    except Exception as e:
        print(f"Error retrieving content filtering categories: {e}")
        return None
    
# Function to get the current settings of Content Filtering
def content_filtering_get_current_settings(dashboard, networkId):
    return dashboard.appliance.getNetworkApplianceContentFiltering(networkId)

# Function to get the current blocked URLs and confirm if already is blocked. 
def content_filtering_url_status(dashboard, networkId, url):
    try:
        response = dashboard.appliance.getNetworkApplianceContentFiltering(networkId)
        blocked = response.get('blockedUrlPatterns', [])
        allowed = response.get('allowedUrlPatterns', [])

        blocked_lower = [u.lower() for u in blocked]
        allowed_lower = [u.lower() for u in allowed]
        url_lower = url.lower()

        if url_lower in blocked_lower and url_lower in allowed_lower:
            return 'conflict'
        elif url_lower in blocked_lower:
            return 'blocked'
        elif url_lower in allowed_lower:
            return 'allowed'
        else:
            return False
    except Exception as e:
        print(f"Error retrieving content filtering URLs: {e}")
        return False
    
# Function to get the current settings of Content Filtering
def content_filtering_get_current_settings(dashboard, networkId):
    return dashboard.appliance.getNetworkApplianceContentFiltering(networkId)


