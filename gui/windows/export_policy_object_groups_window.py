import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from scripts.policy_objects.export_policy_object_groups import export_policy_object_groups
import threading

class ExportPolicyObjectGroupsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Export Policy Object Groups")
        self.geometry("400x250")

        self.create_widgets()

    def create_widgets(self):
            # Title label
            ttk.Label(self, text="Export Policy Object Groups to CSV", font=("Segoe UI", 14)).pack(pady=10)

            # CSV File Selection
            file_frame = ttk.Frame(self)
            file_frame.pack(padx=10, pady=5, fill='x')

            ttk.Label(file_frame, text="CSV File:").pack(side='left')

            self.file_path_var = tk.StringVar()
            file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
            file_entry.pack(side='left', padx=5)

            ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side='left')

            # Start button
            self.start_button = ttk.Button(self, text="Start Export", command=self.run_export_threaded)
            self.start_button.pack(pady=10)

            # Log display area
            self.log_output = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, state='disabled')
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

            result = export_policy_object_groups(csv_file=selected_file, log_callback=self.log_to_gui, debug=True)
            
            if result:
                messagebox.showinfo("Summary", result["summary"])
            else:
                messagebox.showerror("Error", "Export failed. Check the log.")
        finally:
            self.start_button.config(state='normal')