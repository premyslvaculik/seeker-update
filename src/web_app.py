import os
import sys
import webbrowser
from threading import Timer
from flask import Flask, render_template, jsonify, request
from database import Database
from checker import UpdateChecker
from mailer import Mailer

app = Flask(__name__, template_folder="templates", static_folder="static")
db = Database()
checker = UpdateChecker(db)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/devices")
def get_devices():
    brand = request.args.get("brand")
    search = request.args.get("search")
    devices = db.get_all_devices(brand_filter=brand, search_query=search)
    return jsonify(devices)

@app.route("/api/brands")
def get_brands():
    devices = db.get_all_devices()
    brand_counts = {}
    for d in devices:
        b = d["brand"]
        if b not in brand_counts:
            brand_counts[b] = {"name": b, "total": 0, "active": 0, "eol": 0}
        brand_counts[b]["total"] += 1
        if d.get("is_eol"):
            brand_counts[b]["eol"] += 1
        else:
            brand_counts[b]["active"] += 1
    return jsonify(list(brand_counts.values()))

@app.route("/api/reports")
def get_reports():
    reports = db.get_reports()
    return jsonify(reports)

@app.route("/api/reports/<int:report_id>")
def get_report_detail(report_id):
    changes = db.get_report_changes(report_id)
    
    added = [c for c in changes if c["change_type"] == "ADDED"]
    changed = [c for c in changes if c["change_type"] == "STATUS_CHANGED"]
    removed = [c for c in changes if c["change_type"] == "REMOVED_EOL"]

    html_snippet = ""
    if not changes:
        html_snippet = "<p><i>V této kontrole nebyly zjištěny žádné změny.</i></p>"
    else:
        html_snippet += "<h3>📱 Update Seeker - Přehled změn podpory mobilních zařízení</h3>\n\n"
        
        # Section 1: Added
        html_snippet += "<h4>➕ Nově podporovaná zařízení:</h4>\n"
        if added:
            html_snippet += "<ul>\n"
            for item in added:
                html_snippet += f"  <li><b>{item['brand']} {item['model']}</b>: {item['new_value']}</li>\n"
            html_snippet += "</ul>\n"
        else:
            html_snippet += "<p><i>Žádná nová zařízení.</i></p>\n"

        # Section 2: Changed
        html_snippet += "<h4>🔄 Změny v cyklu / stavu podpory:</h4>\n"
        if changed:
            html_snippet += "<ul>\n"
            for item in changed:
                html_snippet += f"  <li><b>{item['brand']} {item['model']}</b>: {item['old_value']} &rarr; <b>{item['new_value']}</b></li>\n"
            html_snippet += "</ul>\n"
        else:
            html_snippet += "<p><i>Žádné změny v cyklech podpory.</i></p>\n"

        # Section 3: Removed / EOL
        html_snippet += "<h4>❌ Odebraná zařízení / Konce podpory (EOL):</h4>\n"
        if removed:
            html_snippet += "<ul>\n"
            for item in removed:
                html_snippet += f"  <li><b>{item['brand']} {item['model']}</b>: {item['old_value']} (Podpora ukončena / Odebráno)</li>\n"
            html_snippet += "</ul>\n"
        else:
            html_snippet += "<p><i>Žádná zařízení nebyla v této kontrole odebrána.</i></p>\n"

    return jsonify({"changes": changes, "added": added, "changed": changed, "removed": removed, "html_snippet": html_snippet})

@app.route("/api/check", methods=["POST"])
def run_check():
    report_id, changes, summary = checker.run_check(force_send_email=False)
    return jsonify({"success": True, "report_id": report_id, "summary": summary, "changes_count": len(changes)})

@app.route("/api/settings", methods=["GET", "POST"])
def manage_settings():
    if request.method == "POST":
        data = request.json or {}
        db.save_settings(data)
        return jsonify({"success": True})
    else:
        return jsonify(db.get_settings())

@app.route("/api/test-email", methods=["POST"])
def test_email():
    settings = db.get_settings()
    dummy_changes = [
        {"brand": "TestBrand", "model": "TestModel 1.0", "change_type": "ADDED", "new_value": "Status: Testovací zpráva"}
    ]
    success, msg = Mailer.send_report_email(settings, dummy_changes, total_devices=100)
    return jsonify({"success": success, "message": msg})

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    if "--no-browser" not in sys.argv:
        Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
