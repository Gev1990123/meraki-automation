# Meraki Automation Scripts

This repository contains Python scripts to automate tasks in Meraki, such as device claiming, VLAN management, configuration templates, firewall settings, content filtering, and more.
---

## 📁 Project Structure (Recommended)
| Folder / File     | Description                                           |
|-------------------|-------------------------------------------------------|
| scripts/          | Python automation scripts                             |
| meraki_utils/     | Helper functions organized by domain (e.g. org)       |
| data/             | Input CSV/YAML files                                  |
| output/           | Generated output files (e.g., reports, logs)          |
| .env              | Environment variables (do not commit)                 |
| requirements.txt  | Python dependencies                                   |
| README.md         | Project documentation                                 |


## ⚙️ Setup
### 1. Clone the repository
git clone https://github.com/Gev1990123/meraki-automation.git
cd meraki-automation

### 2. Configure environment variables
Create a .env file in the root directory with the following values:
MERAKI_API_KEY=your_meraki_api_key
MERAKI_ORG_NAME=your_org_name

### 3. Install Python dependencies
pip install -r requirements.txt

## 🚀 Scripts Overview
Each script is located in the scripts/ directory and can be run individually. Some require corresponding CSV files in the data/ folder.

| Script Name                                           | Description                                                           |
|-------------------------------------------------------|-----------------------------------------------------------------------|
| claim_devices.py                                      | Claims devices to networks using serial numbers.                      |
| audit_unused_policy_objects.py                        | Identify and list unused policy objects.                              |
| create_policy_object_groups.py                        | Create new policy object groups in Meraki.                            |
| create_policy_objects.py                              | Add new policy objects to Meraki.                                     |
| delete_group_policy_objects.py                        | Remove policy objects from specific groups.                           |
| delete_policy_objetcs.py                              | Permanently delete selected Meraki policy objects.                    |
| export_policy_objects.py                              | Export all policy objects to external file.                           |
| export_policy_object_groups.py                        | Save all policy object groups to file.                                |
| find_duplicate_policy_objects.py                      | Detect duplicate policy objects by attributes.                        |
| policy_object_group_sync.py                           | Synchronise object groups between Meraki networks.                    |
| update_policy_object_groups.py                        | Modify existing policy object group settings.                         |
| update_policy_objects.py                              | Update properties of existing policy objects.                         |
| validate_policy_object_names.py                       | Validate and export Meraki policy objects.                            |
| content_filtering_status_report.py                    | Generate content filtering report for networks.                       |
| content_filtering_blocked_requests_by_client.py       | Generate content filtering report for blocked requests by client      |


## 📁 Data Files
Place your CSV files in the data/ folder. Ensure they follow the expected structure (column headers, no missing values).

## ✅ Output
Scripts may output logs or results into the output/ folder for review or backup purposes.

## 🧪 Example
Claim devices to networks:

python scripts/claim_devices.py

For questions or improvements, feel free to open an issue or submit a PR.
