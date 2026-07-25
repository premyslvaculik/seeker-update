import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Any, Optional, Tuple

class Mailer:
    @staticmethod
    def send_report_email(settings: Dict[str, str], changes: List[Dict[str, Any]], total_devices: int) -> Tuple[bool, str]:
        """
        Sends daily report via SMTP based on DB settings.
        Returns (success: bool, message: str).
        """
        smtp_host = settings.get("smtp_host", "").strip()
        smtp_port = int(settings.get("smtp_port", "587") or "587")
        smtp_user = settings.get("smtp_user", "").strip()
        smtp_password = settings.get("smtp_password", "").strip()
        recipient_email = settings.get("recipient_email", "").strip()
        smtp_sender = settings.get("smtp_sender", "").strip() or smtp_user
        use_tls = settings.get("smtp_use_tls", "1") == "1"

        if not smtp_host or not recipient_email:
            return False, "SMTP server nebo e-mail příjemce není nastaven."

        # Counts
        added = [c for c in changes if c["change_type"] == "ADDED"]
        changed = [c for c in changes if c["change_type"] == "STATUS_CHANGED"]
        removed = [c for c in changes if c["change_type"] == "REMOVED_EOL"]

        subject = f"Update Seeker Report - Změn: {len(changes)} (Nové: {len(added)}, Změny: {len(changed)}, EOL: {len(removed)})"

        # HTML Body
        html_changes_items = ""
        if not changes:
            html_changes_items = "<p><i>V dnešní kontrole nebyly zjištěny žádné změny v podporovaných zařízeních.</i></p>"
        else:
            if added:
                html_changes_items += "<h3>➕ Nově podporovaná zařízení:</h3><ul>"
                for item in added:
                    html_changes_items += f"<li><b>{item['brand']} {item['model']}</b>: {item['new_value']}</li>"
                html_changes_items += "</ul>"
            if changed:
                html_changes_items += "<h3>🔄 Změny stavu / cyklu podpory:</h3><ul>"
                for item in changed:
                    html_changes_items += f"<li><b>{item['brand']} {item['model']}</b>: {item['old_value']} &rarr; <b>{item['new_value']}</b></li>"
                html_changes_items += "</ul>"
            if removed:
                html_changes_items += "<h3>❌ Odebraná zařízení / Konce podpory (EOL):</h3><ul>"
                for item in removed:
                    html_changes_items += f"<li><b>{item['brand']} {item['model']}</b>: {item['old_value']}</li>"
                html_changes_items += "</ul>"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.5; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; borderRadius: 8px; }}
                h2 {{ color: #1a73e8; }}
                .stats {{ background-color: #f8f9fa; padding: 12px; border-radius: 6px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📱 Update Seeker - Denní report podpory mobilů</h2>
                <div class="stats">
                    <b>Celkem sledovaných zařízení:</b> {total_devices}<br>
                    <b>Nová zařízení:</b> {len(added)} | <b>Změny:</b> {len(changed)} | <b>Odebraná (EOL):</b> {len(removed)}
                </div>
                {html_changes_items}
                <hr>
                <p style="font-size: 0.8em; color: #777;">Tento report vygenerovala aplikace Update Seeker (EU trh).</p>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_sender
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
                if use_tls:
                    server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.sendmail(smtp_sender, [recipient_email], msg.as_string())
            return True, "E-mail úspěšně odoslán."
        except Exception as e:
            return False, f"Chyba při odesílání e-mailu: {e}"
