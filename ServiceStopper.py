import sys
import subprocess
import os
import ctypes
import traceback

def hide_console_window():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except:
        pass

def log_critical(msg):
    """Ensure logs are visible in console and a popup if something fails."""
    timestamp = "[STARTUP]"
    full_msg = f"{timestamp} {msg}"
    # Also log to a file in case console closes too fast
    try:
        with open("startup_error.log", "a") as f:
            f.write(full_msg + "\n")
    except: pass

# --- Initialization & Dependencies ---
REQUIRED_DEPENDENCIES = [
    ("psutil", "psutil"),
    ("tkinter", None),
    ("json", None),
    ("threading", None)
]

def check_dependencies():
    log_critical("Checking dependencies...")
    log_critical(f"Python: {sys.version.split()[0]} ({sys.executable})")
    for module, pip_name in REQUIRED_DEPENDENCIES:
        try:
            imported = __import__(module)
            log_critical(f"Dependency '{module}' is already installed.")
            if module == "tkinter":
                try:
                    log_critical(f"Tkinter available (Tk {imported.TkVersion})")
                except:
                    log_critical("Tkinter available")
        except ImportError:
            if not pip_name:
                log_critical(f"Dependency '{module}' MISSING. Reinstall Python.")
                ctypes.windll.user32.MessageBoxW(0, f"Missing Python module: {module}\nPlease repair or reinstall Python.", "Dependency Error", 0x10)
                sys.exit(1)
            log_critical(f"Dependency '{module}' MISSING. Attempting installation...")
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "install", pip_name], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    log_critical(f"Successfully installed {module}.")
                else:
                    error_detail = result.stderr if result.stderr else "Unknown error"
                    log_critical(f"FAILED to install {module}. Error: {error_detail}")
                    ctypes.windll.user32.MessageBoxW(0, f"Failed to install {module}.\n\nError: {error_detail}", "Dependency Error", 0x10)
                    sys.exit(1)
            except Exception as e:
                log_critical(f"CRITICAL error during pip installation: {str(e)}")
                ctypes.windll.user32.MessageBoxW(0, f"Critical error during pip install:\n{str(e)}", "Dependency Error", 0x10)
                sys.exit(1)

def elevate():
    """Auto-elevate to Admin if not already."""
    log_critical("Checking admin privileges...")
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            log_critical("Not running as Admin. Requesting elevation...")
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            # 1 = SW_SHOWNORMAL
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            
            if int(result) <= 32:
                log_critical(f"Elevation request FAILED (Code: {result}). User likely denied UAC.")
                sys.exit(0) # User denied, just exit
            else:
                log_critical("Elevation request sent successfully. Closing current process.")
                sys.exit(0)
        else:
            log_critical("Running with Admin privileges.")
    except Exception as e:
        log_critical(f"Elevation check CRASHED: {str(e)}\n{traceback.format_exc()}")
        ctypes.windll.user32.MessageBoxW(0, f"Elevation check crashed:\n{str(e)}", "Privilege Error", 0x10)
        sys.exit(1)

# Run critical checks BEFORE importing heavy modules
if __name__ == "__main__":
    # Clear old startup log
    try:
        if os.path.exists("startup_error.log"): os.remove("startup_error.log")
    except: pass
    
    check_dependencies()
    elevate()
    hide_console_window()

# --- Now safe to import heavy modules ---
try:
    log_critical("Importing UI and system modules...")
    import json
    import threading
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog
    import psutil
    log_critical("Imports successful. Launching UI...")
except Exception as e:
    log_critical(f"IMPORT FAILED: {str(e)}\n{traceback.format_exc()}")
    ctypes.windll.user32.MessageBoxW(0, f"Module Import Failed:\n{str(e)}", "Import Error", 0x10)
    sys.exit(1)

# --- Performance & UI Constants ---
CONFIG_FILE = "profiles.json"
BG_COLOR = "#000000"  # Pure black for deep native look
SIDEBAR_COLOR = "#0A0A0A"
HEADER_COLOR = "#111111"
FG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#0078D4" # Windows Blue
DANGER_COLOR = "#E81123" # Windows Error Red
SUCCESS_COLOR = "#107C10" # Windows Success Green
ROW_HEIGHT = 30

