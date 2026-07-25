import tkinter as tk
from tkinter import ttk
from typing import Optional
from database import Database

class DeviceTab(ttk.Frame):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db

        # Top Control Bar (Filter & Search)
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(control_frame, text="Značka:").pack(side=tk.LEFT, padx=(0, 5))
        self.brand_var = tk.StringVar(value="Všechny")
        self.brand_cb = ttk.Combobox(control_frame, textvariable=self.brand_var, state="readonly", width=15)
        self.brand_cb.pack(side=tk.LEFT, padx=(0, 15))
        self.brand_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_devices())

        ttk.Label(control_frame, text="Hledat model:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_devices())

        ttk.Button(control_frame, text="Obnovit tabulku", command=self.refresh_devices).pack(side=tk.RIGHT)

        # Device Treeview Table
        tree_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("brand", "model", "status", "os_support_end", "security_support_end", "source", "last_checked")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("brand", text="Značka")
        self.tree.heading("model", text="Model zařízení")
        self.tree.heading("status", text="Stav podpory")
        self.tree.heading("os_support_end", text="Konec podpory OS")
        self.tree.heading("security_support_end", text="Konec bezpeč. záplat")
        self.tree.heading("source", text="Zdroj dat")
        self.tree.heading("last_checked", text="Naposledy zkontrolováno")

        self.tree.column("brand", width=100, anchor="w")
        self.tree.column("model", width=200, anchor="w")
        self.tree.column("status", width=170, anchor="center")
        self.tree.column("os_support_end", width=140, anchor="center")
        self.tree.column("security_support_end", width=140, anchor="center")
        self.tree.column("source", width=160, anchor="w")
        self.tree.column("last_checked", width=150, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.refresh_brands()
        self.refresh_devices()

    def refresh_brands(self):
        brands = ["Všechny"] + self.db.get_device_brands()
        self.brand_cb['values'] = brands

    def refresh_devices(self):
        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        brand = self.brand_var.get()
        search = self.search_var.get().strip()

        devices = self.db.get_all_devices(brand_filter=brand, search_query=search)
        for d in devices:
            self.tree.insert("", tk.END, values=(
                d["brand"],
                d["model"],
                d["status"],
                d["os_support_end"],
                d["security_support_end"],
                d["source"],
                d["last_checked"]
            ))
