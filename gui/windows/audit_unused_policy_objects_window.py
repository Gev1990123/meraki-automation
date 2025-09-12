import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from scripts.policy_objects.audit_unused_policy_objects import audit_unused_policy_objects
import threading

class AuditPolicyObjectWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__()
        self.title("Meraki Unused Policy Object Auditor")
        self.geometry("400x250")

        self.create_widgets()

    def create_widgets(self):
        # Title Label
        ttk.Label(self, text="Meraki Policy Object Audit Tool", font=("Arial", 16)).pack(pady=10)

        # CSV File Selection
        file_frame = ttk.Frame(self)
        file_frame.pack(padx=10, pady=5, fill='x')

        ttk.Label(file_frame, text="CSV File:").pack(side='left')

        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        file_entry.pack(side='left', padx=5)

        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side='left')
        
        # Debug Logging
        #ttk.Checkbutton(file_frame, text="Debug Logging", variable=self.debug).grid(row=10, column=1, sticky="w")

        # Run Audit Button
        self.run_button = ttk.Button(self, text="Run Audit", command=self.run_audit_threaded)
        self.run_button.pack(pady=10)

        # Log display area
        self.log_output = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, state='disabled')
        self.log_output.pack(fill='both', expand=True, padx=10, pady=10) 

    def log_to_gui(self, message):
        self.log_output.configure(state='normal')
        self.log_output.insert('end', message + '\n')
        self.log_output.see('end')
        self.log_output.configure(state='disabled')

    def run_creation_threaded(self):
        # Disable the button while running
        self.run_button.config(state='disabled')
        threading.Thread(target=self.run_creation, daemon=True).start()

    def browse_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            title="Select CSV File to Save",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)

    def run_audit_threaded(self):
        self.run_button.config(state="disabled")
        threading.Thread(target=self.run_audit, daemon=True).start()

    def run_audit(self):
        try:
            selected_file = self.file_path_var.get()
            if not selected_file: 
                messagebox.showwarning("Missing File", "Please select a CSV file.")
                self.run_button.config(state='normal')
                return
            
            result = audit_unused_policy_objects(csv_file=selected_file, log_callback=self.log_to_gui, debug=True)

            if result:
                messagebox.showinfo("Summary", result["summary"])
            else:
                messagebox.showerror("Error", "Export failed. Check the log.")
        finally:
            self.run_button.config(state='normal')
