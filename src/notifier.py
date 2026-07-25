import subprocess
import os
import requests
from typing import List, Dict, Any

class Notifier:
    @staticmethod
    def notify_changes(changes: List[Dict[str, Any]], settings: Dict[str, str]):
        """
        Triggers notifications without requiring passwords:
        1. Native Windows System Notification (Toast)
        2. Optional Webhook (ntfy.sh / Discord / Telegram)
        """
        if not changes:
            return

        added = [c for c in changes if c["change_type"] == "ADDED"]
        changed = [c for c in changes if c["change_type"] == "STATUS_CHANGED"]
        removed = [c for c in changes if c["change_type"] == "REMOVED_EOL"]

        summary_parts = []
        if removed:
            summary_parts.append(f"❌ EOL/Odebráno: {len(removed)}")
        if changed:
            summary_parts.append(f"🔄 Změny: {len(changed)}")
        if added:
            summary_parts.append(f"➕ Nové: {len(added)}")

        title = "📱 Update Seeker - Zjištěny změny podpory!"
        body = " ".join(summary_parts) + ". Kliknutím otevřete přehled."

        # 1. Native Windows Toast Notification (Zero password required)
        Notifier._send_windows_toast(title, body)

        # 2. Webhook Notification (ntfy.sh or Discord/Slack - URL only, no password)
        webhook_url = settings.get("webhook_url", "").strip()
        if webhook_url:
            Notifier._send_webhook(webhook_url, title, body, changes)

    @staticmethod
    def _send_windows_toast(title: str, body: str):
        """
        Sends native Windows Toast Notification using PowerShell.
        """
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = @"
        <toast>
            <visual>
                <binding template="ToastGeneric">
                    <text>{title}</text>
                    <text>{body}</text>
                </binding>
            </visual>
        </toast>
"@
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Update Seeker").Show($toast)
        """
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, timeout=5)
        except Exception as e:
            print(f"[Notifier] Windows Toast notification fallback: {e}")

    @staticmethod
    def _send_webhook(url: str, title: str, body: str, changes: List[Dict[str, Any]]):
        """
        Sends notification to ntfy.sh, Discord, or generic Webhook URL.
        """
        try:
            if "ntfy.sh" in url:
                # ntfy.sh simple push notification to phone/desktop
                requests.post(url, data=f"{title}\n{body}".encode("utf-8"), headers={"Title": title}, timeout=5)
            elif "discord.com" in url:
                # Discord Webhook
                payload = {"content": f"**{title}**\n{body}"}
                requests.post(url, json=payload, timeout=5)
            else:
                # Generic POST webhook
                requests.post(url, json={"title": title, "body": body, "changes_count": len(changes)}, timeout=5)
        except Exception as e:
            print(f"[Notifier] Webhook send error: {e}")
