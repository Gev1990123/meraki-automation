import tkinter as tk
from tkinter import ttk
from scripts.device_admin import claim_devices


class ClaimDevicesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Claim Devices")
        self.geometry("400x300")

        ttk.Label(self, text="Network ID:").pack(pady=5)
        self.network_entry = ttk.Entry(self)
        self.network_entry.pack(fill='x', padx=20)

        ttk.Label(self, text="Serial Numbers (comma separated):").pack(pady=5)
        self.serial_entry = ttk.Entry(self)
        self.serial_entry.pack(fill='x', padx=20)

        ttk.Button(self, text="Claim Devices", command=self.on_claim).pack(pady=10)

        self.output = tk.Text(self, height=8)
        self.output.pack(fill='both', padx=20, pady=10)

    def on_claim(self):
        network_id = self.network_entry.get()
        serials = [s.strip() for s in self.serial_entry.get().split(",")]
        try:
            claim_devices(network_id, serials)
            self.output.insert(tk.END, "Devices claimed successfully!\n")
        except Exception as e:
            self.output.insert(tk.END, f"Error: {e}\n")