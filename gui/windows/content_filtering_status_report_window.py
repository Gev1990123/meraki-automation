import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from scripts.content_filtering.content_filtering_status_report import run_content_filtering_report
from meraki_utils.dropdown_utils import get_networks_for_dropdown

class ContentFilteringStatusReportWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Content Filtering Status Report")
        self.geometry("600x400")
        self.resizable(False, False)

        self.create_widgets()
        self.fetch_groups_threaded()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

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

        # Run Button
        self.run_button = ttk.Button(self, text="Run Report", command=self.run_report)
        self.run_button.pack(pady=10)

        # Log display area
        self.log_output = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, state='disabled')
        self.log_output.pack(fill='both', expand=True, padx=10, pady=10)

    def browse_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            title="Select CSV File to Save",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.output_file.set(file_path)

    
    def log_to_gui(self, message):
        self.log_output.configure(state='normal')
        self.log_output.insert('end', message + '\n')
        self.log_output.see('end')
        self.log_output.update_idletasks()
        self.log_output.configure(state='disabled')

    def run_report_threaded(self):
        self.run_button.config(state='disabled')
        threading.Thread(target=self.run_export, daemon=True).start()

    def run_report(self):
        self.run_button.config(state='disabled')
        threading.Thread(target=self.run_export, daemon=True).start()

    def run_export(self):
        try:
            selected_file = self.file_path_var.get()
            if not selected_file:
                messagebox.showwarning("Missing File", "Please select a CSV file.")
                self.run_button.config(state='normal')
                return
            
            network_filter = self.selected_network.get()
            if network_filter == "All":
                network_filter = None

            self.log_to_gui(f"🔍 Running Content Filtering Status Report")

            result = run_content_filtering_report(
                csv_file=selected_file,
                network_filter=network_filter,
                log_callback=self.log_to_gui,
                debug=True
            )

            if result:
                messagebox.showinfo("Summary", result.get("summary", "Report completed."))
                self.log_to_gui("✅ Report completed successfully.")
            else:
                messagebox.showerror("Error", "Export failed. Check the log.")
                self.log_to_gui("Export failed.")

        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))
            self.log_to_gui(f"❌ Error: {str(e)}")
        finally:
            self.run_button.config(state='normal')

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