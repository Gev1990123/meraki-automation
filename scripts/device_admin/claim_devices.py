from meraki_utils.logger import log, set_log_callback
from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id, claim_network_device
from meraki_utils.network import is_network_present, get_network_id
from meraki_utils.helpers import load_csv

def claim_devices(csv_file, debug=False, log_callback=None):
    if log_callback:
        set_log_callback(log_callback)

    log("🔄 Starting to claim Devices") 

    org_id = get_organization_id(dashboard)
    if not org_id:
        log("❌ Organization ID not found.")
        return []
    
    objects = load_csv(csv_file=csv_file, fieldnames=['network_name, serial_number'])

    for obj in objects:
        network_name = obj['network_name']
        serial = obj['serial_number']
        if is_network_present(dashboard, org_id, network_name):
                networkId = get_network_id(dashboard, org_id, network_name)
                if networkId:
                    claim_network_device(serial, networkId)
                    log(f'Network device with serial {serial} has been claimed to {network_name}')
                else:
                    log(f'Network ID for {network_name} not found')
        else:
            log(f'Network {network_name} not present')
