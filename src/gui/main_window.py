import tkinter as tk
from tkinter import ttk, messagebox
import threading
from database import Database
from checker import UpdateChecker
from gui.device_tab import DeviceTab
from gui.history_tab import HistoryTab
from gui.settings_tab import SettingsTab

class MainWindow(tk.Tk):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.checker = UpdateChecker(db)

        self.title("Update Seeker - Kontrola podpory mobilních zařízení (EU)")
        self.geometry("1050x680")
        self.minsize(900, 550)

        # Apply Modern TTK Style
        style = ttk.Style(self)
        style.theme_use("clam")

        # Top Banner / Status Bar
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        title_lbl = ttk.Label(top_bar, text="📱 Update Seeker (EU)", font=("Helvetica", 16, "bold"))
        title_lbl.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Přípraveno.")
        status_lbl = ttk.Label(top_bar, textvariable=self.status_var, font=("Helvetica", 10, "italic"))
        status_lbl.pack(side=tk.RIGHT, padx=10)

        # Main Notebook Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.device_tab = DeviceTab(self.notebook, db)
        self.history_tab = HistoryTab(self.notebook, db)
        self.settings_tab = SettingsTab(self.notebook, db, on_run_check_callback=self.trigger_async_check)

        self.notebook.add(self.device_tab, text=" 📱 Aktualní zařízení ")
        self.notebook.add(self.history_tab, text=" 📜 Historie reportů ")
        self.notebook.add(self.settings_tab, text=" ⚙️ Nastavení a E-mail ")

    def trigger_async_check(self):
        self.status_var.set("Probíhá kontrola zařízení...")
        self.settings_tab.btn_run.config(state="disabled")

        def task():
            try:
                report_id, changes, summary = self.checker.run_check(force_send_email=False)
                self.after(0, lambda: self.on_check_completed(summary, True))
            except Exception as e:
                self.after(0, lambda: self.on_check_completed(f"Chyba: {e}", False))

        threading.Thread(target=task, daemon=True).start()

    def on_check_completed(self, summary: str, success: bool):
        self.settings_tab.btn_run.config(state="normal")
        self.status_var.set(summary)
        if success:
            self.device_tab.refresh_brands()
            self.device_tab.refresh_devices()
            self.history_tab.refresh_reports()
            messagebox.showinfo("Kontrola dokončena", summary)
        else:
            messagebox.showerror("Chyba při kontrole", summary)
