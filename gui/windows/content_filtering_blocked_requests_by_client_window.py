import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from scripts.content_filtering.content_filtering_blocked_requests_by_client import run_blocked_request_report

class BlockedRequestsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Blocked Requests Report")
        self.geometry("600x400")
        
        self.create_widgets()

    def create_widgets(self):
        # Days to check
        tk.Label(self, text="Days to look back:").pack(pady=5)
        self.days_entry = ttk.Entry(self)
        self.days_entry.insert(0, "1")
        self.days_entry.pack(pady=5)

        # Network filter (optional)
        tk.Label(self, text="Network name filter (optional):").pack(pady=5)
        self.network_filter_entry = ttk.Entry(self)
        self.network_filter_entry.pack(pady=5)

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
            
            days = int(self.days_entry.get())
            if not days:
                messagebox.showwarning("Missing days", "Please enter numebr of days.")
                self.run_button.config(state='normal')
                return
            
            network_filter = self.network_filter_entry.get().strip() or None

            result = run_blocked_request_report(days=days, network_filter=network_filter, csv_file=selected_file, log_callback=self.log_to_gui, debug=True)
            
            if result:
                messagebox.showinfo("Summary", result["summary"])
            else:
                messagebox.showerror("Error", "Export failed. Check the log.")
        finally:
            self.run_button.config(state='normal')

    def run_report(self):
        self.run_button.config(state='disabled')
        threading.Thread(target=self.run_export, daemon=True).start()
