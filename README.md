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

| Script Name                   | Description                                               |
|-------------------------------|-----------------------------------------------------------|
| claim_devices.py              | Claims devices to networks using serial numbers           |


## 📁 Data Files
Place your CSV files in the data/ folder. Ensure they follow the expected structure (column headers, no missing values).

## ✅ Output
Scripts may output logs or results into the output/ folder for review or backup purposes.

## 🧪 Example
Claim devices to networks:

python scripts/claim_devices.py

For questions or improvements, feel free to open an issue or submit a PR.
