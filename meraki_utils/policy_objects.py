# Function to confirm if policy object is present
def is_policy_object_present(dashboard, orgId, object_name, object_ip):
    objects = dashboard.organizations.getOrganizationPolicyObjects(orgId)

    if not objects:
        return False

    for object in objects: 
        if object['type'] == 'cidr':
            if object['name'] == object_name or object['cidr'] == object_ip:
                return True
        elif object['type'] == 'fqdn':
            if object['name'] == object_name or object['fqdn'] == object_ip:
                return True

    return False

# Function to get object group id
def get_policy_object_id(dashboard, orgId, object_name, object_ip):
    objects = dashboard.organizations.getOrganizationPolicyObjects(orgId)
    for object in objects:
        if object['type'] == 'cidr':
            if object['name'] == object_name or object['cidr'] == object_ip:
                objectId = object['id']
                return objectId
        if object['type'] == 'fqdn':      
            if object['name'] == object_name or object['fqdn'] == object_ip:
                objectId = object['id']
                return objectId
            
#Function to get all object ID from a group ID
def get_object_ids_from_group_id(dashboard, orgid, groupId):
    group = dashboard.organizations.getOrganizationPolicyObjectsGroup(orgid, groupId)
    return group

# Function to confirm if policy object group is present
def is_policy_object_groups_present(dashboard, orgId, group_name):
    groups = dashboard.organizations.getOrganizationPolicyObjectsGroups(orgId)
    
    if not groups:
        return False

    for group in groups: 
        if group['name'] == group_name:
            return True

    return False

# Function to get policy object group from name
def get_policy_object_group_by_name(dashboard, orgId, group_name):
    groups = dashboard.organizations.getOrganizationPolicyObjectsGroups(orgId)
    for group in groups:
        if group['name'] == group_name:
            return group
    return None

# Function to get policy object from ID
def get_policy_object_by_id(dashboard, orgId, objectId):
    try:
        object = dashboard.organizations.getOrganizationPolicyObject(orgId, objectId)
        return object
    except Exception as e:
        print(f"Error retrieving policy object with ID {objectId}: {e}")
        return None

# Function to get policy object from name
def get_policy_object_by_name(dashboard, orgId, objectName):
    try:
        objects = dashboard.organizations.getOrganizationPolicyObjects(orgId)
        for obj in objects:
            if obj['name'] == objectName:
                return obj
    except Exception as e:
        print(f"Error retrieving policy object with ID {objectName}: {e}")
        return None
    
# Function to get all policy objects in an organisation
def get_all_policy_objects(dashboard, orgId):
    try:
        objects = dashboard.organizations.getOrganizationPolicyObjects(orgId)
        return objects
    except Exception as e:
        print(f"Error retrieving policy objects for organization {orgId}: {e}")
        return []
    
# Function to get all policy object groups in an organisation
def get_all_policy_object_groups(dashboard, orgId):
    try:
        groups = dashboard.organizations.getOrganizationPolicyObjectsGroups(orgId)
        return groups
    except Exception as e:
        print(f"Error retrieving policy object groups for organization {orgId}: {e}")
        return []