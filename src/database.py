import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from config import DB_PATH

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Devices table (latest snapshot)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    status TEXT NOT NULL,
                    os_support_end TEXT,
                    security_support_end TEXT,
                    is_eol INTEGER DEFAULT 0,
                    source TEXT,
                    last_checked TIMESTAMP,
                    UNIQUE(brand, model)
                )
            ''')

            # Reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_devices INTEGER DEFAULT 0,
                    added_count INTEGER DEFAULT 0,
                    removed_count INTEGER DEFAULT 0,
                    changed_count INTEGER DEFAULT 0,
                    summary_text TEXT
                )
            ''')

            # Changes table (diff details per report)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    change_type TEXT NOT NULL, -- ADDED, REMOVED_EOL, STATUS_CHANGED
                    old_value TEXT,
                    new_value TEXT,
                    FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
                )
            ''')

            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

            # Insert default settings if not exists
            default_settings = {
                "smtp_host": "",
                "smtp_port": "587",
                "smtp_user": "",
                "smtp_password": "",
                "smtp_sender": "",
                "recipient_email": "",
                "smtp_use_tls": "1",
                "auto_send_email": "0"
            }
            for k, v in default_settings.items():
                cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (k, v))
            
            conn.commit()

    def get_all_devices(self, brand_filter: Optional[str] = None, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM devices WHERE 1=1"
            params = []
            if brand_filter and brand_filter != "Všechny":
                query += " AND brand = ?"
                params.append(brand_filter)
            if search_query:
                query += " AND (model LIKE ? OR brand LIKE ?)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])
            query += " ORDER BY brand ASC, model ASC"
            
            rows = cursor.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_device_brands(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT DISTINCT brand FROM devices ORDER BY brand ASC").fetchall()
            return [row["brand"] for row in rows]

    def save_device_snapshot(self, fetched_devices: List[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]]]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()

            existing_rows = cursor.execute("SELECT brand, model, status, os_support_end, security_support_end, is_eol FROM devices").fetchall()
            existing_map = {(row["brand"], row["model"]): dict(row) for row in existing_rows}

            fetched_map = {(d["brand"], d["model"]): d for d in fetched_devices}

            changes = []
            added_count = 0
            removed_count = 0
            changed_count = 0

            for key, new_dev in fetched_map.items():
                brand, model = key
                is_dev_eol = new_dev.get("is_eol") or "EOL" in new_dev["status"] or "ukončena" in new_dev["status"].lower()

                if key not in existing_map:
                    if is_dev_eol:
                        removed_count += 1
                        changes.append({
                            "brand": brand,
                            "model": model,
                            "change_type": "REMOVED_EOL",
                            "old_value": "Model zjištěn jako EOL",
                            "new_value": f"Status: {new_dev['status']}, Security End: {new_dev.get('security_support_end', 'N/A')}"
                        })
                    else:
                        added_count += 1
                        changes.append({
                            "brand": brand,
                            "model": model,
                            "change_type": "ADDED",
                            "old_value": "",
                            "new_value": f"Status: {new_dev['status']}, Security End: {new_dev.get('security_support_end', 'N/A')}"
                        })
                else:
                    old_dev = existing_map[key]
                    if (old_dev["status"] != new_dev["status"] or 
                        old_dev["is_eol"] != new_dev["is_eol"] or
                        old_dev["security_support_end"] != new_dev["security_support_end"]):
                        
                        if is_dev_eol and not old_dev.get("is_eol"):
                            removed_count += 1
                            change_type = "REMOVED_EOL"
                        else:
                            changed_count += 1
                            change_type = "STATUS_CHANGED"

                        changes.append({
                            "brand": brand,
                            "model": model,
                            "change_type": change_type,
                            "old_value": f"Status: {old_dev['status']}, Security: {old_dev['security_support_end']}",
                            "new_value": f"Status: {new_dev['status']}, Security: {new_dev['security_support_end']}"
                        })

            for key, old_dev in existing_map.items():
                if key not in fetched_map:
                    removed_count += 1
                    changes.append({
                        "brand": old_dev["brand"],
                        "model": old_dev["model"],
                        "change_type": "REMOVED_EOL",
                        "old_value": f"Status: {old_dev['status']}",
                        "new_value": "Odebráno z podporovaných zařízení (EOL)"
                    })

            summary = f"Celkem: {len(fetched_devices)} | Nové: {added_count} | Změny: {changed_count} | Odebráno: {removed_count}"
            cursor.execute('''
                INSERT INTO reports (timestamp, total_devices, added_count, removed_count, changed_count, summary_text)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (now, len(fetched_devices), added_count, removed_count, changed_count, summary))
            report_id = cursor.lastrowid

            for c in changes:
                cursor.execute('''
                    INSERT INTO changes (report_id, brand, model, change_type, old_value, new_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (report_id, c["brand"], c["model"], c["change_type"], c["old_value"], c["new_value"]))

            cursor.execute("DELETE FROM devices")
            for d in fetched_devices:
                cursor.execute('''
                    INSERT INTO devices (brand, model, status, os_support_end, security_support_end, is_eol, source, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    d["brand"],
                    d["model"],
                    d["status"],
                    d.get("os_support_end", "N/A"),
                    d.get("security_support_end", "N/A"),
                    1 if d.get("is_eol") else 0,
                    d.get("source", "endoflife.date"),
                    now
                ))

            conn.commit()
            return report_id, changes

    def get_reports(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM reports ORDER BY timestamp DESC").fetchall()
            return [dict(row) for row in rows]

    def get_report_changes(self, report_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM changes WHERE report_id = ? ORDER BY brand, model", (report_id,)).fetchall()
            return [dict(row) for row in rows]

    def get_settings(self) -> Dict[str, str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT key, value FROM settings").fetchall()
            return {row["key"]: row["value"] for row in rows}

    def save_settings(self, settings_dict: Dict[str, str]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for k, v in settings_dict.items():
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
            conn.commit()
