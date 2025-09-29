import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from scripts.auditing_validation.network_clients import network_client_stats
from meraki_utils.dropdown_utils import get_networks_for_dropdown
import threading

class NetworkClientsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Network Clients Analysis")
        self.geometry("400x600")

        self.networks = []

        self.create_widgets()
        self.fetch_groups_threaded()

    def create_widgets(self):
            frame = ttk.Frame(self, padding=15)
            frame.pack(fill=tk.BOTH, expand=True)

            # Title label
            ttk.Label(frame, text="Network Client Analysis", font=("Segoe UI", 14)).pack(pady=10)

            # Network filter (optional)
            tk.Label(frame, text="Select a Network (or All):").pack(pady=5)
            self.selected_network = tk.StringVar()
            self.network_combobox = ttk.Combobox(frame, textvariable=self.selected_network, state="readonly")
            self.network_combobox.pack(fill='x', pady=5)

            # High Usage Detection
            self.high_usage_var = tk.BooleanVar(value=False)
            self.usage_threshold_var = tk.StringVar(value="500")
            self.timespan_days_var = tk.StringVar(value="30")

            ## High Usage Detection Checlkbox
            ttk.Checkbutton(frame, text='Enable High Usage Detection', variable=self.high_usage_var).pack(anchor='w', pady=5)

            ## High Usage Threshold Inputs
            threshold_frame = ttk.Frame(frame)
            threshold_frame.pack(anchor='w', fill='x', pady=5)
            ttk.Label(threshold_frame, text="Threshold (MB/day):").grid(row=0, column=0, sticky='w')
            ttk.Entry(threshold_frame, textvariable=self.usage_threshold_var, width=10).grid(row=0, column=1, padx=5)

            ttk.Label(threshold_frame, text="Timespan (days, max 31):").grid(row=0, column=4, sticky='w')
            ttk.Entry(threshold_frame, textvariable=self.timespan_days_var, width=10).grid(row=0, column=5, padx=5)



            # CSV File Selection
            file_frame = ttk.Frame(frame)
            file_frame.pack(padx=10, pady=5, fill='x')

            ttk.Label(file_frame, text="CSV File:").pack(side='left')

            self.file_path_var = tk.StringVar()
            file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
            file_entry.pack(side='left', padx=5)

            ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side='left')

            # Start button
            self.start_button = ttk.Button(frame, text="Start Network Analysis", command=self.run_export_threaded)
            self.start_button.pack(pady=10)

            # Log display area
            self.log_output = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15, state='disabled')
            self.log_output.pack(fill='both', expand=True, padx=10, pady=10) 

    def log_to_gui(self, message):
        self.log_output.configure(state='normal')
        self.log_output.insert('end', message + '\n')
        self.log_output.see('end')
        self.log_output.configure(state='disabled')

    def run_export_threaded(self):
        # Disable the button while running
        self.start_button.config(state='disabled')
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
                self.start_button.config(state='normal')
                return

            selected_network = self.selected_network.get()
            usage_threshold = float(self.usage_threshold_var.get())
            timespan_days = int(self.timespan_days_var.get())
            timespan_seconds = min(timespan_days * 86400, 2678400)

            result = network_client_stats(
                csv_file=selected_file, 
                network_name=selected_network, 
                high_usage_detection=self.high_usage_var.get(), 
                usage_threshold_mb=usage_threshold,
                timespan=timespan_seconds,
                log_callback=self.log_to_gui, 
                debug=True)
            
            if result:
                messagebox.showinfo("Summary", result["summary"])
            else:
                messagebox.showerror("Error", "Export failed. Check the log.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for threshold and timespan.")
        finally:
            self.start_button.config(state='normal')

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
            return ["Any"]  # Or [] if your backend interprets that as "any"
        return selected