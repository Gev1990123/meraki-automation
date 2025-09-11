import tkinter as tk
from tkinter import ttk, messagebox
import threading

from scripts.firewall.create_firewall_rule import create_firewall_rule

class FirewallRuleWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Create Meraki Firewall Rule")
        self.geometry("500x450")

        # Variables (instantiate them)
        self.comment = tk.StringVar()
        self.policy = tk.StringVar()
        self.protocol = tk.StringVar()
        self.src_port = tk.StringVar()
        self.dest_port = tk.StringVar()
        self.enable_syslog = tk.BooleanVar()
        self.rule_position = tk.IntVar()
        self.dry_run = tk.BooleanVar()
        self.debug = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Comment:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.comment, width=40).grid(row=0, column=1, sticky="ew")

        ttk.Label(frame, text="Policy:").grid(row=1, column=0, sticky="w")
        policy_combobox = ttk.Combobox(frame, textvariable=self.policy, state="readonly")
        policy_combobox['values'] = ("allow", "deny")
        policy_combobox.set('')  # No default selected
        policy_combobox.grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="Protocol:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.protocol).grid(row=2, column=1, sticky="ew")

        ttk.Label(frame, text="Source Port:").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.src_port).grid(row=3, column=1, sticky="ew")

        ttk.Label(frame, text="Destination Port:").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.dest_port).grid(row=4, column=1, sticky="ew")

        ttk.Checkbutton(frame, text="Enable Syslog", variable=self.enable_syslog).grid(row=5, column=1, sticky="w")

        ttk.Label(frame, text="Rule Position:").grid(row=6, column=0, sticky="w")
        ttk.Spinbox(frame, from_=1, to=20, textvariable=self.rule_position).grid(row=6, column=1, sticky="ew")

        ttk.Checkbutton(frame, text="Dry Run (simulate only)", variable=self.dry_run).grid(row=7, column=1, sticky="w")
        ttk.Checkbutton(frame, text="Debug Logging", variable=self.debug).grid(row=8, column=1, sticky="w")

        self.run_button = ttk.Button(frame, text="Create Firewall Rule", command=self.run_rule_threaded)
        self.run_button.grid(row=9, column=0, columnspan=2, pady=15)

        self.output_text = tk.Text(frame, height=10, state="disabled")
        self.output_text.grid(row=10, column=0, columnspan=2, sticky="nsew")

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(10, weight=1)

    def run_rule_threaded(self):
        self.run_button.config(state="disabled")
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.log("Starting firewall rule creation...")
        threading.Thread(target=self.run_rule).start()

    def run_rule(self):
        # Basic validation
        if not self.comment.get() or not self.policy.get() or not self.protocol.get():
            self.log("Validation Error: Please complete all required fields.")
            messagebox.showerror("Validation Error", "Please complete all required fields.")
            self.run_button.config(state="normal")
            return

        success, result = create_firewall_rule(
            comment=self.comment.get(),
            policy=self.policy.get(),
            protocol=self.protocol.get(),
            src_port=self.src_port.get(),
            dest_port=self.dest_port.get(),
            enable_syslog=self.enable_syslog.get(),
            rule_position=self.rule_position.get(),
            dry_run=self.dry_run.get(),
            debug=self.debug.get(),
        )
        if success:
            self.log("✅ Firewall rule creation completed.")
            self.log(f"Success networks: {', '.join(result.get('success', []))}")
            self.log(f"Skipped networks: {', '.join(result.get('skipped', []))}")
            self.log(f"Error networks: {', '.join(result.get('error', []))}")
        else:
            self.log("❌ Firewall rule creation failed.")
            self.log(str(result))

        self.run_button.config(state="normal")

    def log(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")
