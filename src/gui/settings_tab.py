import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from mailer import Mailer

class SettingsTab(ttk.Frame):
    def __init__(self, parent, db: Database, on_run_check_callback=None):
        super().__init__(parent, padding=15)
        self.db = db
        self.on_run_check_callback = on_run_check_callback

        # Action Buttons Section
        action_frame = ttk.LabelFrame(self, text="Akce", padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 15))

        self.btn_run = ttk.Button(action_frame, text="▶ Spustit kontrolu zařízení nyní", command=self.run_manual_check)
        self.btn_run.pack(side=tk.LEFT, padx=5)

        # SMTP Settings Section
        smtp_frame = ttk.LabelFrame(self, text="Nastavení E-mailových Notifikací (SMTP)", padding=15)
        smtp_frame.pack(fill=tk.X, pady=(0, 15))

        # Fields
        self.vars = {
            "smtp_host": tk.StringVar(),
            "smtp_port": tk.StringVar(value="587"),
            "smtp_user": tk.StringVar(),
            "smtp_password": tk.StringVar(),
            "smtp_sender": tk.StringVar(),
            "recipient_email": tk.StringVar(),
            "smtp_use_tls": tk.BooleanVar(value=True),
            "auto_send_email": tk.BooleanVar(value=False)
        }

        row = 0
        fields = [
            ("SMTP Server (Host):", "smtp_host", False),
            ("SMTP Port:", "smtp_port", False),
            ("Uživatel / Login:", "smtp_user", False),
            ("Heslo:", "smtp_password", True),
            ("E-mail odesílatele:", "smtp_sender", False),
            ("E-mail příjemce (Váš e-mail):", "recipient_email", False),
        ]

        for label_text, var_key, is_pass in fields:
            ttk.Label(smtp_frame, text=label_text).grid(row=row, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(smtp_frame, textvariable=self.vars[var_key], show="*" if is_pass else "", width=35)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1

        # Checkboxes
        ttk.Checkbutton(smtp_frame, text="Použít šifrování TLS (Port 587 / STARTTLS)", variable=self.vars["smtp_use_tls"]).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        ttk.Checkbutton(smtp_frame, text="Automaticky odesílat denní e-mailový report při kontrole", variable=self.vars["auto_send_email"]).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1

        # Save & Test Buttons
        btn_box = ttk.Frame(smtp_frame)
        btn_box.grid(row=row, column=1, sticky="w", pady=10)

        ttk.Button(btn_box, text="Uložit nastavení", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_box, text="Otestovat odeslání e-mailu", command=self.test_email).pack(side=tk.LEFT)

        self.load_settings()

    def load_settings(self):
        settings = self.db.get_settings()
        for k, v in settings.items():
            if k in self.vars:
                if isinstance(self.vars[k], tk.BooleanVar):
                    self.vars[k].set(v == "1")
                else:
                    self.vars[k].set(v)

    def save_settings(self):
        settings_dict = {}
        for k, var in self.vars.items():
            if isinstance(var, tk.BooleanVar):
                settings_dict[k] = "1" if var.get() else "0"
            else:
                settings_dict[k] = var.get().strip()
        self.db.save_settings(settings_dict)
        messagebox.showinfo("Nastavení", "Nastavení bylo úspěšně uloženo.")

    def test_email(self):
        self.save_settings()
        settings = self.db.get_settings()
        dummy_changes = [
            {"brand": "TestBrand", "model": "TestModel 1.0", "change_type": "ADDED", "new_value": "Status: Testovací zpráva"}
        ]
        success, msg = Mailer.send_report_email(settings, dummy_changes, total_devices=100)
        if success:
            messagebox.showinfo("E-mail Test", "Testovací e-mail byl úspěšně doručen!")
        else:
            messagebox.showerror("E-mail Test", f"Odeslání selhalo: {msg}")

    def run_manual_check(self):
        if self.on_run_check_callback:
            self.on_run_check_callback()
