import webbrowser
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

class SystemTrayApp:
    def __init__(self, on_manual_check=None):
        self.on_manual_check = on_manual_check
        self.icon = None
        self.has_unread_changes = False
        self._init_icon()

    def _create_image(self, alert=False):
        # Generate dynamic 64x64 icon (Smartphone with alert dot)
        img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Phone body (Indigo color)
        bg_color = (99, 102, 241, 255) if not alert else (239, 68, 68, 255)
        draw.rounded_rectangle([14, 6, 50, 58], radius=8, fill=bg_color)
        
        # Phone screen
        draw.rounded_rectangle([18, 12, 46, 48], radius=4, fill=(15, 23, 42, 255))

        # Home button / speaker line
        draw.line([28, 52, 36, 52], fill=(255, 255, 255, 200), width=2)
        draw.line([28, 9, 36, 9], fill=(255, 255, 255, 200), width=2)

        # Alert badge dot if unread changes exist
        if alert:
            draw.ellipse([38, 4, 58, 24], fill=(239, 68, 68, 255), outline=(255, 255, 255, 255), width=2)

        return img

    def _open_web_ui(self):
        webbrowser.open("http://127.0.0.1:5000")
        self.set_alert_state(False)

    def _run_check(self):
        if self.on_manual_check:
            threading.Thread(target=self.on_manual_check, daemon=True).start()

    def set_alert_state(self, has_alert: bool, title: str = "Update Seeker"):
        self.has_unread_changes = has_alert
        if self.icon:
            self.icon.icon = self._create_image(alert=has_alert)
            self.icon.title = title
            if has_alert:
                try:
                    self.icon.notify("Byla zjištěna vyřazená zařízení z podpory! Klikněte pro zobrazení.", "📱 Update Seeker")
                except Exception:
                    pass

    def run(self):
        menu = (
            item("🌐 Otevřít Update Seeker", lambda: self._open_web_ui(), default=True),
            item("⚡ Spustit kontrolu nyní", lambda: self._run_check()),
            item("❌ Ukončit", lambda: self.icon.stop())
        )
        self.icon = pystray.Icon("UpdateSeeker", self._create_image(alert=False), "Update Seeker", menu)
        self.icon.run()

if __name__ == "__main__":
    tray = SystemTrayApp()
    tray.run()
