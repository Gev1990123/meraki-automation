import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from scripts.content_filtering.content_filtering_status_report import run_content_filtering_report

class ContentFilteringStatusReportWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Content Filtering Status Report")
        self.geometry("600x400")

        self.output_file = tk.StringVar()
        self.network_filter = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Network filter (optional)
        tk.Label(self, text="Network name filter (optional):").pack(pady=5)
        self.network_filter_entry = ttk.Entry(self)
        self.network_filter_entry.pack(pady=5)

        # CSV File Selection
        file_frame = ttk.Frame(self)
        file_frame.pack(padx=10, pady=5, fill='x')

        ttk.Label(file_frame, text="CSV File:").pack(side='left')

        self.file_path_var = tk.StringVar()

        # Read-only entry to force user to use the Browse button
        file_entry = ttk.Entry(file_frame, textvariable=self.output_file, width=40, state='readonly')
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

    def run_report(self):
        self.run_button.config(state='disabled')
        threading.Thread(target=self.run_export, daemon=True).start()

    def run_export(self):
        try:
            output_file = self.output_file.get()
            if not output_file:
                messagebox.showwarning("Missing File", "Please select where to save the CSV file.")
                return

            network_filter = self.network_filter.get().strip() or None

            result = run_content_filtering_report(
                csv_file=output_file,
                network_filter=network_filter,
                log_callback=self.log_to_gui,
                debug=True
            )

            if result:
                messagebox.showinfo("Summary", result.get("summary", "Report completed."))
            else:
                messagebox.showerror("Error", "Export failed. Check the log.")
        except Exception as e:
            self.log_to_gui(f"❌ Error: {str(e)}")
        finally:
            self.run_button.config(state='normal')

