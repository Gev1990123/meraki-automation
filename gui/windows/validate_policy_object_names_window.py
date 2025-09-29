import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import logging

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id

from scripts.auditing_validation.validate_policy_object_names import validate_policy_objects

class PolicyObjectValidationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Policy Object Validation")
        self.geometry("600x400")
        self.resizable(False, False)

        ttk.Label(self, text="Output CSV File Name:").pack(pady=5)
        self.output_entry = ttk.Entry(self)
        self.output_entry.insert(0, "policy_object_validation.csv")
        self.output_entry.pack(fill='x', padx=20)

        self.run_button = ttk.Button(self, text="Run Validation", command=self.run_validation)
        self.run_button.pack(pady=10)

        self.result_box = tk.Text(self, height=15)
        self.result_box.pack(fill='both', padx=20, pady=10)

    def log_to_gui(self, message):
        self.log_output.configure(state='normal')
        self.log_output.insert('end', message + '\n')
        self.log_output.see('end')
        self.log_output.configure(state='disabled')

    def run_validation(self):
        output_filename = self.output_entry.get().strip()
        if not output_filename:
            messagebox.showerror("Input Error", "Please enter a valid output filename.")
            return

        org_id = get_organization_id(dashboard)
        if not org_id:
            messagebox.showerror("Error", "Organization ID not found.")
            return

        output_path = Path(__file__).parent.parent.parent / "output" / output_filename

        self.log_to_gui("Running validation...")

        try:
            results = validate_policy_objects(dashboard, org_id, output_path)

            self.log_to_gui(f"Validation complete.\nResults saved to {output_path}\n")

            invalids = [r for r in results if r["status"] == "invalid"]
            if invalids:
                self.log_to_gui("Invalid Policy Objects:")
                for item in invalids:
                    self.log_to_gui(f"{item['name']}: {item['errors']}")
            else:
                self.log_to_gui("All policy objects are valid.")
        except Exception as e:
            self.log_to_gui(f"Validation failed: {e}")
