# Meraki Automation App

A desktop GUI application built with Tkinter to simplify and unify automations for Meraki. Previously a collection of individual scripts, this project now provides a central interface to manage tasks such as device claiming, VLAN management, firewall settings, template application, content filtering and more.

---

## 🛠 Features

- Graphical user interface (Tkinter) for managing Meraki operations  
- Modular windows for different tasks (e.g. claims, updates, reporting)  
- Under-the-hood logic split out into reusable modules  
- Ability to load input from files (CSV, YAML, etc.)  
- Generates output/log files for reporting and auditing  

---

# 🧠 Meraki Automation App

A desktop GUI application built with Tkinter to simplify and unify automations for Cisco Meraki. Previously a collection of individual scripts, this project now provides a central interface to manage tasks such as device claiming, VLAN management, firewall rules, template application, content filtering, and more.

---

## 🛠 Features

- Graphical user interface (Tkinter) for managing Meraki operations  
- Modular windows for different tasks (e.g. claims, updates, reporting)  
- Under-the-hood logic split into reusable modules  
- Ability to load input from files (CSV, YAML, etc.)  
- Generates output/log files for reporting and auditing  

---

## 📂 Project Structure

```text
meraki-automation/
│
├── gui/
│   ├── windows/
│   │   ├── audit_unused_policy_objects_window.py
│   │   ├── claim_devices_window.py
│   │   ├── content_filtering_blocked_requests_by_client_window.py
│   │   ├── content_filtering_status_report_window.py
│   │   ├── create_firewall_rule_window.py
│   │   ├── create_policy_object_groups_window.py
│   │   ├── create_policy_objects_window.py
│   │   ├── delete_group_policy_objects_window.py
│   │   ├── delete_policy_objects_window.py
│   │   ├── export_policy_object_groups_window.py
│   │   ├── export_policy_objects_window.py
│   │   ├── find_duplicate_policy_objects_window.py
│   │   ├── update_policy_object_groups_window.py
│   │   ├── update_policy_objects_window.py
│   │   └── validate_policy_object_names_window.py
│   └── main_app.py               # Tkinter main window & application startup
│
├── meraki_utils/
│   ├── amp.py
│   ├── config.py
│   ├── content_filtering.py
│   ├── firewall.py
│   ├── helpers.py
│   ├── ipds.py
│   ├── logger.py
│   ├── network.py
│   ├── organisation.py
│   ├── policy_objects.py
│   ├── site_codes.py
│   ├── traffic_shaping.py
│   ├── vlan.py
│   └── vpn.py
│
├── scripts/
│   ├── auditing_validation/
│   │   └── validate_policy_object_names.py
│   ├── content_filtering/
│   │   ├── content_filtering_blocked_requests_by_client.py
│   │   └── content_filtering_status_report.py
│   ├── device_admin/
│   │   └── claim_devices.py
│   ├── firewall/
│   │   └── create_firewall_rule.py
│   └── policy_objects/
│       ├── audit_unused_policy_objects.py
│       ├── create_policy_object_groups.py
│       ├── create_policy_objects.py
│       ├── delete_group_policy_objects.py
│       ├── delete_policy_objects.py
│       ├── export_policy_object_groups.py
│       ├── export_policy_objects.py
│       ├── find_duplicate_policy_objects.py
│       ├── update_policy_object_groups.py
│       └── update_policy_objects.py
│
├── requirements.txt
├── .env (not checked in)
└── README.md


---

## ⚙️ Setup / Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/Gev1990123/meraki-automation.git
   cd meraki-automation
2. Create a virtual environment and activate it (recommended)
    python3 -m venv venv
    source venv/bin/activate   # On Linux / macOS
    venv\Scripts\activate      # On Windows
3. Install dependencies
    pip install -r requirements.txt
4. Create a .env file in the project root with required environment variables:
    MERAKI_API_KEY=your_meraki_api_key
    MERAKI_ORG_NAME=your_meraki_organization

---

## 🚀 Usage
To run the application:

python main_app.py

Once open, the GUI will allow you to:

Select which function you want (e.g. Claim Devices, Update VLANs, Generate Reports, etc.)

Provide input (files / form entries)

Execute the task

View output or results in the “output” directory, or via popup messages

---

## 🧪 TODO / Roadmap
- Better input validation & error handling
- Add progress bars or loading indicators
- Add ability to load/save session configs
- Unit tests for logic modules
- Create executable (.exe/.app) for non-developers
- Add dark mode?

--- 

## 👤 Author
Gev1990123
https://github.com/Gev1990123
