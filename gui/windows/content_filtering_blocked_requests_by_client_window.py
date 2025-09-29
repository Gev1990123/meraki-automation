import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from scripts.content_filtering.content_filtering_blocked_requests_by_client import run_blocked_request_report
from meraki_utils.dropdown_utils import get_networks_for_dropdown

class BlockedRequestsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Blocked Requests Report")
        self.geometry("600x400")
        self.resizable(False, False)

        self.create_widgets()
        self.fetch_groups_threaded()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        # Days to check
        ttk.Label(self, text="Days to look back:").pack(pady=5)
        self.days_entry = ttk.Entry(self)
        self.days_entry.insert(0, "1")
        self.days_entry.pack(pady=5)

        # Network filter (optional)
        tk.Label(frame, text="Select a Network (or All):").pack(pady=5)
        self.selected_network = tk.StringVar()
        self.network_combobox = ttk.Combobox(frame, textvariable=self.selected_network, state="readonly")
        self.network_combobox.pack(fill='x', pady=5)

        # CSV File Selection
        file_frame = ttk.Frame(self)
        file_frame.pack(padx=10, pady=5, fill='x')

        ttk.Label(file_frame, text="CSV File:").pack(side='left')

        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        file_entry.pack(side='left', padx=5)

        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side='left')

        # Run button
        self.run_button = ttk.Button(self, text="Run Report", command=self.run_report)
        self.run_button.pack(pady=10)

        # Log display area
        self.log_output = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, state='disabled')
        self.log_output.pack(fill='both', expand=True, padx=10, pady=10) 

    def log_to_gui(self, message):
        self.log_output.configure(state='normal')
        self.log_output.insert('end', message + '\n')
        self.log_output.see('end')
        self.log_output.update_idletasks() 
        self.log_output.configure(state='disabled')

    def run_report_threaded(self):
        # Disable the button while running
        self.run_button.config(state='disabled')
        threading.Thread(target=self.run_export, daemon=True).start()

    def browse_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            title="Select CSV File to Save",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)

    def run_export(self):
        try:
            selected_file = self.file_path_var.get()
            if not selected_file:
                messagebox.showwarning("Missing File", "Please select a CSV file.")
                self.run_button.config(state='normal')
                return
            
            try:
                days = int(self.days_entry.get())
                if days <=0:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("Invalid Input", "Please enter a valid positive integer for days.")
                self.log_to_gui("Invalid days input.")
                return
            
            network_filter = self.selected_network.get()
            if network_filter == "All":
                network_filter = None

            self.log_to_gui(f"🔍 Running blocked requests report for last {days} day(s)...")

            result = run_blocked_request_report(days=days, network_filter=network_filter, csv_file=selected_file, log_callback=self.log_to_gui, debug=True)
            
            if result:
                messagebox.showinfo("Summary", result["summary"])
                self.log_to_gui("✅ Report completed successfully.")
            else:
                messagebox.showerror("Error", "Export failed. Check the log.")
                self.log_to_gui("Export failed.")

        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))
            self.log_to_gui(f"❌ Unexpected error: {e}")
        finally:
            self.run_button.config(state='normal')

    def run_report(self):
        self.run_button.config(state='disabled')
        threading.Thread(target=self.run_export, daemon=True).start()

    def fetch_groups_threaded(self):
        threading.Thread(target=self.fetch_groups, daemon=True).start()
    
    def fetch_groups(self):
        network_names = get_networks_for_dropdown()

        if network_names:
            network_names.sort()
            self.network_name_to_object = {name: None for name in network_names}
            self.network_name_to_object["All"] = None

            def update_combobox():
                self.network_combobox['values'] = ["All"] + network_names
                self.network_combobox.current(0)

            self.after(0, update_combobox)
        else:
            self.log_to_gui("⚠️ No groups found or failed to fetch.")

    def get_selected_groups(self, listbox):
        selected = [listbox.get(i) for i in listbox.curselection()]
        if "Any" in selected:
            return ["Any"]
        return selected