import os
from dotenv import load_dotenv
import meraki

load_dotenv()

MERAKI_API_KEY = os.getenv("MERAKI_API_KEY")
if not MERAKI_API_KEY:
    raise ValueError("Missing MERAKI_API_KEY in environment variables.")

MERAKI_ORG_NAME = os.getenv("MERAKI_ORG_NAME")
if not MERAKI_ORG_NAME:
    raise ValueError("Missing MERAKI_ORG_NAME in environment variables.")

dashboard = meraki.DashboardAPI(MERAKI_API_KEY, suppress_logging=True)