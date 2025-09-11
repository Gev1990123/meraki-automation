import tkinter as tk
from tkinter import ttk, messagebox
from scripts.content_filtering.content_filtering_blocked_requests_by_client import run_blocked_request_report

class BlockedRequestsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Blocked Requests Report")
        self.geometry("400x250")
        
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

        # Debug checkbox
        self.debug_var = tk.BooleanVar()
        self.debug_checkbox = ttk.Checkbutton(self, text="Enable debug logging", variable=self.debug_var)
        self.debug_checkbox.pack(pady=5)

        # Run button
        run_button = ttk.Button(self, text="Run Report", command=self.run_report)
        run_button.pack(pady=10)

    def run_report(self):
        try:
            days = int(self.days_entry.get())
            network_filter = self.network_filter_entry.get().strip() or None
            debug = self.debug_var.get()

            result = run_blocked_request_report(days=days, network_filter=network_filter, debug=debug)
            messagebox.showinfo("Report Result", result)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
