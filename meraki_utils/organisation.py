import os
from dotenv import load_dotenv

load_dotenv()

ORG_NAME = os.getenv("MERAKI_ORG_NAME")

# Function to get the Org ID
def get_organization_id(dashboard):
    orgs = dashboard.organizations.getOrganizations()
    for org in orgs:
        if org['name'] == ORG_NAME:
            return org['id']
    return None

# Funtion to get a list our all the configuration template names
def get_all_conf_templates(dashboard, orgId):
    templates = dashboard.organizations.getOrganizationConfigTemplates(orgId)
    template_list = []
    for template in templates:
        template_list.append({
            'id': template['id'],
            'name': template['name']
        })
    return template_list

# Function to get the configuration template ID
def get_conf_template_id(dashboard, orgId, template_name):
    templates = dashboard.organizations.getOrganizationConfigTemplates(orgId)
    for template in templates:
        if template['name'] == template_name:
            return template['id']
    return None

# Function to check to see if a configuration template is already present
def is_config_template_present(dashboard, orgId, template_name):
    templates = dashboard.organizations.getOrganizationConfigTemplates(orgId)
    for template in templates:
        if template['name'] == template_name:
            return True
    return False