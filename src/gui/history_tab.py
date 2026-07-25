import tkinter as tk
from tkinter import ttk
from database import Database

class HistoryTab(ttk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db

        # Split pane (Left: Reports List, Right: Selected Report Diffs)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Frame: Reports
        left_frame = ttk.LabelFrame(paned, text="Historické kontroly (Reporty)", padding=5)
        paned.add(left_frame, weight=1)

        self.reports_tree = ttk.Treeview(left_frame, columns=("id", "timestamp", "summary"), show="headings", selectmode="browse")
        self.reports_tree.heading("id", text="ID")
        self.reports_tree.heading("timestamp", text="Datum a čas")
        self.reports_tree.heading("summary", text="Souhrn změn")
        self.reports_tree.column("id", width=40, anchor="center")
        self.reports_tree.column("timestamp", width=140, anchor="center")
        self.reports_tree.column("summary", width=220, anchor="w")

        r_vsb = ttk.Scrollbar(left_frame, orient="vertical", command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=r_vsb.set)
        self.reports_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        r_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.reports_tree.bind("<<TreeviewSelect>>", self.on_report_selected)

        # Right Frame: Changes detail
        right_frame = ttk.LabelFrame(paned, text="Detail změn v vybrané kontrole", padding=5)
        paned.add(right_frame, weight=2)

        self.changes_tree = ttk.Treeview(right_frame, columns=("brand", "model", "type", "old", "new"), show="headings")
        self.changes_tree.heading("brand", text="Značka")
        self.changes_tree.heading("model", text="Model")
        self.changes_tree.heading("type", text="Typ změny")
        self.changes_tree.heading("old", text="Původní hodnota")
        self.changes_tree.heading("new", text="Nová hodnota")

        self.changes_tree.column("brand", width=90, anchor="w")
        self.changes_tree.column("model", width=150, anchor="w")
        self.changes_tree.column("type", width=120, anchor="center")
        self.changes_tree.column("old", width=180, anchor="w")
        self.changes_tree.column("new", width=180, anchor="w")

        c_vsb = ttk.Scrollbar(right_frame, orient="vertical", command=self.changes_tree.yview)
        self.changes_tree.configure(yscrollcommand=c_vsb.set)
        self.changes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        c_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_reports()

    def refresh_reports(self):
        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)

        reports = self.db.get_reports()
        for r in reports:
            self.reports_tree.insert("", tk.END, values=(r["id"], r["timestamp"], r["summary_text"]))

    def on_report_selected(self, event):
        selected = self.reports_tree.selection()
        if not selected:
            return
        item_vals = self.reports_tree.item(selected[0], "values")
        report_id = item_vals[0]

        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)

        changes = self.db.get_report_changes(report_id)
        for c in changes:
            self.changes_tree.insert("", tk.END, values=(
                c["brand"],
                c["model"],
                c["change_type"],
                c["old_value"],
                c["new_value"]
            ))
