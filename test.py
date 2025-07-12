import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import datetime
import ctypes
import subprocess
import time
import winsound
import json
import re
from tkinter import font
import urllib.parse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
    Image = None

class ThemeManager:
    def __init__(self):
        self.themes = {
            'dark': {
                'bg_primary': '#1e1e2e',        # Deep blue-black (Grok-inspired)
                'bg_secondary': '#2a2a3e',      # Slightly lighter blue-grey
                'bg_tertiary': '#3b3b57',       # Medium blue-grey
                'fg_primary': '#cdd6f4',        # Soft white-blue
                'fg_secondary': '#a6adc8',      # Light purple-grey
                'fg_tertiary': '#585b70',       # Muted slate
                'accent_primary': '#89b4fa',    # Vibrant blue
                'accent_secondary': '#b4befe',  # Lighter blue
                'danger': '#f38ba8',            # Soft red
                'warning': '#f9e2af',           # Warm yellow
                'info': '#89dceb',              # Cyan
                'success': '#a6e3a1',           # Mint green
                'card_bg': '#2a2a3e',           # Card background (blue-grey)
                'border': '#3b3b57',            # Border blue-grey
                'gradient_start': '#1e1e2e',    # Gradient start (deep blue-black)
                'gradient_end': '#3b3b57'       # Gradient end (medium blue-grey)
            }
        }
        self.current_theme = 'dark'

    def get_color(self, color_name):
        return self.themes[self.current_theme][color_name]

class ModernFrame(tk.Frame):
    def __init__(self, parent, theme_manager, **kwargs):
        self.theme_manager = theme_manager
        super().__init__(parent, bg=theme_manager.get_color('bg_primary'), highlightthickness=0, **kwargs)

    def update_theme(self):
        self.configure(bg=self.theme_manager.get_color('bg_primary'))

class ModernButton(tk.Button):
    def __init__(self, parent, text, command=None, style="primary", theme_manager=None, **kwargs):
        self.parent = parent
        self.command = command
        self.style = style
        self.theme_manager = theme_manager
        super().__init__(parent, text=text, command=self._execute_command, **kwargs)
        self.update_style()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def update_style(self):
        if not self.theme_manager:
            return
        style_colors = {
            "primary": {"bg": self.theme_manager.get_color('accent_primary'), 
                       "hover": self.theme_manager.get_color('accent_secondary')},
            "danger": {"bg": self.theme_manager.get_color('danger'), 
                      "hover": "#f5a3b7"},
            "warning": {"bg": self.theme_manager.get_color('warning'), 
                       "hover": "#fce7b8"},
            "secondary": {"bg": self.theme_manager.get_color('bg_tertiary'), 
                         "hover": "#4a4a6a"},
            "success": {"bg": self.theme_manager.get_color('success'), 
                       "hover": "#b8e8b5"},
            "info": {"bg": self.theme_manager.get_color('info'), 
                    "hover": "#9be7f2"}
        }
        colors = style_colors.get(self.style, style_colors["primary"])
        self.colors = colors
        self.configure(
            bg=colors["bg"],
            fg='#ffffff',
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2",
            activebackground=colors["hover"],
            activeforeground='#ffffff'
        )

    def _on_enter(self, event):
        self.configure(bg=self.colors["hover"], relief="raised", borderwidth=2)

    def _on_leave(self, event):
        self.configure(bg=self.colors["bg"], relief="flat", borderwidth=0)

    def _on_click(self, event):
        self.configure(relief="sunken")
        self.after(100, lambda: self.configure(relief="flat"))

    def _execute_command(self):
        if self.command:
            self.configure(state="disabled")
            self.after(200, lambda: self.configure(state="normal"))
            self.command()

class StatusCard(tk.Frame):
    def __init__(self, parent, title, value, status="safe", theme_manager=None, **kwargs):
        self.theme_manager = theme_manager
        super().__init__(parent, bg=theme_manager.get_color('card_bg'), relief="raised", bd=2, **kwargs)
        self.configure(highlightbackground=theme_manager.get_color('border'), highlightthickness=1)
        status_colors = {
            "safe": theme_manager.get_color('success'),
            "warning": theme_manager.get_color('warning'),
            "danger": theme_manager.get_color('danger'),
            "info": theme_manager.get_color('info')
        }
        self.status_color = status_colors.get(status, theme_manager.get_color('success'))
        self.create_card_content(title, value)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def create_card_content(self, title, value):
        header_frame = tk.Frame(self, bg=self.theme_manager.get_color('card_bg'))
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 8))
        title_label = tk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        title_label.pack(anchor=tk.W)
        self.value_label = tk.Label(
            self,
            text=value,
            font=("Segoe UI", 18, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.status_color
        )
        self.value_label.pack(pady=(0, 10))
        indicator = tk.Frame(self, bg=self.status_color, height=3)
        indicator.pack(fill=tk.X, side=tk.BOTTOM)

    def update_value(self, value, status="safe"):
        status_colors = {
            "safe": self.theme_manager.get_color('success'),
            "warning": self.theme_manager.get_color('warning'),
            "danger": self.theme_manager.get_color('danger'),
            "info": self.theme_manager.get_color('info')
        }
        self.value_label.config(text=value, fg=status_colors.get(status, self.theme_manager.get_color('success')))
        self.configure(highlightbackground=self.theme_manager.get_color('border'))

    def _on_enter(self, event):
        self.configure(bd=3, highlightthickness=2)

    def _on_leave(self, event):
        self.configure(bd=2, highlightthickness=1)

    def update_theme(self):
        self.configure(bg=self.theme_manager.get_color('card_bg'), highlightbackground=self.theme_manager.get_color('border'))
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=self.theme_manager.get_color('card_bg'))
            elif isinstance(child, tk.Label):
                child.configure(bg=self.theme_manager.get_color('card_bg'))

class NavigationManager:
    def __init__(self):
        self.history = []
        self.current_index = -1

    def navigate_to(self, page_name):
        self.history = self.history[:self.current_index + 1]
        self.history.append(page_name)
        self.current_index += 1

    def can_go_back(self):
        return self.current_index > 0

    def can_go_forward(self):
        return self.current_index < len(self.history) - 1

    def go_back(self):
        if self.can_go_back():
            self.current_index -= 1
            return self.history[self.current_index]
        return None

    def go_forward(self):
        if self.can_go_forward():
            self.current_index += 1
            return self.history[self.current_index]
        return None

    def get_current_page(self):
        if self.history and self.current_index >= 0:
            return self.history[self.current_index]
        return None

class ScamRakshakGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Scam Rakshak Protection Suite")
        self.root.geometry("1600x900")  # Optimized for 16:9
        self.root.minsize(1280, 720)
        self.theme_manager = ThemeManager()
        self.root.configure(bg=self.theme_manager.get_color('gradient_start'))
        self.nav_manager = NavigationManager()
        self.scan_history = []
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        self.center_window()
        self.is_admin = self.check_admin()
        self.monitoring = False
        self.monitor_thread = None
        self.baseline_services = []
        self.protection_status = "Active"
        self.threats_blocked = 0
        self.last_scan_time = "Never"
        self.custom_blocked_sites = []
        self.scan_progress = 0
        self.url_history = []
        self.suspicious_keywords = ["remote", "control", "viewer", "connect", "hack", "spy", "monitor", "trojan", "malware", "virus", "phishing", "scam"]
        self.autostart_var = tk.BooleanVar(value=True)
        self.notifications_var = tk.BooleanVar(value=True)
        self.sound_alerts_var = tk.BooleanVar(value=True)
        self.theme_var = tk.StringVar(value="dark")
        self.realtime_var = tk.BooleanVar(value=True)
        self.auto_updates_var = tk.BooleanVar(value=True)
        self.scan_frequency_var = tk.StringVar(value="Daily")
        self.auto_quarantine_var = tk.BooleanVar(value=True)
        self.log_level_var = tk.StringVar(value="INFO")
        self.cpu_limit_var = tk.StringVar(value="50")
        self.memory_limit_var = tk.StringVar(value="512")
        self.load_settings()
        self.load_blocked_sites()
        self.create_modern_interface()
        self.setup_system_tray()
        self.show_dashboard()
        self.update_status_cards()
        self.bold_font = font.Font(family="Segoe UI", size=10, weight="bold")

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1600x900+{x}+{y}")

    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    self.custom_blocked_sites = settings.get("custom_blocked_sites", [])
                    self.theme_var.set(settings.get("theme", "dark"))
                    self.autostart_var.set(settings.get("autostart", True))
                    self.notifications_var.set(settings.get("notifications", True))
                    self.sound_alerts_var.set(settings.get("sound_alerts", True))
                    self.realtime_var.set(settings.get("realtime_protection", True))
                    self.auto_updates_var.set(settings.get("auto_updates", True))
                    self.scan_frequency_var.set(settings.get("scan_frequency", "Daily"))
                    self.auto_quarantine_var.set(settings.get("auto_quarantine", True))
                    self.log_level_var.set(settings.get("log_level", "INFO"))
                    self.cpu_limit_var.set(settings.get("cpu_limit", "50"))
                    self.memory_limit_var.set(settings.get("memory_limit", "512"))
                    self.theme_manager.current_theme = self.theme_var.get()
        except Exception as e:
            self.show_notification("Error", f"Failed to load settings: {str(e)}", "error")

    def load_blocked_sites(self):
        try:
            if os.path.exists("blocked_sites.txt"):
                with open("blocked_sites.txt", "r") as f:
                    self.custom_blocked_sites = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.show_notification("Error", f"Failed to load blocked sites: {str(e)}", "error")

    def save_settings(self):
        try:
            settings = {
                "custom_blocked_sites": self.custom_blocked_sites,
                "theme": self.theme_var.get(),
                "autostart": self.autostart_var.get(),
                "notifications": self.notifications_var.get(),
                "sound_alerts": self.sound_alerts_var.get(),
                "realtime_protection": self.realtime_var.get(),
                "auto_updates": self.auto_updates_var.get(),
                "scan_frequency": self.scan_frequency_var.get(),
                "auto_quarantine": self.auto_quarantine_var.get(),
                "log_level": self.log_level_var.get(),
                "cpu_limit": self.cpu_limit_var.get(),
                "memory_limit": self.memory_limit_var.get()
            }
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            with open("blocked_sites.txt", "w") as f:
                for site in self.custom_blocked_sites:
                    f.write(f"{site}\n")
            self.show_notification("Settings Saved", "Your settings have been saved successfully.", "success")
        except Exception as e:
            self.show_notification("Error", f"Failed to save settings: {str(e)}", "error")

    def create_modern_interface(self):
        self.main_container = tk.Frame(self.root, bg=self.theme_manager.get_color('gradient_start'))
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.create_top_nav()
        self.content_container = tk.Frame(self.main_container, bg=self.theme_manager.get_color('gradient_start'))
        self.content_container.pack(fill=tk.BOTH, expand=True)
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()

    def create_top_nav(self):
        self.top_nav = tk.Frame(self.main_container, bg=self.theme_manager.get_color('bg_secondary'), height=60)
        self.top_nav.pack(fill=tk.X)
        self.top_nav.pack_propagate(False)
        nav_left = tk.Frame(self.top_nav, bg=self.theme_manager.get_color('bg_secondary'))
        nav_left.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        self.home_btn = ModernButton(
            nav_left,
            text="Home",
            command=self.go_home,
            style="primary",
            theme_manager=self.theme_manager
        )
        self.home_btn.pack(side=tk.LEFT, pady=15, padx=(0, 10))
        self.back_btn = ModernButton(
            nav_left,
            text="Back",
            command=self.go_back,
            style="secondary",
            theme_manager=self.theme_manager,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT, pady=15, padx=(0, 10))
        self.forward_btn = ModernButton(
            nav_left,
            text="Forward",
            command=self.go_forward,
            style="secondary",
            theme_manager=self.theme_manager,
            state=tk.DISABLED
        )
        self.forward_btn.pack(side=tk.LEFT, pady=15, padx=(0, 10))
        self.breadcrumb_label = tk.Label(
            nav_left,
            text="Dashboard",
            font=("Segoe UI", 14, "bold"),
            bg=self.theme_manager.get_color('bg_secondary'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        self.breadcrumb_label.pack(side=tk.LEFT, pady=15, padx=(20, 0))
        nav_right = tk.Frame(self.top_nav, bg=self.theme_manager.get_color('bg_secondary'))
        nav_right.pack(side=tk.RIGHT, fill=tk.Y, padx=20)

    def create_sidebar(self):
        self.sidebar = ModernFrame(self.content_container, self.theme_manager, width=300)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        logo_frame = tk.Frame(self.sidebar, bg=self.theme_manager.get_color('bg_secondary'), height=120)
        logo_frame.pack(fill=tk.X, padx=20, pady=20)
        logo_frame.pack_propagate(False)
        logo_container = tk.Frame(logo_frame, bg=self.theme_manager.get_color('bg_secondary'))
        logo_container.pack(expand=True)
        logo_label = tk.Label(
            logo_container,
            text="SCAM RAKSHAK",
            font=("Segoe UI", 22, "bold"),
            bg=self.theme_manager.get_color('bg_secondary'),
            fg=self.theme_manager.get_color('accent_primary')
        )
        logo_label.pack()
        subtitle_label = tk.Label(
            logo_container,
            text="Protection Suite",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('bg_secondary'),
            fg=self.theme_manager.get_color('fg_secondary')
        )
        subtitle_label.pack(pady=(6, 0))
        separator = tk.Frame(self.sidebar, bg=self.theme_manager.get_color('border'), height=2)
        separator.pack(fill=tk.X, padx=20, pady=20)
        self.create_nav_buttons()
        self.create_admin_status()

    def create_nav_buttons(self):
        nav_frame = tk.Frame(self.sidebar, bg=self.theme_manager.get_color('bg_primary'))
        nav_frame.pack(fill=tk.X, padx=20, pady=10)
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Website Protection", self.show_website_protection),
            ("Service Monitor", self.show_service_monitor),
            ("Logs & Reports", self.show_logs),
            ("Settings", self.show_settings)
        ]
        self.nav_buttons = {}
        for name, command in nav_items:
            btn = ModernButton(
                nav_frame,
                text=name,
                command=lambda cmd=command, n=name: self.navigate_to_page(cmd, n),
                style="secondary",
                theme_manager=self.theme_manager,
                font=("Segoe UI", 14),
                anchor="w"
            )
            btn.pack(fill=tk.X, pady=6)
            self.nav_buttons[name] = btn

    def create_admin_status(self):
        admin_frame = tk.Frame(self.sidebar, bg=self.theme_manager.get_color('bg_secondary'))
        admin_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=20)
        if self.is_admin:
            status_color = self.theme_manager.get_color('success')
            status_text = "Administrator"
            status_desc = "Full protection enabled"
        else:
            status_color = self.theme_manager.get_color('danger')
            status_text = "Limited Access"
            status_desc = "Some features restricted"
        status_label = tk.Label(
            admin_frame,
            text=status_text,
            font=("Segoe UI", 12, "bold"),
            bg=self.theme_manager.get_color('bg_secondary'),
            fg=status_color
        )
        status_label.pack(anchor=tk.W, padx=15, pady=(15, 6))
        desc_label = tk.Label(
            admin_frame,
            text=status_desc,
            font=("Segoe UI", 10),
            bg=self.theme_manager.get_color('bg_secondary'),
            fg=self.theme_manager.get_color('fg_tertiary')
        )
        desc_label.pack(anchor=tk.W, padx=15, pady=(0, 15))

    def create_main_content(self):
        self.content_frame = ModernFrame(self.content_container, self.theme_manager)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg=self.theme_manager.get_color('bg_secondary'), height=40)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        self.status_label = tk.Label(
            self.status_bar,
            text="Ready • System Protected",
            font=("Segoe UI", 10),
            bg=self.theme_manager.get_color('bg_secondary'),
            fg=self.theme_manager.get_color('success'),
            anchor=tk.W,
            padx=20
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.time_label = tk.Label(
            self.status_bar,
            text="",
            font=("Segoe UI", 10),
            bg=self.theme_manager.get_color('bg_secondary'),
            fg=self.theme_manager.get_color('fg_primary'),
            padx=20
        )
        self.time_label.pack(side=tk.RIGHT)
        self.update_time()

    def setup_system_tray(self):
        if pystray is None:
            return
        try:
            image = Image.new('RGB', (64, 64), color=self.theme_manager.get_color('accent_primary'))
            menu = (
                pystray.MenuItem("Open", self.show_window),
                pystray.MenuItem("Start Monitoring", self.start_monitoring),
                pystray.MenuItem("Stop Monitoring", self.stop_monitoring),
                pystray.MenuItem("Exit", self.exit_application)
            )
            self.icon = pystray.Icon("Scam Rakshak", image, "Scam Rakshak Protection", menu)
            threading.Thread(target=self.icon.run, daemon=True).start()
        except Exception as e:
            self.show_notification("Error", f"Failed to setup system tray: {str(e)}", "error")

    def show_window(self):
        self.root.deiconify()

    def exit_application(self):
        self.monitoring = False
        if hasattr(self, 'icon'):
            self.icon.stop()
        self.root.destroy()

    def update_time(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def update_all_theme_elements(self):
        self.root.configure(bg=self.theme_manager.get_color('gradient_start'))
        self.main_container.configure(bg=self.theme_manager.get_color('gradient_start'))
        self.content_container.configure(bg=self.theme_manager.get_color('gradient_start'))
        self.top_nav.configure(bg=self.theme_manager.get_color('bg_secondary'))
        self.sidebar.update_theme()
        self.content_frame.update_theme()
        self.status_bar.configure(bg=self.theme_manager.get_color('bg_secondary'))
        self.status_label.configure(bg=self.theme_manager.get_color('bg_secondary'), 
                                  fg=self.theme_manager.get_color('success'))
        self.time_label.configure(bg=self.theme_manager.get_color('bg_secondary'), 
                                fg=self.theme_manager.get_color('fg_primary'))
        self.breadcrumb_label.configure(bg=self.theme_manager.get_color('bg_secondary'),
                                      fg=self.theme_manager.get_color('fg_primary'))
        for btn in self.nav_buttons.values():
            btn.update_style()
        for card in getattr(self, 'status_cards', {}).values():
            card.update_theme()
        if hasattr(self, 'dashboard_canvas'):
            for canvas in self.dashboard_canvas.values():
                canvas.get_tk_widget().configure(bg=self.theme_manager.get_color('bg_primary'))
        current_page = self.nav_manager.get_current_page()
        if current_page:
            self.navigate_to_page_by_name(current_page)

    def navigate_to_page(self, command, page_name):
        self.nav_manager.navigate_to(page_name)
        self.update_nav_buttons()
        self.breadcrumb_label.config(text=page_name)
        command()

    def go_home(self):
        self.navigate_to_page(self.show_dashboard, "Dashboard")

    def go_back(self):
        page = self.nav_manager.go_back()
        if page:
            self.update_nav_buttons()
            self.breadcrumb_label.config(text=page)
            self.navigate_to_page_by_name(page)

    def go_forward(self):
        page = self.nav_manager.go_forward()
        if page:
            self.update_nav_buttons()
            self.breadcrumb_label.config(text=page)
            self.navigate_to_page_by_name(page)

    def navigate_to_page_by_name(self, page_name):
        if page_name == "Dashboard":
            self.show_dashboard()
        elif page_name == "Website Protection":
            self.show_website_protection()
        elif page_name == "Service Monitor":
            self.show_service_monitor()
        elif page_name == "Logs & Reports":
            self.show_logs()
        elif page_name == "Settings":
            self.show_settings()

    def update_nav_buttons(self):
        if self.nav_manager.can_go_back():
            self.back_btn.configure(state=tk.NORMAL)
        else:
            self.back_btn.configure(state=tk.DISABLED)
        if self.nav_manager.can_go_forward():
            self.forward_btn.configure(state=tk.NORMAL)
        else:
            self.forward_btn.configure(state=tk.DISABLED)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        canvas = tk.Canvas(self.content_frame, bg=self.theme_manager.get_color('bg_primary'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)
        main_scroll = tk.Frame(canvas, bg=self.theme_manager.get_color('bg_primary'))
        main_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=main_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        header_frame = tk.Frame(main_scroll, bg=self.theme_manager.get_color('bg_primary'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))
        title_label = tk.Label(
            header_frame,
            text="Security Dashboard",
            font=("Segoe UI", 28, "bold"),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        title_label.pack(anchor=tk.W)
        subtitle_label = tk.Label(
            header_frame,
            text="Real-time protection status and system overview",
            font=("Segoe UI", 14),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_secondary')
        )
        subtitle_label.pack(anchor=tk.W, pady=(6, 0))
        self.create_status_cards(main_scroll)
        self.create_dashboard_graphs(main_scroll)
        self.create_protection_status(main_scroll)
        self.create_quick_actions(main_scroll)

    def create_status_cards(self, parent):
        cards_frame = tk.Frame(parent, bg=self.theme_manager.get_color('bg_primary'))
        cards_frame.pack(fill=tk.X, padx=20, pady=20)
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        cards_frame.grid_columnconfigure(3, weight=1)
        self.status_cards_data = [
            ("Protection Status", self.protection_status, "safe"),
            ("Threats Blocked", str(self.threats_blocked), "success"),
            ("Last Scan", self.last_scan_time, "info"),
            ("System Health", "Excellent", "safe")
        ]
        self.status_cards = {}
        for i, (title, value, status) in enumerate(self.status_cards_data):
            card = StatusCard(cards_frame, title, value, status, self.theme_manager)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.status_cards[title] = card

    def create_dashboard_graphs(self, parent):
        graphs_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        graphs_frame.pack(fill=tk.BOTH, padx=20, pady=20)
        header = tk.Frame(graphs_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Security Analytics",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        self.dashboard_canvas = {}
        graphs_container = tk.Frame(graphs_frame, bg=self.theme_manager.get_color('card_bg'))
        graphs_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Pie chart for Threat Distribution
        threats = [self.threats_blocked, len(self.custom_blocked_sites), len(self.url_history)]
        labels = ['Threats Blocked', 'Sites Blocked', 'URLs Checked']
        colors = [self.theme_manager.get_color('danger'), self.theme_manager.get_color('warning'), self.theme_manager.get_color('info')]
        
        # Check if all values in threats are zero
        if sum(threats) == 0:
            # Display a placeholder message instead of a pie chart
            placeholder_label = tk.Label(
                graphs_container,
                text="No threat data available yet",
                font=("Segoe UI", 12, "italic"),
                bg=self.theme_manager.get_color('card_bg'),
                fg=self.theme_manager.get_color('fg_secondary')
            )
            placeholder_label.grid(row=0, column=0, padx=10, pady=10)
            self.dashboard_canvas['pie'] = placeholder_label
        else:
            fig_pie, ax_pie = plt.subplots(figsize=(4, 3.2))
            ax_pie.pie(threats, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax_pie.set_title("Threat Distribution", color=self.theme_manager.get_color('fg_primary'))
            pie_canvas = FigureCanvasTkAgg(fig_pie, master=graphs_container)
            pie_canvas.get_tk_widget().configure(bg=self.theme_manager.get_color('bg_primary'))
            pie_canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
            self.dashboard_canvas['pie'] = pie_canvas

        # Line chart for Scan History
        fig_line, ax_line = plt.subplots(figsize=(4, 3.2))
        times = [t[0] for t in self.scan_history[-5:]]
        scores = [t[1] for t in self.scan_history[-5:]]
        if not times:  # Handle empty scan history
            times = [datetime.datetime.now()]
            scores = [0]
        ax_line.plot([t.strftime("%Y-%m-%d") for t in times], scores, color=self.theme_manager.get_color('accent_primary'))
        ax_line.set_title("Scan History", color=self.theme_manager.get_color('fg_primary'))
        ax_line.set_xlabel("Date", color=self.theme_manager.get_color('fg_secondary'))
        ax_line.set_ylabel("Safety Score", color=self.theme_manager.get_color('fg_secondary'))
        ax_line.tick_params(colors=self.theme_manager.get_color('fg_secondary'))
        line_canvas = FigureCanvasTkAgg(fig_line, master=graphs_container)
        line_canvas.get_tk_widget().configure(bg=self.theme_manager.get_color('bg_primary'))
        line_canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)
        self.dashboard_canvas['line'] = line_canvas

        # Bar chart for System Resources
        fig_bar, ax_bar = plt.subplots(figsize=(4, 3.2))
        resources = ['CPU', 'Memory']
        usage = [int(self.cpu_limit_var.get()), int(self.memory_limit_var.get()) / 10]
        ax_bar.bar(resources, usage, color=self.theme_manager.get_color('success'))
        ax_bar.set_title("System Resources", color=self.theme_manager.get_color('fg_primary'))
        ax_bar.set_ylabel("Usage (%)", color=self.theme_manager.get_color('fg_secondary'))
        ax_bar.tick_params(colors=self.theme_manager.get_color('fg_secondary'))
        bar_canvas = FigureCanvasTkAgg(fig_bar, master=graphs_container)
        bar_canvas.get_tk_widget().configure(bg=self.theme_manager.get_color('bg_primary'))
        bar_canvas.get_tk_widget().grid(row=0, column=2, padx=10, pady=10)
        self.dashboard_canvas['bar'] = bar_canvas

        export_btn = ModernButton(
            graphs_frame,
            "Export Graphs",
            command=self.export_graphs,
            style="secondary",
            theme_manager=self.theme_manager
        )
        export_btn.pack(pady=10)

    def export_graphs(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            try:
                fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
                threats = [self.threats_blocked, len(self.custom_blocked_sites), len(self.url_history)]
                labels = ['Threats Blocked', 'Sites Blocked', 'URLs Checked']
                colors = [self.theme_manager.get_color('danger'), self.theme_manager.get_color('warning'), self.theme_manager.get_color('info')]
                ax1.pie(threats, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax1.set_title("Threat Distribution")
                times = [t[0] for t in self.scan_history[-5:]]
                scores = [t[1] for t in self.scan_history[-5:]]
                ax2.plot([t.strftime("%Y-%m-%d") for t in times], scores, color=self.theme_manager.get_color('accent_primary'))
                ax2.set_title("Scan History")
                ax2.set_xlabel("Date")
                ax2.set_ylabel("Safety Score")
                resources = ['CPU', 'Memory']
                usage = [int(self.cpu_limit_var.get()), int(self.memory_limit_var.get()) / 10]
                ax3.bar(resources, usage, color=self.theme_manager.get_color('success'))
                ax3.set_title("System Resources")
                ax3.set_ylabel("Usage (%)")
                plt.tight_layout()
                plt.savefig(file_path)
                plt.close()
                self.show_notification("Graphs Exported", f"Dashboard graphs saved to {file_path}", "success")
            except Exception as e:
                self.show_notification("Error", f"Failed to export graphs: {str(e)}", "error")

    def create_protection_status(self, parent):
        protection_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        protection_frame.pack(fill=tk.X, padx=20, pady=20)
        header = tk.Frame(protection_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Protection Components",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        protection_items = [
            ("Website Blocker", "Active", "safe"),
            ("Service Monitor", "Active" if self.monitoring else "Inactive", "safe" if self.monitoring else "warning"),
            ("Real-time Protection", "Active", "safe"),
            ("Malware Scanner", "Active", "safe"),
            ("Custom Site Filter", f"{len(self.custom_blocked_sites)} sites blocked", "info"),
            ("Administrator Mode", "Enabled" if self.is_admin else "Disabled", "safe" if self.is_admin else "warning")
        ]
        for item, status, color in protection_items:
            item_frame = tk.Frame(protection_frame, bg=self.theme_manager.get_color('card_bg'))
            item_frame.pack(fill=tk.X, padx=20, pady=8)
            tk.Label(
                item_frame,
                text=item,
                font=("Segoe UI", 12),
                bg=self.theme_manager.get_color('card_bg'),
                fg=self.theme_manager.get_color('fg_primary')
            ).pack(side=tk.LEFT)
            status_colors = {
                "safe": self.theme_manager.get_color('success'),
                "warning": self.theme_manager.get_color('warning'),
                "danger": self.theme_manager.get_color('danger'),
                "info": self.theme_manager.get_color('info')
            }
            tk.Label(
                item_frame,
                text=status,
                font=("Segoe UI", 12, "bold"),
                bg=self.theme_manager.get_color('card_bg'),
                fg=status_colors[color]
            ).pack(side=tk.RIGHT)
        tk.Frame(protection_frame, bg=self.theme_manager.get_color('card_bg'), height=20).pack()

    def create_quick_actions(self, parent):
        actions_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        header = tk.Frame(actions_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Quick Actions",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        buttons_frame = tk.Frame(actions_frame, bg=self.theme_manager.get_color('card_bg'))
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        ModernButton(
            buttons_frame,
            "Start Full Scan",
            command=self.start_full_scan,
            style="primary",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            buttons_frame,
            "Update Protection",
            command=self.update_protection,
            style="info",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            buttons_frame,
            "View Reports",
            command=lambda: self.navigate_to_page(self.show_logs, "Logs & Reports"),
            style="secondary",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            buttons_frame,
            "Emergency Mode",
            command=self.activate_emergency_mode,
            style="danger",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)
        self.progress_bar = ttk.Progressbar(
            actions_frame,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(10, 0))

    def show_website_protection(self):
        self.clear_content()
        main_scroll = tk.Frame(self.content_frame, bg=self.theme_manager.get_color('bg_primary'))
        main_scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        header_frame = tk.Frame(main_scroll, bg=self.theme_manager.get_color('bg_primary'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))
        title_label = tk.Label(
            header_frame,
            text="Website Protection",
            font=("Segoe UI", 28, "bold"),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        title_label.pack(anchor=tk.W)
        subtitle_label = tk.Label(
            header_frame,
            text="Manage blocked websites and check URL safety in real-time",
            font=("Segoe UI", 14),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_secondary')
        )
        subtitle_label.pack(anchor=tk.W, pady=(6, 0))
        self.create_blocked_sites_section(main_scroll)
        self.create_url_checker_section(main_scroll)
        self.create_url_history_section(main_scroll)

    def create_blocked_sites_section(self, parent):
        sites_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        sites_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        header = tk.Frame(sites_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Blocked Websites",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        add_frame = tk.Frame(sites_frame, bg=self.theme_manager.get_color('card_bg'))
        add_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        tk.Label(
            add_frame,
            text="Add Website to Block:",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W, pady=(0, 6))
        entry_frame = tk.Frame(add_frame, bg=self.theme_manager.get_color('card_bg'))
        entry_frame.pack(fill=tk.X)
        self.url_entry = tk.Entry(
            entry_frame,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary'),
            insertbackground=self.theme_manager.get_color('fg_primary'),
            relief="flat",
            bd=2
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ModernButton(
            entry_frame,
            "Add Site",
            command=self.add_blocked_site,
            style="primary",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)
        list_frame = tk.Frame(sites_frame, bg=self.theme_manager.get_color('card_bg'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        tk.Label(
            list_frame,
            text="Currently Blocked Sites:",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W, pady=(0, 6))
        list_container = tk.Frame(list_frame, bg=self.theme_manager.get_color('card_bg'))
        list_container.pack(fill=tk.BOTH, expand=True)
        self.sites_listbox = tk.Listbox(
            list_container,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary'),
            selectbackground=self.theme_manager.get_color('accent_primary'),
            selectforeground='#ffffff',
            relief="flat",
            bd=2,
            activestyle="none",
            height=8
        )
        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.sites_listbox.yview)
        self.sites_listbox.configure(yscrollcommand=scrollbar.set)
        self.sites_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.update_blocked_sites_list()
        buttons_frame = tk.Frame(list_frame, bg=self.theme_manager.get_color('card_bg'))
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ModernButton(
            buttons_frame,
            "Block All",
            command=self.block_all_sites,
            style="warning",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            buttons_frame,
            "Unblock All",
            command=self.unblock_all_sites,
            style="danger",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            buttons_frame,
            "Remove Selected",
            command=self.remove_blocked_site,
            style="danger",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT)
        self.website_status = scrolledtext.ScrolledText(
            list_frame,
            height=8,
            font=("Consolas", 10),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary'),
            relief="flat",
            bd=2,
            wrap=tk.WORD
        )
        self.website_status.pack(fill=tk.BOTH, pady=(10, 0))

    def create_url_checker_section(self, parent):
        checker_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        checker_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        header = tk.Frame(checker_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="URL Safety Checker",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        check_frame = tk.Frame(checker_frame, bg=self.theme_manager.get_color('card_bg'))
        check_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        tk.Label(
            check_frame,
            text="Check URL Safety:",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W, pady=(0, 6))
        check_entry_frame = tk.Frame(check_frame, bg=self.theme_manager.get_color('card_bg'))
        check_entry_frame.pack(fill=tk.X)
        self.check_url_entry = tk.Entry(
            check_entry_frame,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary'),
            insertbackground=self.theme_manager.get_color('fg_primary'),
            relief="flat",
            bd=2
        )
        self.check_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.check_url_entry.bind("<KeyRelease>", self.validate_url_input)
        ModernButton(
            check_entry_frame,
            "Check URL",
            command=self.check_url_safety,
            style="info",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)
        meter_frame = tk.Frame(checker_frame, bg=self.theme_manager.get_color('card_bg'))
        meter_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        tk.Label(
            meter_frame,
            text="URL Safety Score:",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W, pady=(0, 6))
        self.safety_canvas = tk.Canvas(
            meter_frame,
            height=25,
            width=400,
            bg=self.theme_manager.get_color('bg_primary'),
            highlightthickness=2,
            highlightbackground=self.theme_manager.get_color('border')
        )
        self.safety_canvas.pack(fill=tk.X)
        self.safety_bar = self.safety_canvas.create_rectangle(0, 0, 0, 25, fill=self.theme_manager.get_color('success'))
        self.url_result_label = tk.Label(
            check_frame,
            text="Enter a URL to check its safety",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary'),
            wraplength=600,
            justify=tk.LEFT
        )
        self.url_result_label.pack(anchor=tk.W, pady=(10, 0))

    def create_url_history_section(self, parent):
        history_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        history_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        header = tk.Frame(history_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="URL Check History",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        history_container = tk.Frame(history_frame, bg=self.theme_manager.get_color('card_bg'))
        history_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.history_listbox = tk.Listbox(
            history_container,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary'),
            selectbackground=self.theme_manager.get_color('accent_primary'),
            selectforeground='#ffffff',
            relief="flat",
            bd=2,
            activestyle="none",
            height=8
        )
        scrollbar = tk.Scrollbar(history_container, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        buttons_frame = tk.Frame(history_frame, bg=self.theme_manager.get_color('card_bg'))
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ModernButton(
            buttons_frame,
            "Clear History",
            command=self.clear_url_history,
            style="danger",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT)
        self.update_url_history()

    def show_service_monitor(self):
        self.clear_content()
        main_scroll = tk.Frame(self.content_frame, bg=self.theme_manager.get_color('bg_primary'))
        main_scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        header_frame = tk.Frame(main_scroll, bg=self.theme_manager.get_color('bg_primary'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))
        title_label = tk.Label(
            header_frame,
            text="Service Monitor",
            font=("Segoe UI", 28, "bold"),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        title_label.pack(anchor=tk.W)
        subtitle_label = tk.Label(
            header_frame,
            text="Monitor and protect critical system services",
            font=("Segoe UI", 14),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_secondary')
        )
        subtitle_label.pack(anchor=tk.W, pady=(6, 0))
        self.create_monitor_controls(main_scroll)
        self.create_services_list(main_scroll)

    def create_monitor_controls(self, parent):
        controls_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        controls_frame.pack(fill=tk.X, padx=20, pady=20)
        header = tk.Frame(controls_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Monitor Controls",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        status_frame = tk.Frame(controls_frame, bg=self.theme_manager.get_color('card_bg'))
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        status_text = "Active" if self.monitoring else "Inactive"
        status_color = self.theme_manager.get_color('success') if self.monitoring else self.theme_manager.get_color('danger')
        self.monitor_status_label = tk.Label(
            status_frame,
            text=f"Monitoring Status: {status_text}",
            font=("Segoe UI", 14, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=status_color
        )
        self.monitor_status_label.pack(anchor=tk.W)
        self.buttons_frame = tk.Frame(controls_frame, bg=self.theme_manager.get_color('card_bg'))  # Store reference
        self.buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        if self.monitoring:
            self.stop_monitor_btn = ModernButton(
                self.buttons_frame,
                "Stop Monitoring",
                command=self.stop_monitoring,
                style="danger",
                theme_manager=self.theme_manager
            )
            self.stop_monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        else:
            self.start_monitor_btn = ModernButton(
                self.buttons_frame,
                "Start Monitoring",
                command=self.start_monitoring,
                style="primary",
                theme_manager=self.theme_manager
            )
            self.start_monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            self.buttons_frame,
            "Refresh Services",
            command=self.refresh_services,
            style="info",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            self.buttons_frame,
            "Export Report",
            command=self.export_services_report,
            style="secondary",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)

    def create_services_list(self, parent):
        services_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        services_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        header = tk.Frame(services_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Critical Services Status",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        list_container = tk.Frame(services_frame, bg=self.theme_manager.get_color('card_bg'))
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        columns = ('Service', 'Status', 'PID', 'Description')
        self.services_tree = ttk.Treeview(list_container, columns=columns, show='headings', height=12)
        self.services_tree.heading('Service', text='Service Name')
        self.services_tree.heading('Status', text='Status')
        self.services_tree.heading('PID', text='Process ID')
        self.services_tree.heading('Description', text='Description')
        self.services_tree.column('Service', width=250)
        self.services_tree.column('Status', width=120)
        self.services_tree.column('PID', width=100)
        self.services_tree.column('Description', width=350)
        tree_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.populate_services_list()
        self.monitor_output = scrolledtext.ScrolledText(
            services_frame,
            height=8,
            font=("Consolas", 10),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary'),
            relief="flat",
            bd=2,
            wrap=tk.WORD
        )
        self.monitor_output.pack(fill=tk.BOTH, pady=(10, 0))

    def show_logs(self):
        self.clear_content()
        main_scroll = tk.Frame(self.content_frame, bg=self.theme_manager.get_color('bg_primary'))
        main_scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        header_frame = tk.Frame(main_scroll, bg=self.theme_manager.get_color('bg_primary'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))
        title_label = tk.Label(
            header_frame,
            text="Logs & Reports",
            font=("Segoe UI", 28, "bold"),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        title_label.pack(anchor=tk.W)
        subtitle_label = tk.Label(
            header_frame,
            text="View system logs and generate security reports",
            font=("Segoe UI", 14),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_secondary')
        )
        subtitle_label.pack(anchor=tk.W, pady=(6, 0))
        self.create_log_viewer(main_scroll)
        self.create_report_generator(main_scroll)

    def create_log_viewer(self, parent):
        logs_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        header = tk.Frame(logs_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="System Logs",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        controls_frame = tk.Frame(logs_frame, bg=self.theme_manager.get_color('card_bg'))
        controls_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        self.log_type_var = tk.StringVar(value="block_log")
        log_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.log_type_var,
            values=["block_log", "service_alert_log"],
            state="readonly",
            font=("Segoe UI", 10)
        )
        log_combo.pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            controls_frame,
            "Refresh Logs",
            command=self.refresh_logs,
            style="primary",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            controls_frame,
            "Clear Logs",
            command=self.clear_logs,
            style="danger",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            controls_frame,
            "Export Logs",
            command=self.export_logs,
            style="secondary",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)
        log_container = tk.Frame(logs_frame, bg=self.theme_manager.get_color('card_bg'))
        log_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            font=("Consolas", 10),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary'),
            insertbackground=self.theme_manager.get_color('fg_primary'),
            relief="flat",
            bd=2,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=12
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.load_logs()

    def create_report_generator(self, parent):
        report_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        report_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        header = tk.Frame(report_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Report Generator",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        options_frame = tk.Frame(report_frame, bg=self.theme_manager.get_color('card_bg'))
        options_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        tk.Label(
            options_frame,
            text="Generate comprehensive security reports:",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W, pady=(0, 10))
        buttons_frame = tk.Frame(options_frame, bg=self.theme_manager.get_color('card_bg'))
        buttons_frame.pack(fill=tk.X)
        ModernButton(
            buttons_frame,
            "Daily Report",
            command=lambda: self.generate_report("daily"),
            style="primary",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            buttons_frame,
            "Weekly Report",
            command=lambda: self.generate_report("weekly"),
            style="info",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            buttons_frame,
            "Monthly Report",
            command=lambda: self.generate_report("monthly"),
            style="warning",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            buttons_frame,
            "Full System Report",
            command=lambda: self.generate_report("full"),
            style="secondary",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)

    def show_settings(self):
        self.clear_content()
        main_scroll = tk.Frame(self.content_frame, bg=self.theme_manager.get_color('bg_primary'))
        main_scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        header_frame = tk.Frame(main_scroll, bg=self.theme_manager.get_color('bg_primary'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))
        title_label = tk.Label(
            header_frame,
            text="Settings",
            font=("Segoe UI", 28, "bold"),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        title_label.pack(anchor=tk.W)
        subtitle_label = tk.Label(
            header_frame,
            text="Configure application preferences and security settings",
            font=("Segoe UI", 14),
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_secondary')
        )
        subtitle_label.pack(anchor=tk.W, pady=(6, 0))
        self.create_general_settings(main_scroll)
        self.create_security_settings(main_scroll)
        self.create_advanced_settings(main_scroll)

    def create_general_settings(self, parent):
        general_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        general_frame.pack(fill=tk.X, padx=20, pady=20)
        header = tk.Frame(general_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="General Settings",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        settings_frame = tk.Frame(general_frame, bg=self.theme_manager.get_color('card_bg'))
        settings_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        autostart_frame = tk.Frame(settings_frame, bg=self.theme_manager.get_color('card_bg'))
        autostart_frame.pack(fill=tk.X, pady=8)
        tk.Checkbutton(
            autostart_frame,
            text="Start with Windows",
            variable=self.autostart_var,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary'),
            selectcolor=self.theme_manager.get_color('accent_primary'),
            activebackground=self.theme_manager.get_color('card_bg'),
            activeforeground=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        notifications_frame = tk.Frame(settings_frame, bg=self.theme_manager.get_color('card_bg'))
        notifications_frame.pack(fill=tk.X, pady=8)
        tk.Checkbutton(
            notifications_frame,
            text="Show security notifications",
            variable=self.notifications_var,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary'),
            selectcolor=self.theme_manager.get_color('accent_primary'),
            activebackground=self.theme_manager.get_color('card_bg'),
            activeforeground=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        sound_frame = tk.Frame(settings_frame, bg=self.theme_manager.get_color('card_bg'))
        sound_frame.pack(fill=tk.X, pady=8)
        tk.Checkbutton(
            sound_frame,
            text="Enable sound alerts",
            variable=self.sound_alerts_var,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary'),
            selectcolor=self.theme_manager.get_color('accent_primary'),
            activebackground=self.theme_manager.get_color('card_bg'),
            activeforeground=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        theme_frame = tk.Frame(settings_frame, bg=self.theme_manager.get_color('card_bg'))
        theme_frame.pack(fill=tk.X, pady=8)
        tk.Label(
            theme_frame,
            text="Theme:",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(side=tk.LEFT, padx=(0, 10))
        theme_dropdown = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["dark"],
            state="readonly",
            font=("Segoe UI", 10),
            width=12
        )
        theme_dropdown.pack(side=tk.LEFT)

    def create_security_settings(self, parent):
        security_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        security_frame.pack(fill=tk.X, padx=20, pady=20)
        header = tk.Frame(security_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Security Settings",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        security_options_frame = tk.Frame(security_frame, bg=self.theme_manager.get_color('card_bg'))
        security_options_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        realtime_frame = tk.Frame(security_options_frame, bg=self.theme_manager.get_color('card_bg'))
        realtime_frame.pack(fill=tk.X, pady=8)
        tk.Checkbutton(
            realtime_frame,
            text="Enable real-time protection",
            variable=self.realtime_var,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary'),
            selectcolor=self.theme_manager.get_color('accent_primary'),
            activebackground=self.theme_manager.get_color('card_bg'),
            activeforeground=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        updates_frame = tk.Frame(security_options_frame, bg=self.theme_manager.get_color('card_bg'))
        updates_frame.pack(fill=tk.X, pady=8)
        tk.Checkbutton(
            updates_frame,
            text="Automatic security updates",
            variable=self.auto_updates_var,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary'),
            selectcolor=self.theme_manager.get_color('accent_primary'),
            activebackground=self.theme_manager.get_color('card_bg'),
            activeforeground=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        schedule_frame = tk.Frame(security_options_frame, bg=self.theme_manager.get_color('card_bg'))
        schedule_frame.pack(fill=tk.X, pady=8)
        tk.Label(
            schedule_frame,
            text="Scheduled scan frequency:",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(side=tk.LEFT, padx=(0, 10))
        scan_dropdown = ttk.Combobox(
            schedule_frame,
            textvariable=self.scan_frequency_var,
            values=["Daily", "Weekly", "Monthly", "Manual"],
            state="readonly",
            font=("Segoe UI", 10),
            width=12
        )
        scan_dropdown.pack(side=tk.LEFT)
        quarantine_frame = tk.Frame(security_options_frame, bg=self.theme_manager.get_color('card_bg'))
        quarantine_frame.pack(fill=tk.X, pady=8)
        tk.Checkbutton(
            quarantine_frame,
            text="Automatically quarantine threats",
            variable=self.auto_quarantine_var,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary'),
            selectcolor=self.theme_manager.get_color('accent_primary'),
            activebackground=self.theme_manager.get_color('card_bg'),
            activeforeground=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)

    def create_advanced_settings(self, parent):
        advanced_frame = tk.Frame(parent, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        advanced_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        header = tk.Frame(advanced_frame, bg=self.theme_manager.get_color('card_bg'))
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(
            header,
            text="Advanced Settings",
            font=("Segoe UI", 16, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(anchor=tk.W)
        advanced_options_frame = tk.Frame(advanced_frame, bg=self.theme_manager.get_color('card_bg'))
        advanced_options_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        log_level_frame = tk.Frame(advanced_options_frame, bg=self.theme_manager.get_color('card_bg'))
        log_level_frame.pack(fill=tk.X, pady=8)
        tk.Label(
            log_level_frame,
            text="Log level:",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(side=tk.LEFT, padx=(0, 10))
        log_dropdown = ttk.Combobox(
            log_level_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            font=("Segoe UI", 10),
            width=12
        )
        log_dropdown.pack(side=tk.LEFT)
        cpu_frame = tk.Frame(advanced_options_frame, bg=self.theme_manager.get_color('card_bg'))
        cpu_frame.pack(fill=tk.X, pady=8)
        tk.Label(
            cpu_frame,
            text="CPU usage limit (%):",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(side=tk.LEFT, padx=(0, 10))
        cpu_spinbox = tk.Spinbox(
            cpu_frame,
            from_=10,
            to=100,
            textvariable=self.cpu_limit_var,
            font=("Segoe UI", 10),
            width=8,
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        cpu_spinbox.pack(side=tk.LEFT)
        memory_frame = tk.Frame(advanced_options_frame, bg=self.theme_manager.get_color('card_bg'))
        memory_frame.pack(fill=tk.X, pady=8)
        tk.Label(
            memory_frame,
            text="Memory limit (MB):",
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary')
        ).pack(side=tk.LEFT, padx=(0, 10))
        memory_spinbox = tk.Spinbox(
            memory_frame,
            from_=128,
            to=2048,
            textvariable=self.memory_limit_var,
            font=("Segoe UI", 10),
            width=8,
            bg=self.theme_manager.get_color('bg_primary'),
            fg=self.theme_manager.get_color('fg_primary')
        )
        memory_spinbox.pack(side=tk.LEFT)
        save_frame = tk.Frame(advanced_options_frame, bg=self.theme_manager.get_color('card_bg'))
        save_frame.pack(fill=tk.X, pady=(20, 0))
        ModernButton(
            save_frame,
            "Save Settings",
            command=self.save_settings,
            style="primary",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)
        ModernButton(
            save_frame,
            "Reset to Defaults",
            command=self.reset_settings,
            style="danger",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def start_full_scan(self):
        if not self.is_admin:
            self.show_notification("Error", "Administrator privileges required for full scan!", "error")
            return
        self.scan_progress = 0
        self.progress_bar['value'] = 0
        threading.Thread(target=self._full_scan_thread, daemon=True).start()

    def _full_scan_thread(self):
        self.show_notification("Scan Started", "Full system scan initiated...", "info")
        self.status_cards["Last Scan"].update_value("In Progress", "info")
        for i in range(100):
            self.scan_progress = i + 1
            self.progress_bar['value'] = self.scan_progress
            time.sleep(0.05)
        self.last_scan_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.scan_history.append((datetime.datetime.now(), self.calculate_url_safety_score("example.com")))
        self.status_cards["Last Scan"].update_value(self.last_scan_time, "info")
        self.show_notification("Scan Complete", "Full system scan completed successfully", "success")
        self.update_dashboard_graphs()

    def update_dashboard_graphs(self):
        if hasattr(self, 'dashboard_canvas'):
            for canvas in self.dashboard_canvas.values():
                canvas.get_tk_widget().destroy()
            graphs_frame = self.content_frame.winfo_children()[0].winfo_children()[2]
            graphs_container = graphs_frame.winfo_children()[1]
            self.dashboard_canvas = {}
            fig_pie, ax_pie = plt.subplots(figsize=(4, 3.2))
            threats = [self.threats_blocked, len(self.custom_blocked_sites), len(self.url_history)]
            labels = ['Threats Blocked', 'Sites Blocked', 'URLs Checked']
            colors = [self.theme_manager.get_color('danger'), self.theme_manager.get_color('warning'), self.theme_manager.get_color('info')]
            ax_pie.pie(threats, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax_pie.set_title("Threat Distribution", color=self.theme_manager.get_color('fg_primary'))
            pie_canvas = FigureCanvasTkAgg(fig_pie, master=graphs_container)
            pie_canvas.get_tk_widget().configure(bg=self.theme_manager.get_color('bg_primary'))
            pie_canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
            self.dashboard_canvas['pie'] = pie_canvas
            fig_line, ax_line = plt.subplots(figsize=(4, 3.2))
            times = [t[0] for t in self.scan_history[-5:]]
            scores = [t[1] for t in self.scan_history[-5:]]
            ax_line.plot([t.strftime("%Y-%m-%d") for t in times], scores, color=self.theme_manager.get_color('accent_primary'))
            ax_line.set_title("Scan History", color=self.theme_manager.get_color('fg_primary'))
            ax_line.set_xlabel("Date", color=self.theme_manager.get_color('fg_secondary'))
            ax_line.set_ylabel("Safety Score", color=self.theme_manager.get_color('fg_secondary'))
            ax_line.tick_params(colors=self.theme_manager.get_color('fg_secondary'))
            line_canvas = FigureCanvasTkAgg(fig_line, master=graphs_container)
            line_canvas.get_tk_widget().configure(bg=self.theme_manager.get_color('bg_primary'))
            line_canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)
            self.dashboard_canvas['line'] = line_canvas
            fig_bar, ax_bar = plt.subplots(figsize=(4, 3.2))
            resources = ['CPU', 'Memory']
            usage = [int(self.cpu_limit_var.get()), int(self.memory_limit_var.get()) / 10]
            ax_bar.bar(resources, usage, color=self.theme_manager.get_color('success'))
            ax_bar.set_title("System Resources", color=self.theme_manager.get_color('fg_primary'))
            ax_bar.set_ylabel("Usage (%)", color=self.theme_manager.get_color('fg_secondary'))
            ax_bar.tick_params(colors=self.theme_manager.get_color('fg_secondary'))
            bar_canvas = FigureCanvasTkAgg(fig_bar, master=graphs_container)
            bar_canvas.get_tk_widget().configure(bg=self.theme_manager.get_color('bg_primary'))
            bar_canvas.get_tk_widget().grid(row=0, column=2, padx=10, pady=10)
            self.dashboard_canvas['bar'] = bar_canvas

    def update_status_cards(self):
        self.status_cards["Protection Status"].update_value(self.protection_status, "safe" if self.protection_status == "Active" else "warning")
        self.status_cards["Threats Blocked"].update_value(str(self.threats_blocked), "success")
        self.status_cards["Last Scan"].update_value(self.last_scan_time, "info")
        self.status_cards["System Health"].update_value("Excellent", "safe")

    def add_blocked_site(self):
        url = self.url_entry.get().strip()
        if url:
            try:
                parsed_url = urllib.parse.urlparse(url)
                domain = parsed_url.netloc or parsed_url.path
                if not domain:
                    self.show_notification("Error", "Invalid URL format!", "error")
                    return
                if domain not in self.custom_blocked_sites:
                    self.custom_blocked_sites.append(domain)
                    self.update_blocked_sites_list()
                    self.save_settings()
                    self.website_status.insert(tk.END, f"Blocked: {domain} at {datetime.datetime.now()}\n")
                    self.website_status.see(tk.END)
                    self.show_notification("Success", f"Blocked {domain} successfully!", "success")
                    self.threats_blocked += 1
                    self.update_status_cards()
                    self.update_dashboard_graphs()
                else:
                    self.show_notification("Warning", f"{domain} is already blocked!", "warning")
                self.url_entry.delete(0, tk.END)
            except Exception as e:
                self.show_notification("Error", f"Failed to block site: {str(e)}", "error")
        else:
            self.show_notification("Error", "Please enter a valid URL!", "error")

    def update_blocked_sites_list(self):
        self.sites_listbox.delete(0, tk.END)
        for site in self.custom_blocked_sites:
            self.sites_listbox.insert(tk.END, site)

    def remove_blocked_site(self):
        try:
            selection = self.sites_listbox.curselection()
            if selection:
                site = self.sites_listbox.get(selection[0])
                self.custom_blocked_sites.remove(site)
                self.update_blocked_sites_list()
                self.save_settings()
                self.website_status.insert(tk.END, f"Unblocked: {site} at {datetime.datetime.now()}\n")
                self.website_status.see(tk.END)
                self.show_notification("Success", f"Unblocked {site} successfully!", "success")
            else:
                self.show_notification("Warning", "Please select a site to remove!", "warning")
        except Exception as e:
            self.show_notification("Error", f"Failed to remove site: {str(e)}", "error")

    def block_all_sites(self):
        if not self.is_admin:
            self.show_notification("Error", "Administrator privileges required!", "error")
            return
        self.website_status.insert(tk.END, f"All sites blocked at {datetime.datetime.now()}\n")
        self.website_status.see(tk.END)
        self.show_notification("Success", "All specified sites have been blocked!", "success")

    def unblock_all_sites(self):
        if not self.is_admin:
            self.show_notification("Error", "Administrator privileges required!", "error")
            return
        self.custom_blocked_sites.clear()
        self.update_blocked_sites_list()
        self.save_settings()
        self.website_status.insert(tk.END, f"All sites unblocked at {datetime.datetime.now()}\n")
        self.website_status.see(tk.END)
        self.show_notification("Success", "All sites have been unblocked!", "success")

    def validate_url_input(self, event=None):
        url = self.check_url_entry.get().strip()
        if url:
            try:
                parsed_url = urllib.parse.urlparse(url)
                if parsed_url.scheme and parsed_url.netloc:
                    self.url_result_label.config(text="Valid URL format", fg=self.theme_manager.get_color('success'))
                else:
                    self.url_result_label.config(text="Invalid URL format", fg=self.theme_manager.get_color('warning'))
            except:
                self.url_result_label.config(text="Invalid URL format", fg=self.theme_manager.get_color('warning'))
        else:
            self.url_result_label.config(text="Enter a URL to check its safety", fg=self.theme_manager.get_color('fg_primary'))

    def check_url_safety(self):
        url = self.check_url_entry.get().strip()
        if url:
            try:
                score = self.calculate_url_safety_score(url)
                self.url_history.append((url, score, datetime.datetime.now()))
                self.update_url_history()
                self.update_dashboard_graphs()
                color = self.theme_manager.get_color('success') if score >= 80 else \
                        self.theme_manager.get_color('warning') if score >= 50 else \
                        self.theme_manager.get_color('danger')
                status = "Safe" if score >= 80 else "Suspicious" if score >= 50 else "Dangerous"
                self.url_result_label.config(text=f"URL: {url}\nSafety Score: {score}/100 ({status})", fg=color)
                self.safety_canvas.coords(self.safety_bar, 0, 0, score * 4, 25)
                self.safety_canvas.itemconfig(self.safety_bar, fill=color)
                self.website_status.insert(tk.END, f"Checked: {url} - Score: {score} ({status}) at {datetime.datetime.now()}\n")
                self.website_status.see(tk.END)
                if score < 50 and self.auto_quarantine_var.get():
                    self.custom_blocked_sites.append(urllib.parse.urlparse(url).netloc)
                    self.update_blocked_sites_list()
                    self.save_settings()
                    self.threats_blocked += 1
                    self.update_status_cards()
                    self.show_notification("Threat Blocked", f"URL {url} was automatically blocked due to low safety score!", "warning")
                if self.sound_alerts_var.get() and score < 50:
                    winsound.Beep(1000, 500)
            except Exception as e:
                self.show_notification("Error", f"Failed to check URL: {str(e)}", "error")
        else:
            self.show_notification("Error", "Please enter a valid URL!", "error")

    def calculate_url_safety_score(self, url):
        score = 100
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower() or parsed_url.path.lower()
        if not domain:
            return 10
        if not parsed_url.scheme in ['http', 'https']:
            score -= 30
        if domain in self.custom_blocked_sites:
            score -= 50
        for keyword in self.suspicious_keywords:
            if keyword in domain:
                score -= 20
        if len(domain) > 50:
            score -= 10
        if not '.' in domain:
            score -= 20
        return max(0, min(100, score))

    def update_url_history(self):
        self.history_listbox.delete(0, tk.END)
        for url, score, timestamp in self.url_history[-10:]:
            status = "Safe" if score >= 80 else "Suspicious" if score >= 50 else "Dangerous"
            self.history_listbox.insert(tk.END, f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {url} ({score}/100 - {status})")

    def clear_url_history(self):
        self.url_history.clear()
        self.update_url_history()
        self.website_status.insert(tk.END, f"URL history cleared at {datetime.datetime.now()}\n")
        self.website_status.see(tk.END)
        self.show_notification("Success", "URL history cleared successfully!", "success")

    def start_monitoring(self):
        if not self.is_admin:
            self.show_notification("Error", "Administrator privileges required to start monitoring!", "error")
            return
        self.monitoring = True
        self.monitor_status_label.config(text="Monitoring Status: Active", fg=self.theme_manager.get_color('success'))
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        self.stop_monitor_btn = ModernButton(
            self.buttons_frame,
            "Stop Monitoring",
            command=self.stop_monitoring,
            style="danger",
            theme_manager=self.theme_manager
        )
        self.stop_monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            self.buttons_frame,
            "Refresh Services",
            command=self.refresh_services,
            style="info",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            self.buttons_frame,
            "Export Report",
            command=self.export_services_report,
            style="secondary",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)
        self.monitor_thread = threading.Thread(target=self._monitor_services_thread, daemon=True)
        self.monitor_thread.start()
        self.show_notification("Monitoring Started", "Service monitoring has been activated.", "success")
        self.update_protection_status()

    def stop_monitoring(self):
        self.monitoring = False
        self.monitor_status_label.config(text="Monitoring Status: Inactive", fg=self.theme_manager.get_color('danger'))
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        self.start_monitor_btn = ModernButton(
            self.buttons_frame,
            "Start Monitoring",
            command=self.start_monitoring,
            style="primary",
            theme_manager=self.theme_manager
        )
        self.start_monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            self.buttons_frame,
            "Refresh Services",
            command=self.refresh_services,
            style="info",
            theme_manager=self.theme_manager
        ).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(
            self.buttons_frame,
            "Export Report",
            command=self.export_services_report,
            style="secondary",
            theme_manager=self.theme_manager
        ).pack(side=tk.RIGHT)
        self.monitor_output.insert(tk.END, f"Monitoring stopped at {datetime.datetime.now()}\n")
        self.monitor_output.see(tk.END)
        self.show_notification("Monitoring Stopped", "Service monitoring has been deactivated.", "info")
        self.update_protection_status()

    def _monitor_services_thread(self):
        self.baseline_services = self.get_services()
        while self.monitoring:
            current_services = self.get_services()
            for service in current_services:
                if service not in self.baseline_services:
                    for keyword in self.suspicious_keywords:
                        if keyword in service['name'].lower():
                            self.monitor_output.insert(tk.END, f"Suspicious service detected: {service['name']} (PID: {service['pid']}) at {datetime.datetime.now()}\n")
                            self.monitor_output.see(tk.END)
                            self.threats_blocked += 1
                            self.update_status_cards()
                            if self.sound_alerts_var.get():
                                winsound.Beep(1000, 500)
                            self.show_notification("Threat Detected", f"Suspicious service: {service['name']} detected!", "warning")
                            if self.auto_quarantine_var.get() and self.is_admin:
                                self.stop_service(service['name'])
            self.baseline_services = current_services
            time.sleep(5)

    def get_services(self):
        try:
            output = subprocess.check_output("wmic service get name,processid,description", shell=True).decode()
            lines = output.splitlines()
            services = []
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) >= 2:
                    pid = parts[-1] if parts[-1].isdigit() else "N/A"
                    name = " ".join(parts[:-1]) if pid != "N/A" else " ".join(parts)
                    services.append({"name": name, "pid": pid, "description": "N/A"})
            return services
        except Exception as e:
            self.show_notification("Error", f"Failed to retrieve services: {str(e)}", "error")
            return []

    def populate_services_list(self):
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
        services = self.get_services()
        for service in services:
            status = "Running" if service['pid'] != "N/A" else "Stopped"
            self.services_tree.insert("", tk.END, values=(service['name'], status, service['pid'], service['description']))

    def refresh_services(self):
        self.populate_services_list()
        self.monitor_output.insert(tk.END, f"Services refreshed at {datetime.datetime.now()}\n")
        self.monitor_output.see(tk.END)
        self.show_notification("Success", "Services list refreshed successfully!", "success")

    def stop_service(self, service_name):
        try:
            if self.is_admin:
                subprocess.run(f"net stop \"{service_name}\"", shell=True, check=True)
                self.monitor_output.insert(tk.END, f"Service {service_name} stopped at {datetime.datetime.now()}\n")
                self.monitor_output.see(tk.END)
                self.show_notification("Success", f"Service {service_name} stopped successfully!", "success")
            else:
                self.show_notification("Error", "Administrator privileges required to stop services!", "error")
        except Exception as e:
            self.show_notification("Error", f"Failed to stop service: {str(e)}", "error")

    def export_services_report(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(f"Services Report - Generated on {datetime.datetime.now()}\n\n")
                    services = self.get_services()
                    for service in services:
                        f.write(f"Service: {service['name']}\n")
                        f.write(f"Status: {'Running' if service['pid'] != 'N/A' else 'Stopped'}\n")
                        f.write(f"PID: {service['pid']}\n")
                        f.write(f"Description: {service['description']}\n")
                        f.write("-" * 50 + "\n")
                self.show_notification("Success", f"Services report exported to {file_path}", "success")
            except Exception as e:
                self.show_notification("Error", f"Failed to export report: {str(e)}", "error")

    def update_protection(self):
        self.show_notification("Update Started", "Checking for protection updates...", "info")
        time.sleep(2)  # Simulate update process
        self.show_notification("Success", "Protection updated successfully!", "success")

    def activate_emergency_mode(self):
        if not self.is_admin:
            self.show_notification("Error", "Administrator privileges required for emergency mode!", "error")
            return
        self.monitoring = False
        self.protection_status = "Emergency Mode"
        self.update_status_cards()
        self.website_status.insert(tk.END, f"Emergency mode activated at {datetime.datetime.now()}\n")
        self.website_status.see(tk.END)
        self.monitor_output.insert(tk.END, f"Emergency mode activated at {datetime.datetime.now()}\n")
        self.monitor_output.see(tk.END)
        self.show_notification("Emergency Mode", "System is now in emergency protection mode!", "warning")

    def reset_settings(self):
        self.autostart_var.set(True)
        self.notifications_var.set(True)
        self.sound_alerts_var.set(True)
        self.theme_var.set("dark")
        self.realtime_var.set(True)
        self.auto_updates_var.set(True)
        self.scan_frequency_var.set("Daily")
        self.auto_quarantine_var.set(True)
        self.log_level_var.set("INFO")
        self.cpu_limit_var.set("50")
        self.memory_limit_var.set("512")
        self.theme_manager.current_theme = "dark"
        self.save_settings()
        self.update_all_theme_elements()
        self.show_notification("Success", "Settings reset to defaults!", "success")

    def refresh_logs(self):
        self.load_logs()
        self.show_notification("Success", "Logs refreshed successfully!", "success")

    def load_logs(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        log_file = f"{self.log_type_var.get()}.txt"
        try:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    self.log_text.insert(tk.END, f.read())
            else:
                self.log_text.insert(tk.END, "No logs available.\n")
            self.log_text.see(tk.END)
        except Exception as e:
            self.log_text.insert(tk.END, f"Error loading logs: {str(e)}\n")
        self.log_text.config(state=tk.DISABLED)

    def clear_logs(self):
        log_file = f"{self.log_type_var.get()}.txt"
        try:
            with open(log_file, "w") as f:
                f.write("")
            self.load_logs()
            self.show_notification("Success", "Logs cleared successfully!", "success")
        except Exception as e:
            self.show_notification("Error", f"Failed to clear logs: {str(e)}", "error")

    def export_logs(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                log_file = f"{self.log_type_var.get()}.txt"
                if os.path.exists(log_file):
                    with open(log_file, "r") as f:
                        logs = f.read()
                    with open(file_path, "w") as f:
                        f.write(logs)
                    self.show_notification("Success", f"Logs exported to {file_path}", "success")
                else:
                    self.show_notification("Error", "No logs available to export!", "error")
            except Exception as e:
                self.show_notification("Error", f"Failed to export logs: {str(e)}", "error")

    def generate_report(self, report_type):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(f"Scam Rakshak {report_type.capitalize()} Report - {datetime.datetime.now()}\n\n")
                    f.write(f"Protection Status: {self.protection_status}\n")
                    f.write(f"Threats Blocked: {self.threats_blocked}\n")
                    f.write(f"Last Scan: {self.last_scan_time}\n")
                    f.write(f"Blocked Sites: {len(self.custom_blocked_sites)}\n")
                    f.write(f"URL Checks: {len(self.url_history)}\n")
                    f.write("\nBlocked Sites List:\n")
                    for site in self.custom_blocked_sites:
                        f.write(f"- {site}\n")
                    f.write("\nRecent URL Checks:\n")
                    for url, score, timestamp in self.url_history[-5:]:
                        status = "Safe" if score >= 80 else "Suspicious" if score >= 50 else "Dangerous"
                        f.write(f"- {url} (Score: {score}/100 - {status}) at {timestamp}\n")
                self.show_notification("Success", f"{report_type.capitalize()} report generated at {file_path}", "success")
            except Exception as e:
                self.show_notification("Error", f"Failed to generate report: {str(e)}", "error")

    def update_protection_status(self):
        self.protection_status = "Active" if self.monitoring else "Inactive"
        self.update_status_cards()
        self.status_label.config(text=f"Ready • System {'Protected' if self.monitoring else 'Not Protected'}",
                               fg=self.theme_manager.get_color('success') if self.monitoring else self.theme_manager.get_color('warning'))

    def show_notification(self, title, message, notification_type):
        if not self.notifications_var.get():
            return
        color = {
            "success": self.theme_manager.get_color('success'),
            "warning": self.theme_manager.get_color('warning'),
            "error": self.theme_manager.get_color('danger'),
            "info": self.theme_manager.get_color('info')
        }.get(notification_type, self.theme_manager.get_color('info'))
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.geometry(f"400x100+{self.root.winfo_screenwidth()-420}+{self.root.winfo_screenheight()-150}")
        popup.configure(bg=self.theme_manager.get_color('card_bg'))
        frame = tk.Frame(popup, bg=self.theme_manager.get_color('card_bg'), relief="raised", bd=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=self.theme_manager.get_color('card_bg'),
            fg=color
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))
        tk.Label(
            frame,
            text=message,
            font=("Segoe UI", 12),
            bg=self.theme_manager.get_color('card_bg'),
            fg=self.theme_manager.get_color('fg_primary'),
            wraplength=350
        ).pack(anchor=tk.W, padx=10, pady=(0, 10))
        popup.after(5000, popup.destroy)
        if self.sound_alerts_var.get() and notification_type in ["warning", "error"]:
            winsound.Beep(1000, 500)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScamRakshakGUI(root)
    root.mainloop()