class ServiceStopperUltra(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Service Stopper v4.2 - Admin")
        self.geometry("1100x750")
        self.configure(bg=BG_COLOR)
        
        # State
        self.services_data = {} 
        self.profiles = self.load_profiles()
        self.selected_names = set()
        self.sort_column = "Display Name"
        self.sort_reverse = False
        self.active_profile_name = None
        self.profile_filter = None
        self.start_type_cache = {}
        self.max_log_lines = 2000
        self._exiting = False

        self.setup_styles()
        self.setup_ui()
        self.refresh_data()
        self.integrate_startup_logs()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def load_profiles(self):
        default_recommended = [
            "DPS",            # Diagnostic Policy Service 
            "WdiServiceHost", # Diagnostic Service Host Service 
            "WdiSystemHost",  # Diagnostic System Host Service 
            "BITS",           # Background Intelligent Transfer Service    
            "wuauserv",       # Windows Update 
            "WaaSMedicSvc",   # Windows Update Medic Service 
            "XblAuthManager", # Xbox Live Auth Manager    
            "XboxNetApiSvc",  # Xbox Live Networking Service 
            "ClickToRunSvc",  # Microsoft Office Click-to-Run Service 
            "Spooler"         # Print Spooler Service
        ]
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    # Always ensure Recommended is updated to user's latest spec
                    data["Recommended"] = default_recommended
                    return data
            except: pass
        return {"Recommended": default_recommended}

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview",
            background=BG_COLOR, foreground=FG_COLOR, fieldbackground=BG_COLOR,
            rowheight=ROW_HEIGHT, font=("Segoe UI", 9), borderwidth=0)
        style.map("Treeview", 
            background=[('selected', BG_COLOR)], 
            foreground=[('selected', FG_COLOR)])
        
        style.configure("Treeview.Heading",
            background=HEADER_COLOR, foreground=FG_COLOR,
            font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
        style.map("Treeview.Heading", background=[('active', HEADER_COLOR), ('pressed', HEADER_COLOR)])
        
        style.configure("Vertical.TScrollbar", background=HEADER_COLOR, troughcolor=BG_COLOR, bordercolor=BG_COLOR, arrowcolor=FG_COLOR)
        style.map("Vertical.TScrollbar", background=[('active', "#2A2A2A"), ('pressed', "#2A2A2A")])
        
        # Sidebar Button Style
        style.configure("Sidebar.TButton",
            padding=6, font=("Segoe UI", 8, "bold"),
            background="#252525", foreground="white", borderwidth=0)
        style.map("Sidebar.TButton", 
            background=[('active', "#333333"), ('pressed', "#444444")])

        # Action Button Style
        style.configure("Action.TButton",
            padding=6, font=("Segoe UI", 8, "bold"),
            background=ACCENT_COLOR, foreground="white", borderwidth=0)
        style.map("Action.TButton", 
            background=[('active', "#2563EB")])

        # Danger Button Style
        style.configure("Danger.TButton",
            padding=6, font=("Segoe UI", 8, "bold"),
            background=DANGER_COLOR, foreground="white", borderwidth=0)
        style.map("Danger.TButton", 
            background=[('active', "#DC2626")])

    def log(self, message, level="INFO"):
        if self._exiting or not hasattr(self, "console"):
            return
        if threading.current_thread() is threading.main_thread():
            self._log_ui(message, level)
        else:
            try:
                self.after(0, lambda: self._log_ui(message, level))
            except:
                pass

    def _log_ui(self, message, level="INFO"):
        colors = {"INFO": "#94A3B8", "ERROR": DANGER_COLOR, "SUCCESS": SUCCESS_COLOR, "WARN": "#FBBF24"}
        self.console.config(state="normal")
        self.console.insert("end", f"[{level}] ", level)
        self.console.insert("end", f"{message}\n")
        self.console.tag_config(level, foreground=colors.get(level, FG_COLOR))
        self.console.see("end")
        if self.max_log_lines:
            current_lines = int(self.console.index("end-1c").split(".")[0])
            if current_lines > self.max_log_lines:
                self.console.delete("1.0", f"{current_lines - self.max_log_lines + 1}.0")
        self.console.config(state="disabled")

    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#333", foreground="white", 
                            padx=5, pady=2, font=("Segoe UI Variable Text", 8))
            label.pack()
            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def integrate_startup_logs(self):
        try:
            if os.path.exists("startup_error.log"):
                with open("startup_error.log", "r") as f:
                    for line in f:
                        self.log(line.strip(), "INFO")
                os.remove("startup_error.log")
        except:
            pass
    def get_start_type(self, name):
        if name in self.start_type_cache:
            return self.start_type_cache[name]
        # First, try psutil which often provides start_type directly
        try:
            svc = psutil.win_service_get(name).as_dict()
            st = str(svc.get("start_type") or "").upper()
            if st:
                if "DELAYED" in st:
                    val = "AUTO (DELAYED)"
                elif "AUTO" in st:
                    val = "AUTO"
                elif "DEMAND" in st or "MANUAL" in st:
                    val = "MANUAL"
                elif "DISABLED" in st:
                    val = "DISABLED"
                elif "BOOT" in st:
                    val = "BOOT"
                elif "SYSTEM" in st:
                    val = "SYSTEM"
                else:
                    val = "MANUAL"
                self.start_type_cache[name] = val
                return val
        except:
            pass
        # Fallback to sc qc parsing
        try:
            result = subprocess.run(["sc", "qc", name], capture_output=True, text=True)
            out = result.stdout
            val = "MANUAL"
            for line in out.splitlines():
                if "START_TYPE" in line:
                    upper = line.upper()
                    if "DELAYED_AUTO_START" in upper:
                        val = "AUTO (DELAYED)"
                    elif "AUTO_START" in upper:
                        val = "AUTO"
                    elif "DEMAND_START" in upper or "MANUAL" in upper:
                        val = "MANUAL"
                    elif "DISABLED" in upper:
                        val = "DISABLED"
                    elif "BOOT_START" in upper:
                        val = "BOOT"
                    elif "SYSTEM_START" in upper:
                        val = "SYSTEM"
                    break
            self.start_type_cache[name] = val
            return val
        except:
            self.start_type_cache[name] = "MANUAL"
            return "MANUAL"

    def copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self.console.get("1.0", "end"))
        self.log("Log copied to clipboard", "INFO")

    def clear_log(self):
        self.console.config(state="normal")
        self.console.delete("1.0", "end")
        self.console.config(state="disabled")
        self.log("Log cleared", "INFO")

    def setup_ui(self):
        # --- Main Content (Left Side) ---
        self.main_container = tk.Frame(self, bg=BG_COLOR)
        self.main_container.pack(side="left", fill="both", expand=True)

        # Search Bar Area - COMPACT & ALIGNED
        search_container = tk.Frame(self.main_container, bg=BG_COLOR)
        search_container.pack(fill="x", padx=30, pady=(25, 0))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_list())
        
        # Reduced width search frame
        search_frame = tk.Frame(search_container, bg=HEADER_COLOR, highlightthickness=1, highlightbackground="#333", width=350, height=36)
        search_frame.pack(side="left")
        search_frame.pack_propagate(False)
        
        tk.Label(search_frame, text=" 🔍 ", bg=HEADER_COLOR, fg="#888", font=("Segoe UI", 9)).pack(side="left", padx=(5, 0))
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=HEADER_COLOR, fg="white", 
                                   insertbackground="white", borderwidth=0, font=("Segoe UI", 9))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.search_entry.focus()

        # Treeview Area
        tree_container = tk.Frame(self.main_container, bg=BG_COLOR)
        tree_container.pack(fill="both", expand=True, padx=30, pady=(20, 10))

        # Custom Scrollbar for Treeview
        tree_frame = tk.Frame(tree_container, bg=BG_COLOR)
        tree_frame.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical")
        # Added 'Sel' column for dedicated checkboxes
        self.tree = ttk.Treeview(tree_frame, columns=("Sel", "Display Name", "Name", "Start Type", "Status"), show="headings", yscrollcommand=sb.set)
        sb.config(command=self.tree.yview)
        
        # Configure column widths and alignment
        self.tree.column("Sel", width=28, anchor="center", stretch=False)
        self.tree.column("Display Name", width=360, anchor="w")
        self.tree.column("Name", width=150, anchor="w")
        self.tree.column("Start Type", width=110, anchor="w")
        self.tree.column("Status", width=100, anchor="w")

        self.tree.heading("Sel", text="")
        self.tree.heading("Display Name", text="SERVICE NAME", anchor="w", command=lambda: self.set_sort("Display Name"))
        self.tree.heading("Name", text="ID", anchor="w", command=lambda: self.set_sort("Name"))
        self.tree.heading("Start Type", text="START TYPE", anchor="w", command=lambda: self.set_sort("Start Type"))
        self.tree.heading("Status", text="STATUS", anchor="w", command=lambda: self.set_sort("Status"))
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Button-1>", self.on_click)

        # Dedicated style for the checkbox column to look more visible
        self.tree.tag_configure("chk_font", font=("Segoe UI Symbol", 11))

        # Tags for row coloring
        self.tree.tag_configure("running", foreground=SUCCESS_COLOR)
        self.tree.tag_configure("stopped", foreground="#9CA3AF")
        self.tree.tag_configure("disabled", foreground="#CFAF70")

        # Log Area
        log_frame = tk.Frame(self.main_container, bg=BG_COLOR)
        log_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        log_header = tk.Frame(log_frame, bg=BG_COLOR)
        log_header.pack(fill="x", pady=(0, 5))
        tk.Label(log_header, text="ACTIVITY LOG", bg=BG_COLOR, fg="#555", font=("Segoe UI Variable Text", 8, "bold")).pack(side="left")
        
        copy_btn = tk.Button(log_header, text="COPY LOG", bg=BG_COLOR, fg=ACCENT_COLOR, borderwidth=0, 
                           font=("Segoe UI Variable Text", 7, "bold"), cursor="hand2", command=self.copy_log,
                           activebackground=BG_COLOR, activeforeground="white")
        copy_btn.pack(side="right")

        self.console_frame = tk.Frame(log_frame, bg="#080808", height=140, highlightthickness=0)
        self.console_frame.pack(fill="x")
        self.console_frame.pack_propagate(False)

        self.console_sb = ttk.Scrollbar(self.console_frame, orient="vertical")
        self.console = tk.Text(self.console_frame, bg="#080808", fg="#888", font=("Consolas", 9), 
                              padx=12, pady=12, borderwidth=0, state="disabled", yscrollcommand=self.console_sb.set)
        self.console_sb.config(command=self.console.yview)
        
        self.console_sb.pack(side="right", fill="y")
        self.console.pack(side="left", fill="both", expand=True)

        # --- Sidebar (Right Side) ---
        self.sidebar = tk.Frame(self, bg=SIDEBAR_COLOR, width=260)
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        # Title
        tk.Label(self.sidebar, text="CONTROL PANEL", bg=SIDEBAR_COLOR, fg=ACCENT_COLOR, 
                 font=("Segoe UI Variable Display", 11, "bold")).pack(pady=(30, 20), padx=25, anchor="w")

        # Profiles
        self.create_sidebar_label("PROFILES")
        self.profile_var = tk.StringVar(value="Recommended")
        self.profile_box = ttk.Combobox(self.sidebar, textvariable=self.profile_var, values=list(self.profiles.keys()), state="readonly")
        self.profile_box.pack(pady=5, padx=25, fill="x")

        apply_prof_btn = ttk.Button(self.sidebar, text="Apply Profile", style="Sidebar.TButton", command=self.apply_profile)
        apply_prof_btn.pack(pady=2, padx=25, fill="x")
        save_prof_btn = ttk.Button(self.sidebar, text="Save Current", style="Sidebar.TButton", command=self.save_profile)
        save_prof_btn.pack(pady=2, padx=25, fill="x")

        import_prof_btn = ttk.Button(self.sidebar, text="Import Profiles", style="Sidebar.TButton", command=self.import_profiles)
        import_prof_btn.pack(pady=2, padx=25, fill="x")
        export_prof_btn = ttk.Button(self.sidebar, text="Export Profiles", style="Sidebar.TButton", command=self.export_profiles)
        export_prof_btn.pack(pady=2, padx=25, fill="x")

        self.active_profile_label = tk.Label(self.sidebar, text="Active Profile: None", bg=SIDEBAR_COLOR, fg="#666", font=("Segoe UI", 8))
        self.active_profile_label.pack(pady=(8, 0), padx=25, anchor="w")
        clear_profile_btn = ttk.Button(self.sidebar, text="Clear Profile Filter", style="Sidebar.TButton", command=self.clear_profile_filter)
        clear_profile_btn.pack(pady=2, padx=25, fill="x")
        clear_selection_btn = ttk.Button(self.sidebar, text="Clear Selection", style="Sidebar.TButton", command=self.select_none)
        clear_selection_btn.pack(pady=2, padx=25, fill="x")

        self.create_sidebar_label("ACTIONS")
        ops_row1 = tk.Frame(self.sidebar, bg=SIDEBAR_COLOR)
        ops_row1.pack(fill="x", padx=25, pady=4)
        start_btn = ttk.Button(ops_row1, text="START", style="Action.TButton", command=lambda: self.run_action("start"))
        start_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
        self.create_tooltip(start_btn, "Start selected services")

        stop_btn = ttk.Button(ops_row1, text="STOP", style="Danger.TButton", command=lambda: self.run_action("stop"))
        stop_btn.pack(side="left", expand=True, fill="x", padx=(2, 0))
        self.create_tooltip(stop_btn, "Stop selected services")

        ops_row2 = tk.Frame(self.sidebar, bg=SIDEBAR_COLOR)
        ops_row2.pack(fill="x", padx=25, pady=4)
        pause_btn = ttk.Button(ops_row2, text="PAUSE", style="Sidebar.TButton", command=lambda: self.run_action("pause"))
        pause_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
        self.create_tooltip(pause_btn, "Pause selected services")

        resume_btn = ttk.Button(ops_row2, text="RESUME", style="Sidebar.TButton", command=lambda: self.run_action("resume"))
        resume_btn.pack(side="left", expand=True, fill="x", padx=(2, 0))
        self.create_tooltip(resume_btn, "Resume selected services")

        self.create_sidebar_label("STARTUP TYPE")
        ops_row3 = tk.Frame(self.sidebar, bg=SIDEBAR_COLOR)
        ops_row3.pack(fill="x", padx=25, pady=4)
        man_btn = ttk.Button(ops_row3, text="MANUAL", style="Sidebar.TButton", command=lambda: self.run_action("manual"))
        man_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
        self.create_tooltip(man_btn, "Set start type to Manual")

        auto_btn = ttk.Button(ops_row3, text="AUTO", style="Sidebar.TButton", command=lambda: self.run_action("auto"))
        auto_btn.pack(side="left", expand=True, fill="x", padx=(2, 0))
        self.create_tooltip(auto_btn, "Set start type to Automatic")

        ops_row4 = tk.Frame(self.sidebar, bg=SIDEBAR_COLOR)
        ops_row4.pack(fill="x", padx=25, pady=4)
        delayed_btn = ttk.Button(ops_row4, text="DELAYED", style="Sidebar.TButton", command=lambda: self.run_action("delayed"))
        delayed_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
        self.create_tooltip(delayed_btn, "Set start type to Automatic (Delayed)")

        disabled_btn = ttk.Button(ops_row4, text="DISABLED", style="Sidebar.TButton", command=lambda: self.run_action("disabled"))
        disabled_btn.pack(side="left", expand=True, fill="x", padx=(2, 0))
        self.create_tooltip(disabled_btn, "Set start type to Disabled")

        self.create_sidebar_label("MAINTENANCE")
        update_deps_btn = ttk.Button(self.sidebar, text="Update Dependencies", style="Sidebar.TButton", command=self.update_dependencies)
        update_deps_btn.pack(pady=2, padx=25, fill="x")

        exit_btn = ttk.Button(self.sidebar, text="EXIT", style="Sidebar.TButton", command=self.on_exit)
        exit_btn.pack(side="bottom", pady=16, padx=25, fill="x")
        
        # Right-click menu for console
        self.log_menu = tk.Menu(self, tearoff=0, bg=SIDEBAR_COLOR, fg=FG_COLOR, activebackground=ACCENT_COLOR)
        self.log_menu.add_command(label="Copy All", command=self.copy_log)
        self.log_menu.add_command(label="Clear Log", command=lambda: self.clear_log())
        self.console.bind("<Button-3>", lambda e: self.log_menu.post(e.x_root, e.y_root))

    def create_sidebar_label(self, text):
        tk.Label(self.sidebar, text=text, bg=SIDEBAR_COLOR, fg="#444", font=("Segoe UI Variable Text", 8, "bold")).pack(pady=(25, 5), padx=20, anchor="w")

    def update_dependencies(self):
        def run():
            self.log("Updating dependencies...", "INFO")
            for module, pip_name in REQUIRED_DEPENDENCIES:
                if not pip_name:
                    self.log(f"{module} is built-in; no update needed", "INFO")
                    continue
                try:
                    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", pip_name], capture_output=True, text=True)
                    if result.returncode == 0:
                        out = (result.stdout or "").lower()
                        err = (result.stderr or "").lower()
                        if "already satisfied" in out or "already up-to-date" in out or "requires satisfied" in out or "up-to-date" in err:
                            self.log(f"{pip_name} is already up-to-date", "INFO")
                        else:
                            self.log(f"Updated {pip_name}", "SUCCESS")
                    else:
                        detail = result.stderr.strip() or result.stdout.strip() or f"Exit code {result.returncode}"
                        self.log(f"Failed to update {pip_name}: {detail}", "ERROR")
                except Exception as e:
                    self.log(f"Update error {pip_name}: {str(e)}", "ERROR")
            self.refresh_data()
        threading.Thread(target=run, daemon=True).start()

    def on_exit(self):
        if self._exiting:
            return
        self._exiting = True
        try:
            self.quit()
            self.destroy()
        except:
            pass

    def set_sort(self, col):
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        self.filter_list()

    def on_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            return

        item = self.tree.identify_row(event.y)
        if not item: return
        
        column = self.tree.identify_column(event.x)
        if column == "#1":
            if item in self.selected_names:
                self.selected_names.remove(item)
            else:
                self.selected_names.add(item)
            self.update_item_display(item)

    def update_item_display(self, item_id):
        if not self.tree.exists(item_id): return
        data = self.services_data[item_id]
        is_selected = item_id in self.selected_names
        prefix = "☑" if is_selected else "☐"
        
        status = data['status']
        start_type = data.get('start_type') or self.get_start_type(item_id)
        tags = ["chk_font"]
        if status == "RUNNING": tags.append("running")
        else: tags.append("stopped")
        if start_type == "DISABLED": tags.append("disabled")
        
        self.tree.item(item_id, values=(prefix, data['display'], item_id, start_type, status), tags=tags)

    def refresh_data(self):
        self.start_type_cache = {}
        self.services_data = {}
        for svc in psutil.win_service_iter():
            try:
                info = svc.as_dict()
                self.services_data[info['name']] = {
                    "display": info['display_name'] or info['name'],
                    "status": info['status'].upper(),
                    "start_type": self.get_start_type(info['name'])
                }
            except: pass
        self.filter_list()

    def filter_list(self):
        search = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        
        cols = {"Display Name": "SERVICE NAME", "Name": "ID", "Start Type": "START TYPE", "Status": "STATUS"}
        for col_id, base_text in cols.items():
            indicator = " ▲" if self.sort_column == col_id and not self.sort_reverse else \
                        " ▼" if self.sort_column == col_id and self.sort_reverse else ""
            self.tree.heading(col_id, text=base_text + indicator)

        items = list(self.services_data.items())
        if self.sort_column == "Name":
            items.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)
        elif self.sort_column == "Display Name":
            items.sort(key=lambda x: x[1]['display'].lower(), reverse=self.sort_reverse)
        elif self.sort_column == "Start Type":
            items.sort(key=lambda x: x[1].get('start_type', '').lower(), reverse=self.sort_reverse)
        elif self.sort_column == "Status":
            items.sort(key=lambda x: x[1]['status'], reverse=self.sort_reverse)

        for name, data in items:
            if self.profile_filter and name not in self.profile_filter:
                continue
            if search in name.lower() or search in data['display'].lower():
                is_selected = name in self.selected_names
                prefix = "☑" if is_selected else "☐"
                
                start_type = data.get('start_type') or self.get_start_type(name)
                tags = ["chk_font"]
                if data['status'] == "RUNNING": tags.append("running")
                else: tags.append("stopped")
                if start_type == "DISABLED": tags.append("disabled")
                
                self.tree.insert("", "end", iid=name, values=(prefix, data['display'], name, start_type, data['status']), tags=tags)

    def select_all(self):
        search = self.search_var.get().lower()
        for name, data in self.services_data.items():
            if search in name.lower() or search in data['display'].lower():
                self.selected_names.add(name)
        self.filter_list()
        self.log(f"Selected all visible", "INFO")

    def select_none(self):
        self.selected_names.clear()
        self.filter_list()
        self.log("Selection cleared", "INFO")

    def apply_profile(self):
        prof = self.profile_var.get()
        if prof in self.profiles:
            selected_list = self.profiles[prof]
            self.selected_names = set(selected_list)
            self.active_profile_name = prof
            self.profile_filter = set(selected_list)
            self.active_profile_label.config(text=f"Active Profile: {prof} ({len(selected_list)})")
            self.filter_list()
            
            count = len(self.selected_names)
            names_str = ", ".join(selected_list)
            self.log(f"Applied: {prof} ({count} services)", "SUCCESS")
            self.log(f"Selected: {names_str}", "INFO")

    def save_profile(self):
        name = simpledialog.askstring("New Profile", "Profile name:")
        if not name: return
        
        if self.selected_names:
            self.profiles[name] = list(self.selected_names)
            with open(CONFIG_FILE, 'w') as f: json.dump(self.profiles, f, indent=4)
            self.profile_box['values'] = list(self.profiles.keys())
            self.profile_var.set(name)
            self.log(f"Saved: {name}", "SUCCESS")

    def clear_profile_filter(self):
        self.active_profile_name = None
        self.profile_filter = None
        self.active_profile_label.config(text="Active Profile: None")
        self.filter_list()

    def import_profiles(self):
        path = filedialog.askopenfilename(title="Import Profiles", filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.profiles.update(data)
                with open(CONFIG_FILE, 'w') as f: json.dump(self.profiles, f, indent=4)
                self.profile_box['values'] = list(self.profiles.keys())
                self.log("Profiles imported", "SUCCESS")
            else:
                self.log("Invalid profile file format", "ERROR")
        except Exception as e:
            self.log(f"Import failed: {str(e)}", "ERROR")

    def export_profiles(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Export Profiles")
        if not path:
            return
        try:
            with open(path, 'w') as f:
                json.dump(self.profiles, f, indent=4)
            self.log("Profiles exported", "SUCCESS")
        except Exception as e:
            self.log(f"Export failed: {str(e)}", "ERROR")

    def run_action(self, action):
        if not self.selected_names:
            self.log("No selection!", "WARN")
            return
        
        if action == "stop":
            confirm = messagebox.askyesno("Confirm Stop", 
                                         f"Stop {len(self.selected_names)} selected services?")
            if not confirm: return
        
        threading.Thread(target=self._execute, args=(list(self.selected_names), action), daemon=True).start()

    def _execute(self, names, action):
        success, fail = 0, 0
        self.log(f"Executing {action.upper()}...", "INFO")
        error_map = {
            5: "Access is denied",
            1056: "Already running",
            1060: "Service not installed",
            1061: "Cannot accept control",
            1062: "Already stopped",
            1068: "Dependency service not started",
            1072: "Service marked for deletion"
        }
        for name in names:
            try:
                cmd = []
                if action == "start": cmd = ["sc", "start", name]
                elif action == "stop": cmd = ["sc", "stop", name]
                elif action == "pause": cmd = ["sc", "pause", name]
                elif action == "resume": cmd = ["sc", "continue", name]
                elif action == "manual": cmd = ["sc", "config", name, "start=", "demand"]
                elif action == "auto": cmd = ["sc", "config", name, "start=", "auto"]
                elif action == "delayed": cmd = ["sc", "config", name, "start=", "delayed-auto"]
                elif action == "disabled": cmd = ["sc", "config", name, "start=", "disabled"]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    success += 1
                elif action == "stop" and result.returncode == 1062:
                    self.log(f"{name} is already stopped", "INFO")
                    success += 1
                elif action == "start" and result.returncode == 1056:
                    self.log(f"{name} is already running", "INFO")
                    success += 1
                else:
                    details = result.stderr.strip() or result.stdout.strip()
                    mapped = error_map.get(result.returncode)
                    if mapped and not details:
                        details = mapped
                    if details:
                        self.log(f"Failed {name}: {details} (exit code {result.returncode})", "ERROR")
                    else:
                        self.log(f"Failed {name}: exit code {result.returncode}", "ERROR")
                    fail += 1
            except Exception as e:
                fail += 1
                self.log(f"Critical error {name}: {str(e)}", "ERROR")
        
        self.log(f"Done: {success} OK, {fail} Failed", "SUCCESS" if fail == 0 else "WARN")
        # Give Windows a moment to update service status before refreshing
        self.after(1000, self.refresh_data)
        self.after(3000, self.refresh_data)

if __name__ == "__main__":
    app = ServiceStopperUltra()
    app.mainloop()
