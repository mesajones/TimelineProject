import tkinter as tk
from tkinter import messagebox

from utils import validate_ip
from config.settings import FOREGROUND, BACKGROUND, DEFAULT_FONT


class NetworkErrorDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, initial_ip: str = "", initial_port: str = "") -> None:
        super().__init__(parent)
        # Store the initial values
        self.default_font = DEFAULT_FONT
        self.title("Network Error: Please try different IP address and port")
        self.initial_ip = initial_ip
        self.initial_port = initial_port

        self.frame = tk.Frame(self, bg=BACKGROUND)
        self.frame.pack(expand=True, fill=tk.BOTH)

        # Make it modal
        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)  # Handle close button click

        self.initialize_dialog()  # Initialize dialog contents

    def initialize_dialog(self):
        # Initialize the dialog contents here

        self.geometry("400x100")

        self.ip_label = tk.Label(self.frame, text="Enter IP:", bg=BACKGROUND, foreground=FOREGROUND, font=self.default_font,
                                 justify=tk.RIGHT)
        self.ip_label.grid(row=0, column=0)

        self.ip_entry = tk.Entry(self.frame, bg=BACKGROUND, foreground=FOREGROUND, font=self.default_font)
        self.ip_entry.grid(row=0, column=1, sticky="ew")
        self.ip_entry.insert(0, self.initial_ip)
        self.ip_entry.bind("<Return>", self.on_enter)

        self.port_label = tk.Label(self.frame, text="Enter Port:", bg=BACKGROUND, foreground=FOREGROUND,
                                   font=self.default_font, justify=tk.RIGHT)
        self.port_label.grid(row=1, column=0)

        self.port_entry = tk.Entry(self.frame, bg=BACKGROUND, foreground=FOREGROUND, font=self.default_font)
        self.port_entry.grid(row=1, column=1, sticky="ew")
        self.port_entry.insert(0, self.initial_port)
        self.port_entry.bind("<Return>", self.on_enter)

        self.apply_button = tk.Button(self.frame, text="Apply", command=self.on_apply, bg=BACKGROUND,
                                      foreground=FOREGROUND, font=self.default_font)
        self.apply_button.grid(row=2, column=0)

        self.cancel_button = tk.Button(self.frame, text="Cancel", command=self.on_cancel, bg=BACKGROUND,
                                       foreground=FOREGROUND, font=self.default_font)
        self.cancel_button.grid(row=2, column=1)

    def on_enter(self, event):
        self.on_apply()

    def on_apply(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()

        if self.validate(ip, port):
            self.result = ip, int(port)  # Convert port to int here
            self.destroy()
        else:
            messagebox.showerror("Error", "Please enter valid IP and port")

    def validate(self, ip, port):
        if not validate_ip(ip):
            messagebox.showerror("Invalid Input", "Invalid IP Address")
            return False

        if not port.isdigit() or not (49152 <= int(port) <= 65535):
            messagebox.showerror("Invalid Input", "Port must be an integer between 49152 and 65535.")
            return False

        return True

    def on_cancel(self, event=None):
        # Handle cancel button click
        self.result = None, None
        self.destroy()
        

class MainGUI:
    def __init__(self, root, loop, client):
        self.root = root
        self.loop = loop
        self.client = client

        self.root.title("Timeline App")
        self.root.geometry("800x600")
        self.root.configure(bg=BACKGROUND)
        