import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from scripts.policy_objects.audit_unused_policy_objects import audit_unused_policy_objects

class AuditPolicyObjectWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__()
        self.title("Meraki Unused Policy Object Auditor")
        self.geometry("400x250")

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Meraki Policy Object Audit Tool", font=("Arial", 16)).pack(pady=10)

        # Run + Debug options
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.run_button = ttk.Button(button_frame, text="Run Audit", command=self.run_audit)
        self.run_button.grid(row=0, column=0, padx=10)

        self.debug_var = tk.BooleanVar()
        ttk.Checkbutton(button_frame, text="Enable Debug Logging", variable=self.debug_var).grid(row=0, column=1)

        # Output log
        self.log_output = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=20)
        self.log_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log(self, message):
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.see(tk.END)

    def run_audit(self):
        self.log_output.delete("1.0", tk.END)
        self.run_button.config(state=tk.DISABLED)
        self.log("🔍 Starting audit...")

        try:
            output_path = audit_unused_policy_objects(
                log_callback=self.log,
                debug=self.debug_var.get()
            )
            if output_path:
                messagebox.showinfo("Audit Complete", f"CSV exported to:\n{output_path}")
            else:
                messagebox.showerror("Error", "Audit failed. See log output.")
        finally:
            self.run_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    app = AuditPolicyObjectWindow()
    app.mainloop()
