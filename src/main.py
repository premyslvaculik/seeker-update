import sys
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import Database
from checker import UpdateChecker

def main():
    parser = argparse.ArgumentParser(description="Update Seeker - Mobile device update support tracker (EU)")
    parser.add_argument("--headless", action="store_true", help="Spustit kontrolu na pozadí (bez GUI) a odeslat případný report e-mailem.")
    parser.add_argument("--force-email", action="store_true", help="Vynutit odeslání e-mailu bez ohledu na nastavení.")
    args = parser.parse_args()

    db = Database()

    if args.headless:
        print("[UpdateSeeker CLI] Spouštím v headless režimu...")
        checker = UpdateChecker(db)
        report_id, changes, summary = checker.run_check(force_send_email=args.force_email)
        print(f"[UpdateSeeker CLI] Dokončeno: {summary}")
        sys.exit(0)
    else:
        # Launch Web GUI App
        import web_app
        print("[UpdateSeeker] Spouštím moderní Web UI na http://127.0.0.1:5000...")
        web_app.open_browser()
        web_app.app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    main()
