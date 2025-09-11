import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from scripts.policy_objects.update_policy_object_groups import get_policy_object_groups_for_dropdown, update_policy_objects_in_group
import threading

class UpdatePolicyObjectsInGroupWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Update Policy Objects in a Group")
        self.geometry("400x250")

        self.group_name_to_object = {}
        self.selected_group_name = tk.StringVar()

        self.create_widgets()
        self.fetch_groups_threaded()
    
    def create_widgets(self):
            # Title label
            ttk.Label(self, text="Update Policy Objects in a Group", font=("Segoe UI", 14)).pack(pady=10)

            # CSV File Selection
            file_frame = ttk.Frame(self)
            file_frame.pack(padx=10, pady=5, fill='x')

            ttk.Label(file_frame, text="CSV File:").pack(side='left')

            self.file_path_var = tk.StringVar()
            file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
            file_entry.pack(side='left', padx=5)

            ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side='left')

            # Policy Object Group Dropdown
            group_frame = ttk.Frame(self)
            group_frame.pack(padx=10, pady=5, fill='x')

            ttk.Label(group_frame, text="Policy Object Group:").pack(side='left')
            self.group_dropdown = ttk.Combobox(group_frame, textvariable=self.selected_group_name, state="readonly", width=35)
            self.group_dropdown.pack(side='left', padx=5)


            # Start button
            self.start_button = ttk.Button(self, text="Start Update", command=self.run_creation_threaded)
            self.start_button.pack(pady=10)

            # Log display area
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
        if file_path:
            self.file_path_var.set(file_path)

    def run_creation(self):
        try:
            selected_file = self.file_path_var.get()
            selected_group = self.group_dropdown.get()

            if not selected_file:
                messagebox.showwarning("Missing File", "Please select a CSV file.")
                return
            
            if not selected_group:
                messagebox.showwarning("Missing Selection", "Please select a policy object group.")
                return

            if not selected_group:
                messagebox.showerror("Error", "Selected group not found in API response.")
                return


            result = update_policy_objects_in_group(csv_file=selected_file, policy_object_group=selected_group, log_callback=self.log_to_gui, debug=True)
            
            if result:
                messagebox.showinfo("Summary", result["summary"])
            else:
                messagebox.showerror("Error", "Object creation failed. Check the log.")
        finally:
            self.start_button.config(state='normal')    
    
    def fetch_groups_threaded(self):
        threading.Thread(target=self.fetch_groups, daemon=True).start()

    def fetch_groups(self):
        groups = get_policy_object_groups_for_dropdown(log_callback=self.log_to_gui)

        if groups:
            group_names = [g['name'] for g in groups]
            self.group_name_to_object = {g['name']: g for g in groups}

            def update_dropdown():
                self.group_dropdown['values'] = group_names
                self.group_dropdown.current(0)

            self.after(0, update_dropdown)
        else:
            self.log_to_gui("⚠️ No groups found or failed to fetch.")