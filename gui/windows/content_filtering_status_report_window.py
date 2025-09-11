import tkinter as tk
from tkinter import ttk
import threading

from scripts.content_filtering.content_filtering_status_report import run_content_filtering_report

class ContentFilteringStatusReportWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Content Filtering Status Report")
        self.geometry("600x400")

        self.output_file = tk.StringVar(value="content_filtering_status_report.csv")
        self.network_filter = tk.StringVar()
        self.compare_baseline = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Output File:").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.output_file, width=50).pack(anchor="w", pady=(0, 10))

        ttk.Label(frame, text="Network Filter (optional):").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.network_filter, width=50).pack(anchor="w", pady=(0, 10))

        ttk.Checkbutton(frame, text="Compare to Baseline", variable=self.compare_baseline).pack(anchor="w", pady=(0, 10))

        ttk.Button(frame, text="Run Report", command=self.run_report_threaded).pack(pady=10)

        self.output_text = tk.Text(frame, height=12)
        self.output_text.pack(fill="both", expand=True)

    def run_report_threaded(self):
        threading.Thread(target=self.run_report).start()

    def run_report(self):
        self.output_text.delete(1.0, tk.END)
        self.log("Running report...")

        try:
            results, message = run_content_filtering_report(
                output_filename=self.output_file.get(),
                network_filter=self.network_filter.get(),
                compare_to_baseline=self.compare_baseline.get()
            )
            self.log(f"✅ {message}")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")

    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
