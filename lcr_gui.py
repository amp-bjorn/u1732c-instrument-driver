import tkinter as tk
from tkinter import ttk, messagebox
import csv
import math
import serial.tools.list_ports
from datetime import datetime
from U1732C import U1732C

class LCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("U1732C LCR Meter - Professional")
        self.root.geometry("1024x768") # Slightly wider to accommodate 4 buttons
        self.root.minsize(700, 480)
        self.root.configure(bg="#1e1e1e")
        
        self.lcr = None
        self.is_running = False
        self.log_to_csv = tk.BooleanVar(value=False)
        self.refresh_rate = tk.IntVar(value=1000)
        self.units = {"R": "Ω", "C": "F", "L": "H", "Z": "Ω", "ESR": "Ω", "AI": ""}
        
        self.setup_styles()
        self.setup_ui()
        self.update_port_list()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = "#1e1e1e"
        fg_color = "#ffffff"
        button_color = "#454545"

        style.configure("TFrame", background=bg_color)
        style.configure("TLabelframe", background=bg_color, foreground=fg_color)
        style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color, font=("Segoe UI", 9, "bold"))
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=button_color, foreground=fg_color, borderwidth=1, font=("Segoe UI", 8))
        style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
        style.configure("TCombobox", fieldbackground=button_color, background=button_color, foreground=fg_color)
        style.configure("Large.TLabel", font=("Segoe UI", 48, "bold"), foreground="#00ff41", background=bg_color)

    def setup_ui(self):
        # Grid Configuration
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # --- LEFT PANEL (Controls) ---
        left_panel = ttk.Frame(self.root, padding="10")
        left_panel.grid(row=0, column=0, sticky="nsw")

        # Serial Port Group (using 2 columns for a tighter fit)
        port_frame = ttk.LabelFrame(left_panel, text="Connection", padding=5)
        port_frame.pack(fill=tk.X, pady=5)
        self.port_var = tk.StringVar()
        self.port_cb = ttk.Combobox(port_frame, textvariable=self.port_var, width=15)
        self.port_cb.grid(row=0, column=0, padx=2, pady=2)
        self.conn_btn = ttk.Button(port_frame, text="CONNECT", width=12, command=self.toggle_connection)
        self.conn_btn.grid(row=0, column=1, padx=2, pady=2)

        # Mode & Frequency & Factors (4 buttons per row)
        self.create_grid_group(left_panel, "Mode", ["SER", "PAL"], self.set_mode, cols=4)
        self.create_grid_group(left_panel, "Frequency", ["100", "120", "1k", "10k"], self.set_freq, cols=4)
        self.create_grid_group(left_panel, "Factors", ["D", "Q", "TH"], self.set_factor, cols=4)

        # Function Group (4 per row)
        self.create_grid_group(left_panel, "Function", ["R", "C", "L", "Z", "ESR", "AI"], self.update_function, cols=4)

        # Range Group (Dynamic - 4 per row)
        self.range_frame = ttk.LabelFrame(left_panel, text="Range", padding=5)
        self.range_frame.pack(fill=tk.X, pady=5)

        # System Control
        sys_frame = ttk.LabelFrame(left_panel, text="System", padding=5)
        sys_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        self.toggle_btn = ttk.Button(sys_frame, text="START MEASURING", command=self.toggle_sampling, state=tk.DISABLED)
        self.toggle_btn.pack(fill=tk.X, pady=2)
        
        lower_sys = ttk.Frame(sys_frame)
        lower_sys.pack(fill=tk.X)
        ttk.Label(lower_sys, text="Int:").pack(side=tk.LEFT)
        ttk.Combobox(lower_sys, textvariable=self.refresh_rate, values=[500, 1000, 2000, 5000], width=5).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(lower_sys, text="Log", variable=self.log_to_csv).pack(side=tk.LEFT, padx=5)

        # --- RIGHT PANEL (Readouts) ---
        right_panel = ttk.Frame(self.root, padding="20")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)

        self.main_readout = ttk.Label(right_panel, text="OFFLINE", style="Large.TLabel", anchor="center")
        self.main_readout.grid(row=0, column=0, pady=(60, 20))

        self.sub_readout = tk.Text(right_panel, height=12, width=40, 
                                   bg="#121212", fg="#00ff41", 
                                   font=("Consolas", 10), borderwidth=0, 
                                   highlightthickness=0, state=tk.DISABLED)
        self.sub_readout.grid(row=1, column=0, sticky="n")

    def create_grid_group(self, parent, label, items, cmd, cols=4):
        frame = ttk.LabelFrame(parent, text=label, padding=5)
        frame.pack(fill=tk.X, pady=2)
        for i, item in enumerate(items):
            btn = ttk.Button(frame, text=item, width=7, command=lambda x=item: cmd(x))
            btn.grid(row=i//cols, column=i%cols, sticky="ew", padx=1, pady=1)

    def update_port_list(self):
        if not self.lcr:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            self.port_cb['values'] = ports
        self.root.after(3000, self.update_port_list)

    def toggle_connection(self):
        if self.lcr is None:
            try:
                self.lcr = U1732C(self.port_var.get())
                self.lcr.read_identity()
                self.update_function("AI") 
                self.conn_btn.config(text="DISCONNECT")
                self.toggle_btn.config(state=tk.NORMAL)
                self.main_readout.config(text="READY")
            except Exception as e:
                messagebox.showerror("Connection Error", f"Could not connect: {e}")
                self.lcr = None
        else:
            self.is_running = False
            self.lcr.close()
            self.lcr = None
            self.conn_btn.config(text="CONNECT")
            self.toggle_btn.config(state=tk.DISABLED, text="START MEASURING")
            self.main_readout.config(text="OFFLINE")

    def update_function(self, func):
        if not self.lcr: return
        self.lcr.set_function(func)
        for w in self.range_frame.winfo_children(): w.destroy()
        
        ranges = self.lcr.ranges.get(func, [])
        for i, r in enumerate(ranges):
            btn = ttk.Button(self.range_frame, text=r, width=7, command=lambda rng=r: self.lcr.set_range(rng))
            btn.grid(row=i//4, column=i%4, sticky="ew", padx=1, pady=1)

    def set_mode(self, m): 
        if self.lcr: self.lcr.set_mode(m)
    def set_freq(self, f): 
        if self.lcr: self.lcr.set_frequency(f)
    def set_factor(self, fa): 
        if self.lcr: self.lcr.set_factor(fa)

    def format_eng(self, val):
        if abs(val) < 1e-21: return "0.00"
        exp = int(math.floor(math.log10(abs(val)) / 3) * 3)
        prefixes = {12:'T', 9:'G', 6:'M', 3:'k', 0:'', -3:'m', -6:'u', -9:'n', -12:'p', -15:'f'}
        return f"{val/(10**exp):.3f} {prefixes.get(exp, 'e'+str(exp))}"

    def toggle_sampling(self):
        self.is_running = not self.is_running
        self.toggle_btn.config(text="STOP MEASURING" if self.is_running else "START MEASURING")
        if self.is_running: self.poll_meter()

    def poll_meter(self):
        if not self.is_running or not self.lcr: return
        try:
            val = self.lcr.get_measurement()
            all_vals = self.lcr.get_all_measurements()
            unit = self.units.get(self.lcr._current_function, "")
            
            self.main_readout.config(text=f"{self.format_eng(val)}{unit}")
            
            self.sub_readout.config(state=tk.NORMAL)
            self.sub_readout.delete("1.0", tk.END)
            for k, v in all_vals.items():
                self.sub_readout.insert(tk.END, f"{k:>8}: {v:12.6e}\n")
            self.sub_readout.config(state=tk.DISABLED)
            
            if self.log_to_csv.get(): self.write_log(all_vals)
        except Exception as e:
            print(f"Polling Error: {e}")
            
        self.root.after(self.refresh_rate.get(), self.poll_meter)

    def write_log(self, data):
        filename = f"lcr_log_{datetime.now().strftime('%Y%m%d')}.csv"
        file_exists = False
        try:
            with open(filename, 'r'): file_exists = True
        except FileNotFoundError: pass

        with open(filename, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=["timestamp"] + list(data.keys()))
            if not file_exists: w.writeheader()
            row = {"timestamp": datetime.now().isoformat()}
            row.update(data)
            w.writerow(row)

if __name__ == "__main__":
    root = tk.Tk()
    app = LCRApp(root)
    root.mainloop()