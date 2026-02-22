"""
GFNS Database Viewer — Native Desktop App
Run: python gfns_db_viewer.py
Opens a real DB Browser-style window. No browser needed.
"""

import sqlite3, os, threading, time
import tkinter as tk
from tkinter import ttk, messagebox, font

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gfns_data.db")

TABLES = [
    ("── FINANCIAL ──────────────", None),
    ("bank_capital_adequacy",       "🏦"),
    ("liquidity_coverage",          "💧"),
    ("debt_exposure",               "📊"),
    ("solvency_stress",             "🔥"),
    ("── FINANCIAL SHIELD ───────", None),
    ("identity_sessions",           "🛡"),
    ("embedded_data",               "🔗"),
    ("binary_data",                 "⬛"),
    ("encrypted_data",              "🔐"),
]

COL_WIDTHS = {
    "id":                     45,
    "institution":           160,
    "region":                110,
    "tier1_capital_ratio":    90,
    "cet1_ratio":             80,
    "capital_conservation":   90,
    "risk_weighted_assets":   90,
    "leverage_ratio":         80,
    "dscr":                   60,
    "status":                 80,
    "recorded_at":           140,
    "lcr_pct":                70,
    "hqla_buffer_bn":         90,
    "net_cash_outflow_bn":    90,
    "intraday_liquidity":     90,
    "repo_market_access":     90,
    "cb_facility_util":       80,
    "sovereign_exposure_pct": 110,
    "npl_ratio":              75,
    "loan_to_deposit":        85,
    "interbank_exposure_bn":  110,
    "cds_spread_bps":         90,
    "concentration_risk":     100,
    "stress_index":           80,
    "altman_zscore":          85,
    "equity_volatility":      90,
    "bail_in_eligibility":    100,
    "contagion_index":        90,
    "recovery_rate":          85,
    "session_id":            200,
    "id_hash":               200,
    "fraud_verdict":         180,
    "is_duplicate":           70,
    "fields_count":           70,
    "created_at":            140,
    "field_name":             80,
    "raw_token":              80,
    "binary_bits":           220,
    "char_count":             70,
    "position":               60,
    "character":              60,
    "binary_rep":             90,
    "decimal_val":            70,
    "salt_b64":              180,
    "cipher_b64":            180,
    "hmac_b64":              180,
    "algo":                  180,
    "cipher_len":             75,
    "decrypted_ok":           80,
}

STATUS_COLOURS = {
    "HEALTHY":   "#2ecc71",
    "WARNING":   "#f39c12",
    "CRITICAL":  "#e74c3c",
    "CLEAN":     "#2ecc71",
    "DUPLICATE": "#e74c3c",
    "OPEN":      "#2ecc71",
    "TIGHT":     "#f39c12",
    "STRESSED":  "#e74c3c",
    "Low":       "#2ecc71",
    "Moderate":  "#f39c12",
    "High":      "#e74c3c",
    "Severe":    "#c0392b",
}


class GFNSViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GFNS Database Viewer  —  gfns_data.db")
        self.geometry("1280x780")
        self.configure(bg="#1a1a2e")
        self.minsize(900, 600)

        self.current_table = tk.StringVar()
        self.search_var    = tk.StringVar()
        self.row_count_var = tk.StringVar(value="0 rows")
        self.status_var    = tk.StringVar(value="Ready")
        self._all_rows     = []
        self._columns      = []

        self._build_style()
        self._build_ui()
        self._check_db()
        self.after(200, lambda: self._load_table("bank_capital_adequacy"))
        self._start_autorefresh()

    # ─────────────────────────────────────────────────────
    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Treeview (the data grid)
        style.configure("Treeview",
            background="#0f0f1a",
            foreground="#c8d0e0",
            rowheight=24,
            fieldbackground="#0f0f1a",
            borderwidth=0,
            font=("Consolas", 10),
        )
        style.configure("Treeview.Heading",
            background="#1e1e3a",
            foreground="#7f8cba",
            font=("Consolas", 9, "bold"),
            relief="flat",
            padding=(6, 4),
        )
        style.map("Treeview",
            background=[("selected", "#2d2d5a")],
            foreground=[("selected", "#ffffff")],
        )
        style.map("Treeview.Heading",
            background=[("active", "#2a2a4a")],
        )
        # Sidebar treeview
        style.configure("Sidebar.Treeview",
            background="#141428",
            foreground="#6e7a9a",
            rowheight=26,
            fieldbackground="#141428",
            borderwidth=0,
            font=("Consolas", 10),
        )
        style.map("Sidebar.Treeview",
            background=[("selected", "#2d2d5a")],
            foreground=[("selected", "#89b4fa")],
        )
        # Scrollbar
        style.configure("Dark.Vertical.TScrollbar",
            background="#1e1e3a", troughcolor="#0f0f1a",
            arrowcolor="#3a3a5c", borderwidth=0)
        style.configure("Dark.Horizontal.TScrollbar",
            background="#1e1e3a", troughcolor="#0f0f1a",
            arrowcolor="#3a3a5c", borderwidth=0)

    # ─────────────────────────────────────────────────────
    def _build_ui(self):
        # ── TOP BAR ──────────────────────────────────────
        topbar = tk.Frame(self, bg="#0d0d1f", height=38)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="◈  GFNS SQLite Database Viewer",
                 bg="#0d0d1f", fg="#89b4fa",
                 font=("Consolas", 11, "bold")).pack(side="left", padx=14)

        tk.Label(topbar, text="gfns_data.db  |  SQLite 3",
                 bg="#0d0d1f", fg="#444466",
                 font=("Consolas", 9)).pack(side="right", padx=14)

        self._conn_label = tk.Label(topbar, text="● Connected",
                 bg="#0d0d1f", fg="#2ecc71",
                 font=("Consolas", 9))
        self._conn_label.pack(side="right", padx=8)

        # ── TOOLBAR ──────────────────────────────────────
        toolbar = tk.Frame(self, bg="#161630", height=36)
        toolbar.pack(fill="x", side="top")
        toolbar.pack_propagate(False)

        self._make_btn(toolbar, "⟳  Refresh", self._refresh).pack(side="left", padx=(8,2), pady=5)
        self._make_btn(toolbar, "▤  Schema",  self._show_schema).pack(side="left", padx=2, pady=5)

        tk.Frame(toolbar, bg="#2a2a4a", width=1).pack(side="left", fill="y", padx=6, pady=6)

        tk.Label(toolbar, text="Filter:", bg="#161630", fg="#5a6a8a",
                 font=("Consolas", 9)).pack(side="left")
        search_entry = tk.Entry(toolbar, textvariable=self.search_var,
            bg="#0f0f1f", fg="#c8d0e0", insertbackground="#89b4fa",
            font=("Consolas", 10), bd=1, relief="solid",
            highlightthickness=1, highlightcolor="#3a3a6a",
            highlightbackground="#2a2a4a", width=24)
        search_entry.pack(side="left", padx=6, pady=6)
        self.search_var.trace_add("write", lambda *_: self._filter())

        tk.Label(toolbar, textvariable=self.row_count_var,
                 bg="#161630", fg="#4a5a7a",
                 font=("Consolas", 9)).pack(side="right", padx=14)

        # ── BODY ─────────────────────────────────────────
        body = tk.Frame(self, bg="#1a1a2e")
        body.pack(fill="both", expand=True)

        # SIDEBAR
        sidebar = tk.Frame(body, bg="#141428", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="TABLES",
                 bg="#141428", fg="#3a4a6a",
                 font=("Consolas", 8, "bold"),
                 padx=12, pady=8).pack(anchor="w")

        self._sidebar = ttk.Treeview(sidebar, style="Sidebar.Treeview",
                                     show="tree", selectmode="browse")
        self._sidebar.pack(fill="both", expand=True)
        self._sidebar.column("#0", width=210, minwidth=210)
        self._sidebar.bind("<<TreeviewSelect>>", self._on_sidebar_select)
        self._populate_sidebar()

        tk.Frame(body, bg="#0d0d1f", width=1).pack(side="left", fill="y")

        # MAIN DATA AREA
        main = tk.Frame(body, bg="#0f0f1a")
        main.pack(side="left", fill="both", expand=True)

        # Table label bar
        self._table_label_bar = tk.Frame(main, bg="#1a1a3a", height=28)
        self._table_label_bar.pack(fill="x")
        self._table_label_bar.pack_propagate(False)
        self._table_label = tk.Label(self._table_label_bar, text="",
            bg="#1a1a3a", fg="#89b4fa",
            font=("Consolas", 9, "bold"), padx=12)
        self._table_label.pack(side="left", fill="y")

        # Grid frame
        grid_frame = tk.Frame(main, bg="#0f0f1a")
        grid_frame.pack(fill="both", expand=True)

        self._tree = ttk.Treeview(grid_frame, style="Treeview",
                                  show="headings", selectmode="browse")

        vsb = ttk.Scrollbar(grid_frame, orient="vertical",
                            command=self._tree.yview,
                            style="Dark.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(grid_frame, orient="horizontal",
                            command=self._tree.xview,
                            style="Dark.Horizontal.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        # Row tags for status colours
        for status, colour in STATUS_COLOURS.items():
            self._tree.tag_configure(f"status_{status}", foreground=colour)
        self._tree.tag_configure("alt", background="#131325")

        # ── STATUSBAR ────────────────────────────────────
        statusbar = tk.Frame(self, bg="#0d0d1f", height=22)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)
        tk.Label(statusbar, textvariable=self.status_var,
                 bg="#0d0d1f", fg="#3a4a6a",
                 font=("Consolas", 8), padx=12).pack(side="left", fill="y")
        tk.Label(statusbar, text="Auto-refresh: 5s",
                 bg="#0d0d1f", fg="#2a3a5a",
                 font=("Consolas", 8), padx=12).pack(side="right", fill="y")

    def _make_btn(self, parent, text, cmd):
        btn = tk.Button(parent, text=text, command=cmd,
            bg="#1e1e3a", fg="#7a8ab0",
            activebackground="#2a2a4a", activeforeground="#c8d0e0",
            font=("Consolas", 9), bd=0, padx=10, pady=2,
            cursor="hand2", relief="flat")
        return btn

    # ─────────────────────────────────────────────────────
    def _populate_sidebar(self):
        for name, icon in TABLES:
            if icon is None:
                iid = self._sidebar.insert("", "end", text=f"  {name}",
                    tags=("group",))
                self._sidebar.tag_configure("group",
                    foreground="#3a4a6a", font=("Consolas", 8))
            else:
                self._sidebar.insert("", "end", text=f"  {icon}  {name}",
                    values=(name,), tags=("table",))
        self._sidebar.tag_configure("table", foreground="#6e7a9a")

    def _on_sidebar_select(self, event):
        sel = self._sidebar.selection()
        if not sel:
            return
        item = self._sidebar.item(sel[0])
        if "table" not in item["tags"]:
            return
        tbl = item["values"][0]
        self._load_table(tbl)

    # ─────────────────────────────────────────────────────
    def _check_db(self):
        if not os.path.exists(DB_PATH):
            self._conn_label.config(text="● DB not found", fg="#e74c3c")
            messagebox.showwarning("Database not found",
                f"Could not find:\n{DB_PATH}\n\nRun backend_server.py first to create the database.")

    def _get_conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    # ─────────────────────────────────────────────────────
    def _load_table(self, table_name):
        self.current_table.set(table_name)
        self.search_var.set("")
        self.status_var.set(f"Loading {table_name}...")

        try:
            conn = self._get_conn()
            cur  = conn.cursor()
            rows = cur.execute(f"SELECT * FROM {table_name}").fetchall()
            conn.close()
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            return

        self._columns  = list(rows[0].keys()) if rows else []
        self._all_rows = [dict(r) for r in rows]

        self._table_label.config(text=f"  SELECT * FROM {table_name}   ({len(rows)} rows)")
        self._render_grid(self._all_rows)
        self._update_sidebar_counts()
        self.status_var.set(f"Table: {table_name}  |  {len(rows)} rows  |  {len(self._columns)} columns")

    def _render_grid(self, rows):
        # Clear
        for col in self._tree["columns"]:
            self._tree.heading(col, text="")
        self._tree["columns"] = []
        for item in self._tree.get_children():
            self._tree.delete(item)

        if not rows:
            self.row_count_var.set("0 rows")
            return

        cols = list(rows[0].keys())
        self._tree["columns"] = cols

        for col in cols:
            w = COL_WIDTHS.get(col, 120)
            self._tree.heading(col, text=col.upper(),
                command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=w, minwidth=40,
                             stretch=False, anchor="w")

        for i, row in enumerate(rows):
            vals   = [row[c] for c in cols]
            status = row.get("status") or row.get("fraud_verdict") or \
                     row.get("concentration_risk") or row.get("repo_market_access") or ""
            tags   = []
            if status in STATUS_COLOURS:
                tags.append(f"status_{status}")
            if i % 2 == 1:
                tags.append("alt")
            self._tree.insert("", "end", values=vals, tags=tags)

        self.row_count_var.set(f"{len(rows)} rows")

    # ─────────────────────────────────────────────────────
    def _filter(self):
        q = self.search_var.get().lower()
        if not q:
            filtered = self._all_rows
        else:
            filtered = [r for r in self._all_rows
                        if any(q in str(v).lower() for v in r.values())]
        self._render_grid(filtered)

    def _sort_by(self, col):
        rows = self._all_rows[:]
        try:
            rows.sort(key=lambda r: (r[col] is None, r[col]))
        except TypeError:
            rows.sort(key=lambda r: str(r[col] or ""))
        self._all_rows = rows
        self._render_grid(rows)

    # ─────────────────────────────────────────────────────
    def _show_schema(self):
        tbl = self.current_table.get()
        if not tbl:
            return
        try:
            conn = self._get_conn()
            info = conn.execute(f"PRAGMA table_info({tbl})").fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        win = tk.Toplevel(self)
        win.title(f"Schema — {tbl}")
        win.geometry("700x420")
        win.configure(bg="#0f0f1a")

        tk.Label(win, text=f"CREATE TABLE {tbl}",
                 bg="#0f0f1a", fg="#f9e2af",
                 font=("Consolas", 11, "bold"), padx=16, pady=10).pack(anchor="w")

        frame = tk.Frame(win, bg="#0f0f1a")
        frame.pack(fill="both", expand=True, padx=12, pady=(0,12))

        tree = ttk.Treeview(frame, style="Treeview",
                            columns=("cid","name","type","notnull","dflt","pk"),
                            show="headings", selectmode="browse")
        for col, lbl, w in [
            ("cid","#",30),("name","Column Name",160),("type","Type",100),
            ("notnull","NOT NULL",70),("dflt","Default",100),("pk","PK",40)]:
            tree.heading(col, text=lbl)
            tree.column(col, width=w, minwidth=30)

        for row in info:
            tree.insert("", "end", values=(
                row[0], row[1], row[2],
                "YES" if row[3] else "NO",
                row[4] or "—",
                "✓" if row[5] else ""
            ))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview,
                            style="Dark.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

    # ─────────────────────────────────────────────────────
    def _update_sidebar_counts(self):
        try:
            conn = self._get_conn()
            for name, icon in TABLES:
                if icon is None:
                    continue
                n = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                # update sidebar text to include count
                for iid in self._sidebar.get_children():
                    item = self._sidebar.item(iid)
                    if "table" in item["tags"] and item["values"] and item["values"][0] == name:
                        self._sidebar.item(iid, text=f"  {icon}  {name}  [{n}]")
            conn.close()
        except Exception:
            pass

    # ─────────────────────────────────────────────────────
    def _refresh(self):
        tbl = self.current_table.get()
        if tbl:
            self._load_table(tbl)

    def _start_autorefresh(self):
        def loop():
            while True:
                time.sleep(5)
                tbl = self.current_table.get()
                if tbl in ("identity_sessions","embedded_data","binary_data","encrypted_data"):
                    self.after(0, self._refresh)
        t = threading.Thread(target=loop, daemon=True)
        t.start()


if __name__ == "__main__":
    app = GFNSViewer()
    app.mainloop()