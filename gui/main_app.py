import tkinter as tk
from tkinter import messagebox
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
        self.resizable(False, True)

        self.buttons = [
            ("Claim Devices", ClaimDevicesWindow),
            ("Vlaidate Policy Objects", PolicyObjectValidationWindow),
            ("Blocked Requests Report", BlockedRequestsWindow),
            ("Content Filtering Status Report", ContentFilteringStatusReportWindow),
            ("Create a Firewall Rule", FirewallRuleWindow),
            ("Policy Object Unused Audit Tool", AuditPolicyObjectWindow),
            ("Create Policy Object Groups", CreatePolicyObjectGroupsWindow),
            ("Delete Policy Object Groups", DeletePolicyObjectGroupsWindow),
            ("Export Policy Object Groups",ExportPolicyObjectGroupsWindow),
            ("Create Policy Objects",CreatePolicyObjectsWindow),
            ("Delete Policy Objects",DeletePolicyObjectsWindow),
            ("Export Policy Objects",ExportPolicyObjectsWindow),
            ("Find Duplicate Policy Objects",FindDuplicatePolicyObjectsWindow),
            ("Update Policy Objects in a Group",UpdatePolicyObjectsInGroupWindow),
            ("Update Policy Objects",UpdatePolicyObjectsWindow),
            ("Network Client Analysis",NetworkClientsWindow)
        ]

        self.create_widgets()

    def create_widgets(self):
        for text, window_class in self.buttons:
            btn = tk.Button(self, text=text, width=30, command=lambda w=window_class: self.open_window(w))
            btn.pack(pady=5)

    def open_window(self, window_class):
        try:
            window_class(self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open window: {e}")
    
if __name__ == "__main__":
    app = MerakiApp()
    app.mainloop()

    