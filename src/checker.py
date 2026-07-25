from typing import List, Dict, Any, Tuple
from database import Database
from connectors.endoflife import EndOfLifeConnector
from connectors.motorola import MotorolaConnector
from connectors.honor import HonorConnector
from connectors.xiaomi import XiaomiConnector
from mailer import Mailer

class UpdateChecker:
    def __init__(self, db: Database):
        self.db = db
        self.connectors = [
            EndOfLifeConnector(),
            MotorolaConnector(),
            HonorConnector(),
            XiaomiConnector()
        ]

    def run_check(self, force_send_email: bool = False) -> Tuple[int, List[Dict[str, Any]], str]:
        """
        Executes all connectors, updates DB, generates diffs and sends emails.
        Returns (report_id, changes_list, status_summary_str).
        """
        all_devices = []
        print("[UpdateChecker] Spouštím kontrolu konektorů...")

        for conn in self.connectors:
            try:
                devices = conn.fetch_devices()
                all_devices.extend(devices)
                print(f"  -> {conn.__class__.__name__}: Načteno {len(devices)} zařízení.")
            except Exception as e:
                print(f"  -> Chyba v konektoru {conn.__class__.__name__}: {e}")

        # Save snapshot into Database and compute diffs
        report_id, changes = self.db.save_device_snapshot(all_devices)
        print(f"[UpdateChecker] Kontrola dokončena. Report ID #{report_id}. Nalezeno {len(changes)} změn.")

        # Email dispatch if enabled or forced
        settings = self.db.get_settings()
        email_msg = ""
        if force_send_email or settings.get("auto_send_email") == "1":
            success, mail_res = Mailer.send_report_email(settings, changes, len(all_devices))
            email_msg = f" | E-mail: {mail_res}"
            print(f"[UpdateChecker] {email_msg}")

        summary = f"Načteno {len(all_devices)} zařízení. Nové: {len([c for c in changes if c['change_type']=='ADDED'])}, Změny: {len([c for c in changes if c['change_type']=='STATUS_CHANGED'])}, EOL: {len([c for c in changes if c['change_type']=='REMOVED_EOL'])}{email_msg}"
        return report_id, changes, summary
