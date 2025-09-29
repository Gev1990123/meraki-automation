import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from scripts.device_admin import claim_devices


class ClaimDevicesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Claim Devices")
        self.geometry("400x300")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # Title Label
        ttk.Label(self, text="Claim Devices", font=("Segoe UI", 14)).pack(pady=10)

        # CSV File Selection
        file_frame = ttk.Frame(self)
        file_frame.pack(padx=10, pady=5, fill='x')

        ttk.Label(file_frame, text="CSV File:").pack(side='left')

        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        file_entry.pack(side='left', padx=5)

        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side='left')

        # Start Button
        self.start_button = ttk.Button(self, text="Claim Devices", command=self.run_creation_threaded)
        self.start_button.pack(pady=10)

        # Log Display Area
        self.log_output = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, state='disabled')
        self.log_output.pack(fill='both', expand=True, padx=10, pady=10) 

    def log_to_gui(self, message):
        self.log_output.configure(state='normal')
        self.log_output.insert('end', message + '\n')
        self.log_output.see('end')
        self.log_output.configure(state='disabled')

    def run_creation_threaded(self):
        # Disable the button while running
        self.start_button.config(state='disabled')
        threading.Thread(target=self.run_creation, daemon=True).start()

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path.lower().endswith(".csv"):
            messagebox.showerror("Invalid File", "Please select a CSV file.")
            return

        if file_path:
            self.file_path_var.set(file_path)

    def run_creation(self):
        try:
            selected_file = self.file_path_var.get()
            if not selected_file:
                messagebox.showwarning("Missing File", "Please select a CSV file.")
                return

            result = claim_devices(csv_file=selected_file, log_callback=self.log_to_gui, debug=True)

            if result:
                messagebox.showinfo("Summary", result["summary"])
            else:
                messagebox.showerror("Error", "Object creation failed. Check the log.")
        except Exception as e:
            messagebox.showerror("Execution Error", f"An error occurred: {e}")
        finally:
            self.start_button.config(state='normal')
