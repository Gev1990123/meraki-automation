import tkinter as tk
from tkinter import ttk
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gui.windows.claim_devices_window import ClaimDevicesWindow
from gui.windows.validate_policy_object_names_window import PolicyObjectValidationWindow
from gui.windows.content_filtering_blocked_requests_by_client_window import BlockedRequestsWindow
from gui.windows.content_filtering_status_report_window import ContentFilteringStatusReportWindow
from gui.windows.create_firewall_rule_window import FirewallRuleWindow
from gui.windows.audit_unused_policy_objects_window import AuditPolicyObjectWindow
from gui.windows.create_policy_object_groups_window import CreatePolicyObjectGroupsWindow
from gui.windows.create_policy_objects_window import CreatePolicyObjectsWindow
from gui.windows.delete_group_policy_objects_window import DeletePolicyObjectGroupsWindow
from gui.windows.delete_policy_objects_window import DeletePolicyObjectsWindow
from gui.windows.export_policy_object_groups_window import ExportPolicyObjectGroupsWindow
from gui.windows.export_policy_objects_window import ExportPolicyObjectsWindow
from gui.windows.find_duplicate_policy_objects_window import FindDuplicatePolicyObjectsWindow
from gui.windows.update_policy_object_groups_window import UpdatePolicyObjectsInGroupWindow
from gui.windows.update_policy_objects_window import UpdatePolicyObjectsWindow
from gui.windows.network_clients_window import NetworkClientsWindow

class MerakiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Meraki Automation Hub")
        self.geometry("400x800")

        ttk.Label(self, text="Select an action:", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self, text="Claim Devices", command=self.open_claim_devices).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Validate Policy Objects", command=self.open_policy_validation).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Blocked Requests Report", command=self.content_filtering_blocked_requests_by_client).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Content Filtering Status Report", command=self.content_filtering_status_report).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Create a Firewall Rule", command=self.create_firewall_rule).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Policy Object Unused Audit Tool", command=self.policy_object_audit).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Create Policy Object Groups", command=self.create_policy_object_group).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Delete Policy Object Groups", command=self.delete_policy_object_groups).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Export Policy Object Groups", command=self.export_policy_object_groups).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Create Policy Objects", command=self.create_policy_objects).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Delete Policy Objects", command=self.delete_policy_objects).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Export Policy Objects", command=self.export_policy_objects).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Find Duplicate Policy Objects", command=self.find_duplciate_policy_objects).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Update Policy Objects in a Group", command=self.update_policy_objects_in_group).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Update Policy Objects", command=self.update_policy_objects).pack(fill='x', padx=20, pady=5)    
        ttk.Button(self, text="Network Client Analysis", command=self.network_clients_analysis).pack(fill='x', padx=20, pady=5)      


    def open_claim_devices(self):
        ClaimDevicesWindow(self)

    def open_policy_validation(self):
        PolicyObjectValidationWindow(self)

    def content_filtering_blocked_requests_by_client(self):
        BlockedRequestsWindow(self)

    def content_filtering_status_report(self):
        ContentFilteringStatusReportWindow(self)

    def create_firewall_rule(self):
        FirewallRuleWindow(self)

    def policy_object_audit(self):
        AuditPolicyObjectWindow(self)

    def create_policy_object_group(self):
        CreatePolicyObjectGroupsWindow(self)

    def create_policy_objects(self):
        CreatePolicyObjectsWindow(self)

    def delete_policy_object_groups(self):
        DeletePolicyObjectGroupsWindow(self)

    def delete_policy_objects(self):
        DeletePolicyObjectsWindow(self)

    def export_policy_object_groups(self):
        ExportPolicyObjectGroupsWindow(self)

    def export_policy_objects(self):
        ExportPolicyObjectsWindow(self)

    def find_duplciate_policy_objects(self):
        FindDuplicatePolicyObjectsWindow(self)

    def update_policy_objects_in_group(self):
        UpdatePolicyObjectsInGroupWindow(self)

    def update_policy_objects(self):
        UpdatePolicyObjectsWindow(self)

    def network_clients_analysis(self):
        NetworkClientsWindow(self)

if __name__ == "__main__":
    app = MerakiApp()
    app.mainloop()

    