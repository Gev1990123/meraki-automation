import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import logging

from meraki_utils.config import dashboard
from meraki_utils.organisation import get_organization_id
from meraki_utils.logger import setup_logger

# Import the refactored function
from scripts.auditing_validation.validate_policy_object_names import validate_policy_objects

setup_logger()
logger = logging.getLogger(__name__)

class PolicyObjectValidationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Policy Object Validation")
        self.geometry("600x400")

        ttk.Label(self, text="Output CSV File Name:").pack(pady=5)
        self.output_entry = ttk.Entry(self)
        self.output_entry.insert(0, "policy_object_validation.csv")
        self.output_entry.pack(fill='x', padx=20)

        self.run_button = ttk.Button(self, text="Run Validation", command=self.run_validation)
        self.run_button.pack(pady=10)

        self.result_box = tk.Text(self, height=15)
        self.result_box.pack(fill='both', padx=20, pady=10)

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

        self.result_box.delete('1.0', tk.END)
        self.result_box.insert(tk.END, "Running validation...\n")

        try:
            results = validate_policy_objects(dashboard, org_id, output_path)
            self.result_box.insert(tk.END, f"Validation complete.\nResults saved to {output_path}\n\n")
            invalids = [r for r in results if r["status"] == "invalid"]
            if invalids:
                self.result_box.insert(tk.END, f"Invalid Policy Objects:\n")
                for item in invalids:
                    self.result_box.insert(tk.END, f"{item['name']}: {item['errors']}\n")
            else:
                self.result_box.insert(tk.END, "All policy objects are valid.\n")
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            self.result_box.insert(tk.END, f"Validation failed: {e}\n")
