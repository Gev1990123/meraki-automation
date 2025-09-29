from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.network import get_all_prod_networks
from meraki_utils.logger import log, set_log_callback



def get_networks_for_dropdown(log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return []
    
    try:
        networks = get_all_prod_networks(dashboard, org_id)
        return [n['name'] for n in networks]
    except Exception as e:
        return []
    
