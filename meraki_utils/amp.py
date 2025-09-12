from meraki_utils.logger import log

#Function to get the current mode of the Advanced Malware Protection (AMP)
def amp_get_mode(dashboard, networkId):
    try:
        response = dashboard.appliance.getNetworkApplianceSecurityMalware(networkId)
        return response.get('mode') == 'enabled'
    except Exception as e:
        log(f"Error retrieving AMP mode for network {networkId}: {e}")
        return None
    
#Function to get if a current url is apart of the allowed URLs
def amp_check_allowed_urls(dashboard, networkId, url):
    try:
        response = dashboard.appliance.getNetworkApplianceSecurityMalware(networkId)
        allowed_urls = {entry['url'] for entry in response.get('allowedUrls', [])}
        return url in allowed_urls
    except Exception as e:
        return f"Error checking allowed URLs: {e}"

#Function to get if a current file (sha256) is apart of the allowed files
def amp_check_allowed_files(dashboard, networkId, file_sha256):
    try:
        response = dashboard.appliance.getNetworkApplianceSecurityMalware(networkId)
        allowed_files = {entry['sha256'] for entry in response.get('allowedFiles', [])}
        return file_sha256 in allowed_files
    except Exception as e:
        return f"Error checking allowed file: {e}"
    
#Function to get current AMP settings
def amp_get_current_settings(dashboard, networkId):
    return dashboard.appliance.getNetworkApplianceSecurityMalware(networkId)

