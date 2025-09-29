import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading

from scripts.firewall.create_firewall_rule import create_firewall_rule, get_policy_object_groups_for_dropdown

class FirewallRuleWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Create Meraki Firewall Rule")
        self.geometry("500x450")
        self.resizable(False, False)

        # Variables (instantiate them)
        self.comment = tk.StringVar()
        self.policy = tk.StringVar()
        self.protocol = tk.StringVar()
        self.src = tk.StringVar()
        self.dst = tk.StringVar()
        self.src_port = tk.StringVar()
        self.dest_port = tk.StringVar()
        self.enable_syslog = tk.BooleanVar()
        self.rule_position = tk.IntVar()
        self.dry_run = tk.BooleanVar()
        self.debug = tk.BooleanVar()

        self.group_names = []
        
        self.create_widgets()
        self.fetch_groups_threaded()

    def create_widgets(self):
        # Title label
        ttk.Label(self, text="Create a Firewall Rule", font=("Segoe UI", 14)).pack(pady=10)

        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        # Comment (Firewall Rule Name)
        ttk.Label(frame, text="Comment:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.comment, width=40).grid(row=0, column=1, sticky="ew")

        # Policy (Firewall Policy Allow/Deny)
        ttk.Label(frame, text="Policy:").grid(row=1, column=0, sticky="w")
        policy_combobox = ttk.Combobox(frame, textvariable=self.policy, state="readonly")
        policy_combobox['values'] = ("allow", "deny")
        policy_combobox.set('')  # No default selected
        policy_combobox.grid(row=1, column=1, sticky="ew")

        # Protocol (Firewall Protocol TCP/UDP/Any)
        ttk.Label(frame, text="Protocol:").grid(row=2, column=0, sticky="w")
        protocol_combobox = ttk.Combobox(frame, textvariable=self.protocol, state="readonly")
        protocol_combobox['values'] = ("tcp", "udp", "any")
        protocol_combobox.set('')  # No default selected
        protocol_combobox.grid(row=2, column=1, sticky="ew")

        # Source Groups (Firewall Source Groups)
        ttk.Label(frame, text="Source Group(s):").grid(row=3, column=0, sticky="nw")
        self.src_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=False, height=6)
        self.src_listbox.grid(row=3, column=1, sticky="ew")

        # Destination Groups (Firewall Destination Groups)
        ttk.Label(frame, text="Destination Group(s):").grid(row=4, column=0, sticky="nw")
        self.dst_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=False, height=6)
        self.dst_listbox.grid(row=4, column=1, sticky="ew")

        # Source Ports (Firewall Source Ports)
        ttk.Label(frame, text="Source Port:").grid(row=5, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.src_port).grid(row=5, column=1, sticky="ew")

        # Destination Ports (Firewall Destination Ports)
        ttk.Label(frame, text="Destination Port:").grid(row=6, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.dest_port).grid(row=6, column=1, sticky="ew")

        # Enable Syslog (Firewall SysLogs)
        ttk.Checkbutton(frame, text="Enable Syslog", variable=self.enable_syslog).grid(row=7, column=1, sticky="w")

        # Rule Position (Firewall Rule Position)
        ttk.Label(frame, text="Rule Position:").grid(row=8, column=0, sticky="w")
        ttk.Spinbox(frame, from_=1, to=20, textvariable=self.rule_position).grid(row=8, column=1, sticky="ew")

        # Dry Run 
        ttk.Checkbutton(frame, text="Dry Run (simulate only)", variable=self.dry_run).grid(row=9, column=1, sticky="w")

        # Debug Logging
        ttk.Checkbutton(frame, text="Debug Logging", variable=self.debug).grid(row=10, column=1, sticky="w")

        # Button
        self.run_button = ttk.Button(frame, text="Create Firewall Rule", command=self.run_rule_threaded)
        self.run_button.grid(row=11, column=0, columnspan=2, pady=15)

        # Log Display Area
        self.log_output = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, state='disabled')
        self.log_output.pack(fill='both', expand=True, padx=10, pady=10) 

    def log_to_gui(self, message):
        self.log_output.configure(state='normal')
        self.log_output.insert('end', message + '\n')
        self.log_output.see('end')
        self.log_output.configure(state='disabled')

    def run_rule_threaded(self):
        self.run_button.config(state="disabled")
        self.log_output.config(state="normal")
        self.log_output.delete(1.0, tk.END)
        self.log_to_gui("Starting firewall rule creation...")
        threading.Thread(target=self.run_rule).start()

    def run_rule(self):
        try:
            if not self.comment.get() or not self.policy.get() or not self.protocol.get():
                self.log_to_gui("❌ Validation Error: Please complete all required fields.")
                messagebox.showerror("Validation Error", "Please complete all required fields.")
                return
            
            src_groups = self.get_selected_groups(self.src_listbox)
            dst_groups = self.get_selected_groups(self.dst_listbox)

            if not src_groups or not dst_groups:
                self.log_to_gui("❌ Source and Destination groups must be selected.")
                messagebox.showwarning("Missing Groups", "Please select at least one source and destination group.")
                return

            success, result = create_firewall_rule(
                comment=self.comment.get(),
                policy=self.policy.get(),
                protocol=self.protocol.get(),
                src=src_groups,
                src_port=self.src_port.get(),
                dst=dst_groups,
                dst_port=self.dest_port.get(),
                enable_syslog=self.enable_syslog.get(),
                rule_position=self.rule_position.get(),
                dry_run=self.dry_run.get(),
                debug=self.debug.get(),
                log_callback=self.log
            )


            if success:
                self.log_to_gui("✅ Firewall rule creation completed.")
                self.log_to_gui(f"Success networks: {', '.join(result.get('success', []))}")
                self.log_to_gui(f"Skipped networks: {', '.join(result.get('skipped', []))}")
                self.log_to_gui(f"Error networks: {', '.join(result.get('error', []))}")
            else:
                self.log_to_gui("❌ Firewall rule creation failed.")
                self.log_to_gui(str(result))

        except Exception as e:
            self.log_to_gui(f"❌ Error: {e}")
        finally:
            self.run_button.config(state="normal")

    def fetch_groups_threaded(self):
        threading.Thread(target=self.fetch_groups, daemon=True).start()

    def fetch_groups(self):
        groups = get_policy_object_groups_for_dropdown(log_callback=self.log_to_gui)

        if groups:
            group_names = [g['name'] for g in groups]
            group_names.append("Any")

            group_names.sort()

            self.group_name_to_object = {g['name']: g for g in groups}
            self.group_name_to_object["Any"] = None

            def update_listboxes():
                self.src_listbox.delete(0, tk.END)
                self.dst_listbox.delete(0, tk.END)

                for name in group_names:
                    self.src_listbox.insert(tk.END, name)
                    self.dst_listbox.insert(tk.END, name)

            self.after(0, update_listboxes)
        else:
            self.log_to_gui("⚠️ No groups found or failed to fetch.")

    def get_selected_groups(self, listbox):
        selected = [listbox.get(i) for i in listbox.curselection()]
        if "Any" in selected:
            return ["Any"]  # Or [] if your backend interprets that as "any"
        return selected